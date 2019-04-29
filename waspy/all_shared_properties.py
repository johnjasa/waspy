from __future__ import division, print_function
import numpy as np

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint
from openmdao.api import IndepVarComp, Problem, ScipyOptimizeDriver, SqliteRecorder, ExecComp, SqliteRecorder
from openaerostruct.structures.wingbox_fuel_vol_delta import WingboxFuelVolDelta
from openaerostruct.utils.constants import grav_constant


def add_geometry_to_problem(prob, surfaces):

    # Loop over each surface in the surfaces list
    for surface in surfaces:

        # Get the surface name and create a group to contain components
        # only for this surface
        name = surface['name']

        aerostruct_group = AerostructGeometry(surface=surface)

        # Add group to the problem with the name of the surface.
        prob.model.add_subsystem(name, aerostruct_group)

    return prob

def connect_problem(prob, surfaces, case_settings):
    # Loop through and add a certain number of aerostruct points
    for i in range(2):

        point_name = 'AS_point_{}'.format(i)
        # Connect the parameters within the model for each aerostruct point

        # Create the aero point group and add it to the model
        AS_point = AerostructPoint(surfaces=surfaces, internally_connect_fuelburn=False)

        prob.model.add_subsystem(point_name, AS_point)

        # Connect flow properties to the analysis point
        prob.model.connect('v', point_name + '.v', src_indices=[i])
        prob.model.connect('Mach_number', point_name + '.Mach_number', src_indices=[i])
        prob.model.connect('re', point_name + '.re', src_indices=[i])
        prob.model.connect('rho', point_name + '.rho', src_indices=[i])
        prob.model.connect('CT', point_name + '.CT')
        prob.model.connect('R', point_name + '.R')
        prob.model.connect('W0', point_name + '.W0')
        prob.model.connect('speed_of_sound', point_name + '.speed_of_sound', src_indices=[i])
        prob.model.connect('empty_cg', point_name + '.empty_cg')
        prob.model.connect('load_factor', point_name + '.load_factor', src_indices=[i])
        prob.model.connect('fuel_mass', point_name + '.total_perf.L_equals_W.fuelburn')
        prob.model.connect('fuel_mass', point_name + '.total_perf.CG.fuelburn')

        for surface in surfaces:

            name = surface['name']

            if surface['distributed_fuel_weight'] or surface['struct_weight_relief']:
                prob.model.connect('load_factor', point_name + '.coupled.load_factor', src_indices=[i])

            com_name = point_name + '.' + name + '_perf.'
            prob.model.connect(name + '.local_stiff_transformed', point_name + '.coupled.' + name + '.local_stiff_transformed')
            prob.model.connect(name + '.nodes', point_name + '.coupled.' + name + '.nodes')

            # Connect aerodyamic mesh to coupled group mesh
            prob.model.connect(name + '.mesh', point_name + '.coupled.' + name + '.mesh')

            if surface['struct_weight_relief']:
                prob.model.connect(name + '.element_mass', point_name + '.coupled.' + name + '.element_mass')

            # Connect performance calculation variables
            prob.model.connect(name + '.nodes', com_name + 'nodes')
            prob.model.connect(name + '.cg_location', point_name + '.' + 'total_perf.' + name + '_cg_location')
            prob.model.connect(name + '.structural_mass', point_name + '.' + 'total_perf.' + name + '_structural_mass')

            # Connect wingbox properties to von Mises stress calcs
            prob.model.connect(name + '.Qz', com_name + 'Qz')
            prob.model.connect(name + '.J', com_name + 'J')
            prob.model.connect(name + '.A_enc', com_name + 'A_enc')
            prob.model.connect(name + '.htop', com_name + 'htop')
            prob.model.connect(name + '.hbottom', com_name + 'hbottom')
            prob.model.connect(name + '.hfront', com_name + 'hfront')
            prob.model.connect(name + '.hrear', com_name + 'hrear')

            prob.model.connect(name + '.spar_thickness', com_name + 'spar_thickness')
            prob.model.connect(name + '.t_over_c', com_name + 't_over_c')

            coupled_name = point_name + '.coupled.' + name
            if case_settings['engine_thrust']:
                prob.model.connect('engine_thrusts', coupled_name + '.engine_thrusts')
            if case_settings['engine_mass']:
                prob.model.connect('point_masses', coupled_name + '.point_masses')
            if case_settings['engine_mass'] or case_settings['engine_thrust']:
                prob.model.connect('point_mass_locations', coupled_name + '.point_mass_locations')

    prob.model.connect('alpha', 'AS_point_0' + '.alpha')
    prob.model.connect('alpha_maneuver', 'AS_point_1' + '.alpha')

    if case_settings['distributed_fuel_weight']:
        # Here we add the fuel volume constraint componenet to the model
        prob.model.add_subsystem('fuel_vol_delta', WingboxFuelVolDelta(surface=surface))
        prob.model.connect('wing.struct_setup.fuel_vols', 'fuel_vol_delta.fuel_vols')
        prob.model.connect('AS_point_0.fuelburn', 'fuel_vol_delta.fuelburn')

        prob.model.connect('wing.struct_setup.fuel_vols', 'AS_point_0.coupled.wing.struct_states.fuel_vols')
        prob.model.connect('wing.struct_setup.fuel_vols', 'AS_point_1.coupled.wing.struct_states.fuel_vols')

        prob.model.connect('fuel_mass', 'AS_point_0.coupled.wing.struct_states.fuel_mass')
        prob.model.connect('fuel_mass', 'AS_point_1.coupled.wing.struct_states.fuel_mass')

    comp = ExecComp('fuel_diff = (fuel_mass - fuelburn) / fuelburn', units='kg')
    prob.model.add_subsystem('fuel_diff', comp,
        promotes_inputs=['fuel_mass'],
        promotes_outputs=['fuel_diff'])
    prob.model.connect('AS_point_0.fuelburn', 'fuel_diff.fuelburn')

    return prob

