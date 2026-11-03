"""Weekly Bayesian optimisation pipeline for the eight black-box functions.

What it does: loads the latest data, fits a Gaussian Process (GP) and a Random Forest (RF) for each function,
scores 10,000 random candidate points with UCB and EI, and prints the proposed next points. The final query for
each week was chosen by hand from these outputs plus the extra searches described in CHANGELOG.md (local
searches, line searches, F1 pattern search; the scripts are in scripts/). The reasons are in README.md.

Run it from the command line with `python src/pipeline.py`, or step through it in
notebooks/01_bayesian_optimisation_pipeline.ipynb. The stages must run in order (fit, predict, acquire), because
the Gaussian Process fits and the random candidates share one seeded random generator.

This is the method used in Weeks 1 to 7. From Week 8 the picks came mainly from scripts/exploit_search.py, which
refits a different Gaussian Process (one Matern 2.5 kernel for every function) and searches small boxes around each
best point.
"""
import warnings

import matplotlib.pyplot as plt
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern, WhiteKernel

from config import FUNCTION_SETTINGS, LOCAL_HALF_WIDTH, N_CANDIDATES, SEED
from data_io import FUNCTION_IDS, load_week
from plotting_utils import (expected_improvement, local_candidates, plot_2d_function, unsampled_mask,
                            upper_confidence_bound)
from surrogate_models import fit_random_forest_surrogate, log_magnitude, random_forest_predict

# Hide scikit-learn's warnings about the kernel fit (for example a length scale reaching its bound) so the weekly
# printout stays readable. Note that this hides every other warning too.
warnings.filterwarnings("ignore")


def setup():
    """Seed the random generator (the 10,000 random candidates are the same on every run) and set the plot style."""
    np.random.seed(SEED)
    plt.style.use("seaborn-v0_8-darkgrid")


