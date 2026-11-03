"""Curve fits along a line, used to place the next probe when the surrogate models were no help.

When a Gaussian Process pointed at a point next to a failed one, I fitted a simple curve through the few points
along the direction I had been stepping, and probed near its peak (a parabola through three points, or a cubic
through four). The numbers below are the weekly results recorded in CHANGELOG.md at the time, so this script does
not read data/. Each section says which week's decision it supported.

Usage: python scripts/profile_fits.py
"""
import numpy as np


def vertex(x, y):
    """Peak (or trough) of the best-fit parabola through the points. Returns (x at the vertex, y at the vertex,
    the parabola's coefficients)."""
    c = np.polyfit(x, y, 2)
    xv = -c[1] / (2 * c[0])
    return xv, np.polyval(c, xv), c


print("--- F1 (the log of its output is roughly a parabola along each input) ---")
# Week 10 to 11: profile along x1 at x2 = 0.564941 (three points)
x = np.array([0.576552, 0.582552, 0.594552])
y = np.array([1.6491745e-5, 2.3026329e-5, -8.4464255e-5])
xv, yv, c = vertex(x, y)
print(f"x1 profile: vertex x1={xv:.5f}, peak y={yv:.3e}, zero crossings at x1={np.sort(np.roots(c).real).round(5)}")

# Week 11 to 12: log10 profile along x2 for the three best-stripe points
x2 = np.array([0.552941, 0.564941, 0.579941])
ly = np.log10([1.9084e-6, 2.30263e-5, 1.427785e-4])
xv, yv, c = vertex(x2, ly)
print(f"log10 parabola along x2: vertex x2={xv:.4f}, peak log10={yv:.2f}; slope at 0.5799 = {2 * c[0] * 0.579941 + c[1]:.1f} per unit")
for s in (0.008, 0.010, 0.012, 0.015):
    print(f"   x2={0.579941 + s:.6f}  log10 pred={np.polyval(c, 0.579941 + s):.2f} ({10 ** np.polyval(c, 0.579941 + s):.2e})")

# Week 12 to 13: after the step along x2 overshot (the sign flipped), profile along x2 with four points
x2 = np.array([0.552941, 0.564941, 0.579941, 0.591941])
y = np.array([1.9084e-6, 2.30263e-5, 1.427785e-4, -2.144060e-4])
c3 = np.polyfit(x2, y, 3)
xs = np.linspace(0.575, 0.592, 3401)
ys = np.polyval(c3, xs)
print(f"cubic through 4 points: peak x2={xs[ys.argmax()]:.4f} y={ys.max():.3e}; "
      f"zero crossing x2={xs[np.where(np.diff(np.sign(ys)))[0]]}")
xv, yv, _ = vertex(x2[1:], y[1:])
print(f"parabola through last 3: vertex x2={xv:.4f} y={yv:.3e}")
print(f"linear zero crossing between last two: x2={0.579941 + 0.012 * 1.427785 / (1.427785 + 2.144060):.4f}")

print("\n--- F2 (a narrow peak: moves of 0.003 changed the output by 0.04 to 0.12) ---")
xv, yv, _ = vertex([0.696361, 0.699372, 0.702383], [0.604239, 0.666952, 0.630413])
print(f"x1 parabola: vertex x1={xv:.5f}, peak {yv:.4f}")
xv, yv, _ = vertex([0.901314, 0.911737, 0.924057], [0.542, 0.666952, 0.605])
print(f"x2 parabola (x1 differs slightly): vertex x2={xv:.5f}, peak {yv:.4f}")
xv, yv, _ = vertex([0.901314, 0.911737, 0.91454], [0.542, 0.666952, 0.5498])
print(f"x2 parabola through (0.9013, 0.911737, 0.91454): vertex x2={xv:.5f} peak {yv:.4f}")
b2 = np.array([0.699372, 0.911737])
last = np.array([0.702383, 0.911806])
print("x1 probe on the other side of the best:", np.round(np.array([b2[0] - (last[0] - b2[0]), b2[1]]), 6))

print("\n--- F3 (repeat the full successful step) ---")
p1 = np.array([0.421890, 0.412697, 0.464681])
p2 = np.array([0.401915, 0.392969, 0.455665])
print("full successful step from best:", np.round(p2 + (p2 - p1), 6))

print("\n--- F4 (a line search along the steps that worked) ---")
P = {0: np.array([0.384555, 0.428957, 0.409752, 0.392875]), 1: np.array([0.367331, 0.419785, 0.411319, 0.396967]),
     2: np.array([0.350331, 0.410785, 0.413319, 0.400967]), 2.5: np.array([0.341831, 0.406285, 0.414319, 0.402967])}
Y = {0: 0.367529, 1: 0.608202, 2: 0.616893, 2.5: 0.475518}
t = np.array(list(P))
tv, yv, _ = vertex(t, np.array([Y[k] for k in P]))
print(f"line profile: vertex t={tv:.3f}, peak y={yv:.4f}")
print("point at t=1.5 (midway between the Week 8 and Week 9 points):", np.round(P[1] + 0.5 * (P[2] - P[1]), 6))
tv, yv, _ = vertex([0, 1, 1.4, 2, 2.5], [0.367529, 0.608202, 0.656564, 0.616893, 0.475518])
print(f"line profile after the Week 11 point: vertex t={tv:.3f}, peak {yv:.4f}")

print("\n--- F6 (split the failed step into a part along the old success line and a perpendicular part) ---")
Pa = np.array([0.466585, 0.400845, 0.655431, 0.814342, 0.117872])  # old best, -0.1902
Pb = np.array([0.451463, 0.383362, 0.638745, 0.795203, 0.137146])  # best, -0.1036
Pc = np.array([0.443605, 0.375980, 0.622451, 0.802268, 0.156989])  # failed step, -0.1838
u = (Pb - Pa) / np.linalg.norm(Pb - Pa)  # direction of the old success
dc = Pc - Pb
perp = dc - dc.dot(u) * u
print(f"perpendicular part of the failed step (size {np.linalg.norm(perp):.4f}):", np.round(perp, 5))
print("half step in the opposite perpendicular direction:", np.round(Pb - 0.5 * perp, 6))
tv, yv, _ = vertex([0, 1, 1.5], [-0.1902, -0.1036, -0.1108])
print(f"line profile vertex t={tv:.3f}, peak {yv:.4f}")
