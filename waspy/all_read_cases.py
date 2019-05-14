from __future__ import division, print_function
import sys
major_python_version = sys.version_info[0]

if major_python_version == 2:
    import tkFont
    import Tkinter as Tk
else:
    import tkinter as Tk
    from tkinter import font as tkFont

from six import iteritems
import numpy as np
from openmdao.recorders.sqlite_reader import SqliteCaseReader

import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['lines.linewidth'] = 2
matplotlib.rcParams['axes.edgecolor'] = 'gray'
matplotlib.rcParams['axes.linewidth'] = 0.5
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2Tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as manimation
import sqlitedict
import niceplots

#####################
# User-set parameters
#####################

def read_db(db_name):
    output_dict = {}

    cr = SqliteCaseReader(db_name, pre_load=True)
    last_case = next(reversed(cr.get_cases('driver')))

    names = []
    for key in cr.system_metadata.keys():
        try:
            surfaces = cr.system_metadata[key]['component_options']['surfaces']
            for surface in surfaces:
                names.append(surface['name'])
            break
        except:
            pass

    obj_keys = last_case.get_objectives()
    output_dict['opt'] = True
    obj_key = list(obj_keys.keys())[0]

    output_dict['twist'] = []
    output_dict['mesh'] = []
    output_dict['def_mesh'] = []
    output_dict['def_mesh_maneuver'] = []
    output_dict['spar_thickness'] = []
    output_dict['skin_thickness'] = []
    output_dict['t_over_c'] = []
    sec_forces = []
    sec_forces_maneuver = []
    normals = []
    normals_maneuver = []
    widths = []
    widths_maneuver = []
    output_dict['lift'] = []
    output_dict['lift_ell'] = []
    output_dict['lift_maneuver'] = []
    output_dict['lift_ell_maneuver'] = []
    output_dict['lift_ell_span'] = []
    output_dict['vonmises'] = []
    alpha_maneuver = []
    rho = []
    rho_maneuver = []
    output_dict['alpha'] = []
    output_dict['v'] = []
    output_dict['CL'] = []
    output_dict['CD'] = []
    output_dict['AR'] = []
    output_dict['S_ref'] = []
    output_dict['obj'] = []
    output_dict['struct_masses'] = []
    output_dict['cg'] = []
    output_dict['point_mass_locations'] = []
    output_dict['total_weight'] = []

    pt_names = ['AS_point_0', 'AS_point_1']
    pt_name = pt_names[0]

    n_names = len(names)

    # loop to pull data out of case reader and organize it into arrays
    for i, case in enumerate(cr.get_cases()):

        output_dict['obj'].append(case.outputs[obj_key])

        # Loop through each of the surfaces
        for name in names:

            output_dict['mesh'].append(case.outputs[name+'.mesh'])
            output_dict['skin_thickness'].append(case.outputs[name+'.skin_thickness'])
            output_dict['spar_thickness'].append(case.outputs[name+'.spar_thickness'])
            output_dict['t_over_c'].append(case.outputs[name+'.t_over_c'])
            output_dict['struct_masses'].append(case.outputs[name+'.structural_mass'])

            vm_var_name = '{pt_name}.{surf_name}_perf.vonmises'.format(pt_name=pt_names[1], surf_name=name)
            output_dict['vonmises'].append(np.max(case.outputs[vm_var_name], axis=1))

            def_mesh_var_name = '{pt_name}.coupled.{surf_name}.def_mesh'.format(pt_name=pt_name, surf_name=name)
            output_dict['def_mesh'].append(case.outputs[def_mesh_var_name])

            def_mesh_var_name = '{pt_name}.coupled.{surf_name}.def_mesh'.format(pt_name=pt_names[1], surf_name=name)
            output_dict['def_mesh_maneuver'].append(case.outputs[def_mesh_var_name])

            normals_var_name = '{pt_name}.coupled.{surf_name}.normals'.format(pt_name=pt_name, surf_name=name)
            normals.append(case.outputs[normals_var_name])

            normals_var_name = '{pt_name}.coupled.{surf_name}.normals'.format(pt_name=pt_names[1], surf_name=name)
            normals_maneuver.append(case.outputs[normals_var_name])

            widths_var_name = '{pt_name}.coupled.{surf_name}.widths'.format(pt_name=pt_name, surf_name=name)
            widths.append(case.outputs[widths_var_name])

            widths_var_name = '{pt_name}.coupled.{surf_name}.widths'.format(pt_name=pt_names[1], surf_name=name)
            widths_maneuver.append(case.outputs[widths_var_name])

            sec_forces.append(case.outputs[pt_name+'.coupled.aero_states.' + name + '_sec_forces'])
            sec_forces_maneuver.append(case.outputs[pt_names[1]+'.coupled.aero_states.' + name + '_sec_forces'])

            cl_var_name = '{pt_name}.{surf_name}_perf.CL1'.format(pt_name=pt_name, surf_name=name)
            output_dict['CL'].append(case.outputs[cl_var_name])

            cd_var_name = '{pt_name}.CD'.format(pt_name=pt_name)
            output_dict['CD'].append(case.outputs[cd_var_name])

            S_ref_var_name = '{pt_name}.coupled.{surf_name}.aero_geom.S_ref'.format(pt_name=pt_name, surf_name=name)
            output_dict['S_ref'].append(case.outputs[S_ref_var_name])

            output_dict['twist'].append(case.outputs[name+'.geometry.twist'])

        alpha_maneuver.append(case.outputs['alpha_maneuver'] * np.pi / 180.)
        rho.append(case.outputs['rho'])
        rho_maneuver.append(case.outputs['rho'])
        output_dict['alpha'].append(case.outputs['alpha'] * np.pi / 180.)
        output_dict['v'].append(case.outputs['v'])
        output_dict['cg'].append(case.outputs['{pt_name}.cg'.format(pt_name=pt_name)])
        output_dict['total_weight'].append(case.outputs['AS_point_0.total_perf.total_weight'])

        # If there are point masses, save them
        try:
            output_dict['point_mass_locations'].append(case.outputs['point_mass_locations'])
            output_dict['point_masses_exist'] = True
        except:
            output_dict['point_masses_exist'] = False
            pass

    yield_stress_dict = {}

    for name in names:
        surface = cr.system_metadata[name]['component_options']['surface']
        yield_stress_dict[name + '_yield_stress'] = surface['yield']

        output_dict[name + '_fem_origin'] = (surface['data_x_upper'][0].real *(surface['data_y_upper'][0].real-surface['data_y_lower'][0].real) + \
        surface['data_x_upper'][-1].real*(surface['data_y_upper'][-1].real-surface['data_y_lower'][-1].real)) / \
        ( (surface['data_y_upper'][0].real-surface['data_y_lower'][0].real) + (surface['data_y_upper'][-1].real-surface['data_y_lower'][-1].real))

        le_te_coords = np.array([surface['data_x_upper'][0].real, surface['data_x_upper'][-1].real, surface['wing_weight_ratio']])

        np.save(str('temp_' + name + '_le_te'), le_te_coords)

    num_iters = np.max([int(len(output_dict['mesh']) / n_names), 1])

    # For now, do not mirror the parameters across the symmetry plane
    mirror = False
    if mirror:

        new_mesh = []
        new_skinthickness = []
        new_sparthickness = []
        new_toverc = []
        new_vonmises = []
        new_twist = []
        new_sec_forces = []
        new_sec_forces_maneuver = []
        new_def_mesh = []
        new_def_mesh_maneuver = []
        new_widths = []
        new_widths_maneuver = []
        new_normals = []
        new_normals_maneuver = []

        for i in range(num_iters):
            for j, name in enumerate(names):
                mirror_mesh = output_dict['mesh'][i*n_names+j].copy()
                mirror_mesh[:, :, 1] *= -1.
                mirror_mesh = mirror_mesh[:, ::-1, :][:, 1:, :]
                new_mesh.append(np.hstack((output_dict['mesh'][i*n_names+j], mirror_mesh)))

                sparthickness = output_dict['spar_thickness'][i*n_names+j]
                new_sparthickness.append(np.hstack((sparthickness[0], sparthickness[0][::-1])))
                skinthickness = output_dict['skin_thickness'][i*n_names+j]
                new_skinthickness.append(np.hstack((skinthickness[0], skinthickness[0][::-1])))
                toverc = output_dict['t_over_c'][i*n_names+j]
                new_toverc.append(np.hstack((toverc[0], toverc[0][::-1])))
                vonmises = output_dict['vonmises'][i*n_names+j]
                new_vonmises.append(np.hstack((vonmises, vonmises[::-1])))

                mirror_mesh = output_dict['def_mesh'][i*n_names+j].copy()
                mirror_mesh[:, :, 1] *= -1.
                mirror_mesh = mirror_mesh[:, ::-1, :][:, 1:, :]
                new_def_mesh.append(np.hstack((output_dict['def_mesh'][i*n_names+j], mirror_mesh)))

                mirror_normals = normals[i*n_names+j].copy()
                mirror_normals = mirror_normals[:, ::-1, :][:, 1:, :]
                new_normals.append(np.hstack((normals[i*n_names+j], mirror_normals)))

                mirror_forces = sec_forces[i*n_names+j].copy()
                mirror_forces = mirror_forces[:, ::-1, :]
                new_sec_forces.append(np.hstack((sec_forces[i*n_names+j], mirror_forces)))

                mirror_mesh_maneuver = output_dict['def_mesh_maneuver'][i*n_names+j].copy()
                mirror_mesh_maneuver[:, :, 1] *= -1.
                mirror_mesh_maneuver = mirror_mesh_maneuver[:, ::-1, :][:, 1:, :]
                new_def_mesh_maneuver.append(np.hstack((output_dict['def_mesh_maneuver'][i*n_names+j], mirror_mesh_maneuver)))

                mirror_normals_maneuver = normals_maneuver[i*n_names+j].copy()
                mirror_normals_maneuver = mirror_normals_maneuver[:, ::-1, :][:, 1:, :]
                new_normals_maneuver.append(np.hstack((normals_maneuver[i*n_names+j], mirror_normals_maneuver)))

                mirror_forces_maneuver = sec_forces_maneuver[i*n_names+j].copy()
                mirror_forces_maneuver = mirror_forces_maneuver[:, ::-1, :]
                new_sec_forces_maneuver.append(np.hstack((sec_forces_maneuver[i*n_names+j], mirror_forces_maneuver)))

                new_widths.append(np.hstack((widths[i*n_names+j], widths[i*n_names+j][::-1])))
                new_widths_maneuver.append(np.hstack((widths_maneuver[i*n_names+j], widths_maneuver[i*n_names+j][::-1])))
                twist = output_dict['twist'][i*n_names+j]
                new_twist.append(np.hstack((twist[0], twist[0][::-1][1:])))

        output_dict['mesh'] = new_mesh

        output_dict['skin_thickness'] = new_skinthickness
        output_dict['spar_thickness'] = new_sparthickness
        output_dict['t_over_c'] = new_toverc
        output_dict['vonmises'] = new_vonmises

        output_dict['def_mesh'] = new_def_mesh
        output_dict['twist'] = new_twist
        widths = new_widths
        widths_maneuver = new_widths_maneuver
        sec_forces = new_sec_forces
        sec_forces_maneuver = new_sec_forces_maneuver

    for i in range(num_iters):
        for j, name in enumerate(names):
            m_vals = output_dict['mesh'][i*n_names+j].copy()
            a = output_dict['alpha'][i]
            cosa = np.cos(a)
            sina = np.sin(a)

            forces = np.sum(sec_forces[i*n_names+j], axis=0)

            lift = (-forces[:, 0] * sina + forces[:, 2] * cosa) / \
                widths[i*n_names+j]/0.5/rho[i][0]/output_dict['v'][i][0]**2
            a_maneuver = alpha_maneuver[i]
            cosa_maneuver = np.cos(a_maneuver)
            sina_maneuver = np.sin(a_maneuver)
            forces_maneuver = np.sum(sec_forces_maneuver[i*n_names+j], axis=0)
            lift_maneuver= (-forces_maneuver[:, 0] * sina_maneuver + forces_maneuver[:, 2] * cosa_maneuver) / \
                widths_maneuver[i*n_names+j]/0.5/rho_maneuver[i][1]/output_dict['v'][i][1]**2

            span = (m_vals[0, :, 1] / (m_vals[0, -1, 1] - m_vals[0, 0, 1]))
            span = span - span[0]

            lift_area = np.sum(lift * (span[1:] - span[:-1]))
            lift_area_maneuver = np.sum(lift_maneuver * (span[1:] - span[:-1]))

            lift_ell_span = np.linspace(0., 1., 200)

            lift_ell = 4 * lift_area / np.pi * np.sqrt(1 - lift_ell_span**2)
            lift_ell = lift_ell[::-1]

            normalize_factor = max(lift_ell) / 4 * np.pi
            lift_ell = lift_ell / normalize_factor
            lift = lift / normalize_factor

            lift_ell_maneuver = 4 * lift_area_maneuver / np.pi * np.sqrt(1 - lift_ell_span**2)

            normalize_factor = max(lift_ell_maneuver) / 4 * np.pi
            lift_ell_maneuver = lift_ell_maneuver / normalize_factor
            lift_maneuver = lift_maneuver / normalize_factor

            output_dict['lift'].append(lift)
            output_dict['lift_ell'].append(lift_ell)
            output_dict['lift_maneuver'].append(lift_maneuver)
            output_dict['lift_ell_maneuver'].append(lift_ell_maneuver)
            output_dict['lift_ell_span'].append(lift_ell_span[::-1])

            wingspan = np.abs(m_vals[0, -1, 1] - m_vals[0, 0, 1])
            output_dict['AR'].append(wingspan**2 / output_dict['S_ref'][i*n_names+j])

    # # Don't recenter anything for the time being, so we get the absolute positioning.
    # # recenter def_mesh points for better viewing
    # for i in range(num_iters):
    #     center = np.zeros((3))
    #     for j in range(n_names):
    #         center += np.mean(output_dict['def_mesh'][i*n_names+j], axis=(0,1))
    #     for j in range(n_names):
    #         output_dict['def_mesh'][i*n_names+j] -= center / n_names
    #     output_dict['cg'][i] -= center / n_names
    #     if output_dict['point_masses_exist']:
    #         output_dict['point_mass_locations'][i] -= center / n_names
    #
    # # recenter mesh points for better viewing
    # for i in range(num_iters):
    #     center = np.zeros((3))
    #     for j in range(n_names):
    #         center += np.mean(output_dict['mesh'][i*n_names+j], axis=(0,1))
    #     for j in range(n_names):
    #         output_dict['mesh'][i*n_names+j] -= center / n_names


    for key in output_dict:
        if type(output_dict[key]) == list:
            if len(output_dict[key]) > 5:
                output_dict[key] = np.array(output_dict[key])

    return output_dict