def banner(title):
    """Print a section title between two lines of '=', with a blank line before it (one per function)."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _heading(title):
    """Print a stage title between two lines of '=' (one per stage: fitting, predicting)."""
    print("=" * 60)
    print(title)
    print("=" * 60)


def _point(values):
    """Format a point the way the capstone portal wants it: x1-x2-...-xn with six decimals."""
    return "-".join(f"{v:.6f}" for v in values)


def show_shapes(data):
    """Print the shapes, to check the data loaded correctly."""
    for f in FUNCTION_IDS:
        inputs, outputs = data[f]
        print(f"func{f}: inputs {inputs.shape}, outputs {outputs.shape}")


def analyse(data):
    """Report the best point so far for each function. The best points are reused later as the centres of the
    local search boxes (F3 and F4). Returns {function: {'idx', 'input', 'output'}}."""
    best = {}
    for f in FUNCTION_IDS:
        inputs, outputs = data[f]
        idx = np.argmax(outputs)
        print(f"\nfunc{f}:")
        print(f"  - Dimensions: {inputs.shape[1]}D")
        print(f"  - Data points: {len(outputs)}")
        print(f"  - Output range: [{outputs.min():.6f}, {outputs.max():.6f}]")
        print(f"  - Best output: {outputs[idx]:.6f}")
        print(f"  - Best input: {inputs[idx]}")
        best[f] = {"idx": idx, "input": inputs[idx], "output": outputs[idx]}
    return best


def build_gp(settings, normalize_y=False):
    """A Gaussian Process with the kernel chosen for this function (see config.py).

    alpha=1e-6 is added to the diagonal of the kernel matrix (the reason for this value was not recorded).
    n_restarts_optimizer=10 restarts the kernel fit from random starting values, so it is less likely to get stuck
    in a poor local optimum.
    """
    # The shape of the function: RBF (very smooth) or Matern (rougher; nu sets how rough), from config.py
    base = RBF(length_scale=settings["length_scale"]) if settings["kernel"] == "rbf" else \
        Matern(length_scale=settings["length_scale"], nu=settings["nu"])
    # ConstantKernel scales the kernel to the size of the outputs; the fit learns its value
    kernel = ConstantKernel(1.0) * base
    # White noise (F1 only) lets the fit treat tiny differences between outputs as noise
    if settings["white_noise"]:
        kernel = kernel + WhiteKernel(noise_level=0.01)
    return GaussianProcessRegressor(kernel=kernel, alpha=1e-6, n_restarts_optimizer=10, normalize_y=normalize_y)


def fit_models(data):
    """Fit a GP and a Random Forest (200 trees) for each function, and for F1 also log-space versions of both.

    The Random Forest is a second opinion. Its uncertainty is the spread across the trees. From Week 8 it was not
    used for the final picks, as it cannot predict above the best value it has seen.
    F1 is about 0 almost everywhere (1e-245 to 1e-3), so the raw-value models cannot see differences between
    points; log10|y| exposes the gradient.
    """
    _heading("FITTING GP FOR EACH FUNCTION")
    models = {}
    for f in FUNCTION_IDS:
        inputs, outputs = data[f]
        settings = FUNCTION_SETTINGS[f]
        entry = {}
        # GP and Random Forest on the raw outputs
        entry["gp"] = build_gp(settings).fit(inputs, outputs)
        print(f"✅ func{f} fitted ({settings['fit_label']})")
        entry["rf"] = fit_random_forest_surrogate(inputs, outputs)
        print(f"✅ func{f} fitted (Random Forest, 200 trees)")
        # F1 only: the same two models fitted to log10|y| (the GP with normalised outputs)
        if f == 1:
            entry["z"] = log_magnitude(outputs)
            entry["gp_log"] = build_gp(settings, normalize_y=True).fit(inputs, entry["z"])
            entry["rf_log"] = fit_random_forest_surrogate(inputs, entry["z"])
            print("✅ func1 fitted (log10|y| GP and Random Forest)")
        models[f] = entry
    return models


def predict_candidates(data, models):
    """Score 10,000 random candidate points per function with the GP and the Random Forest.

    A GP prediction is cheap, so 10,000 candidates give decent coverage in 2 to 3 dimensions (it is coarse in
    8 dimensions). Returns {function: {'candidates', 'mean', 'std', 'mean_rf', 'std_rf', ...}}.
    """
    _heading("MAKING PREDICTIONS FOR EACH FUNCTION")
    preds = {}
    for f in FUNCTION_IDS:
        banner(f"FUNCTION {f}: MAKING PREDICTIONS")
        # 10,000 random points spread uniformly over the whole input range [0, 1] in every dimension
        candidates = np.random.random((N_CANDIDATES, FUNCTION_SETTINGS[f]["dim"]))
        gp, rf = models[f]["gp"], models[f]["rf"]

        # GP prediction (mean and uncertainty) at every candidate
        mean, std = gp.predict(candidates, return_std=True)
        print(f"Predictions for Function {f}:")
        print(f"  Mean range: [{mean.min():.6f}, {mean.max():.6f}]")
        print(f"  Std range: [{std.min():.6f}, {std.max():.6f}]")
        # the highest mean is a pure exploit pick that ignores uncertainty
        best_idx = np.argmax(mean)
        print(f"  Best predicted point: {candidates[best_idx]}")
        print(f"  Best predicted mean: {mean[best_idx]:.6f}")

        # Random Forest prediction at the same candidates, for comparison
        mean_rf, std_rf = random_forest_predict(rf, candidates)
        best_idx_rf = np.argmax(mean_rf)
        print(f"Predictions for Function {f} (Random Forest):")
        print(f"  Mean range: [{mean_rf.min():.6f}, {mean_rf.max():.6f}]")
        print(f"  Std range: [{std_rf.min():.6f}, {std_rf.max():.6f}]")
        print(f"  Best predicted point: {candidates[best_idx_rf]}")
        print(f"  Best predicted mean: {mean_rf[best_idx_rf]:.6f}")

        preds[f] = {"candidates": candidates, "mean": mean, "std": std, "mean_rf": mean_rf, "std_rf": std_rf}

        if f == 1:  # log-space predictions (values below are log10|y|, not y)
            mean_log, std_log = models[1]["gp_log"].predict(candidates, return_std=True)
            mean_rf_log, std_rf_log = random_forest_predict(models[1]["rf_log"], candidates)
            print("Predictions for Function 1 (log10|y|):")
            print(f"  GP mean range: [{mean_log.min():.6f}, {mean_log.max():.6f}]  "
                  f"std range: [{std_log.min():.6f}, {std_log.max():.6f}]")
            print(f"  RF mean range: [{mean_rf_log.min():.6f}, {mean_rf_log.max():.6f}]  "
                  f"std range: [{std_rf_log.min():.6f}, {std_rf_log.max():.6f}]")
            preds[1].update(mean_log=mean_log, std_log=std_log, mean_rf_log=mean_rf_log, std_rf_log=std_rf_log)
    return preds


def _ucb_ei(candidates, valid, mean, std, y_best, kappa, xi):
    """Highest UCB and highest EI among the valid candidates. Returns (ucb, idx_ucb, ei, idx_ei).

    Invalid candidates (too close to a sampled point) get a score of -inf, so argmax can never choose them.
    """
    ucb = upper_confidence_bound(mean, std, kappa=kappa)
    idx_ucb = np.argmax(np.where(valid, ucb, -np.inf))
    ei = expected_improvement(mean, std, y_best, xi=xi)
    idx_ei = np.argmax(np.where(valid, ei, -np.inf))
    return ucb, idx_ucb, ei, idx_ei


def acquire(data, models, preds, best):
    """Score every candidate with UCB (mean + kappa * std, which favours uncertain points, so it explores) and EI
    (expected gain over the best value so far, which is more cautious). The highest score among the valid
    candidates is the proposed next point. When UCB and EI agree, the pick is more trustworthy.

    kappa and xi are set per function in config.py. Candidates within 0.001 of an already-sampled point are
    excluded, so acquisition cannot recommend re-querying a point I already have (added in Week 6, after F1, F4
    and F5 repeated points in Weeks 3 and 4). For F3 and F4 there is also a local search in a small box around the
    best point instead of the whole range. Returns {function: {'ucb': point, 'ei': point}}.
    """
    picks = {}
    for f in FUNCTION_IDS:
        banner(f"FUNCTION {f}: ACQUISITION")
        inputs, outputs = data[f]
        settings = FUNCTION_SETTINGS[f]
        p = preds[f]
        candidates = p["candidates"]
        kappa, xi = settings["kappa"], settings["xi"]
        y_best = outputs.max()  # EI measures improvement over this value
        valid = unsampled_mask(candidates, inputs)  # False for any candidate within 0.001 of a sampled point

        # GP acquisition: the main picks
        ucb, i_ucb, ei, i_ei = _ucb_ei(candidates, valid, p["mean"], p["std"], y_best, kappa, xi)
        print("UCB:")
        print(f"  Next point: {_point(candidates[i_ucb])}")
        print(f"  UCB value: {ucb[i_ucb]:.6f}")
        print(f"  Mean: {p['mean'][i_ucb]:.6f}")
        print(f"  Std: {p['std'][i_ucb]:.6f}")
        print(f"\nEI (y_best={y_best:.6f}):")
        print(f"  Next point: {_point(candidates[i_ei])}")
        print(f"  EI value: {ei[i_ei]:.6f}")
        print(f"  Mean: {p['mean'][i_ei]:.6f}")
        print(f"  Std: {p['std'][i_ei]:.6f}")
        picks[f] = {"ucb": candidates[i_ucb], "ei": candidates[i_ei]}

        # Random Forest acquisition (comparison model), with the same kappa, xi and exclusions
        ucb_rf, i_ucb_rf, ei_rf, i_ei_rf = _ucb_ei(candidates, valid, p["mean_rf"], p["std_rf"], y_best, kappa, xi)
        print("\n[Random Forest] UCB:")
        print(f"  Next point: {_point(candidates[i_ucb_rf])}")
        print(f"  UCB value: {ucb_rf[i_ucb_rf]:.6f}")
        print(f"  Mean: {p['mean_rf'][i_ucb_rf]:.6f}")
        print(f"  Std: {p['std_rf'][i_ucb_rf]:.6f}")
        print(f"\n[Random Forest] EI (y_best={y_best:.6f}):")
        print(f"  Next point: {_point(candidates[i_ei_rf])}")
        print(f"  EI value: {ei_rf[i_ei_rf]:.6f}")
        print(f"  Mean: {p['mean_rf'][i_ei_rf]:.6f}")
        print(f"  Std: {p['std_rf'][i_ei_rf]:.6f}")

        # Extra picks: F1's log-space models, and the local search box for F3 and F4
        if f == 1:
            _acquire_f1_log(models, p, candidates, valid)

        if settings["local_search"]:
            _local_search(f, inputs, models[f], best[f]["input"], y_best, xi)
    return picks


def _acquire_f1_log(models, p, candidates, valid):
    """F1 log-space acquisition (all values are in log10|y| units). These are the models used for F1 in Week 7,
    before the switch to a pattern search in Week 8. Uses F1's log-space kappa and xi from config.py."""
    settings = FUNCTION_SETTINGS[1]
    z_best = models[1]["z"].max()  # best observed log10|y|, the target EI tries to beat
    kappa, xi = settings["kappa_log"], settings["xi_log"]

    ucb, i_ucb, ei, i_ei = _ucb_ei(candidates, valid, p["mean_log"], p["std_log"], z_best, kappa, xi)
    ucb_rf, i_ucb_rf, ei_rf, i_ei_rf = _ucb_ei(candidates, valid, p["mean_rf_log"], p["std_rf_log"], z_best, kappa, xi)

    print(f"\n[Log-space GP] UCB, best observed log10|y|={z_best:.6f}:")
    print(f"  Next point: {_point(candidates[i_ucb])}")
    print(f"  Predicted log10|y|: {p['mean_log'][i_ucb]:.6f}  Std: {p['std_log'][i_ucb]:.6f}")
    print("\n[Log-space GP] EI:")
    print(f"  Next point: {_point(candidates[i_ei])}")
    print(f"  EI value: {ei[i_ei]:.6f}")
    print(f"  Predicted log10|y|: {p['mean_log'][i_ei]:.6f}  Std: {p['std_log'][i_ei]:.6f}")
    print("\n[Log-space RF] UCB:")
    print(f"  Next point: {_point(candidates[i_ucb_rf])}")
    print(f"  Predicted log10|y|: {p['mean_rf_log'][i_ucb_rf]:.6f}  Std: {p['std_rf_log'][i_ucb_rf]:.6f}")
    print("\n[Log-space RF] EI:")
    print(f"  Next point: {_point(candidates[i_ei_rf])}")
    print(f"  EI value: {ei_rf[i_ei_rf]:.6f}")
    print(f"  Predicted log10|y|: {p['mean_rf_log'][i_ei_rf]:.6f}  Std: {p['std_rf_log'][i_ei_rf]:.6f}")


