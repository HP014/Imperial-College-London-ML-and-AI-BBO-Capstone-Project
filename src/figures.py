"""Builds the project figures from the weekly data in data/Week_N and saves them to results/figures.

It also writes results/prediction_log.csv from the PRED list below (used by Figure 5).
Run it with `python src/figures.py`, or call build_all() from notebooks/02_results_and_figures.ipynb.
"""
import csv

import matplotlib.pyplot as plt
import numpy as np

from data_io import load_week
from paths import FIGURES, RESULTS, latest_week

FUNCS = list(range(1, 9))
# One colour per function (F1 to F8), from a colour-blind-safe palette
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#7A3E9D", "#4D4D4D"]

# The model's prediction for each weekly pick, and the output that came back:
# (result week, function, model, predicted mean, predicted std, actual output).
# The predictions were typed in from the console output saved before each weekly query (Weeks 6 and 7 from
# src/pipeline.py, Week 8 onwards from scripts/exploit_search.py). Picks placed by hand (a line search, half step,
# pattern search or other probe) had no model prediction, so they are not listed: F1 from Week 8, F4 in most weeks
# from Week 8, F6 from Week 10, F2 from Week 11 and F3 from Week 12. The log is also saved to results/prediction_log.csv.
PRED = [
    (6, 1, "RF", -0.000379, 0.001105, 1.996e-160),
    (6, 2, "RF", 0.489254, 0.191454, 0.509906), (6, 3, "GP", -0.011337, 0.070444, -0.109417),
    (6, 4, "GP", 2.190803, 0.807856, -2.828047), (6, 5, "RF", 2478.795994, 891.593453, 1956.558439),
    (6, 6, "GP", -0.397033, 0.107374, -0.190210), (6, 7, "RF", 1.716387, 0.592852, 1.058698),
    (6, 8, "GP", 9.878465, 0.177402, 9.733138),
    (7, 2, "GP", 0.464596, 0.220531, 0.605451), (7, 3, "GP", -0.012460, 0.019560, -0.014985),
    (7, 4, "GP", 0.799120, 0.187332, 0.270739), (7, 5, "GP", 2610.483560, 133.165568, 2369.014443),
    (7, 6, "GP", -0.337344, 0.135992, -0.433513), (7, 7, "GP", 1.695659, 0.187464, 0.925125),
    (7, 8, "GP", 9.832707, 0.194460, 9.892785),
    (8, 2, "GP", 0.587400, 0.085300, 0.666952), (8, 3, "GP", -0.013300, 0.011500, -0.012401),
    (8, 5, "GP", 3023.591100, 54.061700, 3174.771021), (8, 6, "GP", -0.176100, 0.013900, -0.103648),
    (8, 7, "GP", 2.100700, 0.078700, 2.200994), (8, 8, "GP", 9.919700, 0.015300, 9.909957),
    (9, 2, "GP", 0.660300, 0.077700, 0.541969), (9, 3, "GP", -0.011000, 0.004100, -0.005410),
    (9, 5, "GP", 3335.117800, 24.674900, 3341.826050), (9, 6, "GP", -0.141700, 0.053500, -0.183826),
    (9, 7, "GP", 2.303000, 0.026800, 2.332485), (9, 8, "GP", 9.928700, 0.013600, 9.927641),
    (10, 2, "GP", 0.596100, 0.070500, 0.630413), (10, 3, "GP", 0.001500, 0.008700, -0.014070),
    (10, 5, "GP", 3491.758800, 21.554800, 3532.851177), (10, 7, "GP", 2.400500, 0.025000, 2.464515),
    (10, 8, "GP", 9.945100, 0.013800, 9.936602),
    (11, 3, "GP", -0.004000, 0.008600, -0.012375), (11, 5, "GP", 3742.100000, 5.000000, 3747.600069),
    (11, 7, "GP", 2.533300, 0.040000, 2.598802), (11, 8, "GP", 9.952800, 0.010300, 9.948881),
    (12, 4, "GP", 0.797400, 0.108100, 0.497855), (12, 5, "GP", 3976.323300, 3.431300, 3984.690348),
    (12, 7, "GP", 2.696800, 0.030000, 2.715793), (12, 8, "GP", 9.962100, 0.009100, 9.963415),
    (13, 5, "GP", 4242.677847, 3.657399, 4246.414237), (13, 7, "GP", 2.766079, 0.028999, 2.754408),
    (13, 8, "GP", 9.975166, 0.001473, 9.974578),
]


def _style():
    """A shared look for every figure: higher resolution, light grid, no top or right border, bold titles."""
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25, "axes.titleweight": "bold",
    })