folders = ['baseline', 'viscous', 'wave_drag', 'struct_weight', 'fuel_weight', 'engine_mass', 'engine_thrust']

case_keys = {
    'baseline' : 'Baseline',
    'viscous' : 'viscous drag',
    'wave_drag' : 'wave drag',
    'struct_weight' : 'struct-weight relief',
    'fuel_weight' : 'fuel-weight relief',
    'engine_mass' : 'engine-weight relief',
    'engine_thrust' : 'engine thrust loads',
}

import seaborn as sns
pal = sns.color_palette('muted')
some_colors = pal.as_hex()

colors = ['#696969'] + some_colors

def load_all_cases():
    # Loop through all the runs and load their DBs into the data dict

    data = {}
    for folder in folders:
        print(folder)
        filename = f'{folder}/aerostruct.db'
        data[folder] = read_db(filename)

    print(data[folder].keys())

    return data

def load_baselines():
    # Loop through all the runs and load their DBs into the data dict

    wings = ['CRM', 'Q400', 'tiltwing']
    data = {}
    for wing in wings:
        filename = f'{wing}/baseline/aerostruct.db'
        data[wing] = read_db(filename)

    return data

def print_results(data):
    # get max name length:
    max_name_len = max([len(folder) for folder in folders])+2

    len_header = max_name_len+3+7*13
    print("-"*len_header)
    print("                            Relative to baseline ptimized wing properties")
    print("-"*len_header)

    max_name_len = str(max_name_len)
    line_tmpl = '{:<'+max_name_len+'}|  '+'{:>10}'*8
    print(line_tmpl.format('Case', 'fuel burn', 'rel fuel burn', 'struct mass, kg', 'rel struct mass',  'drag', 'rel drag', 'TOGW', 'rel TOGW'))

    line_tmpl = '{:<'+max_name_len+'} &  '+'\\num{{{:8.1f}}} & {:8.1f} & ' * 3 + '\\num{{{:8.1f}}} & {:8.1f} \\\\'
    for idx, folder in enumerate(folders):
        struct_mass = data[folder]['struct_masses'][-1][0]
        fuelburn = data[folder]['obj'][-1][0]
        CD = data[folder]['CD'][-1][0] * 10e3
        TOGW = data[folder]['total_weight'][-1][0] / 9.81

        if idx==0:
            base_struct_mass = data[folder]['struct_masses'][-1][0]
            base_fuelburn = data[folder]['obj'][-1][0]
            base_CD = data[folder]['CD'][-1][0] * 10e3
            base_TOGW = data[folder]['total_weight'][-1][0] / 9.81

        struct_mass = data[folder]['struct_masses'][-1][0]
        fuelburn = data[folder]['obj'][-1][0]
        CD = data[folder]['CD'][-1][0] * 10e3
        TOGW = data[folder]['total_weight'][-1][0] / 9.81

        del_struct_mass = (struct_mass - base_struct_mass) / base_struct_mass * 100.
        del_fuelburn = (fuelburn - base_fuelburn) / base_fuelburn * 100.
        del_CD = (CD - base_CD) / base_CD * 100.
        del_TOGW = (TOGW - base_TOGW) / base_TOGW * 100.

        if idx > 0:
            case = 'w/o ' + case_keys[folder]
        else:
            case = case_keys[folder]

        print(line_tmpl.format(case, fuelburn, del_fuelburn, struct_mass, del_struct_mass, CD, del_CD, TOGW, del_TOGW))

