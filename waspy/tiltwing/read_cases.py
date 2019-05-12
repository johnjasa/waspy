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
    'viscous' : (0.0481, 0.0027),
    'engine_mass' : (0.12, 0.009),
    'baseline' : (0.45, 0.0054),
    'wave_drag' : (0.45, 0.0050),
    'struct_weight' : (0.45, 0.0058),
    'fuel_weight' : (0.45, 0.0062),
    'engine_thrust' : (0.45, 0.0046),
}

print_results(data)
plot_thicknesses(data, folders, live_plot=False, annotate_data=thickness_labels)

anchor = 0.8
spacing = 0.06
lift_labels = {
    'baseline' : (0.1, anchor + 1 * spacing),
    'viscous' : (0.1, anchor - 5 * spacing),
    'wave_drag' : (0.1, anchor - 4 * spacing),
    'struct_weight' : (0.1, anchor + 0 * spacing),
    'fuel_weight' : (0.1, anchor - 3 * spacing),
    'engine_mass' : (0.1, anchor - 2 * spacing),
    'engine_thrust' : (0.1, anchor - spacing),
    'elliptical' : (0.6, 1.1),
}

plot_lifts(data, folders, live_plot=False, annotate_data=lift_labels)

anchor = 0.115
spacing = 0.005
tc_labels = {
    'viscous' : (0.2, 0.19),
    'engine_mass' : (0.1, anchor - 0 * spacing),
    'fuel_weight' : (0.1, anchor - 1 * spacing),
    'struct_weight' : (0.1, anchor - 2 * spacing),
    'engine_thrust' : (0.1, anchor - 3 * spacing),
    'baseline' : (0.1, anchor - 4 * spacing),
    'wave_drag' : (0.1, anchor - 5 * spacing),
}

plot_tc(data, folders, live_plot=False, annotate_data=tc_labels)

anchor = 5
x_anchor = 0.3
spacing = 0.16
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
