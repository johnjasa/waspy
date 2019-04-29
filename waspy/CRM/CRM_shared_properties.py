from __future__ import division, print_function
import numpy as np

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint
from openmdao.api import IndepVarComp, Problem, ScipyOptimizeDriver, SqliteRecorder, ExecComp, SqliteRecorder
from openaerostruct.structures.wingbox_fuel_vol_delta import WingboxFuelVolDelta
from openaerostruct.utils.constants import grav_constant


def get_surfaces(case_settings):

    # Provide coordinates for a portion of an airfoil for the wingbox cross-section as an nparray with dtype=complex (to work with the complex-step approximation for derivatives).
    # These should be for an airfoil with the chord scaled to 1.
    # We use the 10% to 60% portion of the NASA SC2-0612 airfoil for this case
    # We use the coordinates available from airfoiltools.com. Using such a large number of coordinates is not necessary.
    # The first and last x-coordinates of the upper and lower surfaces must be the same

    upper_x = np.array([0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.6], dtype = 'complex128')
    lower_x = np.array([0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.6], dtype = 'complex128')
    upper_y = np.array([ 0.0447,  0.046,  0.0472,  0.0484,  0.0495,  0.0505,  0.0514,  0.0523,  0.0531,  0.0538, 0.0545,  0.0551,  0.0557, 0.0563,  0.0568, 0.0573,  0.0577,  0.0581,  0.0585,  0.0588,  0.0591,  0.0593,  0.0595,  0.0597,  0.0599,  0.06,    0.0601,  0.0602,  0.0602,  0.0602,  0.0602,  0.0602,  0.0601,  0.06,    0.0599,  0.0598,  0.0596,  0.0594,  0.0592,  0.0589,  0.0586,  0.0583,  0.058,   0.0576,  0.0572,  0.0568,  0.0563,  0.0558,  0.0553,  0.0547,  0.0541], dtype = 'complex128')
    lower_y = np.array([-0.0447, -0.046, -0.0473, -0.0485, -0.0496, -0.0506, -0.0515, -0.0524, -0.0532, -0.054, -0.0547, -0.0554, -0.056, -0.0565, -0.057, -0.0575, -0.0579, -0.0583, -0.0586, -0.0589, -0.0592, -0.0594, -0.0595, -0.0596, -0.0597, -0.0598, -0.0598, -0.0598, -0.0598, -0.0597, -0.0596, -0.0594, -0.0592, -0.0589, -0.0586, -0.0582, -0.0578, -0.0573, -0.0567, -0.0561, -0.0554, -0.0546, -0.0538, -0.0529, -0.0519, -0.0509, -0.0497, -0.0485, -0.0472, -0.0458, -0.0444], dtype = 'complex128')

    # Create a dictionary to store options about the surface
    mesh_dict = {'num_y' : 31,
                 'num_x' : 3,
                 'wing_type' : 'uCRM_based',
                 'symmetry' : True,
                 'chord_cos_spacing' : 0,
                 'span_cos_spacing' : 0,
                 'num_twist_cp' : 6,
                 }

    mesh, twist_cp = generate_mesh(mesh_dict)

    surf_dict = {
                # Wing definition
                'name' : 'wing',        # name of the surface
                'symmetry' : True,     # if true, model one half of wing
                'S_ref_type' : 'wetted', # how we compute the wing area,
                                         # can be 'wetted' or 'projected'
                'mesh' : mesh,
                'twist_cp' : np.array([4., 5., 8., 8., 8., 9.]),

                'fem_model_type' : 'wingbox',
                'data_x_upper' : upper_x,
                'data_x_lower' : lower_x,
                'data_y_upper' : upper_y,
                'data_y_lower' : lower_y,

                'spar_thickness_cp' : np.array([0.004, 0.005, 0.005, 0.008, 0.008, 0.01]), # [m]
                'skin_thickness_cp' : np.array([0.005, 0.01, 0.015, 0.020, 0.025, 0.026]),

                'original_wingbox_airfoil_t_over_c' : 0.12,

                # Aerodynamic deltas.
                # These CL0 and CD0 values are added to the CL and CD
                # obtained from aerodynamic analysis of the surface to get
                # the total CL and CD.
                # These CL0 and CD0 values do not vary wrt alpha.
                # They can be used to account for things that are not included, such as contributions from the fuselage, nacelles, tail surfaces, etc.
                'CL0' : 0.0,
                'CD0' : 0.0078,

                'with_viscous' : case_settings['with_viscous'],  # if true, compute viscous drag
                'with_wave' : case_settings['with_wave'],     # if true, compute wave drag

                # Airfoil properties for viscous drag calculation
                'k_lam' : 0.05,         # percentage of chord with laminar
                                        # flow, used for viscous drag
                'c_max_t' : .38,       # chordwise location of maximum thickness
                't_over_c_cp' : np.array([0.08, 0.08, 0.08, 0.10, 0.10, 0.08]),



                # Structural values are based on aluminum 7075
                'E' : 73.1e9,              # [Pa] Young's modulus
                'G' : (73.1e9/2/1.33),     # [Pa] shear modulus (calculated using E and the Poisson's ratio here)
                'yield' : (420.e6 / 1.5),  # [Pa] allowable yield stress
                'mrho' : 2.78e3,           # [kg/m^3] material density
                'strength_factor_for_upper_skin' : 1.0, # the yield stress is multiplied by this factor for the upper skin

                'wing_weight_ratio' : 1.25,
                'exact_failure_constraint' : False, # if false, use KS function

                'struct_weight_relief' : case_settings['struct_weight_relief'],
                'distributed_fuel_weight' : case_settings['distributed_fuel_weight'],

                'fuel_density' : 803.,      # [kg/m^3] fuel density (only needed if the fuel-in-wing volume constraint is used)
                'Wf_reserve' :15000.,       # [kg] reserve fuel mass

                }

    if case_settings['engine_mass'] or case_settings['engine_thrust']:
        surf_dict['n_point_masses'] = 1

    if case_settings['planform_opt']:
        # surf_dict['chord_cp'] = np.array([3., 4., 5., 6., 7., 10.])
        surf_dict['span'] = 58.6
        surf_dict['sweep'] = 0.

    surfaces = [surf_dict]

    return surfaces

