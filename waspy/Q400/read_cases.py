from __future__ import division, print_function
import pickle
from waspy.all_read_cases import load_all_cases, print_results, plot_thicknesses, plot_lifts, plot_tc, plot_twist, folders


read_OM_db = False

if read_OM_db:
    data = load_all_cases()
    with open('data.pkl', 'wb') as f:
        pickle.dump(data, f)
else:
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)

thickness_labels = {
    'baseline' : (0.5, 0.008),
    'viscous' : (0.0481, 0.0055),
    'wave_drag' : (-0.03, 0.0097),
    'struct_weight' : (0.0919, 0.0120),
    'fuel_weight' : (0.317, 0.0100),
    'engine_mass' : (0.19, 0.0113),
    'engine_thrust' : (-0.03, 0.0093),
}
anchor = .01
x_anchor = 0.6
spacing = 0.0004
thickness_labels = {
    'viscous' : (0.0, 0.006),
    'engine_mass' : (x_anchor, anchor - 0 * spacing),
    'fuel_weight' : (x_anchor, anchor - 1 * spacing),
    'struct_weight' : (x_anchor, anchor - 2 * spacing),
    'baseline' : (x_anchor, anchor - 3 * spacing),
    'engine_thrust' : (x_anchor, anchor - 4 * spacing),
    'wave_drag' : (x_anchor, anchor - 5 * spacing),
}


print_results(data)
plot_thicknesses(data, folders, live_plot=False, annotate_data=thickness_labels)

anchor = 0.8
spacing = 0.06
lift_labels = {
    'baseline' : (0.1, anchor + spacing),
    'viscous' : (0.1, anchor - 5 * spacing),
    'wave_drag' : (0.1, anchor - 4 * spacing),
    'struct_weight' : (0.1, anchor + 0 * spacing),
    'fuel_weight' : (0.1, anchor - 3 * spacing),
    'engine_mass' : (0.1, anchor - 2 * spacing),
    'engine_thrust' : (0.1, anchor - spacing),
    'elliptical' : (0.6, 1.1),
}

plot_lifts(data, folders, live_plot=False, annotate_data=lift_labels)

tc_labels = {
    'viscous' : (0.2, 0.19),
    'fuel_weight' : (0.05, 0.17),
    'struct_weight' : (0.5, 0.14),
    'engine_thrust' : (0.1, 0.125),
    'wave_drag' : (0.1, 0.12),
    'engine_mass' : (0.1, 0.115),
    'baseline' : (0.1, 0.110),
}

plot_tc(data, folders, live_plot=False, annotate_data=tc_labels)

anchor = 6
x_anchor = 0.4
spacing = 0.13
twist_labels = {
    'baseline' : (x_anchor, anchor + spacing),
    'viscous' : (x_anchor, anchor - 5 * spacing),
    'wave_drag' : (x_anchor, anchor - 4 * spacing),
    'struct_weight' : (x_anchor, anchor + 0),
    'fuel_weight' : (x_anchor, anchor - 3 * spacing),
    'engine_mass' : (x_anchor, anchor - 2 * spacing),
    'engine_thrust' : (x_anchor, anchor - spacing),
}

plot_twist(data, folders, live_plot=False, annotate_data=twist_labels)
