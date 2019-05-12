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
    'baseline' : (0.8, 0.02),
    'viscous' : (0.0576, 0.0168),
    'wave_drag' : (0.0576, 0.012),
    'struct_weight' : (0.28, 0.024),
    'fuel_weight' : (0.6, 0.026),
    'engine_mass' : (0.8, 0.019),
    'engine_thrust' : (0.8, 0.018),
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
    'wave_drag' : (0.6, 0.142),
    'struct_weight' : (0.35, 0.122),
    'fuel_weight' : (0.05, 0.124),
    'baseline' : (0.2, 0.089),
    'viscous' : (0.2, 0.086),
    'engine_mass' : (0.2, 0.083),
    'engine_thrust' : (0.2, 0.080),
}

plot_tc(data, folders, live_plot=False, annotate_data=tc_labels)

anchor = 6
x_anchor = 0.4
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
