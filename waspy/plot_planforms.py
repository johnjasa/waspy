from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt

from waspy.all_read_cases import load_baselines


wings = ['CRM', 'Q400', 'tiltwing']
colors = ['k', 'k', 'k']

crm_y_offset = 13.4513

data = load_baselines()

plt.figure()
for idx, wing in enumerate(wings):
    mesh = data[wing]['def_mesh'][0]

    mesh = mesh[:, ::-1, :]
    mesh[:, :, 1] = -mesh[:, :, 1]

    mesh[:, :, 0] = mesh[:, :, 0] - np.max(mesh[:, 0, 0]) + idx**.5 * 8
    mesh[:, :, 1] = mesh[:, :, 1] - np.min(mesh[:, 0, 1])
    mesh[:, :, 0] = mesh[:, :, 0] + crm_y_offset

    le = mesh[0, :, :]
    te = mesh[-1, :, :]
    root = mesh[:, -1, :]
    tip = mesh[:, 0, :]

    plt.plot(le[:, 0], le[:, 1], color=colors[idx], zorder=100)
    plt.plot(te[:, 0], te[:, 1], color=colors[idx], zorder=100)
    plt.plot(root[:, 0], root[:, 1], color=colors[idx], zorder=100)
    plt.plot(tip[:, 0], tip[:, 1], color=colors[idx], zorder=100)

    plt.plot(mesh[:, :, 0], mesh[:, :, 1], lw=1, color='gray')
    plt.plot(mesh[:, :, 0].T, mesh[:, :, 1].T, lw=1, color='gray')


ax = plt.gca()
ax.set_aspect('equal')
# ax.axis('off')

spines = ['bottom', 'right']

# Loop over the spines in the axes and shift them
for loc, spine in ax.spines.items():
    if loc in spines:
        spine.set_smart_bounds(True)
    else:
        spine.set_color('none')  # don't draw spine

# turn off ticks where there is no spine
if 'right' in spines:
    ax.yaxis.set_ticks_position('right')
else:
    # no yaxis ticks
    ax.yaxis.set_ticks([])

if 'bottom' in spines:
    ax.xaxis.set_ticks_position('bottom')
else:
    # no xaxis ticks
    ax.xaxis.set_ticks([])

plt.annotate('uCRM', (10, 20), color=colors[0])
plt.annotate('Q400', (19, 15.2), color=colors[1])
plt.annotate('Tiltwing', (21.8, 9.), color=colors[2])

plt.xlabel('Chordwise direction, meters')
plt.ylabel('Spanwise direction, meters')
ax.yaxis.set_label_position("right")

plt.tight_layout()
plt.savefig('planforms.pdf')
