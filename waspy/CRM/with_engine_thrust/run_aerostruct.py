from __future__ import division, print_function

from waspy.CRM.CRM_shared_properties import surfaces, add_prob_vars, add_opt_problem
from waspy.all_shared_properties import add_geometry_to_problem, connect_problem, add_driver, run_problem

prob = add_prob_vars()

prob = add_geometry_to_problem(prob, surfaces)

prob = connect_problem(prob, surfaces)

prob = add_driver(prob)

prob = add_opt_problem(prob)

run_problem(prob)
