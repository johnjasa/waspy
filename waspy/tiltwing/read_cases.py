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
    'baseline' : (0.43, 0.0054),
    'viscous' : (0.0481, 0.003),
    'wave_drag' : (0.43, 0.0050),
    'struct_weight' : (0.43, 0.0058),
    'fuel_weight' : (0.43, 0.0062),
    'engine_mass' : (0.12, 0.009),
    'engine_thrust' : (0.43, 0.0046),
}

print_results(data)
plot_thicknesses(data, folders, live_plot=False, annotate_data=thickness_labels)

anchor = 0.8
spacing = 0.06
lift_labels = {
    'baseline' : (0.1, anchor + 0.0),
    'viscous' : (0.1, anchor - 5 * spacing),
    'wave_drag' : (0.1, anchor - 4 * spacing),
    'struct_weight' : (0.1, anchor + spacing),
    'fuel_weight' : (0.1, anchor - 3 * spacing),
    'engine_mass' : (0.1, anchor - 2 * spacing),
    'engine_thrust' : (0.1, anchor - spacing),
    'elliptical' : (0.6, 1.1),
}

plot_lifts(data, folders, live_plot=False, annotate_data=lift_labels)

tc_labels = {
    'viscous' : (0.4, 0.183),
    'fuel_weight' : (0.1, 0.13),
    'engine_thrust' : (0.1, 0.125),
    'struct_weight' : (0.1, 0.12),
    'wave_drag' : (0.1, 0.115),
    'engine_mass' : (0.1, 0.11),
    'baseline' : (0.1, 0.105),
}

plot_tc(data, folders, live_plot=False, annotate_data=tc_labels)

anchor = 5
x_anchor = 0.3
spacing = 0.2
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
