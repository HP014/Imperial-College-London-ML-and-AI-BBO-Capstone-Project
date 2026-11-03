"""Acquisition functions, candidate helpers and plotting helpers, shared by src/pipeline.py and scripts/.

- upper_confidence_bound and expected_improvement: the two acquisition functions that score candidate points.
- local_candidates: random candidate points in a small box around the best point.
- unsampled_mask: the duplicate-query safeguard (excludes candidates too close to a point already queried).
- plot_2d_function: the contour maps of the 2D functions in pipeline.py.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm  # the normal distribution, used by expected_improvement
import warnings
warnings.filterwarnings('ignore')  # hide library warnings when this module is imported


def plot_2d_function(X1, X2, Z, title="2D Function"):
    """
    Plot a 2D function as a contour plot.
    
    Parameters:
    -----------
    X1, X2 : 2D arrays, meshgrid coordinates
    Z : 2D array, function values
    title : str, plot title
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    
    contour = ax.contourf(X1, X2, Z, levels=20, cmap='viridis')
    plt.colorbar(contour, ax=ax)
    ax.set_xlabel('x1', fontsize=12)
    ax.set_ylabel('x2', fontsize=12)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    return fig, ax


def upper_confidence_bound(mu, sigma, kappa=2.0):
    """
    Upper Confidence Bound (UCB) acquisition function.

    UCB = mean + kappa * std

    A point scores highly if it is predicted to be good, or if the model is unsure about it. kappa sets how much
    the uncertainty counts: kappa = 0 picks the highest predicted mean (pure exploitation).

    Parameters:
    -----------
    mu : predicted mean
    sigma : predicted standard deviation
    kappa : exploration parameter (higher = more exploration)
    """
    return mu + kappa * sigma


def expected_improvement(mu, sigma, y_best, xi=0.01):
    """
    Expected Improvement (EI) acquisition function.
    
    EI = E[max(f(x) - y_best - xi, 0)]
       = (mu - y_best - xi) * Phi(Z) + sigma * phi(Z),  with Z = (mu - y_best - xi) / sigma

    The expected amount by which a point beats the best value so far by more than xi (Phi and phi are the normal
    distribution's CDF and density). A larger xi demands a bigger gain, which favours uncertain points (more
    exploration).

    Parameters:
    -----------
    mu : predicted mean
    sigma : predicted standard deviation
    y_best : best observed value so far
    xi : exploration parameter
    """
    # sigma can be 0 (at a sampled point), which divides by zero; those points are set to EI = 0 below
    with np.errstate(divide='warn'):
        improvement = mu - y_best - xi
        Z = improvement / sigma
        ei = improvement * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0.0] = 0.0
    return ei


def local_candidates(center, half_width=0.04, n=20000, seed=42):
    """
    Random candidates inside a small box around `center`, clipped to [0, 1].
    Uses its own generator so it does not change the global random stream.

    half_width is the distance from the centre to the edge of the box in each input (0.04 means +/-0.04).
    n is the number of candidates (20,000). Clipping keeps every candidate inside the valid input range, so near
    an edge some candidates sit exactly on 0 or 1.
    """
    center = np.asarray(center, dtype=float)
    rng = np.random.default_rng(seed)
    pts = center + rng.uniform(-half_width, half_width, size=(n, center.size))
    return np.clip(pts, 0.0, 1.0)


def unsampled_mask(candidates, existing_points, min_dist=1e-3):
    """
    Boolean mask marking which candidates are NOT within min_dist of any
    already-sampled point. Use this to exclude near-duplicate points before
    picking the next query with argmax, so the acquisition function can't
    recommend re-sampling a point you've already queried.

    Parameters:
    -----------
    candidates : array-like, shape (n_candidates, n_dims)
    existing_points : array-like, shape (n_samples, n_dims), already-sampled inputs
    min_dist : float, minimum Euclidean distance to count as a new point
    """
    # distance from every candidate to every sampled point; keep a candidate only if its nearest one is far enough
    dists = np.linalg.norm(candidates[:, None, :] - existing_points[None, :, :], axis=2)
    return dists.min(axis=1) >= min_dist