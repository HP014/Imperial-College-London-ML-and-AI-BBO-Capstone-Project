# Model Card

## Overview

- **Name:** Adaptive GP/RF Bayesian optimisation.
- **Type:** a sequential, model-based optimiser for expensive black-box functions, with a person choosing between the model suggestions each week (Bayesian optimisation with a human in the loop).
- **Version and status:** one approach that changed over thirteen weeks. This card describes it as it stood after the final round (Week 13). Section "How the approach evolved" lists the changes.
- **Code:** `src/pipeline.py` (the weekly method), `src/config.py`, `src/surrogate_models.py`, `src/plotting_utils.py` and `src/figures.py`, run through `notebooks/01_bayesian_optimisation_pipeline.ipynb`. The extra searches behind the weekly choices are in `scripts/`.
- **Author:** Hilton Patel (GitHub: HP014).

## Intended Use

**Suitable for:**
- Maximising an expensive, unknown function on a bounded box ([0, 1] on every input) with a very small budget: one query per round and tens of points in total.
- Low to moderate dimensions (2 to 8 inputs in this project).
- Settings where a person reviews each suggestion before it is used.

**Avoid using it for:**
- High-dimensional problems (more than about 10 inputs). Random candidate search and a single smoothness assumption both scale poorly.
- Large batch or fully automated runs. The pipeline relies on a person to choose between suggestions each week.
- Safety-critical or real-world decisions without further validation. It has only been tested on eight synthetic functions.
- Problems with constraints, noisy outputs or discrete and categorical inputs. None of these were handled.

## Model Description

**Input:** For each of the eight functions, the model is fitted to every query made so far: a list of input points, each a vector of 2 to 8 numbers between 0 and 1 (F1 and F2 have 2, F3 has 3, F4 and F5 have 4, F6 has 5, F7 has 6, F8 has 8), together with the output each one returned. To make a prediction, it takes any candidate input point in the same range.

**Output:** For a candidate point, the models give a predicted output (a mean) and an uncertainty (a standard deviation). An acquisition function turns these into a score, and the final output of the process is the next point to query for each function, one per function per week.

**Model Architecture:**
- **Gaussian Process regression** (scikit-learn `GaussianProcessRegressor`). The kernel is RBF for F1 and F2 and Matern (smoothness 2.5 or 1.5) for F3 to F8. Kernel parameters are fitted by maximising the log marginal likelihood with 10 random restarts. Later refits use a floor of 0.05 on the length scale and normalised outputs.
- **Random Forest regression** (200 trees, seed 42). The mean is the average over trees and the uncertainty is the standard deviation across trees.
- **Acquisition:** Upper Confidence Bound (mean plus kappa times uncertainty) and Expected Improvement, applied to 10,000 random candidate points, with a rule that excludes any candidate within 0.001 of an already-sampled point.
- **Adaptations:** log-space versions of both models for F1 (the output is converted to the log of its absolute value), a local search in a ±0.04 box around the best point for F3 and F4, a small-step pattern search for F1, and in the final rounds a search for the highest predicted value within ±0.02 of each best point.

## How the approach evolved

- **Weeks 1 to 5:** a Gaussian Process per function, scored with UCB and EI over 10,000 random candidates, with kappa and xi set by dimension and adjusted by judgement after each result.
- **Week 6:** a Random Forest added as a second surrogate, and a rule blocking any candidate within 0.001 of a sampled point, after four queries had been exact repeats.
- **Week 7:** log-space models for F1, and a local search around the best point for F3 and F4.
- **Week 8:** a switch to exploitation, searching a ±0.02 box around each best point, with a length-scale floor and normalised outputs for the Gaussian Process. All eight functions set a new best.
- **Weeks 8 to 13:** where the models gave no usable guidance, direct measurement with a pattern search for F1 and line searches and half steps for F4 and F6, plus an anisotropic Gaussian Process for F4. Week 13 was the final query.

The reasons for every weekly choice are in `CHANGELOG.md`, and the evidence is in the "Key decisions and why" section of `README.md`.

## Performance

**How performance is measured.** This is not a standard train/test problem. There are very few points and each new point is only available once I submit it, so I measure two things:

1. **Optimisation outcome:** the best output found so far per function. All eight functions improved over the thirteen weeks. All eight set a new best in Week 8, five of the eight did so again in Week 9, three did in Week 10, six did in Week 11, four did in Week 12, and five did in Week 13 (see the table in `README.md` and `results/figures/fig1_best_so_far.png`).
2. **Prediction quality:** before each weekly query, I recorded the model's predicted output and uncertainty for the point I chose. Once the real output came back, I measured the error in standard deviations, `(actual - predicted) / predicted std`. This is the only out-of-sample check available, because the real output was never used to fit the prediction it is compared with. The log is in `results/prediction_log.csv`.

| Model | Predictions | Within 1 std | Within 2 std | Mean absolute error in std |
|---|---|---|---|---|
| GP | 39 | 49% | 79% | 1.44 |
| Random Forest | 3 | 67% | 100% | 0.60 |