def _history(n_weeks):
    """Every week's cumulative data: {week: {function: (inputs, outputs)}}."""
    return {w: load_week(w) for w in range(1, n_weeks + 1)}


def _best_by_week(history, n_weeks):
    """Best output after each week; week 0 is the initial design (Week_1 data without its newest query)."""
    best = {}
    for f in FUNCS:
        # history[w][f] is (inputs, outputs); [1][:-1] is Week 1's outputs minus its one new query
        vals = [history[1][f][1][:-1].max()]
        vals += [history[w][f][1].max() for w in range(1, n_weeks + 1)]
        best[f] = np.array(vals)
    return best


def _scale(f, v):
    """F1 spans many orders of magnitude, so it is shown on a log10 scale."""
    return np.log10(v) if f == 1 else v


def fig1_best_so_far(best, dims, weeks, out):
    """Figure 1: best output so far, one panel per function."""
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
    for ax, f, c in zip(axes.ravel(), FUNCS, COLORS):
        # A step line, as the best so far only changes when a week sets a new best
        y = _scale(f, best[f])
        ax.step(weeks, y, where="post", color=c, lw=2)
        ax.plot(weeks, y, "o", color=c, ms=5)
        ax.set_title(f"F{f} ({dims[f]}D)")
        ax.set_xticks(weeks)
        ax.set_xlabel("Week")
        ax.set_ylabel("log10 of best output" if f == 1 else "Best output so far")
        # Label the final best value at the end of the line
        final = f"{best[f][-1]:.3g}"
        ax.annotate(final, (weeks[-1], y[-1]), textcoords="offset points", xytext=(-4, 8), ha="right",
                    fontsize=9, color=c, fontweight="bold")
    fig.suptitle("Best output found so far, by week", fontsize=14, fontweight="bold")
    fig.savefig(out / "fig1_best_so_far.png")
    plt.close(fig)


def fig2_progress(best, weeks, out):
    """Figure 2: progress from the initial design to the final best, all functions on one axis."""
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    for f, c in zip(FUNCS, COLORS):
        y = _scale(f, best[f])
        # Rescale so the starting best is 0 and the final best is 1, which puts every function on the same axis
        prog = (y - y[0]) / (y[-1] - y[0])
        ax.plot(weeks, prog, "-o", color=c, lw=2, ms=4, label=f"F{f}" + (" (log scale)" if f == 1 else ""))
    ax.axhline(1, color="black", lw=0.8, ls="--")
    ax.set_xticks(weeks)
    ax.set_xlabel("Week")
    ax.set_ylabel("Progress (0 = initial design, 1 = final best)")
    ax.set_title("Progress towards the final best for every function", fontweight="bold")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    fig.savefig(out / "fig2_progress_all_functions.png")
    plt.close(fig)


def fig3_exploration_vs_exploitation(history, n_weeks, out):
    """Figure 3: how far each weekly query is from the previous best (explore vs exploit)."""
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    weekly = np.arange(1, n_weeks + 1)
    for f, c in zip(FUNCS, COLORS):
        d = []
        for w in weekly:
            # This week's query is the last row of week w; the previous best comes from the data before it
            # (for Week 1, the initial points)
            Xw, _ = history[w][f]
            Xp, yp = (history[w - 1][f] if w > 1 else (history[1][f][0][:-1], history[1][f][1][:-1]))
            # Distance divided by sqrt(number of inputs), so functions of different dimension are comparable
            d.append(np.linalg.norm(Xw[-1] - Xp[np.argmax(yp)]) / np.sqrt(Xw.shape[1]))
        ax.plot(weekly, d, "-o", color=c, lw=1.8, ms=4, label=f"F{f}")
    ax.set_xticks(weekly)
    ax.set_xlabel("Week of query")
    ax.set_ylabel("Distance from previous best (per dimension)")
    ax.set_title("Exploration vs exploitation: the shift to small steps around the best", fontweight="bold")
    ax.legend(ncol=4, frameon=False)
    fig.savefig(out / "fig3_exploration_vs_exploitation.png")
    plt.close(fig)


