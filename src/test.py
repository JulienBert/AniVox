import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5agg')

tP0 = (156, 54, 118)
tP1 = (166, 53, 197)

# Control points
#                          z
#       + p1             /
#      /                +--- x
#     /                 |
#    + p0               y
#
#
# Diamond drawing
#
#        + p0                  + pq
#      /   \                 p/
#  pm +--+--+ pp      pm +---+---+ pp
#     \   p /               / 
#     \     /              + pr
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
p0p = p0 - p

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter((p0[0], p1[0], p[0]), (p0[1], p1[1], p[1]), (p0[2], p1[2], p[2]))

# Rot around y-axis
pm = np.array([p0p[2], p0p[1], -p0p[0]])
pp = np.array([-p0p[2], p0p[1], p0p[0]])

pm = p + pm
pp = p + pp
print(pm, pp)
ax.scatter((pm[0], pp[0]), (pm[1], pp[1]), (pm[2], pp[2]))

# Rot around x-axis
pq = np.array([p0p[0], -p0p[2], p0p[1]])
pr = np.array([p0p[0], p0p[2], -p0p[1]])
pq = p + pq
pr = p + pr

print(pr, pq)
ax.scatter((pq[0], pr[0]), (pq[1], pr[1]), (pq[2], pr[2]))

ax.set_xlim((0, 500))
ax.set_ylim((0, 500))
ax.set_zlim((0, 500))

plt.show()


"""
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

"""