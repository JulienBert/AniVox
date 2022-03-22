import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5agg')

tP0 = (180, 215, 0)
tP1 = (165, 360, 0)

# Control points
#                          z
#       + p0             /
#      /                +--- x
#     /                 |
#    + p1               y
#
#
# Diamond drawing
#
#        + p0
#      /   \
#  pm +--+--+ pp
#     \   p /
#     \     /
#      \   /
#      \   /
#       \ /
#        + p1
#
#

d = 10 # width and height of the diamond head

## Compute p

p0 = np.array([tP0[0], tP0[1], tP0[2]])
p1 = np.array([tP1[0], tP1[1], tP1[2]])

# get vector p1p0
p1p0 = p1-p0
p1p0 = p1p0 / np.linalg.norm(p1p0) 

p = p0 + d*p1p0

## From p get pp (on xy-plan)

# express p0 according to p
p0p = p0 - p
# rotate -pi/2   ->  [[0, -1], [1, 0]]
pp = np.array([-p0p[1], p0p[0], 1])
# move back pp to global frame
pp = p + pp

## From p get pm (on xy-plan)

# express p0 according to p
p0p = p0 - p
# rotate pi/2   ->  [[0, 1], [-1, 0]]
pm = np.array([p0p[1], -p0p[0], 1])
# move back pp to global frame
pm = p + pm


# import matplotlib
# gui_env = ['TKAgg','GTKAgg','Qt4Agg','WXAgg']
# for gui in gui_env:
#     try:
#         print("testing", gui)
#         matplotlib.use(gui,warn=False, force=True)
#         from matplotlib import pyplot as plt
#         break
#     except:
#         continue
# print ("Using:",matplotlib.get_backend())




plt.plot([p0[0], p1[0]], [p0[1], p1[1]])

plt.scatter(p[0], p[1])

plt.scatter(pp[0], pp[1])
plt.scatter(pm[0], pm[1])

plt.xlim([0, 300])
plt.ylim([0, 600])
plt.show()