def add_driver(prob, case_settings):
    from openmdao.api import pyOptSparseDriver
    prob.driver = pyOptSparseDriver()
    prob.driver.options['optimizer'] = "SNOPT"
    prob.driver.opt_settings['Major optimality tolerance'] = 1e-6
    prob.driver.opt_settings['Major feasibility tolerance'] = 1e-6
    prob.driver.opt_settings['Major iterations limit'] = 200
    prob.driver.opt_settings['Verify level'] = -1
    prob.driver.opt_settings['Nonderivative linesearch'] = None

    recorder = SqliteRecorder("aerostruct.db")
    prob.driver.add_recorder(recorder)

    # We could also just use prob.driver.recording_options['includes']=['*'] here, but for large meshes the database file becomes extremely large. So we just select the variables we need.
    prob.driver.recording_options['includes'] = [
        'alpha', 'rho', 'v', 'cg',
        'AS_point_1.cg', 'AS_point_0.cg',
        'AS_point_0.coupled.wing_loads.loads',
        'AS_point_1.coupled.wing_loads.loads',
        'AS_point_0.coupled.wing.normals',
        'AS_point_1.coupled.wing.normals',
        'AS_point_0.coupled.wing.widths',
        'AS_point_1.coupled.wing.widths',
        'AS_point_0.coupled.aero_states.wing_sec_forces',
        'AS_point_1.coupled.aero_states.wing_sec_forces',
        'AS_point_0.wing_perf.CL1',
        'AS_point_1.wing_perf.CL1',
        'AS_point_0.coupled.wing.S_ref',
        'AS_point_1.coupled.wing.S_ref',
        'wing.geometry.twist',
        'wing.mesh',
        'wing.skin_thickness',
        'wing.spar_thickness',
        'wing.t_over_c',
        'wing.structural_mass',
        'AS_point_0.wing_perf.vonmises',
        'AS_point_1.wing_perf.vonmises',
        'AS_point_0.coupled.wing.def_mesh',
        'AS_point_1.coupled.wing.def_mesh',
        'AS_point_0.CD',
        'AS_point_1.CD',
        'AS_point_0.total_perf.total_weight',
        'AS_point_1.total_perf.total_weight',
        'AS_point_0.CM',
        'AS_point_1.CM',
        'AS_point_0.wing_perf.failure',
        'AS_point_1.wing_perf.failure',
        'AS_point_0.wing_perf.CDv',
        'AS_point_1.wing_perf.CDv',
        'AS_point_0.wing_perf.aero_funcs.CDw',
        'AS_point_1.wing_perf.aero_funcs.CDw',
        'wing.struct_setup.fuel_vols',
        'wing.A',
        'wing.A_enc',
        'wing.A_int',
        'wing.Iy',
        'wing.Qz',
        'wing.Iz',
        'wing.J',
        ]

    if case_settings['engine_mass'] or case_settings['engine_thrust']:
        prob.driver.recording_options['includes'].extend(['point_mass_locations'])

    prob.driver.recording_options['record_objectives'] = True
    prob.driver.recording_options['record_constraints'] = True
    prob.driver.recording_options['record_desvars'] = True
    prob.driver.recording_options['record_inputs'] = True

    return prob

def run_problem(prob):

    prob.driver.options['debug_print'] = ['desvars', 'nl_cons', 'objs']

    # Set up the problem
    prob.setup()

    from openmdao.api import view_model
    view_model(prob, show_browser=False)

    prob.run_driver()
