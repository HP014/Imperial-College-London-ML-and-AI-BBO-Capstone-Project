# Changelog

## Repository restructure - After Week 13

No result or pick changed. The code was reorganised so that anyone can clone the repository and run it.

- **Folders:** `Data/` became `data/`. The code moved into `src/`, two notebooks were added in `notebooks/`, the extra analysis scripts went into `scripts/`, and `requirements.txt` was added. File names from earlier weeks that appear below (`surrogate_models.py`, `plotting_utils.py`) are now in `src/`.
- **The weekly script:** `Improved RA_12_1.py` (eight near-identical blocks and fixed `C:\Users\...` paths) became `src/pipeline.py`, which loops over the functions, with the per-function settings and their reasons in `src/config.py`. The old code that appended a week's data by hand became `append_week()` in `src/data_io.py`, which refuses to overwrite an existing week.
- **Checked:** the new pipeline printed exactly the same 478 lines as the old script on the Week 13 data (apart from the old script's own printout of the Week 13 queries), the notebook printed the same lines again, and the figures and prediction log rebuilt byte for byte identical.
- **Scripts:** the working scripts used for the exploit searches, curve fits, anisotropic Gaussian Process test, F6 probe, Random Forest check and kappa check were cleaned up and added. `exploit_search.py`, `anisotropic_gp_check.py`, `rf_box_check.py`, `f6_gradient_probe.py`, `local_quadratic_check.py` and `prediction_check.py` (for Week 13) reproduce the original scripts' numbers. `kappa_sensitivity.py` was written for this and reproduces the README's figures for Week 8 (for example F2's predicted value falling from 0.660 to 0.616 and F4's pick not moving).

## Final Results - After Week 13

Week 13 was the last query, so there is nothing to propose. This section records the final results against the predictions and the documents refreshed.

**Week 13 results against predictions:** Five functions set a new best on the final query: F2 (0.7419, up from 0.6670), F4 (0.7141, up from 0.6566), F5 (4246.4, up from 3984.7), F7 (2.7544, up from 2.7158) and F8 (9.9746, up from 9.9634). F1, F3 and F6 did not improve. The three GP picks that had a prediction all landed within about one standard deviation: F5 +1.0, F7 -0.4 and F8 -0.4.

- F1: the step back to x2 = 0.577 gave 1.15e-4, just below the best of 1.43e-4. The gain of 1.1x to 1.2x did not appear. Along x1 = 0.5805 there are now three useful points (x2 = 0.577 gives 1.15e-4, 0.5799 gives 1.43e-4 and 0.5919 gives -2.14e-4), so the top of the stripe is close to x2 = 0.58 and the best stays at 1.43e-4.
- F2: refinement at x2 = 0.9095 gave 0.7419, a gain of 0.075. The curve through the x2 profile had predicted about 0.72, which I had called optimistic, and the result beat it.
- F3: lowering x3 by 0.006 gave -0.00925, a loss of 0.0038 against the best (-0.0054). This is a smaller loss than the earlier moves (0.007 to 0.0098), so the peak may be a little broader than I had assumed.
- F4: the probe in a new direction gained 0.058, to 0.7141. The GP had predicted nothing above the best, so this was a direction found by the probe and not by the model.
- F5: predicted 4242.7 (std 3.7), actual 4246.4. A gain of 262 over the previous best.
- F6: the repeated step lost 0.0136 (-0.0711 against the best of -0.0575). The step that gained 0.034 in Week 12 did not repeat.
- F7: predicted 2.7661 (std 0.029), actual 2.7544, a new best (up 0.039).
- F8: predicted 9.9752 (std 0.0015), actual 9.9746, a new best (up 0.011).

**Final totals:** 279 observations across the eight functions. New bests by week were 3, 3, 3, 0, 2, 1 and 3 in Weeks 1 to 7, then 8, 5, 3, 6, 4 and 5 in Weeks 8 to 13. That is 46 in total, and 31 of them came from Week 8 onwards, after the switch to small steps around each best point. The prediction check now covers 39 GP predictions: 49% within one standard deviation, 79% within two and a mean absolute error of 1.44 standard deviations.

**Documents and figures refreshed:** The README, model card, datasheet and figures now run to Week 13, with Week 13 shown in green on the prediction-error figure. The script loads `Data/Week_13`.

## Week 13 - Model & Pipeline Changes

**Week 12 results against predictions:** Four functions set a new best: F5 (3984.7, up from 3747.6), F6 (-0.0575, up from -0.0916), F7 (2.7158, up from 2.5988) and F8 (9.9634, up from 9.9489). F1, F2, F3 and F4 did not improve. F5 beat its prediction by 2.4 standard deviations, F7 and F8 landed within one, and F4 missed by 2.8 below.

- F1: step +0.012 in x2, predicted about +2.2e-4 from a curve fit, actual -2.14e-4. The sign flipped. The best is unchanged at 1.43e-4.
- F2: refinement point, actual 0.5498 (a loss of 0.117 for a move of 0.0028 in x2).
- F3: diagonal probe, actual -0.0152 (a loss of 0.0098 over a distance of 0.014).
- F4: anisotropic GP pick, predicted 0.797 (std 0.108), actual 0.4979.
- F5: predicted 3976.3 (std 3.4), actual 3984.7.
- F6: probe step, actual -0.0575 (a gain of 0.034).
- F7: predicted 2.6968 (std 0.030), actual 2.7158.
- F8: predicted 9.9621 (std 0.0091), actual 9.9634.

**F1 steps back inside the stripe:** The output went from +1.43e-4 to -2.14e-4 as x2 rose from 0.5799 to 0.5919, so the top is between them or just below. A parabola through the last three points (and the GP) peaks at x2 = 0.5753, a cubic through the last four at 0.578, and the zero crossing is near 0.585 to 0.587. I take x2 = 0.577 and hold x1 at 0.5805. The expected gain is about 1.1x to 1.2x, and the confidence is low because x1 also changed between some of those points.

**F2 and F3 look like narrow peaks:** For F2, raising x2 by 0.0028 lost 0.117, while the point at x2 = 0.9013 sits 0.125 lower, so the peak is below 0.9117. A curve through those three points puts it at 0.908 (with an optimistic predicted value of 0.72), so I take 0.9095. For F3, every move around the best has lost between 0.007 and 0.0098, whatever the distance (0.014 to 0.034), which looks like a narrow spike with a flat background of about -0.013 to -0.015. I probe within 0.006 of the best, changing x3 only, since a curve through the earlier x3 values peaked slightly below the best's x3. Low confidence.

**F4 probes a new direction:** The anisotropic GP missed this week (2.8 standard deviations below), although it still predicted the point better than the plain GP (error 0.30 against 0.48). The loss of 0.159 is about what the curvature along F4's line predicts for a move of that size, so both the line and the direction I just tried are used up, and the GP now predicts nothing above the best. I step 0.01 along a direction at right angles to both, mostly x4 with a little x1 and x2. Low confidence.

**F6 repeats the step that worked:** The 0.012 probe gained 0.034, and the GP's local predictions near the best have been wrong in direction on each recent test (it predicted -0.119 here), so I repeat the same step (x3 and x5 up, x4 slightly down).

**Dials unchanged:** kappa and xi were left at their script values. The picks come from small boxes, and four functions improved.

**Documents and figures refreshed:** The README, model card, datasheet and figures now run to Week 12. The prediction-error check covers 36 GP predictions, 47% of them within one standard deviation and 78% within two. The legend on the prediction-error figure moved below the plot because it was covering a point.

**Model choice per function (Week 13 queries):**

- F1: Step back inside the stripe, `[0.580530, 0.577000]`. The curve fits put the peak between x2 = 0.5753 and 0.578.
- F2: Refinement, `[0.699500, 0.909500]`. A curve through the x2 profile peaks near 0.908. Low confidence.
- F3: Single-input probe, `[0.401915, 0.392969, 0.449665]`. x3 down by 0.006, since the best looks like a narrow spike. Low confidence.
- F4: Probe, `[0.361506, 0.417260, 0.411229, 0.408367]`. A new direction at right angles to the two used up. Low confidence.
- F5: Exploit GP, `[0.443723, 0.974215, 1.000000, 1.000000]`. Predicted 4242.7. Its quoted uncertainty (std 3.7) is far too small, so treat it as a direction only.
- F6: Repeated step, `[0.462932, 0.383449, 0.655245, 0.783097, 0.148552]`. The same step that gained 0.034 last week.
- F7: Exploit GP, `[0.046509, 0.182924, 0.282867, 0.276940, 0.284300, 0.674593]`. Predicted 2.7661 (std 0.029).
- F8: Exploit GP, `[0.177156, 0.134345, 0.109926, 0.135300, 0.935393, 0.535055, 0.174600, 0.640185]`. Predicted 9.9752 (std 0.0015). The GP's length scale sits at its upper bound, so it is modelling a near-linear trend. Read this as a direction.

## Week 12 - Model & Pipeline Changes

**Week 11 results against predictions:** Six functions set a new best: F1 (1.43e-4, up from 2.30e-5), F4 (0.6566, up from 0.6169), F5 (3747.6, up from 3532.9), F6 (-0.0916, up from -0.1036), F7 (2.5988, up from 2.4645) and F8 (9.9489, up from 9.9366). F2 and F3 did not improve. F4's line-search prediction (about 0.645) was close, F5 and F8 landed within about one standard deviation, and F7 beat its prediction by 1.6 standard deviations.

- F1: step along the stripe, actual 1.43e-4 (6.2x the previous best).
- F2: probe on the other side in x1, actual 0.6042 (a loss of 0.063).
- F3: predicted -0.0040 (std 0.0086), actual -0.0124.
- F4: line-search point, predicted about 0.645, actual 0.6566.
- F5: predicted 3742.1 (std 5), actual 3747.6.
- F6: perpendicular half step, actual -0.0916 (a gain of 0.012).
- F7: predicted 2.5333 (std 0.040), actual 2.5988.
- F8: predicted 9.9528 (std 0.0103), actual 9.9489.

**F1 gains are slowing:** The log of the output rose by 1.08 over the earlier x2 step and by 0.79 over this one. A curve through the three points along x2 peaks at x2 = 0.5916 with a predicted value of about 2.2e-4, only 1.5x higher. x1 also changed slightly this week, so the curve is rough. The next step is +0.012 in x2 with x1 held at 0.5805.

**F2 and F3 narrow in on their peaks:** For F2, moving x1 down by 0.003 lost 0.063 and moving it up lost 0.037, so the peak is bracketed. Curves through the points give x1 = 0.69977 and x2 = 0.9145, with an expected gain of only 0.005 to 0.01. For F3, most of the loss in Weeks 10 and 11 is explained by x3 moving away from 0.4557 (a curve through the x3 values peaks at 0.4545), and the earlier diagonal climb in x1 and x2 lost very little. I keep x3 at 0.4545 and move x1 and x2 down by 0.01. This is low confidence.

**F4 uses an anisotropic GP:** F4's line search is used up. The curve along it peaks at t = 1.42 and I am at 1.425, so more steps along it would gain about 0.002. A GP with a separate length scale for each input predicted the last three points better than the plain GP (absolute errors of 0.14, 0.49 and 0.50 against 0.83, 0.59 and 0.57), although it was overconfident on one of them (5.9 standard deviations). Its fitted length scales (0.32, 0.37, 0.95, 0.63) say x1 and x2 matter most, and it picks a point with x3 higher by 0.02, predicting 0.797 (std 0.108). Treat that prediction as optimistic.

**F6 probe after the old directions are used up:** The old success line and the perpendicular half step both peak about where I am now. The GP's local gradient contradicted what actually happened in both of those directions, so I do not trust it there. I take a 0.012 step in the direction both GP versions agree on after removing those two directions (x3 up, x5 up, x4 slightly down). Low confidence.

**Tried and dropped:** A local quadratic fit around the best point for F3, F4 and F6 had hold-out errors as large as the spread of the data, so it was not used.

**Dials unchanged:** kappa and xi were left at their script values. The picks still come from small boxes, and six functions improved.

**Documents and figures refreshed:** The README, model card, datasheet and figures now run to Week 11. The prediction-error check covers 32 GP predictions, 47% of them within one standard deviation and 81% within two.

**Model choice per function (Week 12 queries):**

- F1: Step along the stripe, `[0.580530, 0.591941]`. The curve through the x2 profile peaks at 0.5916, predicted about 2.2e-4.
- F2: Refinement, `[0.699770, 0.914540]`. Curves through the x1 and x2 profiles peak there. Expected gain is small.
- F3: Low-confidence step, `[0.391915, 0.382969, 0.454500]`. x3 sits at the fitted peak and x1 and x2 move down by 0.01.
- F4: Anisotropic GP, `[0.363909, 0.403787, 0.432014, 0.401644]`. Predicted 0.797 (std 0.108). The line search is used up.
- F5: Exploit GP, `[0.424258, 0.954274, 1.000000, 1.000000]`. Predicted 3976.3. Its quoted uncertainty (std 3.4) is far too small, so treat it as a direction only.
- F6: Probe, `[0.457292, 0.383089, 0.649005, 0.785017, 0.140272]`. The old directions are used up, so this is a step in the direction both GP versions agree on. Low confidence.
- F7: Exploit GP, `[0.027362, 0.185569, 0.295060, 0.258313, 0.303215, 0.675226]`. Predicted 2.6968 (std 0.030). x1 turns up because the GP is almost indifferent to it near the lower limit.
- F8: Exploit GP, `[0.196605, 0.119250, 0.103984, 0.118977, 0.953556, 0.522762, 0.173345, 0.650246]`. Predicted 9.9621 (std 0.0091), continuing the steady climb.

## Week 11 - Model & Pipeline Changes

**Week 10 results against predictions:** Three functions set a new best: F5 (3532.9, up from 3341.8), F7 (2.4645, up from 2.3325) and F8 (9.9366, up from 9.9276). F1, F2, F3, F4 and F6 did not improve. F5 and F7 beat their predictions by 1.9 and 2.6 standard deviations, F2 and F8 landed within one, and F3 missed by 1.8.

- F1: x1 probe back by 0.006 returned 1.65e-5. The best is unchanged at 2.30e-5.
- F2: predicted 0.596 (std 0.071), actual 0.630.
- F3: predicted +0.0015 (std 0.0087), actual -0.0141.
- F4: halved step, actual 0.4755 (a loss of 0.14).
- F5: predicted 3491.8 (std 21.6), actual 3532.9.
- F6: halved step, actual -0.1108.
- F7: predicted 2.4005 (std 0.025), actual 2.4645.
- F8: predicted 9.9451 (std 0.0138), actual 9.9366.

**F1 profile along x1:** With three points along x1 at x2 = 0.5649 (+1.65e-5, +2.30e-5, then -8.4e-5), a curve through them peaks at x1 = 0.5805 (about 2.5e-5) and crosses zero at 0.574 and 0.587, so the positive stripe is only about 0.0135 wide. The x1 position is now pinned down, so the next query sits at the peak in x1 and steps +0.015 in x2, the direction that gave a 12x gain.

**Line searches for F4 and F6:** For F4 I fitted a curve through the four points along my recent steps. It peaks between the Week 8 and Week 9 points (about 40% of the way along, predicted 0.645), so I am sampling there. For F6 the old success line is used up, since a curve through its three points peaks at -0.1022, barely above the best. The failed Week 9 step had a large component at right angles to that line, so I take half a step in the opposite perpendicular direction.

**F2 and F3:** For F2, moving x1 up by 0.003 lost 0.037, so the next probe is the same distance on the other side. For F3, the peak along the diagonal I was following is already at the Week 9 point, so continuing would go past it. I am following the GP's pick instead, which lowers x3 while shifting x1 up and x2 down.

**Dials unchanged:** kappa and xi were left at their script values again, since the picks come from small boxes and several functions are still improving.

**Documents and figures refreshed:** The README, model card, datasheet and figures now run to Week 10. The prediction-error check covers 28 GP predictions, 46% of them within one standard deviation.

**Model choice per function (Week 11 queries):**

- F1: Step along the stripe, `[0.580530, 0.579941]`. The x1 peak is located, so x2 moves up by 0.015.
- F2: Probe, `[0.696361, 0.911737]`. The same distance on the other side of the best in x1.
- F3: GP, `[0.410917, 0.373592, 0.435732]`. Predicted -0.0040 (std 0.0086). Low confidence.
- F4: Line-search point, `[0.360106, 0.415960, 0.412169, 0.398667]`. Predicted about 0.645 from the fitted curve along the line.
- F5: Exploit GP, `[0.404793, 0.934333, 1.000000, 1.000000]`. Predicted 3742.1. Its quoted uncertainty (std 5) is far too small, so treat it as a direction only.
- F6: Perpendicular half step, `[0.451652, 0.382729, 0.642765, 0.786937, 0.131992]`. The old line is exhausted.
- F7: Exploit GP, `[0.007862, 0.197102, 0.307793, 0.238998, 0.320152, 0.693900]`. Predicted 2.5333 (std 0.040).
- F8: Exploit GP, `[0.216054, 0.104155, 0.098042, 0.102654, 0.971719, 0.510469, 0.172090, 0.660307]`. Predicted 9.9528 (std 0.0103).

## Week 10 - Model & Pipeline Changes

**Week 9 results against predictions:** Five functions set a new best: F3 (-0.0054, up from -0.0124), F4 (0.6169, up from 0.6082), F5 (3341.8, up from 3174.8), F7 (2.3325, up from 2.2010) and F8 (9.9276, up from 9.9100). F1, F2 and F6 did not improve. F5 and F8 landed almost exactly on their predictions, F3 and F7 beat theirs by about 1.3 and 1.1 standard deviations, and F2 landed 1.5 standard deviations below.

- F1: the +0.012 x1 probe returned -8.4e-5, so the sign flipped. The best is unchanged at 2.30e-5.
- F2: predicted 0.660 (std 0.078), actual 0.542.
- F3: predicted -0.0110 (std 0.0041), actual -0.0054.
- F4: direction step, actual 0.6169 (a gain of only 0.009, after 0.24 the week before).
- F5: predicted 3335.1 (std 24.7), actual 3341.8.
- F6: predicted -0.142 (std 0.054), actual -0.1838.
- F7: predicted 2.303 (std 0.027), actual 2.3325.
- F8: predicted 9.9287 (std 0.0136), actual 9.9276.

**F1 uses a smaller probe:** The x1 step flipped the sign of F1's output (positive at x1 = 0.5826, -8.4e-5 at 0.5946), so F1 changes sign on a scale finer than my 0.012 step. The next probe steps back by 0.006 in x1 and keeps x2 fixed. With three points along x1 at the same x2, the profile along that direction can be fitted and the positive peak located, if F1 behaves like a wave. The GP's own pick extrapolates to a predicted value of about 0.09, which I do not believe, so I did not use it.

**Pattern search when gains fade or fail (F4 and F6):** F4's gain shrank to +0.009 after +0.24 the week before, so I am halving the step along the same direction. F6 lost 0.08 on its last step. The refitted GP keeps proposing points next to that failed one, even with a larger exclusion zone, because it predicts everything nearby is worse than the best. I therefore halved the step that worked two weeks earlier (lower x1, x2, x3 and x4, higher x5). Both picks are low confidence.

**Dials unchanged:** kappa and xi were left at their script values for the same reasons as before: the picks come from small boxes where kappa barely moves them, and five functions improved under this approach.

**Documents and figures refreshed:** The README, model card, datasheet and figures now run to Week 9. The prediction-error check covers 23 GP predictions, 48% of them within one standard deviation.

**Model choice per function (Week 10 queries):**

- F1: Probe, `[0.576552, 0.564941]`. The sign flip shows the structure is finer than my step, so this steps back by 0.006 in x1 to give a third point along x1.
- F2: Exploit GP, `[0.702383, 0.911806]`. The peak is narrow (x2 = 0.912 gave 0.667, while 0.901 gave 0.542), so I am probing x1 only, with x2 held at the best value. Predicted 0.596 (std 0.071).
- F3: Exploit GP, `[0.382075, 0.373632, 0.475388]`. Continues the trend towards lower x1 and x2. Predicted +0.0015 (std 0.0087).
- F4: Halved step, `[0.341831, 0.406285, 0.414319, 0.402967]`. The gain is fading, so I halve the last step. No usable GP prediction.
- F5: Exploit GP, `[0.385328, 0.914392, 1.000000, 1.000000]`. Continues the climb towards higher x1 and x2. Predicted 3491.8 (std 21.6).
- F6: Halved step, `[0.443902, 0.374621, 0.630402, 0.785634, 0.146783]`. The last step failed, and the GP only proposes points next to it, so I halve the step that worked earlier. No usable GP prediction.
- F7: Exploit GP, `[0.000000, 0.190343, 0.312125, 0.219162, 0.339982, 0.712002]`. Continues the trend. Predicted 2.4005 (std 0.025). The first input reaches the lower limit of 0.
- F8: Exploit GP, `[0.235938, 0.086039, 0.079257, 0.113212, 0.959261, 0.496497, 0.186807, 0.647764]`. Continues the steady climb. Predicted 9.9451 (std 0.0138).

## Week 9 - Model & Pipeline Changes

**Week 8 results against predictions:** All eight functions set a new best for the first time: F1 (2.30e-5, up from 1.91e-6), F2 (0.6670, up from 0.6112), F3 (-0.0124, up from -0.0150), F4 (0.6082, up from 0.3675), F5 (3174.8, up from 2986.9), F6 (-0.1036, up from -0.1902), F7 (2.2010, up from 2.0242) and F8 (9.9100, up from 9.8928). Five picks beat their prediction, F3 landed on it, and F8 was marginally under (9.910 against 9.920) while still improving. F6 beat its prediction by 5 standard deviations and F5 by 2.8, so the models are being too cautious about these peaks.

- F1: x2 probe of +0.012 multiplied the output by 12.1 (1.91e-6 to 2.30e-5).
- F2: predicted 0.587 (std 0.085), actual 0.667.
- F3: predicted -0.0133 (std 0.0115), actual -0.0124.
- F4: direction step from the nearest points, actual 0.608 against a previous best of 0.368.
- F5: predicted 3023.6 (std 54.1), actual 3174.8.
- F6: predicted -0.1761 (std 0.0139), actual -0.1036.
- F7: predicted 2.1007 (std 0.0787), actual 2.2010.
- F8: predicted 9.9197 (std 0.0153), actual 9.9100.

**Why kappa and xi were not changed:** The Week 9 picks come from a ±0.02 box around each best point, where the GP's uncertainty is small. I checked how far the UCB pick moves as kappa goes from 0 to 2 in that box. For most functions it moves by under 0.03 in input space and costs only a few percent of predicted value (for example F2 falls from 0.660 to 0.616). F4 does not move at all, because its GP is about equally uncertain everywhere nearby (std about 0.54), so adding uncertainty cannot change the ranking. F8 moves the most (0.04 to 0.07), but only because it has eight inputs. Since all eight functions improved under pure exploitation, there is no evidence that more exploration is needed. The box size is the exploration dial I would turn first, and if a function stalls for about two weeks I will widen the box to ±0.04 to ±0.08 and add a small kappa of 0.5 to 1.0. The kappa and xi values in the script are unchanged.

**F4 repeats a successful step:** The GP predicts nothing above F4's best anywhere nearby and its pick goes against the move that worked, so I am repeating the successful step (lower x1 and x2, slightly higher x3 and x4) in the pattern-search style. The nearest-neighbour gradient estimate is badly conditioned (F4 also contains a duplicated row), so I am not using it.

**F1 continues the pattern search:** The x2 probe worked, so the next step probes x1 by +0.012 from the new best. If the value rises, I keep going that way, and if it drops I reverse. The GP alternative `[0.579743, 0.584776]` (continuing in x2) was noted but not chosen, since the x1 probe gives the second direction needed.

**Model choice per function (Week 9 queries):**

- F1: Pattern search probe, `[0.594552, 0.564941]`. The x2 step multiplied the output by 12, and the x1 step gives the second direction.
- F2: Exploit GP, `[0.698109, 0.901314]`. Predicted 0.660 (std 0.078), continuing towards lower x2, which is the direction that worked.
- F3: Exploit GP, `[0.401915, 0.392969, 0.455665]`. Predicted -0.0110 (std 0.0041), continuing towards lower x1 and x2.
- F4: Repeated step, `[0.350331, 0.410785, 0.413319, 0.400967]`. Low confidence, since the GP gives no usable signal here.
- F5: Exploit GP, `[0.371546, 0.894421, 1.000000, 1.000000]`. Predicted 3335.1 (std 24.7). Inputs 3 and 4 stay at the 1.0 limit, so the peak may lie at or beyond it.
- F6: Exploit GP, `[0.443605, 0.375980, 0.622451, 0.802268, 0.156989]`. Predicted -0.142, slightly below the best, but it moves in the same direction as the step that worked.
- F7: Exploit GP, `[0.004450, 0.176780, 0.315376, 0.202900, 0.359673, 0.731508]`. Predicted 2.303 (std 0.027). The first input is close to the lower limit of 0.
- F8: Exploit GP, `[0.255752, 0.070913, 0.098188, 0.104820, 0.944183, 0.507066, 0.169066, 0.638957]`. Predicted 9.9287 (std 0.0136), continuing the steady climb.

## Week 8 - Model & Pipeline Changes

**Week 7 results against predictions:** Three functions set a new best: F1 (1.91e-6, up from 7.7e-16), F3 (-0.014985, up from -0.020138) and F8 (9.892785, up from 9.890584). The local searches added last week helped: F3 landed on target and F4 recovered from -2.83 to 0.271, although F4 was still 2.8 standard deviations below its prediction. F7 was the biggest miss, 4.1 standard deviations below prediction.

- F1: log-space GP predicted log10|y| of 4.3 (an extrapolation), actual 1.91e-6. New best.
- F2: GP predicted 0.465 (std 0.221), actual 0.605.
- F3: local GP predicted -0.0125 (std 0.0196), actual -0.0150. New best.
- F4: local GP predicted 0.799 (std 0.187), actual 0.271.
- F5: GP predicted 2610.5 (std 133.2), actual 2369.0, now my second best result.
- F6: GP predicted -0.337 (std 0.136), actual -0.434.
- F7: GP predicted 1.696 (std 0.187), actual 0.925.
- F8: GP predicted 9.833 (std 0.194), actual 9.893. New best.

**Exploit around the best point:** With most functions now having an established best region, this round I exploited instead of exploring. For each function I searched a box of ±0.02 around its best point and chose the highest predicted value, excluding anything within 0.003 of a sampled point. The GPs were refitted with a floor of 0.05 on the length scale and normalised outputs, because the previous fits for F2 and F5 collapsed into spiky, near white-noise kernels (length scales of 0.0085 and 1e-5) that made local predictions meaningless. Small steps were chosen on purpose, since F2, F4 and F7 have all dropped sharply when moving away from their best. Expected gains are small (about 1 to 3 percent where the model predicts any). These searches were run outside the main script, so the script itself has not changed beyond loading the Week 7 data.

**F1 is the exception:** I tried fitting a single Gaussian bump to F1's positive outputs, on the idea that log10(y) would then be a simple curved surface. It failed a hold-out test: fitted without the newest point, it predicted 10^-31 for a value that was actually 10^-5.7, and its centre estimate moved across x1 0.48 to 0.63 and x2 0.55 to 0.75 when resampled. F1 appears to have several narrow, separate features (a large negative spike near [0.650, 0.682] and a positive one near my best point) that a GP cannot pin down with this few points. Since F1's outputs are exact (repeated queries returned identical values), I am switching to a pattern search, a basic derivative-free method. A small step from the best point shows which direction the value climbs. Week 8 steps +0.012 in x2, Week 9 steps +0.012 in x1, and Week 10 jumps along the combined direction. A large rise means keep going that way, and a drop means reverse. The cost is that this takes about three weeks, with one query per week.

**Model choice per function (Week 8 queries):**

- F1: Pattern search probe, `[0.582552, 0.564941]`. A GP and a Gaussian bump both failed on this data, so I am measuring the direction of improvement directly with a small step in x2.
- F2: Exploit GP, `[0.699372, 0.911737]`. Predicted 0.587 (std 0.085), slightly below my best of 0.6112, so this is a close neighbour probe on a noisy peak (three points within 0.007 scored 0.611, 0.606 and 0.510) and not an expected gain.
- F3: Exploit GP, `[0.421890, 0.412697, 0.464681]`. Predicted -0.0133 (std 0.0115) against a best of -0.0150, continuing the trend of the last local search.
- F4: Gradient step, `[0.367331, 0.419785, 0.411319, 0.396967]`. The refitted GP predicts nothing above my best anywhere nearby, so I estimated a direction from the four nearest points instead. Every step towards higher x1 lost value, so this is a 0.02 step towards lower x1 and x2. Low confidence, since it is four equations for four unknowns.
- F5: Exploit GP, `[0.368833, 0.874433, 1.000000, 1.000000]`. Predicted 3023.6 (std 54.1) against a best of 2986.9. Two inputs sit at the upper limit of 1.0 because the search box was clipped there.
- F6: Exploit GP, `[0.451463, 0.383362, 0.638745, 0.795203, 0.137146]`. Predicted -0.1761 (std 0.0139) against a best of -0.1902. Last week's move away from the best lost value, so I am staying close to it.
- F7: Exploit GP, `[0.024039, 0.163217, 0.318627, 0.186638, 0.379364, 0.751014]`. Predicted 2.1007 (std 0.0787) against a best of 2.0242. Last week's global pick missed by 4.1 standard deviations, so I am staying within the best region.
- F8: Exploit GP, `[0.275641, 0.051067, 0.092131, 0.088784, 0.933418, 0.490818, 0.173071, 0.626653]`. Predicted 9.9197 (std 0.0153) against a best of 9.8928, continuing the steady climb.

## Week 7 - Model & Pipeline Changes

**Week 6 results against predictions:** Only F6 set a new best (-0.190210, up from -0.312637). The Random Forest's uncertainty held up well: all four RF picks landed within about 1.1 standard deviations of their prediction. The GP was overconfident on F3 (1.4 std below prediction) and F4 (about 6 std below), but did better than predicted on F6. With only eight points this is a hint rather than proof.

- F1: RF EI predicted -0.0004, actual ~0 (2.0e-160). Flat again.
- F2: RF predicted 0.489 (std 0.191), actual 0.510.
- F3: GP EI predicted -0.011 (std 0.070), actual -0.109.
- F4: GP predicted 2.191 (std 0.808), actual -2.828.
- F5: RF predicted 2478.8 (std 891.6), actual 1956.6, now my third best result.
- F6: GP EI predicted -0.397 (std 0.107), actual -0.190, a new best.
- F7: RF predicted 1.716 (std 0.593), actual 1.059.
- F8: GP EI predicted 9.878 (std 0.177), actual 9.733.

**F1 log-space surrogates:** F1's outputs range from 1e-245 up to 1e-3, so a GP or Random Forest fitted on the raw values cannot tell points apart, because squared error treats everything near zero as identical. Added `log_magnitude()` to `surrogate_models.py`, which converts outputs to log10 of their absolute value (exact zeros are floored at about 1e-323 so they do not become infinity). F1 now also has a GP and a Random Forest fitted on those log values, printed alongside the original raw-value models. In log terms there is a clear gradient, and the log-space GP points to `[0.582552, 0.552941]`, the middle of the cluster of my strongest-magnitude points, instead of the corners the raw-value GP kept choosing. Its predicted value there is an extrapolation, so only the location should be trusted. The sign of the output is dropped in this model, and F1 does change sign, so this finds the active region rather than the exact peak.

**Local search for F3 and F4:** The global search samples 10,000 random points across the whole range. For F3 and F4 it chose far-off points that the models themselves predicted to be poor (F4's GP predicted -13 at its pick, against a best of 0.3675), because uncertainty is highest in the empty regions. Added `local_candidates()` to `plotting_utils.py` and a local search block for each function, which samples 20,000 candidates within ±0.04 of the current best point, removes anything within 0.001 of a sampled point, and scores the rest with EI. It uses its own random generator, so it does not shift the random candidates for the other functions. This only refines around a known peak and cannot find a different one, so it is only suitable where the best region is already located.

**Model choice per function (Week 7 queries):**

- F1: Log-space GP, EI, `[0.582552, 0.552941]`. The raw-value models cannot see the gradient, and this is a new region in the middle of the best-magnitude points.
- F2: GP, UCB and EI agree, `[0.697363, 0.924057]`. The RF points to the same region, and the GP has the higher predicted mean (0.465 vs 0.368).
- F3: Local GP search, `[0.440115, 0.432545, 0.483849]`. The global picks went to the edges with worse predicted means than my best, so I refine around the best point instead (predicted -0.0125 against -0.0201).
- F4: Local GP search, `[0.403556, 0.394705, 0.411007, 0.391402]`. Both global picks were far-off exploration, and the output falls off sharply around the best point. The predicted 0.799 is optimistic and should not be taken at face value.
- F5: GP, UCB and EI agree, `[0.295410, 0.843355, 0.963558, 0.983218]`. The RF points to the same high-value corner, and the GP now has real signal there (2610.5, std 133.2).
- F6: GP, UCB and EI agree, `[0.462193, 0.356005, 0.790249, 0.946497, 0.010447]`. The GP was right last week. Its predicted mean (-0.337) is below my new best, so this is an exploration move.
- F7: GP, UCB, `[0.066665, 0.164650, 0.371860, 0.143913, 0.531545, 0.861796]`. Highest predicted mean (1.696) and close to my best region. The RF missed last week and its new pick wanders far from the productive region.
- F8: GP, EI, `[0.295487, 0.058669, 0.090934, 0.073349, 0.953221, 0.508102, 0.191138, 0.616910]`. Predicted mean 9.833 (std 0.194), a safe refinement near my current best.

**Limitation noted:** Picks for the higher-dimensional functions (F4, F5, F8) change when the random candidate set changes, because 10,000 random points is a coarse search in 4 to 8 dimensions. Adding one more GP fit earlier in the script shifted those three picks, so they should be read as good directions rather than exact optima.

## Week 6 - Model & Pipeline Changes

**Random Forest surrogate:** Up to now I'd only used a GP with UCB/EI, so I added a Random Forest as a second surrogate model to compare against on every function. Implemented in `surrogate_models.py` as `fit_random_forest_surrogate()` and `random_forest_predict()`. Since sklearn's `RandomForestRegressor` doesn't give an uncertainty estimate directly, `random_forest_predict()` computes std as the spread across each individual tree's prediction, so it slots into the existing UCB/EI functions unchanged. Rolled out to func1 and func5 first, then func7/func8, then func2/func3/func4/func6, so all 8 functions now print a GP pick and an RF pick side by side.

- func1: RF proposed a genuinely different point to GP, which kept returning to the same known-flat corners regardless of kernel/κ changes.
- func5: RF was the clearest win: its predicted mean (2478.80) landed near my actual best known point, while GP had no real signal that far from data (mean 0, std 316).
- func4: RF's predictions here are not trustworthy: a mean of -6.65 (std 8.71), way outside the observed range (-1.28 to 0.37). With only 35 points in 4D it looks like the RF is extrapolating noise rather than learning structure, so I'm ignoring RF for func4 until there's more data.

**Duplicate-query safeguard:** Realised GP had recommended a point I'd already sampled (func1's Week 4 query was an exact repeat of Week 3's). Added `unsampled_mask()` to `plotting_utils.py`, which excludes any candidate within 0.001 (Euclidean) of an already-sampled point before picking the argmax on UCB/EI, so acquisition can no longer suggest re-running an experiment I've already done. Applied across all 8 functions.

**Model choice per function (GP vs. RF):**

- F1: RF (EI). GP's UCB/EI both kept landing on points I'd already sampled or on the same flat corners; RF proposed genuinely new territory to explore instead.
- F2: RF (UCB/EI agree). RF's pick is almost identical to my current best point but with a higher predicted mean (0.4893 vs GP's 0.4105). Both models agree the region is good, RF is just more optimistic.
- F3: GP (EI). GP EI has the least-negative predicted mean of any of the four options (-0.0113 vs RF's -0.1121); the landscape here is flat enough that RF isn't adding real signal over GP.
- F4: GP (UCB/EI agree). RF's predictions are not trustworthy here: a mean of -6.65 (std 8.71) is way outside anything ever observed (-1.28 to 0.37), which looks like extrapolation noise rather than learned structure given only 35 points in 4D.
- F5: RF (UCB/EI agree). RF's predicted mean (2478.80) sits near my actual best known point; GP has no real signal this far from data (mean 0, std 316, essentially a blind guess).
- F6: GP (EI). Best predicted mean of all four candidates (-0.3970 vs RF's best of -0.8256).
- F7: RF (UCB/EI agree). Similar mean to GP (1.7164 vs 1.6919) but RF reports much higher, more honest uncertainty (std 0.5929 vs GP's 0.1918).
- F8: GP (EI). A safe refinement close to my current best (9.8906) rather than RF's much larger, riskier exploratory jump.

## Week 5 - Strategy Notes

**Results coming in (Week 4):** F1 3.8e-34, F2 0.150, F3 -0.0932, F4 0.3675 (a repeat of the best point), F5 2986.9 (a repeat of the peak), F6 -0.469, F7 1.642, F8 9.738.

- F1: Changed to an RBF kernel with a 0.3 length scale and added white noise. Still flat and nothing of note found. UCB keeps repeating the same point regardless of kernel or κ, so I follow EI to test a completely new region near the corner.
- F2: UCB and EI agree on a new region, which gives me confidence. I keep κ=2.0 and ξ=0.05 and follow the agreed point.
- F3: UCB and EI disagree. EI has the higher mean (-0.0089 vs -0.0889) and lower uncertainty, so I follow EI with κ=1.5 and ξ=0.01.
- F4: UCB and EI agree, so I continue exploring around the best (0.3675) with κ=1.5 and ξ=0.005.
- F5: UCB and EI agree on a region with very high uncertainty (std 316.23). I follow it to help the GP learn, keeping κ=1.5.
- F6: EI has a much higher mean (-0.3614 vs -1.1148) and lower uncertainty, so I follow EI with κ=2.5.
- F7: UCB and EI agree on a point with a mean close to the best (2.0242). I refine that region with κ=1.7.
- F8: EI has a higher mean (9.8504 vs 9.6249) and lower uncertainty, so I follow EI with κ=3.0 and ξ=0.02.

## Week 4 - Strategy Notes

**Results coming in (Week 3):** New bests for F4 (0.3675), F7 (2.0242) and F8 (9.8884). F1 3.8e-34, F2 0.258, F3 -0.114, F5 2986.9 (the peak, re-queried), F6 -0.878.

- F1: Still flat. UCB repeats the same point, so I follow EI again. The Matern (ν=1.5) kernel is kept and κ stays at 2.5. It remains the toughest function.
- F2: A lower output, so the extra exploration did not pay off. I keep κ=2.0 and ξ=0.05 and follow the point where UCB and EI agree.
- F3: Another decline. UCB and EI agree on a new region with a better predicted mean (0.0015) than the best (-0.0348), so I follow it with κ=1.5.
- F4: New best (0.3675). I exploit by following UCB, which refines around the best with very low uncertainty (std 0.0010).
- F5: The peak is confirmed at 2986.94 with no change. UCB and EI agree on refining this region, so I keep exploiting it.
- F6: A lower output. EI has a higher mean and lower uncertainty than UCB, so I follow EI with κ=2.5.
- F7: New best (2.0242). UCB and EI agree, so I refine the region with κ=1.7.
- F8: New best (9.8884). EI has a higher mean and lower uncertainty, so I follow EI with κ=3.0 and ξ=0.02.

## Week 3 - Strategy Notes

**Results coming in (Week 2):** New bests for F4 (-0.0055), F6 (-0.3126) and F7 (1.683). F2 fell to 0.481, F3 to -0.433 (a failed corner), F5 to 2152.7 and F8 to 9.685.

- F1: Switched the kernel from RBF to Matern (ν=1.5) for more flexibility, to catch patterns the RBF might miss in the flat landscape. I raised κ to encourage exploration and followed EI because it chose a new region. Next step is to account for noise.
- F2: Exploitation failed with a lower output. I raised κ to 2 and increased ξ for more exploration.
- F3: The new output was far worse. I return to the best known point (-0.0348, still from the original data) and exploit it with κ=1.5.
- F4: A better output. I exploit and lower κ to 1.5.
- F5: Exploring nearby gave a lower output, so I go back to the peak, refine it, and exploit it heavily to find the exact maximum.
- F6: Further improvement. I keep κ the same to continue encouraging exploration.
- F7: Improvement seen. I focus more on exploitation by lowering κ to about 1.7.
- F8: A slightly lower output, so I explore more aggressively by raising κ and ξ.

## Week 2 - Strategy Notes

**Results coming in (Week 1):** New bests for F4 (-0.289), F5 (2986.94, a huge peak) and F8 (9.781). F1 1.9e-245 (flat), F2 0.021, F3 -0.110, F6 -1.118, F7 1.361.

- F1: Continue to explore, as it remains a tougher case (EI picked a point on the boundary).
- F2: Looks promising, so I exploit with slight exploration.
- F3: Strong evidence for the current region, so I keep exploring it.
- F4: A more balanced mix of exploring and exploiting.
- F5: Found a massive maximum. UCB wants to repeat the same point, which gives no new information, so I explore nearby with high uncertainty. If that fails, I go back.
- F6: Following EI to explore a promising region.
- F7: Seemed stagnant, so I reduced κ (from 2.5 to 2.0) to focus on the better region while leaving space to explore.
- F8: Following EI, where the GP predicts improvement.

So far improvements have been seen. The configurations for F1 and F7 need experimenting.

## Week 1 - Strategy Notes

I fitted a GP for each function, with kernels chosen by dimension (RBF for F1 and F2, Matern 2.5 for F3 and F4, Matern 1.5 for F5 to F8), and scored 10,000 random candidate points with UCB and EI. κ followed a simple rule by dimension (1.5 for the 2D functions, 2.0 for F3 to F5, 2.5 for F6 to F8) with ξ at 0.01 for all.
**Observations across Weeks 1 to 5:** F1 stayed flat throughout, and F2 never beat its starting 0.6112. F5's peak came in Week 1. The repeated queries (F1 Weeks 3 and 4, F4 Week 4, F5 Weeks 3 and 4) happened because UCB and EI kept proposing known points and I followed them, which led to the duplicate safeguard added later. An F1 print statement said κ=0.01 while the code used 1.5, which turned out to be a typo in the label.