def add_prob_vars(case_settings, surfaces):
    # Create the problem and assign the model group
    prob = Problem()

    # Add problem information as an independent variables component
    indep_var_comp = IndepVarComp()
    indep_var_comp.add_output('v', val=np.array([.85 * 295.07, .64 * 340.294]), units='m/s')
    indep_var_comp.add_output('alpha', val=0., units='deg')
    indep_var_comp.add_output('alpha_maneuver', val=0., units='deg')
    indep_var_comp.add_output('Mach_number', val=np.array([0.85, 0.64]))
    indep_var_comp.add_output('re',val=np.array([0.348*295.07*.85*1./(1.43*1e-5), \
                              1.225*340.294*.64*1./(1.81206*1e-5)]),  units='1/m')
    indep_var_comp.add_output('rho', val=np.array([0.348, 1.225]), units='kg/m**3')
    indep_var_comp.add_output('CT', val=0.53/3600, units='1/s')
    indep_var_comp.add_output('R', val=14.307e6, units='m')
    indep_var_comp.add_output('speed_of_sound', val= np.array([295.07, 340.294]), units='m/s')
    indep_var_comp.add_output('load_factor', val=np.array([1., 2.5]))
    indep_var_comp.add_output('empty_cg', val=np.zeros((3)), units='m')
    indep_var_comp.add_output('fuel_mass', val=10000., units='kg')

    if case_settings['engine_mass']:
        indep_var_comp.add_output('W0_without_point_masses', val=148000 + surfaces[0]['Wf_reserve'] - 7.5e3,  units='kg')

        prob.model.add_subsystem('W0_comp',
            ExecComp('W0 = W0_without_point_masses + sum(point_masses)', units='kg'),
            promotes=['*'])

        point_masses = np.array([[7.5e3]])
        point_mass_locations = np.array([[26.476,   -10.8331,   1.773]])

        indep_var_comp.add_output('point_masses', val=point_masses, units='kg')

    else:
        indep_var_comp.add_output('W0', val=148000 + surfaces[0]['Wf_reserve'], units='kg')

    if case_settings['engine_thrust']:
        engine_thrusts = np.array([[80.e3]])
        indep_var_comp.add_output('engine_thrusts', val=engine_thrusts, units='N')

    if case_settings['engine_mass'] or case_settings['engine_thrust']:
        indep_var_comp.add_output('point_mass_locations', val=point_mass_locations, units='m')

    prob.model.add_subsystem('prob_vars',
         indep_var_comp,
         promotes=['*'])

    return prob

def add_opt_problem(prob, case_settings):
    prob.model.add_objective('AS_point_0.fuelburn', scaler=1e-4)

    prob.model.add_design_var('wing.twist_cp', lower=-15., upper=15., scaler=0.1)
    prob.model.add_design_var('wing.spar_thickness_cp', lower=0.003, upper=0.1, scaler=1e2)
    prob.model.add_design_var('wing.skin_thickness_cp', lower=0.003, upper=0.1, scaler=1e2)
    prob.model.add_design_var('wing.geometry.t_over_c_cp', lower=0.07, upper=0.2, scaler=10.)
    prob.model.add_design_var('fuel_mass', lower=0., upper=2e5, scaler=1e-5)
    prob.model.add_design_var('alpha_maneuver', lower=-15., upper=15)

    if case_settings['planform_opt']:
        prob.model.add_design_var('wing.geometry.span', lower=50., upper=80., scaler=1.)
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
