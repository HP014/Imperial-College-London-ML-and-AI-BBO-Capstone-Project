"""Does kappa matter inside a small box around the best point?

For each function, fit the exploit-search Gaussian Process, search a +/-0.02 box around the best point, and pick the
highest UCB point for kappa from 0 to 2. Report how far the pick moves in input space and how much predicted value it
costs compared with kappa = 0. This is the check behind the README's note that kappa was left alone from Week 9: inside
a small box the picks barely move, so the box size, not kappa, is the exploration setting.

Usage: python scripts/kappa_sensitivity.py [--week N]   (the Week 9 decision used Week 8 data)
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
from plotting_utils import local_candidates, unsampled_mask, upper_confidence_bound  # noqa: E402

warnings.filterwarnings("ignore")  # hide scikit-learn's kernel-fit warnings so the output stays readable
KAPPAS = (0.0, 0.5, 1.0, 1.5, 2.0)  # the kappa values tried; the table compares the first (0) with the last (2)


def symlog(y, thresh=1e-6):
    """Sign-preserving log of F1's outputs, the same as in exploit_search.py."""
    return np.sign(y) * np.log10(1.0 + np.abs(y) / thresh)


def main():
    # Read the --week option and load that week's data
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=8, help="week of data to use (default: 8)")
    data = load_week(parser.parse_args().week)

    print(f"{'':4}{'pred at kappa=0':>16}{'pred at kappa=2':>17}{'change':>9}{'pick moved':>12}   (box +/-0.02)")
    for f in range(1, 9):
        # Fit the exploit-search GP (the same model as exploit_search.py)
        X, y = data[f]
        target = symlog(y) if f == 1 else y
        kern = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(0.3, (0.05, 3.0), nu=2.5) + WhiteKernel(1e-4, (1e-8, 1e-1))
        gp = GaussianProcessRegressor(kernel=kern, alpha=1e-8, normalize_y=True, n_restarts_optimizer=10,
                                      random_state=0).fit(X, target)

        # Score the candidates in a +/-0.02 box with UCB at each kappa and keep the highest-scoring point for each
        cand = local_candidates(X[np.argmax(y)], half_width=0.02)
        valid = unsampled_mask(cand, X, min_dist=0.003)
        m, s = gp.predict(cand, return_std=True)
        picks = [int(np.argmax(np.where(valid, upper_confidence_bound(m, s, kappa=k), -np.inf))) for k in KAPPAS]

        # How far the kappa = 2 pick is from the kappa = 0 pick, and the change in predicted value between them
        moved = np.linalg.norm(cand[picks[-1]] - cand[picks[0]])
        change = (m[picks[-1]] - m[picks[0]]) / abs(m[picks[0]]) if m[picks[0]] != 0 else float("nan")
        print(f"F{f:<3}{m[picks[0]]:>16.4f}{m[picks[-1]]:>17.4f}{change:>9.1%}{moved:>12.3f}")


if __name__ == "__main__":
    main()
