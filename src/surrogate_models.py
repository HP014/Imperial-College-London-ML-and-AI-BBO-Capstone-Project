"""
The Random Forest surrogate (a second opinion alongside the Gaussian Process in
pipeline.py), and the log transform used for F1.

fit_random_forest_surrogate returns a fitted model, and random_forest_predict
returns (mean, std), so the same acquisition functions (upper_confidence_bound,
expected_improvement) in plotting_utils.py can score its predictions.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor


def log_magnitude(y, floor=1e-323):
    """
    log10 of the absolute output, for functions whose outputs span hundreds of
    orders of magnitude (e.g. F1). Exact zeros are floored at the smallest
    positive float64 so they map to about -323 instead of -inf. The sign is dropped.
    """
    return np.log10(np.maximum(np.abs(np.asarray(y, dtype=float)), floor))


def fit_random_forest_surrogate(X_train, y_train, n_estimators=200, random_state=42):
    """
    Fit a Random Forest surrogate model.

    Random Forests split on relative order rather than magnitude, so they
    are much more robust than a GP to functions with extreme or wildly
    varying output scales.

    Parameters:
    -----------
    X_train : array-like, shape (n_samples, n_dims)
    y_train : array-like, shape (n_samples,)
    n_estimators : int, number of trees in the forest
    random_state : int, for reproducibility
    """
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)
    return model


def random_forest_predict(model, X_test):
    """
    Predict mean and std from a fitted Random Forest.

    scikit-learn's RandomForestRegressor.predict() only returns the mean
    (the average across trees). To get an uncertainty estimate usable by
    UCB/EI, we instead collect each individual tree's prediction and take
    the mean and standard deviation across trees.

    Parameters:
    -----------
    model : fitted RandomForestRegressor
    X_test : array-like, shape (n_samples, n_dims)

    Returns:
    --------
    mean : array, shape (n_samples,)
    std : array, shape (n_samples,)
    """
    tree_predictions = np.stack([tree.predict(X_test) for tree in model.estimators_], axis=0)
    mean = tree_predictions.mean(axis=0)
    std = tree_predictions.std(axis=0)
    return mean, std