def fig4_f1_map(history, n_weeks, out):
    """Figure 4: F1 map. Almost every output is effectively zero, with a narrow stripe of signal."""
    X1, y1 = history[n_weeks][1]
    # Colour by size of output (log10 |y|), clipped at -30 so the tiny values do not swamp the colour scale
    mag = np.log10(np.maximum(np.abs(y1), 1e-300))
    mag = np.clip(mag, -30, None)
    fig, ax = plt.subplots(figsize=(7.5, 6.5), constrained_layout=True)
    # Positive, negative and exactly-zero outputs get different markers
    pos, neg, zero = y1 > 0, y1 < 0, y1 == 0
    sc = ax.scatter(X1[pos, 0], X1[pos, 1], c=mag[pos], cmap="viridis", s=90, edgecolor="black", vmin=-30, vmax=0,
                    label="positive")
    ax.scatter(X1[neg, 0], X1[neg, 1], c=mag[neg], cmap="viridis", s=110, marker="v", edgecolor="black", vmin=-30,
               vmax=0, label="negative")
    ax.scatter(X1[zero, 0], X1[zero, 1], c="dimgrey", s=70, marker="x", label="exactly zero")
    # Circle and label the best point and the largest negative output
    b = np.argmax(y1)
    ax.scatter(X1[b, 0], X1[b, 1], s=420, facecolor="none", edgecolor="#D55E00", lw=2.5, label="final best")
    ax.annotate("final best\n(1.4e-4)", X1[b], textcoords="offset points", xytext=(-95, -42), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#D55E00"))
    big_neg = np.argmin(y1)
    ax.annotate(f"large negative spike\n({y1[big_neg]:.1e})", X1[big_neg], textcoords="offset points",
                xytext=(45, 90), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("F1: almost every output is effectively zero", fontweight="bold")
    fig.colorbar(sc, ax=ax, label="log10 |output| (clipped at -30)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False, fontsize=9)
    fig.savefig(out / "fig4_f1_map.png")
    plt.close(fig)


def fig5_prediction_error(out):
    """Figure 5: how far the results landed from what the model predicted, in standard deviations."""
    # Save the prediction log, with z = (actual - predicted) / predicted std for each row
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "prediction_log.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["result_week", "function", "model", "predicted_mean", "predicted_std", "actual", "z_score"])
        for wk, f, m, mu, sd, act in PRED:
            wr.writerow([wk, f, m, mu, sd, act, round((act - mu) / sd, 3)])

    # One colour per result week, and a small sideways offset per week so the points for one function do not overlap
    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    wk_color = {6: "#56B4E9", 7: "#E69F00", 8: "#009E73", 9: "#CC79A7", 10: "#D55E00", 11: "#0072B2",
                12: "#882255", 13: "#117733"}
    offset = {6: -0.42, 7: -0.30, 8: -0.18, 9: -0.06, 10: 0.06, 11: 0.18, 12: 0.30, 13: 0.42}
    # Plot every prediction except F1's (its outputs are on a very different scale): circles for GP, squares for RF
    for wk, f, m, mu, sd, act in PRED:
        if f == 1:
            continue
        z = (act - mu) / sd
        ax.scatter(f + offset[wk], z, color=wk_color[wk], s=70, edgecolor="black", zorder=3,
                   marker="o" if m == "GP" else "s")
    # Grey band = within one standard deviation, where about 68% of points would sit if the model were well calibrated
    ax.axhspan(-1, 1, color="grey", alpha=0.15)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(range(2, 9))
    ax.set_xticklabels([f"F{f}" for f in range(2, 9)])
    ax.set_ylabel("(actual - predicted) / predicted std")
    ax.set_title("Prediction error in standard deviations (shaded band = within 1 std)", fontweight="bold")
    # Legend built by hand: one entry per week colour, then one per marker shape
    handles = [plt.Line2D([], [], marker="o", ls="", color=wk_color[w], markeredgecolor="black",
                          label=f"Week {w} result") for w in (6, 7, 8, 9, 10, 11, 12, 13)]
    handles += [plt.Line2D([], [], marker="o", ls="", color="white", markeredgecolor="black", label="GP pick"),
                plt.Line2D([], [], marker="s", ls="", color="white", markeredgecolor="black", label="RF pick")]
    ax.legend(handles=handles, frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.06))
    fig.savefig(out / "fig5_prediction_error.png")
    plt.close(fig)


def build_all(out=FIGURES):
    """Rebuild every figure from the data and save the PNGs to `out` (default: results/figures)."""
    _style()
    out.mkdir(parents=True, exist_ok=True)
    # Load every week's data once and work out the best so far, then build each figure from it
    n_weeks = latest_week()
    history = _history(n_weeks)
    best = _best_by_week(history, n_weeks)
    dims = {f: history[1][f][0].shape[1] for f in FUNCS}  # number of inputs per function
    weeks = np.arange(0, n_weeks + 1)  # 0 = the initial design, then Weeks 1 to 13

    fig1_best_so_far(best, dims, weeks, out)
    fig2_progress(best, weeks, out)
    fig3_exploration_vs_exploitation(history, n_weeks, out)
    fig4_f1_map(history, n_weeks, out)
    fig5_prediction_error(out)
    return sorted(p.name for p in out.glob("*.png"))


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")  # save the figures to file without opening a window
    print("Saved:", *build_all())