def _local_search(f, inputs, entry, best_input, y_best, xi):
    """Local search: refine inside a small box around the best point instead of searching the whole range (global
    picks for F3 and F4 chase uncertain edges or far-off regions with very negative predictions). The box is
    +/-0.04 (LOCAL_HALF_WIDTH in config.py), about a sixth of the typical spacing between points, so it stays
    local. This was the Week 7 local search; from Week 8 the smaller +/-0.02 boxes in scripts/exploit_search.py
    were used instead. Only EI is used here."""
    # 20,000 random points in the box, minus any too close to a sampled point
    local = local_candidates(best_input, half_width=LOCAL_HALF_WIDTH)
    valid_local = unsampled_mask(local, inputs)

    # Highest EI inside the box, from the GP and then from the Random Forest
    mean, std = entry["gp"].predict(local, return_std=True)
    ei = expected_improvement(mean, std, y_best, xi=xi)
    i = np.argmax(np.where(valid_local, ei, -np.inf))

    mean_rf, std_rf = random_forest_predict(entry["rf"], local)
    ei_rf = expected_improvement(mean_rf, std_rf, y_best, xi=xi)
    i_rf = np.argmax(np.where(valid_local, ei_rf, -np.inf))

    print(f"\n[Local search ±{LOCAL_HALF_WIDTH} around best] GP EI:")
    print(f"  Next point: {_point(local[i])}")
    print(f"  EI value: {ei[i]:.6f}")
    print(f"  Mean: {mean[i]:.6f}")
    print(f"  Std: {std[i]:.6f}")
    print(f"\n[Local search ±{LOCAL_HALF_WIDTH} around best] RF EI:")
    print(f"  Next point: {_point(local[i_rf])}")
    print(f"  EI value: {ei_rf[i_rf]:.6f}")
    print(f"  Mean: {mean_rf[i_rf]:.6f}")
    print(f"  Std: {std_rf[i_rf]:.6f}")


