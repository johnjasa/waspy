from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt

from waspy.all_read_cases import load_baselines


wings = ['CRM', 'Q400', 'tiltwing']
colors = ['k', 'k', 'k']

crm_y_offset = 23.4513 + .88

data = load_baselines()

x = 1
y = 0

plt.figure()
for idx, wing in enumerate(wings):
    mesh = data[wing]['def_mesh'][0]
    point_mass_loc = data[wing]['point_mass_locations'][0][0]

    mesh = mesh[:, ::-1, :]
    mesh[:, :, 1] = -mesh[:, :, 1]
    mesh[:, :, 0] = -mesh[:, :, 0]

    point_mass_loc[0] *= -1
    point_mass_loc[1] *= -1

    mesh[:, :, 0] = mesh[:, :, 0] - np.max(mesh[:, 0, 0]) - idx**.35 * 18
    mesh[:, :, 1] = mesh[:, :, 1] - np.min(mesh[:, 0, 1])
    mesh[:, :, 0] = mesh[:, :, 0] + crm_y_offset

    point_mass_loc[0] = point_mass_loc[0] - np.max(mesh[:, 0, 0]) - idx**.35 * 18
    point_mass_loc[1] = point_mass_loc[1] - np.min(mesh[:, 0, 1])
    point_mass_loc[0] = point_mass_loc[0] + crm_y_offset

    le = mesh[0, :, :]
    te = mesh[-1, :, :]
    root = mesh[:, -1, :]
    tip = mesh[:, 0, :]

    plt.plot(le[:, x], le[:, y], color=colors[idx], zorder=100)
    plt.plot(te[:, x], te[:, y], color=colors[idx], zorder=100)
    plt.plot(root[:, x], root[:, y], color=colors[idx], zorder=100)
    plt.plot(tip[:, x], tip[:, y], color=colors[idx], zorder=100)

    plt.plot(mesh[:, :, x], mesh[:, :, y], lw=1, color='gray')
    plt.plot(mesh[:, :, x].T, mesh[:, :, y].T, lw=1, color='gray')

    # plt.scatter(point_mass_loc[x], point_mass_loc[y], s=70, color='b')

ax = plt.gca()
ax.set_aspect('equal')
# ax.axis('off')

spines = ['bottom', 'left']

# Loop over the spines in the axes and shift them
for loc, spine in ax.spines.items():
    if loc in spines:
        spine.set_smart_bounds(True)
    else:
        spine.set_color('none')  # don't draw spine

# turn off ticks where there is no spine
if 'left' in spines:
    ax.yaxis.set_ticks_position('left')
else:
    # no yaxis ticks
    ax.yaxis.set_ticks([])

if 'bottom' in spines:
    ax.xaxis.set_ticks_position('bottom')
else:
    # no xaxis ticks
    ax.xaxis.set_ticks([])

plt.annotate('uCRM-9', (8, 20), color=colors[0])
plt.annotate('Q400', (5, 6.5), color=colors[1])
plt.annotate('Commuter', (9, 0.2), color=colors[2])

plt.xlabel('Chordwise direction, meters')
plt.ylabel('Spanwise direction, meters')

plt.tight_layout()
plt.savefig('planforms.pdf')
