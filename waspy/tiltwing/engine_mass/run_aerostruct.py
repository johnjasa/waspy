from __future__ import division, print_function

from waspy.master_functions import setup_and_run_problem


# Set these individual settings for each problem. Later functions
# will parse these and set up the model correctly.
case_settings = {
    'planform' : 'tiltwing',
    'planform_opt' : False,
    'with_viscous' : True,
    'with_wave' : True,
    'compressibility' : False,
    'struct_weight_relief' : True,
    'distributed_fuel_weight' : True,
    'engine_mass' : False,
    'engine_thrust' : True,
    }

setup_and_run_problem(case_settings)
