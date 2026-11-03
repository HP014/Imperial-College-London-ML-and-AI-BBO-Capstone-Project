"""A local quadratic fit around the best point, tested by leave-one-out: tried for F3, F4 and F6 and dropped.

Fit y = c + g.x - k|x|^2 (a simple bowl) to the points nearest the best, find its peak, and check how well it
predicts each point it was not fitted on. In Week 12 the hold-out errors were about as large as the spread of the
data, so the fit was not used (see CHANGELOG.md).

Usage: python scripts/local_quadratic_check.py [--week N]   (the Week 12 decision used Week 11 data)
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_io import load_week  # noqa: E402


def local_fit(data, f, n_near):
    """Fit the bowl to function f's n_near points nearest its best point, and print the fit, its leave-one-out
    error and its peak."""
    # The n_near points nearest the best, shifted so the best point sits at the origin
    X, y = data[f]
    b = X[np.argmax(y)]
    d = np.linalg.norm(X - b, axis=1)
    idx = np.argsort(d)[:n_near]
    Z = X[idx] - b
    t = y[idx]

    # Least-squares fit of y = c + g.x + a|x|^2 (columns: constant, each input, squared distance); k = -a
    A = np.column_stack([np.ones(len(Z)), Z, (Z ** 2).sum(1)])
    coef, *_ = np.linalg.lstsq(A, t, rcond=None)

    # Leave-one-out: refit without each point in turn and record the error predicting that point
    errs = []
    for j in range(len(idx)):
        m = np.ones(len(idx), bool)
        m[j] = False
        cf, *_ = np.linalg.lstsq(A[m], t[m], rcond=None)
        errs.append(A[j] @ cf - t[j])

    # The bowl's peak is at x = g / 2k from the best point; it only has a peak if k > 0 (it curves downwards)
    g, k = coef[1:-1], -coef[-1]
    peak = b + g / (2 * k) if k > 0 else None
    print(f"\nF{f}: n_near={n_near} radius={d[idx].max():.3f} params={A.shape[1]} k={k:.3f}  "
          f"LOO rmse={np.sqrt(np.mean(np.square(errs))):.4f}  (y spread {t.std():.4f})")
    print("   fitted peak:", None if peak is None else np.round(peak, 6), "dist from best:",
          None if peak is None else round(float(np.linalg.norm(peak - b)), 4))
    if peak is not None:
        pred = coef[0] + g @ (peak - b) - k * ((peak - b) ** 2).sum()
        print("   predicted at peak:", round(float(pred), 4), " best:", y.max())


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--week", type=int, default=11, help="week of data to use (default: 11)")
    data = load_week(parser.parse_args().week)
    # Each function is fitted with three neighbourhood sizes, to see whether the result depends on that choice
    for f, ns in ((3, (8, 10, 12)), (4, (10, 14, 18)), (6, (10, 14, 18))):
        for n in ns:
            local_fit(data, f, n)


if __name__ == "__main__":
    main()
