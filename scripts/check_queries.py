"""Sanity checks on a week's queries before they are submitted (here: on the ones that were submitted).

For each function, compare the newest query in week N with the data up to week N-1: how close it is to the nearest
sampled point (a distance near 0 means a wasted repeat), how far it is from the previous best, whether every value is
inside [0, 1], and whether it is valid for the portal (the course FAQ gives 0.000000 to 0.999999). I submitted exactly
1.000000 for F5 in Weeks 8 to 13 and 0.000000 for F7 in Week 10, and the portal accepted them (see the README).

Usage: python scripts/check_queries.py [--week N]   (default: the latest week in data/)
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_io import load_week  # noqa: E402
from paths import latest_week  # noqa: E402


def main():
    # Read the --week option and load the data before and after that week's queries
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=None, help="week whose queries to check (default: the latest)")
    week = parser.parse_args().week or latest_week()
    before, after = load_week(week - 1), load_week(week)

    for f in range(1, 9):
        X, y = before[f]
        q = after[f][0][-1]  # this week's query: the last input row of the week's data
        d = np.linalg.norm(X - q, axis=1)  # distance from the query to every earlier point
        b = X[np.argmax(y)]  # the best point before this week
        # One line per function: nearest earlier point, distance from the best, and the two range checks
        print(f"F{f}: nearest sampled {d.min():.4f} | distance from best {np.linalg.norm(q - b):.4f} | "
              f"in [0,1]: {bool(np.all((q >= 0) & (q <= 1)))} | portal range 0 to 0.999999: "
              f"{bool(np.all((q >= 0) & (q <= 0.999999)))}")


if __name__ == "__main__":
    main()