def _grid():
    """A 30 x 30 grid of test points over the 2D functions. Returns the two grid arrays (for contour plots) and the
    same 900 points as a (900, 2) array (for model predictions)."""
    x1 = np.linspace(0, 1, 30)
    x2 = np.linspace(0, 1, 30)
    X1, X2 = np.meshgrid(x1, x2)
    return X1, X2, np.column_stack([X1.ravel(), X2.ravel()])


def plot_prediction_maps(data, models, functions=(1, 2), show=True):
    """Mean prediction and uncertainty maps for the 2D functions. For inspection only; they do not change the picks."""
    X1, X2, X_test = _grid()
    for f in functions:
        banner(f"VISUALIZING FUNCTION {f} PREDICTIONS")
        inputs, outputs = data[f]
        mu, sigma = models[f]["gp"].predict(X_test, return_std=True)
        best_idx = np.argmax(outputs)

        # Map 1: the GP's predicted mean, with the sampled points coloured by their output
        fig, ax = plot_2d_function(X1, X2, mu.reshape(30, 30), title=f"Function {f}: GP Mean Prediction")
        ax.scatter(inputs[:, 0], inputs[:, 1], c=outputs, s=80, edgecolors="black", cmap="viridis",
                   vmin=outputs.min(), vmax=outputs.max())
        ax.scatter(inputs[best_idx, 0], inputs[best_idx, 1], color="red", s=200, marker="*", label="Best observed")
        ax.legend()
        if show:
            plt.show()

        # Map 2: the GP's uncertainty (std), which is lowest next to the sampled points
        fig, ax = plot_2d_function(X1, X2, sigma.reshape(30, 30), title=f"Function {f}: Prediction Uncertainty")
        ax.scatter(inputs[:, 0], inputs[:, 1], s=80, edgecolors="black", facecolors="none")
        ax.scatter(inputs[best_idx, 0], inputs[best_idx, 1], color="red", s=200, marker="*", label="Best observed")
        ax.legend()
        if show:
            plt.show()


