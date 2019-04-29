from __future__ import division, print_function

from waspy.master_functions import setup_and_run_problem


# Set these individual settings for each problem. Later functions
# will parse these and set up the model correctly.
case_settings = {
    'planform' : 'CRM',
    'with_viscous' : True,
    'with_wave' : True,
    'compressibility' : False,
    'struct_weight_relief' : False,
    'distributed_fuel_weight' : False,
    'engine_mass' : False,
    'engine_thrust' : False,
    }

setup_and_run_problem(case_settings)
