# References and technical foundations

This document explains which established methods and papers my approach rests on, how each one is used in this project, and where to find the sources. The weekly reasoning is in `CHANGELOG.md`, and the evidence for each decision is in the "Key decisions and why" section of `README.md`.

## Main technical justification

Bayesian optimisation is a well-established method for problems where each evaluation is expensive and no gradients are available, which is exactly the situation here: one query per function per week, and no formula to differentiate. It fits a surrogate model to the points so far, then uses an acquisition function to choose the next point. The surrogate gives a prediction and an uncertainty, and the acquisition function turns those into a score that balances exploring uncertain regions against refining promising ones. Shahriari et al. (2016) give a broad review of the method.

## Methods and where they come from

**Gaussian Process regression (the surrogate).** A Gaussian Process models an unknown function with a mean prediction and a standard deviation at every point, and it works with very few observations. The standard reference is Rasmussen and Williams (2006). I used scikit-learn's `GaussianProcessRegressor`, with kernel parameters fitted by maximising the log marginal likelihood (10 restarts).

**Kernels (RBF and Matern).** The RBF kernel assumes a very smooth function, and the Matern kernel allows a rougher one, with a smoothness setting (nu) of 2.5 or 1.5 here. Rasmussen and Williams (2006) describe both. I used RBF for the two 2D functions and Matern for the rest, because the higher-dimensional functions are sparser and less predictable. A white-noise kernel was added for F1 only.

**Upper Confidence Bound (UCB).** The score is the predicted mean plus kappa times the standard deviation. Srinivas et al. (2010) analyse this rule for Gaussian Processes (GP-UCB) and show how kappa controls the trade-off between exploration and exploitation. In the code it is `upper_confidence_bound(mu, sigma, kappa)` in `src/plotting_utils.py`.

**Expected Improvement (EI).** The score is the expected amount by which a point beats the best value so far, with a margin xi. Jones, Schonlau and Welch (1998) introduced it in their Efficient Global Optimization method. It is more cautious than UCB, so I used both together. In the code it is `expected_improvement(mu, sigma, y_best, xi)` in `src/plotting_utils.py`.

**Random Forest (second surrogate).** Breiman (2001) describes Random Forests. A forest has no built-in uncertainty, so I used the standard deviation of the individual trees' predictions. It was used in Week 6 and set aside afterwards (see the model card for why).

**Pattern search and line searches (F1, F4 and F6).** When the surrogate models gave no usable guidance, I stepped away from the best point and measured the function directly. A pattern search is a basic derivative-free method, going back to Hooke and Jeeves (1961), and I used it for F1 and in the same style for F4 and F6.

## Libraries

- **scikit-learn** (Pedregosa et al., 2011): `GaussianProcessRegressor`, the `RBF`, `Matern` and `WhiteKernel` kernels, and `RandomForestRegressor`. It was the right choice because it is clean, well documented, works well with small datasets and gives the uncertainty estimates the acquisition functions need. PyTorch or TensorFlow would be far more complex for this amount of data.
- **NumPy** (Harris et al., 2020): arrays, the stored data and the candidate search.
- **SciPy** (Virtanen et al., 2020): the normal distribution used in Expected Improvement.
- **Matplotlib** (Hunter, 2007): all figures.

## Sources

- Breiman, L. (2001). Random Forests. *Machine Learning*.
- Harris, C. R. et al. (2020). Array programming with NumPy. *Nature*.
- Hooke, R. and Jeeves, T. A. (1961). "Direct Search" solution of numerical and statistical problems. *Journal of the ACM*.
- Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*.
- Jones, D. R., Schonlau, M. and Welch, W. J. (1998). Efficient Global Optimization of Expensive Black-Box Functions. *Journal of Global Optimization*.
- Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*.
- Rasmussen, C. E. and Williams, C. K. I. (2006). *Gaussian Processes for Machine Learning*. MIT Press. Free online at https://gaussianprocess.org/gpml/
- Shahriari, B., Swersky, K., Wang, Z., Adams, R. P. and de Freitas, N. (2016). Taking the Human Out of the Loop: A Review of Bayesian Optimization. *Proceedings of the IEEE*.
- Srinivas, N., Krause, A., Kakade, S. M. and Seeger, M. (2010). Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design. *International Conference on Machine Learning (ICML)*.
- Virtanen, P. et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*.

## What I would consult next

- **Information-theoretic acquisition functions:** Entropy Search (Hennig and Schuler, 2012) and Predictive Entropy Search (Hernandez-Lobato et al., 2014), which may do better than UCB and EI on some functions.
- **BoTorch** (Balandat et al., 2020), a Bayesian optimisation library built on PyTorch, with more advanced acquisition functions and batch optimisation, particularly for the higher-dimensional functions.
- **Other libraries** such as GPyOpt and scikit-optimize, for alternative Gaussian Process and forest-based optimisers to compare against.
- **Regret analysis papers and recent surveys,** to understand the theoretical guarantees of my approach.

Further sources:
- Balandat, M. et al. (2020). BoTorch: A Framework for Efficient Monte-Carlo Bayesian Optimization. *Advances in Neural Information Processing Systems*.
- Hennig, P. and Schuler, C. J. (2012). Entropy Search for Information-Efficient Global Optimization. *Journal of Machine Learning Research*.
- Hernandez-Lobato, J. M., Hoffman, M. W. and Ghahramani, Z. (2014). Predictive Entropy Search for Efficient Global Optimization of Black-box Functions. *Advances in Neural Information Processing Systems*.
