from __future__ import division, print_function

from waspy.all_shared_properties import add_geometry_to_problem, connect_problem, add_driver, run_problem


def setup_and_run_problem(case_settings):

    if case_settings['planform'] == 'CRM':
        from waspy.CRM.CRM_shared_properties import add_prob_vars, add_opt_problem, get_surfaces

    if case_settings['planform'] == 'Q400':
        from waspy.Q400.Q400_shared_properties import add_prob_vars, add_opt_problem, get_surfaces

    surfaces = get_surfaces(case_settings)

    prob = add_prob_vars(case_settings, surfaces)

    prob = add_geometry_to_problem(prob, surfaces)

    prob = connect_problem(prob, surfaces, case_settings)

    prob = add_driver(prob, case_settings)

    prob = add_opt_problem(prob, case_settings)

    run_problem(prob)

    return prob
