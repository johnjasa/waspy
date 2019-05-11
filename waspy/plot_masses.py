from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt

from waspy.all_read_cases import load_baselines


wings = ['CRM']
colors = ['k']

data = load_baselines()

fig, ax = plt.subplots(1, figsize=(8, 6))

# Plot the wing mesh first
for idx, wing in enumerate(wings):
    mesh = data[wing]['def_mesh'][0]

    mesh = mesh[:, ::-1, :]
    mesh[:, :, 1] = -mesh[:, :, 1]

    mesh[:, :, 0] = mesh[:, :, 0]
    mesh[:, :, 1] = mesh[:, :, 1]
    mesh[:, :, 0] = mesh[:, :, 0]

    le = mesh[0, :, :]
    te = mesh[-1, :, :]
    root = mesh[:, -1, :]
    tip = mesh[:, 0, :]

    ax.plot(le[:, 1], le[:, 0], color=colors[idx], zorder=100)
    ax.plot(te[:, 1], te[:, 0], color=colors[idx], zorder=100)
    ax.plot(root[:, 1], root[:, 0], color=colors[idx], zorder=100)
    ax.plot(tip[:, 1], tip[:, 0], color=colors[idx], zorder=100)

    # Optionally include the mesh panels
    # ax.plot(mesh[:, :, 1], mesh[:, :, 0], lw=1, color='gray')
    # ax.plot(mesh[:, :, 1].T, mesh[:, :, 0].T, lw=1, color='gray')

    point_mass_loc = data[wing]['point_mass_locations'][0][0]
    ax.scatter(-point_mass_loc[1], point_mass_loc[0], s=70, color='b')

    fem_origin = data[wing]['wing_fem_origin']
    nodes = (mesh[-1, :, :] - mesh[0, :, :]) * fem_origin + mesh[0, :, :]

    ax.scatter(nodes[:, 1], nodes[:, 0], color='k')

    # Hard-coded for CRM
    weightings = np.array([  9.49473935e-17,   1.34418721e-16,   1.99455398e-16,   3.08626154e-16,
            5.03366861e-16,   8.74211750e-16,   1.63095605e-15,   3.30527210e-15,
            7.38230171e-15,   1.85246710e-14,   5.36203020e-14,   1.85854143e-13,
            8.15678205e-13,   4.95224723e-12,   4.84736920e-11,   1.03404947e-09,
            1.00563338e-07,   8.22961993e-04,   9.99176166e-01,   7.68161334e-07,
            2.59237625e-09,   6.83381619e-11,   4.65355199e-12,   5.52326891e-13,
            9.47624126e-14,   2.10573397e-14])
    weightings = weightings[::-1]

    for i_node, node in enumerate(nodes):
        if weightings[i_node] > 1e-8:
            ax.plot([node[1], -point_mass_loc[1]], [node[0], point_mass_loc[0]], lw=weightings[i_node]*2, zorder=-10, color='k')

ax.set_aspect('equal')
ax.axis('off')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig('masses.pdf')
