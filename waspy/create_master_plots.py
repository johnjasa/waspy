from __future__ import division, print_function
import pickle
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['lines.linewidth'] = 2
matplotlib.rcParams['axes.edgecolor'] = 'gray'
matplotlib.rcParams['axes.linewidth'] = 0.5
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2Tk
import matplotlib.pyplot as plt

from waspy.all_read_cases import load_all_cases, ax_plot_thicknesses, ax_plot_lifts, ax_plot_tc, ax_plot_twist, folders
import niceplots


wings = ['CRM', 'Q400', 'tiltwing']
labels = ['Skin thickness [m]', 'Normalized lift', 'Thickness-to-chord ratio', 'Twist [degrees]']
wing_labels = ['uCRM-9', 'Q400', 'Commuter']

fig, axarr = plt.subplots(3, 4, figsize=(30, 22))

# TODO : add the label positions from the other read_cases files, this is just for uCRM right now

for i_row, ax_row in enumerate(axarr):
    for i_col, ax in enumerate(ax_row):
        print(i_row, i_col, ax)

        with open(wings[i_row] + '/data.pkl', 'rb') as f:
            data = pickle.load(f)

        if i_col == 0:
            thickness_labels = {
                'viscous' : (0.0576, 0.0168),
                'wave_drag' : (0.0576, 0.012),
                'fuel_weight' : (0.6, 0.026),
                'baseline' : (0.2, 0.010),
                'struct_weight' : (0.2, 0.009),
                'engine_mass' : (0.2, 0.008),
                'engine_thrust' : (0.2, 0.007),
            }

            ax_plot_thicknesses(ax, data, folders, live_plot=False, annotate_data=thickness_labels)

        if i_col == 1:
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

            ax_plot_lifts(ax, data, folders, live_plot=False, annotate_data=lift_labels)

        if i_col == 2:
            tc_labels = {
                'wave_drag' : (0.6, 0.142),
                'fuel_weight' : (0.0, 0.124),
                'struct_weight' : (0.3, 0.12),
                'baseline' : (0.15, 0.085),
                'viscous' : (0.15, 0.082),
                'engine_mass' : (0.15, 0.079),
                'engine_thrust' : (0.15, 0.076),
            }

            ax_plot_tc(ax, data, folders, live_plot=False, annotate_data=tc_labels)

        if i_col == 3:
            anchor = 6
            x_anchor = 0.4
            spacing = 0.22
            twist_labels = {
                'baseline' : (x_anchor, anchor + spacing),
                'viscous' : (x_anchor, anchor - 5 * spacing),
                'wave_drag' : (x_anchor, anchor - 4 * spacing),
                'struct_weight' : (x_anchor, anchor + 0),
                'fuel_weight' : (x_anchor, anchor - 3 * spacing),
                'engine_mass' : (x_anchor, anchor - 2 * spacing),
                'engine_thrust' : (x_anchor, anchor - spacing),
            }

            ax_plot_twist(ax, data, folders, live_plot=False, annotate_data=twist_labels)

        niceplots.adjust_spines(ax)

        if i_row == 0:
            ax.set_title(labels[i_col], fontsize=24)
        if i_row == 2:
            ax.set_xlabel('Normalized span')
        if i_col == 0:
            ax.set_ylabel(wing_labels[i_row], fontsize=24)

plt.savefig('all_plots.pdf')