def compute_span(mesh):
    span = (mesh[0, :, 1] / (mesh[0, -1, 1] - mesh[0, 0, 1]))
    span = span - span[0] - 1
    span *= -1
    return span

def get_flat_data(mesh, y_data):
    # Span is at the nodes, or fenceposts
    span = compute_span(mesh)
    repeats = np.ones((len(span)), dtype='int') * 2
    repeats[0] = repeats[-1] = 1

    span = np.repeat(span, repeats)

    # y_data are the fences, in between, per panel
    flat_y_data = np.repeat(y_data, 2)

    return span, flat_y_data

def plot_thicknesses(data, cases, live_plot=True, annotate_data={}):
    plt.figure()

    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        skin_thickness = case_data['skin_thickness'][-1][0]

        span, skin_thickness = get_flat_data(mesh, skin_thickness)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            plt.plot(span, skin_thickness, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            plt.plot(span, skin_thickness, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            plt.annotate(label, annotate_data[case], color=colors[idx])

    if live_plot:
        niceplots.draggable_legend()
    niceplots.adjust_spines()

    plt.xlabel('Normalized span')
    plt.ylabel('Skin thickness [m]')

    if live_plot:
        plt.show()
    else:
        # plt.tight_layout()
        plt.savefig('thicknesses.pdf')

def plot_lifts(data, cases, live_plot=True, annotate_data={}):
    plt.figure()

    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        lift = case_data['lift'][-1]

        span = compute_span(mesh)

        span = (span[1:] + span[:-1]) / 2

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            plt.plot(span, lift, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            plt.plot(span, lift, label=label, color=colors[idx], zorder=100)
            plt.plot(case_data['lift_ell_span'][-1], case_data['lift_ell'][-1], '--', color='gray', label='Elliptical')

        if not live_plot:
            plt.annotate(label, annotate_data[case], color=colors[idx])
            if idx == 0:
                plt.annotate('Elliptical', annotate_data['elliptical'], color='gray')


    if live_plot:
        niceplots.draggable_legend()
    niceplots.adjust_spines()

    plt.xlabel('Normalized span')
    plt.ylabel('Normalized lift distribution')

    if live_plot:
        plt.show()
    else:
        # plt.tight_layout()
        plt.savefig('lifts.pdf')


def plot_tc(data, cases, live_plot=True, annotate_data={}):
    plt.figure()

    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        t_over_c = case_data['t_over_c'][-1][0]

        span, t_over_c = get_flat_data(mesh, t_over_c)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            plt.plot(span, t_over_c, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            plt.plot(span, t_over_c, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            plt.annotate(label, annotate_data[case], color=colors[idx])

    if live_plot:
        niceplots.draggable_legend()
    niceplots.adjust_spines()

    plt.xlabel('Normalized span')
    plt.ylabel('Thickness-to-chord ratio')

    if live_plot:
        plt.show()
    else:
        # plt.tight_layout()
        plt.savefig('tc.pdf')

def plot_twist(data, cases, live_plot=True, annotate_data={}):
    plt.figure()

    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        twist = case_data['twist'][-1][0]

        span = compute_span(mesh)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            plt.plot(span, twist, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            plt.plot(span, twist, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            plt.annotate(label, annotate_data[case], color=colors[idx])

    if live_plot:
        niceplots.draggable_legend()
    niceplots.adjust_spines()

    plt.xlabel('Normalized span')
    plt.ylabel('Twist [degrees]')

    if live_plot:
        plt.show()
    else:
        # plt.tight_layout()
        plt.savefig('twists.pdf')



def ax_plot_thicknesses(ax, data, cases, live_plot=True, annotate_data={}):
    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        skin_thickness = case_data['skin_thickness'][-1][0]

        span, skin_thickness = get_flat_data(mesh, skin_thickness)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            ax.plot(span, skin_thickness, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            ax.plot(span, skin_thickness, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            ax.annotate(label, annotate_data[case], color=colors[idx])

def ax_plot_lifts(ax, data, cases, live_plot=True, annotate_data={}):

    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        lift = case_data['lift'][-1]

        span = compute_span(mesh)

        span = (span[1:] + span[:-1]) / 2

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            ax.plot(span, lift, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            ax.plot(span, lift, label=label, color=colors[idx], zorder=100)
            ax.plot(case_data['lift_ell_span'][-1], case_data['lift_ell'][-1], '--', color='gray', label='Elliptical')

        if not live_plot:
            ax.annotate(label, annotate_data[case], color=colors[idx])
            if idx == 0:
                ax.annotate('Elliptical', annotate_data['elliptical'], color='gray')

def ax_plot_tc(ax, data, cases, live_plot=True, annotate_data={}):
    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        t_over_c = case_data['t_over_c'][-1][0]

        span, t_over_c = get_flat_data(mesh, t_over_c)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            ax.plot(span, t_over_c, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            ax.plot(span, t_over_c, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            ax.annotate(label, annotate_data[case], color=colors[idx])

def ax_plot_twist(ax, data, cases, live_plot=True, annotate_data={}):
    for idx, case in enumerate(cases):
        case_data = data[case]

        mesh = case_data['mesh'][-1]
        twist = case_data['twist'][-1][0]

        span = compute_span(mesh)

        if idx > 0:
            label = 'w/o ' + case_keys[case]
            ax.plot(span, twist, label=label, color=colors[idx])
        else:
            label = case_keys[case]
            ax.plot(span, twist, label=label, color=colors[idx], zorder=100)

        if not live_plot:
            ax.annotate(label, annotate_data[case], color=colors[idx])
