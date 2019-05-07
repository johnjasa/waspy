from __future__ import division, print_function
import numpy as np

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint
from openmdao.api import IndepVarComp, Problem, ScipyOptimizeDriver, SqliteRecorder, ExecComp, SqliteRecorder
from openaerostruct.structures.wingbox_fuel_vol_delta import WingboxFuelVolDelta
from openaerostruct.utils.constants import grav_constant


def get_surfaces(case_settings):

    feet_to_m = 0.3048

    # Total number of nodes to use in the spanwise (num_y) and
    # chordwise (num_x) directions. Vary these to change the level of fidelity.
    num_y = 51
    num_x = 5

    # Create a mesh dictionary to feed to generate_mesh to actually create
    # the mesh array.
    mesh_dict = {'num_y' : num_y,
                 'num_x' : num_x,
                 'wing_type' : 'rect',
                 'symmetry' : True,
                 'span_cos_spacing' : 0.5,
                 'span' : 52.5 * feet_to_m,
                 'root_chord' : 4.564 * feet_to_m,
                 }

    chord_cp = np.ones(8)
    chord_cp[1] = 0.65
    chord_cp[0] = 0.6

    xshear_cp = np.zeros(8)
    xshear_cp[1] = .35
    xshear_cp[0] = .4

    mesh = generate_mesh(mesh_dict)

    # Airfoil information for NACA-0015
    upper_x = np.array([0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6], dtype = 'complex128')
    upper_y = np.array([0.05853, 0.06682, 0.07172, 0.07427, 0.07502, 0.07254, 0.06617, 0.05704], dtype = 'complex128')
    lower_x = np.array([0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6], dtype = 'complex128')
    lower_y = np.array([-0.05853, -0.06682, -0.07172, -0.07427, -0.07502, -0.07254, -0.06617, -0.05704], dtype = 'complex128')

    surf_dict = {
                # Wing definition
                'name' : 'wing',        # name of the surface
                'symmetry' : True,     # if true, model one half of wing
                'S_ref_type' : 'wetted', # how we compute the wing area,
                                         # can be 'wetted' or 'projected'
                'mesh' : mesh,
                'twist_cp' : np.ones((4)) * 5.,
                'chord_cp' : chord_cp,
                'xshear_cp' : xshear_cp,

                'fem_model_type' : 'wingbox',
                'data_x_upper' : upper_x,
                'data_x_lower' : lower_x,
                'data_y_upper' : upper_y,
                'data_y_lower' : lower_y,

                'spar_thickness_cp' : np.ones((4)) * 0.002, # [m]
                'skin_thickness_cp' : np.ones((4)) * 0.002, # [m]

                'original_wingbox_airfoil_t_over_c' : 0.15,

                # Aerodynamic deltas.
                # These CL0 and CD0 values are added to the CL and CD
                # obtained from aerodynamic analysis of the surface to get
                # the total CL and CD.
                # These CL0 and CD0 values do not vary wrt alpha.
                # They can be used to account for things that are not included, such as contributions from the fuselage, nacelles, tail surfaces, etc.
                'CL0' : 0.0,
                'CD0' : 0.011,

                'with_viscous' : case_settings['with_viscous'],  # if true, compute viscous drag
                'with_wave' : case_settings['with_wave'],     # if true, compute wave drag

                # Airfoil properties for viscous drag calculation
                'k_lam' : 0.05,         # percentage of chord with laminar
                                        # flow, used for viscous drag
                'c_max_t' : .38,        # chordwise location of maximum thickness
                't_over_c_cp' : np.array([0.1, 0.1, 0.15, 0.15]),

                # Structural values are based on aluminum 7075
                'E' : 73.1e9,              # [Pa] Young's modulus
                'G' : (73.1e9/2/1.33),     # [Pa] shear modulus (calculated using E and the Poisson's ratio here)
                'yield' : (420.e6 / 1.5),  # [Pa] allowable yield stress
                'mrho' : 2.78e3,           # [kg/m^3] material density
                'strength_factor_for_upper_skin' : 1.0, # the yield stress is multiplied by this factor for the upper skin

                'wing_weight_ratio' : 2.5 * 0.8,
                'exact_failure_constraint' : False, # if false, use KS function

                'struct_weight_relief' : case_settings['struct_weight_relief'],
                'distributed_fuel_weight' : case_settings['distributed_fuel_weight'],

                'fuel_density' : 803.,      # [kg/m^3] fuel density (only needed if the fuel-in-wing volume constraint is used)
                'Wf_reserve' : 150.,       # [kg] reserve fuel mass

                }

    if case_settings['engine_mass'] or case_settings['engine_thrust']:
        surf_dict['n_point_masses'] = 2

    if case_settings['planform_opt']:
        # surf_dict['chord_cp'] = np.array([3., 4., 5., 6., 7., 10.])
        surf_dict['span'] = 15.
        surf_dict['sweep'] = 0.

    surfaces = [surf_dict]

    return surfaces

