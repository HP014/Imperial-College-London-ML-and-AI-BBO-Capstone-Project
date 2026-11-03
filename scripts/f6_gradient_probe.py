"""F6: where does the Gaussian Process say the output rises, once the directions already used up are removed?

F6's old success line and the perpendicular half step had both peaked near the current best, so the picks next to
them were no use. This takes the Gaussian Process's local gradient at the best point (with and without a separate
length scale per input), removes the two used-up directions, and proposes a small step along what is left. It was
the basis of the Week 12 probe (see CHANGELOG.md). The gradient there contradicted what actually happened in the old
directions, so the step was treated as low confidence.

Usage: python scripts/f6_gradient_probe.py [--week N]   (the Week 12 decision used Week 11 data)
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_io import load_week  # noqa: E402

warnings.filterwarnings("ignore")  # hide scikit-learn's kernel-fit warnings so the output stays readable
np.set_printoptions(linewidth=200, suppress=True)  # print arrays on one line, without scientific notation

# Row numbers in F6's data (20 initial points, so the Week N query is row 19 + N)
OLD_BEST_ROW = 25    # the Week 6 query, F6's best at the time (-0.1902)
LATER_BEST_ROW = 27  # the Week 8 query, the best after the switch to small steps (-0.1036)


def main():
    # Read the --week option and load F6's data
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=11, help="week of data to use (default: 11)")
    X, y = load_week(parser.parse_args().week)[6]
    B = X[np.argmax(y)]  # the current best point
    Pa, Pb = X[OLD_BEST_ROW], X[LATER_BEST_ROW]

    # The two directions already used up, as unit vectors:
    # u1 = the old success line (Week 6 best to Week 8 best)
    # u2 = the later step (Week 8 best to the current best), with its u1 part removed so u1 and u2 are perpendicular
    u1 = Pb - Pa
    u1 /= np.linalg.norm(u1)
    u2 = B - Pb
    u2 /= np.linalg.norm(u2)
    u2 = u2 - (u2 @ u1) * u1
    u2 /= np.linalg.norm(u2)

    # Fit the exploit-search GP twice: one shared length scale ('iso'), then one per input ('ARD')
    for ard in (False, True):
        ls = np.full(5, 0.3) if ard else 0.3
        k = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(ls, (0.05, 5.0), nu=2.5) + WhiteKernel(1e-4, (1e-8, 1e-1))
        m = GaussianProcessRegressor(kernel=k, alpha=1e-8, normalize_y=True, n_restarts_optimizer=10,
                                     random_state=0).fit(X, y)

        # The GP's gradient at the best point, by central differences: predict a small step (h) either side along
        # each input and divide the difference by 2h
        h = 0.004
        g = np.zeros(5)
        for j in range(5):
            e = np.zeros(5)
            e[j] = h
            g[j] = (m.predict([B + e])[0] - m.predict([B - e])[0]) / (2 * h)

        # Remove the parts of the gradient along u1 and u2, leaving only the unused directions
        gp_ = g - (g @ u1) * u1 - (g @ u2) * u2
        print("ARD" if ard else "iso", "gradient", np.round(g, 3), "| along u1", round(float(g @ u1), 3),
              "along u2", round(float(g @ u2), 3))
        print("   gradient with u1,u2 removed:", np.round(gp_, 3), "norm", round(float(np.linalg.norm(gp_)), 3))

        # Two candidate steps from the best point along what is left, with the GP's prediction at each
        for step in (0.01, 0.015):
            q = B + step * gp_ / np.linalg.norm(gp_)
            mu, sd = m.predict([q], return_std=True)
            print(f"   step {step}: {np.round(q, 6)} pred {mu[0]:.4f} +- {sd[0]:.4f}")


if __name__ == "__main__":
    main()
