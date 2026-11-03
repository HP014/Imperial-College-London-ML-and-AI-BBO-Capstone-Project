"""Model and acquisition settings for each function.

kernel / length_scale / nu: chosen by hand, in order of function number. A smooth RBF kernel for the two 2D
functions, and Matern (which allows a rougher function) for the rest, as the higher-dimensional functions have
sparser data and are less predictable. The length scale is only a starting point, because the fit optimises it.
kappa (UCB) and xi (EI): set by a starting rule based on dimension (kappa 1.5 for 2D, 2.0 for F3 to F5, 2.5 for F6
to F8, xi 0.01), then adjusted by judgement. README.md has the table of values and the reasons, and CHANGELOG.md
has the weekly reasoning. fit_label is the text printed when the Gaussian Process is fitted.

These settings are used by src/pipeline.py (the method for Weeks 1 to 7). The Week 8 onwards exploit search in
scripts/exploit_search.py does not read them: it uses one Matern 2.5 kernel for every function.
"""

N_CANDIDATES = 10000  # random candidate points scored per function (coarse in 8 dimensions)
SEED = 42  # the 10,000 candidates are the same on every run
LOCAL_HALF_WIDTH = 0.04  # box around the best point for the local search (F3 and F4)

FUNCTION_SETTINGS = {
    # F1: white noise is a precaution, not a measured noise level, as nearly all F1 outputs are near zero.
    # Raw models: kappa 0.1 came from a Week 5 test. F1 was flat and UCB kept picking the same point whatever the
    # kernel or kappa, so I tried kappa 0.1 (near pure exploitation) with RBF plus white noise, and the pick did not
    # change. The reason for xi 0.1 is not recorded. The log-space models (used for F1 from Week 7) follow the
    # starting rule for 2D functions, with the default xi.
    1: dict(dim=2, kernel="rbf", length_scale=0.3, nu=None, white_noise=True, kappa=0.1, xi=0.1,
            kappa_log=1.5, xi_log=0.01, fit_label="2D, RBF length_scale=0.3", local_search=False),
    # F2: kept high to keep exploring, as F2 never beat its starting 0.6112 in Weeks 1 to 5.
    2: dict(dim=2, kernel="rbf", length_scale=0.2, nu=None, white_noise=False, kappa=2.0, xi=0.1,
            fit_label="2D, RBF length_scale=0.2", local_search=False),
    # F3 and F4: kappa lowered from the starting rule to focus on a proposed maximum. Both also get a local search
    # in a +/-0.04 box around the best point (F3: global picks chase uncertain edges; F4: a narrow peak whose
    # neighbours drop sharply).
    3: dict(dim=3, kernel="matern", length_scale=0.1, nu=2.5, white_noise=False, kappa=1.5, xi=0.01,
            fit_label="3D, Matern nu=2.5", local_search=True),
    4: dict(dim=4, kernel="matern", length_scale=0.1, nu=2.5, white_noise=False, kappa=1.5, xi=0.01,
            fit_label="4D, Matern nu=2.5", local_search=True),
    # F5: kappa lowered from the starting rule to focus on its Week 1 peak.
    5: dict(dim=4, kernel="matern", length_scale=0.2, nu=1.5, white_noise=False, kappa=1.5, xi=0.01,
            fit_label="4D, Matern nu=1.5, length_scale=0.2", local_search=False),
    # F6: kappa follows the starting rule for 5D.
    6: dict(dim=5, kernel="matern", length_scale=0.1, nu=1.5, white_noise=False, kappa=2.5, xi=0.01,
            fit_label="5D, Matern nu=1.5", local_search=False),
    # F7: kappa lowered from the starting rule to focus on a proposed maximum near a new best.
    7: dict(dim=6, kernel="matern", length_scale=0.15, nu=1.5, white_noise=False, kappa=1.7, xi=0.01,
            fit_label="6D, Matern nu=1.5, length_scale=0.15", local_search=False),
    # F8: raised from the starting rule (2.5, 0.01) in Week 3 to explore more aggressively after a slightly lower
    # output, then kept.
    8: dict(dim=8, kernel="matern", length_scale=0.2, nu=1.5, white_noise=False, kappa=3.0, xi=0.02,
            fit_label="8D, Matern nu=1.5, length_scale=0.2", local_search=False),
}
