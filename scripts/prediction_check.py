"""How close was the model's prediction to what actually came back?

For week N, fit the Gaussian Process on the data up to week N-1 (the same exploit-search model as
exploit_search.py), predict the query submitted in week N, and compare it with the output that came back. The error
is measured in standard deviations: (actual - predicted) / predicted std.

The prediction log in results/prediction_log.csv was typed in from the console output saved before each weekly
query (see src/figures.py). For Week 8 onwards this script reproduces the logged predictions for the picks that came
from this model. It prints a line for every function, but picks placed by hand (line searches, half steps, other
probes) had no model prediction and are not in the log. Only 49% of the 39 logged GP predictions landed within one
standard deviation, which is why the Gaussian Process's uncertainty is treated with caution. F1 is on a very
different scale, so it is left out by default.

Usage: python scripts/prediction_check.py [--week N] [--functions 5 7 8]   (default: the latest week, F2 to F8)
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
from paths import latest_week  # noqa: E402

warnings.filterwarnings("ignore")  # hide scikit-learn's kernel-fit warnings so the output stays readable


def main():
    # Read the --week and --functions options and load the data before and after that week's queries
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=None, help="week whose query to check (default: the latest)")
    parser.add_argument("--functions", type=int, nargs="+", default=list(range(2, 9)))
    args = parser.parse_args()
    week = args.week or latest_week()
    before, after = load_week(week - 1), load_week(week)

    for f in args.functions:
        X, y = before[f]
        query, actual = after[f][0][-1], after[f][1][-1]  # this week's query and the output that came back
        # Fit the exploit-search GP on the data before the query (it never sees the result), then predict the query
        kern = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(0.3, (0.05, 3.0), nu=2.5) + WhiteKernel(1e-4, (1e-8, 1e-1))
        gp = GaussianProcessRegressor(kernel=kern, alpha=1e-8, normalize_y=True, n_restarts_optimizer=10,
                                      random_state=0).fit(X, y)
        m, s = gp.predict(np.array([query]), return_std=True)
        print(f"F{f}: predicted {m[0]:.6f} std {s[0]:.6f} | actual {actual:.6f} | z = {(actual - m[0]) / s[0]:+.2f}")


if __name__ == "__main__":
    main()