def plot_acquisition_maps(data, models, picks, functions=(1, 2), show=True):
    """UCB and EI maps for the 2D functions. For inspection only. The plots use an illustrative kappa of 1.5 and xi
    of 0.01, not the kappa and xi used for each function's pick."""
    X1, X2, X_test = _grid()
    for f in functions:
        banner(f"VISUALIZING ACQUISITION: FUNCTION {f}")
        inputs, outputs = data[f]
        y_best = outputs.max()
        gp = models[f]["gp"]

        # Map 1: UCB over the grid, with the UCB pick from acquire() as a red star
        mu, sigma = gp.predict(X_test, return_std=True)
        ucb_grid = mu.reshape(30, 30) + 1.5 * sigma.reshape(30, 30)
        fig, ax = plot_2d_function(X1, X2, ucb_grid, title=f"Function {f}: UCB Acquisition (κ=1.5)")
        ax.scatter(inputs[:, 0], inputs[:, 1], c="white", s=80, edgecolors="black", alpha=0.5)
        ax.scatter(picks[f]["ucb"][0], picks[f]["ucb"][1], color="red", s=300, marker="*", label="Next query (UCB)")
        ax.legend()
        if show:
            plt.show()

        # Map 2: EI over the grid, one grid point at a time, with the EI pick from acquire() as a red star
        ei_grid = np.zeros_like(X1)
        for i in range(30):
            for j in range(30):
                point = np.array([[X1[i, j], X2[i, j]]])
                m, s = gp.predict(point, return_std=True)
                ei_grid[i, j] = expected_improvement(m, s, y_best, xi=0.01)
        fig, ax = plot_2d_function(X1, X2, ei_grid, title=f"Function {f}: Expected Improvement (y_best={y_best:.6f})")
        ax.scatter(inputs[:, 0], inputs[:, 1], c="white", s=80, edgecolors="black", alpha=0.5)
        ax.scatter(picks[f]["ei"][0], picks[f]["ei"][1], color="red", s=300, marker="*", label="Next query (EI)")
        ax.legend()
        if show:
            plt.show()


def run(week=None, show=True):
    """Run the whole pipeline for one week of data (default: the latest) and print what it proposes.

    The order matters: fit_models and predict_candidates draw from the same seeded random generator.
    """
    setup()
    data = load_week(week)
    show_shapes(data)
    best = analyse(data)
    models = fit_models(data)
    preds = predict_candidates(data, models)
    plot_prediction_maps(data, models, show=show)
    picks = acquire(data, models, preds, best)
    plot_acquisition_maps(data, models, picks, show=show)
    return data, models, preds, picks


if __name__ == "__main__":
    run()