def add_prob_vars(case_settings, surfaces):
    # Create the problem and assign the model group
    prob = Problem()

    # Add problem information as an independent variables component
    indep_var_comp = IndepVarComp()
    indep_var_comp.add_output('v', val=np.array([102.9, .75 * 102.9]), units='m/s')
    indep_var_comp.add_output('alpha', val=0., units='deg')
    indep_var_comp.add_output('alpha_maneuver', val=0., units='deg')
    indep_var_comp.add_output('Mach_number', val=np.array([0.305, 0.75 * 0.305]))
    indep_var_comp.add_output('re',val=np.array([6.03e6, 0.75 * 6.03e6]),  units='1/m')
    indep_var_comp.add_output('rho', val=np.array([1.05549, 1.225]), units='kg/m**3')
    indep_var_comp.add_output('CT', val=0.45/3600, units='1/s')
    indep_var_comp.add_output('R', val=0.74e6, units='m')
    indep_var_comp.add_output('speed_of_sound', val= np.array([334.4, 342.]), units='m/s')
    indep_var_comp.add_output('load_factor', val=np.array([1., 2.5]))
    indep_var_comp.add_output('empty_cg', val=np.zeros((3)), units='m')
    indep_var_comp.add_output('fuel_mass', val=800., units='kg')

    if case_settings['engine_mass'] or case_settings['engine_thrust']:
        point_mass_locations = np.array([[-0.85, -3., 0.15],
                                         [-0.55, -6., 0.15]])
        indep_var_comp.add_output('point_mass_locations', val=point_mass_locations, units='m')

    if case_settings['engine_thrust']:
        engine_thrusts = np.array([[250., 250.]])
        indep_var_comp.add_output('engine_thrusts', val=engine_thrusts, units='N')

    # TODO : need to fix this one too
    if case_settings['engine_mass']:
        indep_var_comp.add_output('W0_without_point_masses', val=6000. + surfaces[0]['Wf_reserve'] - 350.,  units='kg')

        prob.model.add_subsystem('W0_comp',
            ExecComp('W0 = W0_without_point_masses + sum(point_masses)', units='kg', point_masses=np.zeros((2))),
            promotes=['*'])

        point_masses = np.array([[175., 175.]])
        indep_var_comp.add_output('point_masses', val=point_masses, units='kg')

    else:
        indep_var_comp.add_output('W0', val=6000 + surfaces[0]['Wf_reserve'],  units='kg')

    prob.model.add_subsystem('prob_vars',
         indep_var_comp,
         promotes=['*'])

    return prob

def add_opt_problem(prob, case_settings):
    prob.model.add_objective('AS_point_0.fuelburn', ref=1.e3)

    prob.model.add_design_var('wing.twist_cp', lower=-15., upper=15., scaler=0.1)
    prob.model.add_design_var('wing.spar_thickness_cp', lower=0.001, upper=0.1, scaler=1e2)
    prob.model.add_design_var('wing.skin_thickness_cp', lower=0.001, upper=0.1, scaler=1e2)
    prob.model.add_design_var('wing.geometry.t_over_c_cp', lower=0.07, upper=0.2, scaler=0.1)
    prob.model.add_design_var('fuel_mass', lower=0., upper=2e5, scaler=1e-3)
    prob.model.add_design_var('alpha_maneuver', lower=-15., upper=55)

    # Don't actually do planform opt please, these values are wrong
    if case_settings['planform_opt']:
        prob.model.add_design_var('wing.geometry.span', lower=20., upper=50., scaler=1.)
        prob.model.add_design_var('wing.sweep', lower=-20., upper=20., scaler=1.)
        # prob.model.add_design_var('wing.geometry.chord_cp', lower=5., upper=20.)
        # need area constraint
        S_ref = 414.8
        prob.model.add_constraint('AS_point_0.coupled.wing.S_ref', equals=S_ref)

    prob.model.add_constraint('AS_point_0.CL', equals=0.5)
    prob.model.add_constraint('AS_point_1.L_equals_W', equals=0.)
    prob.model.add_constraint('AS_point_1.wing_perf.failure', upper=0.)

    prob.model.add_constraint('fuel_diff', equals=0., scaler=0.1)

    if case_settings['distributed_fuel_weight']:
        prob.model.add_constraint('fuel_vol_delta.fuel_vol_delta', lower=0.)

    return prob
