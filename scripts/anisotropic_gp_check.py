"""Does a Gaussian Process with a separate length scale per input (anisotropic) predict better than the plain one?

For each chosen function, predict the last three weekly points from the data before each, with both versions, and
report the absolute errors and z-scores. Then fit the anisotropic version to all the data, print its length scales
(short = that input matters) and its highest predicted point in small boxes around the best point. This was tried on
F4 in Week 12 (see CHANGELOG.md): it predicted the last three points better than the plain GP, but was
overconfident on one of them.

Usage: python scripts/anisotropic_gp_check.py [--week N] [--functions 3 4 6 2]
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
from plotting_utils import local_candidates, unsampled_mask  # noqa: E402

warnings.filterwarnings("ignore")  # hide scikit-learn's kernel-fit warnings so the output stays readable
np.set_printoptions(linewidth=200, suppress=True)  # print arrays on one line, without scientific notation


def build_gp(d, anisotropic):
    """The exploit-search Gaussian Process (see exploit_search.py), with the length-scale ceiling raised to 5.

    anisotropic=False: one length scale shared by all d inputs (printed as 'iso').
    anisotropic=True: a separate length scale for each input (printed as 'ARD', automatic relevance
    determination). A short fitted length scale means the output changes quickly along that input.
    """
    ls = np.full(d, 0.3) if anisotropic else 0.3
    k = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(ls, (0.05, 5.0), nu=2.5) + WhiteKernel(1e-4, (1e-8, 1e-1))
    return GaussianProcessRegressor(kernel=k, alpha=1e-8, normalize_y=True, n_restarts_optimizer=10, random_state=0)


def main():
    # Read the --week and --functions options and load that week's data
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=None, help="week of data to use (default: the latest)")
    parser.add_argument("--functions", type=int, nargs="+", default=[3, 4, 6, 2])
    args = parser.parse_args()
    data = load_week(args.week)

    for f in args.functions:
        X, y = data[f]
        d = X.shape[1]
        print(f"\nF{f}")
        # Hold-out test: predict each of the last 3 weekly points from only the data before it, with both versions.
        # The error is reported as an absolute difference and as a z-score (error / predicted std).
        for anisotropic in (False, True):
            zs, errs = [], []
            for n_hold in (3, 2, 1):
                # fit on every row before the held-out point, then predict that one point (row -n_hold)
                model = build_gp(d, anisotropic).fit(X[:-n_hold], y[:-n_hold])
                mu, sd = model.predict(X[-n_hold:-n_hold + 1] if n_hold > 1 else X[-1:], return_std=True)
                errs.append(abs(mu[0] - y[-n_hold]))
                zs.append((y[-n_hold] - mu[0]) / sd[0])
            print(f"  {'ARD' if anisotropic else 'iso'} hold-out abs err (last 3 weekly points): "
                  f"{np.round(errs, 4)} z={np.round(zs, 2)}")
        # Fit the anisotropic version to all the data and print its length scale for each input
        model = build_gp(d, True).fit(X, y)
        print("  ARD length scales:", np.round(model.kernel_.k1.k2.length_scale, 3))
        # Its highest predicted mean in two small boxes around the best point (excluding points within 0.003)
        b = X[np.argmax(y)]
        for hw in (0.02, 0.03):
            c = local_candidates(b, half_width=hw)
            v = unsampled_mask(c, X, min_dist=0.003)
            mu, sd = model.predict(c, return_std=True)
            j = int(np.argmax(np.where(v, mu, -np.inf)))
            print(f"  ARD box +-{hw}: pick {np.round(c[j], 6)} pred {mu[j]:.4f} +- {sd[j]:.4f} (best {y.max():.4f})")


if __name__ == "__main__":
    main()