The data covers Weeks 6 to 13 and excludes F1, whose predictions are on a different scale. The Random Forest figures come from only three predictions, so they are not a reliable comparison with the GP. A well-calibrated model would be within one standard deviation about 68% of the time.

![Prediction error](results/figures/fig5_prediction_error.png)

## Limitations

- **Very little data.** Each function has between 23 and 53 points, in 2 to 8 dimensions. Every conclusion here is tentative.
- **Overconfidence.** The GP was wrong by a large amount for F3, F4 and F7, by up to about 6 standard deviations in earlier weeks, so its uncertainty is often too small.
- **Assumptions that do not hold for every function.** The GP assumes a smooth function with a moderate output range. F1 breaks this (outputs from about 1e-245 to 1e-3), and neither the GP nor the Random Forest learned anything useful from it on raw values. The log-space version drops the sign of the output, and F1 does change sign.
- **Random Forest extrapolation.** In Week 6 the Random Forest predicted values far outside anything observed for F4 (a mean of about -6.7 with a standard deviation of about 8.7, against observed values between -1.3 and 0.4).
- **Coarse candidate search.** Choosing from 10,000 random points is coarse in 4 to 8 dimensions, and the chosen points for F4, F5 and F8 changed when one extra model fit shifted the random numbers. The picks are better read as good directions than exact optima.
- **No noise check.** I treated the outputs as exactly repeatable because repeated queries of F1, F4 and F5 returned identical values. The course describes F2's output as noisy, and I never repeated an F2 query, so I could not check it. For the other functions I have not tested this further.
- **Local searches cannot find new peaks.** The exploit steps refine around a known best point and could miss a better region elsewhere.
- **Duplicates.** Four early rows are repeated queries. They were kept and slightly over-weight those points.

## Interpretability considerations

- **Which inputs matter.** A Gaussian Process with a separate length scale for each input shows how quickly the output changes along each one: short means that input matters, long means it barely does. For F4 the fitted scales (0.32, 0.37, 0.95, 0.63) said x1 and x2 matter most. For F8 the scale sat at its upper bound, which means the model saw a near-linear trend and not a peak.
- **Why a point was chosen.** Every pick is a transparent score: the predicted mean plus kappa times the uncertainty (UCB), or the expected gain over the best so far (EI). Every weekly choice has a written reason in `CHANGELOG.md`.
- **How far to trust the uncertainty.** The Gaussian Process's standard deviations were too small: only 49% of 39 predictions landed within one standard deviation. I therefore treat its predictions as directions and not as forecasts, and several picks were checked by direct measurement instead.
- **What is harder to read.** The F1 log-space model drops the sign of the output, so it shows where the output is large and not whether it is positive. The Random Forest's uncertainty is only the spread across its trees. No feature-importance analysis was done for the forest.
- **The human step.** Choosing between models and settings by hand is explainable week by week but not automated, so the whole process is harder to reproduce exactly than a fixed algorithm.

## Trade-offs

- **Exploration versus exploitation.** Large kappa or xi values explore unfamiliar regions and risk wasted queries (a week spent on a poor point). Small steps around the best point were reliable in the final rounds, but they risk settling on a local peak. I chose this balance per function by judgement, not by search.
- **GP versus Random Forest.** The GP gives smoother, better-calibrated uncertainty when its assumptions hold, but fails on extreme scales and rough functions, and gets more expensive as data grows. The Random Forest is robust to scale and roughness, but it extrapolates poorly with little data in higher dimensions, as it did for F4. It also cannot predict above the best value it has seen, which makes it unsuitable for the small exploit steps used in the later weeks.
- **Cost of a query.** Only one real query per function per week is allowed, so there is little room to test a model idea. This is why methods were checked on past data and with small steps before being used.
- **Where it performs poorly.** Functions with sharp, narrow features (F1, and the peak around F4's best point) and the higher-dimensional functions, where the data is thinnest.

## Ethical considerations

- **Transparency supports reproducibility.** Every weekly data snapshot is kept unchanged, the Random Forest seed is fixed (42), and each weekly choice is explained in `CHANGELOG.md`. The final-round searches were run as separate scripts, which are in `scripts/`, so a week's picks from Week 8 onwards come from those scripts and not from the main pipeline alone.
- **Honest reporting.** The wasted duplicate queries, the Random Forest's failure on F4, the overconfident predictions and the points where a method did not work are documented and not hidden, so anyone adapting the method can see where it breaks.
- **Real-world adaptation.** The same loop could tune lab experiments, manufacturing settings or model hyperparameters, where a bad query has real costs in materials, time, energy or safety. Stating the limits above means the approach is not trusted beyond what it has shown, and the human review step should be kept.
- **No personal data.** The data is purely numeric and synthetic, so privacy and fairness risks are minimal for this project.

## Is this level of detail enough?

I think this structure is sufficient. It covers what someone needs to reproduce the method (the models, settings and weekly steps), judge it (the metrics and per-function results) and avoid misusing it (intended use, limitations and failure modes). The reasoning behind each week's choices is in `CHANGELOG.md` and not repeated here, since adding every candidate's score for every round would make the card harder to read without helping someone decide whether to use the approach.
