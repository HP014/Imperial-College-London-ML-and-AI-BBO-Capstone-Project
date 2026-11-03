"""Why a Random Forest is no use for small steps: inside a small box around the best point it predicts almost
nothing but a few repeated values, and a very wide uncertainty.

For F2, F5, F7 and F8, fit the Random Forest and score 20,000 candidates in a +/-0.02 box around the best point.
This is the check behind the README's note that the Random Forest was set aside from Week 8.

Usage: python scripts/rf_box_check.py [--week N]   (default: the latest week in data/)
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_io import load_week  # noqa: E402
from plotting_utils import local_candidates  # noqa: E402
from surrogate_models import fit_random_forest_surrogate, random_forest_predict  # noqa: E402

warnings.filterwarnings("ignore")  # hide library warnings so the output stays readable


def main():
    # Read the --week option and load that week's data
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=None, help="week of data to use (default: the latest)")
    data = load_week(parser.parse_args().week)

    for f in (2, 5, 7, 8):
        # Fit the pipeline's Random Forest (200 trees, seed 42) and predict 20,000 points in the box
        X, y = data[f]
        b = X[np.argmax(y)]
        rf = fit_random_forest_surrogate(X, y)
        c = local_candidates(b, half_width=0.02)
        m, s = random_forest_predict(rf, c)
        # Count the distinct predictions (a forest gives the same value across whole regions) and the mean spread
        print(f"F{f}: RF over 20,000 candidates in the +-0.02 box -> {len(np.unique(np.round(m, 6)))} distinct "
              f"predicted values; range {m.min():.4f} to {m.max():.4f} (best {y.max():.4f}); mean std {s.mean():.4f}")


if __name__ == "__main__":
    main()
