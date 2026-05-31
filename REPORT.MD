 
# while(1):evolve — Forecasting-Sybilion

---

## Team

- **Asma Lehiany** — Machine learning pipeline, backend implementation, system design, and domain modeling
- **Oliver Pacheco Montero** — Documentation and project presentation materials
- **Anton Dudnik** — Data handling, validation, and compliance of external and aggregated macro datasets
- **Shokhrukh Kholmatov** — Mathematical modeling, regression framework design, and interaction-term formulation for shock attribution

**Track:** Forecasting AI (Sybilion)

---

## What we do

We built a commodity forecasting and decision-support system that models how geopolitical, policy, and mining shocks affect critical metal prices using regression and external forecasts. It is designed for analysts and decision-makers in energy, EV supply chains, and commodities markets. The system transforms raw macro signals into actionable trading and risk-management recommendations such as hedge, buy, sell, or wait.

---

## Problem

Given a baseline forecast of metal prices, how do different real-world shock categories (geopolitical, mining/supply-chain, policy) and their interactions quantitatively distort that baseline?

So the task becomes not just predicting prices, but decomposing deviations from a forecasted equilibrium path into interpretable shock contributions.

## Approach

We built a two-stage forecasting and attribution framework for metal prices. First, a baseline forecast (Sybillion) estimates prices under neutral conditions. Then, we apply a structural regression model on geopolitical, mining, and policy shock indices (and their interactions) to estimate how these shocks systematically distort the baseline, enabling counterfactual forecasting under different shock scenarios.

Rough path for the solutions:

1. Baseline generation (Sybillion model)

- produces expected price trajectory under neutral conditions


2. Shock feature construction

- G_t, P_t, M_t: macro shock intensities
- interaction terms: G_tP_t, G_tM_t, M_tP_t

3. Regression layer (your model)

- learns marginal impact of each shock on log-price deviations

4. Counterfactual adjustment

- final step:

- adjust baseline forecast by estimated shock contributions
- create an agent which transforms raw macro signals into actionable trading and risk-management recommendations such as hedge, buy, sell, or wait.


So effectively:

```Final Forecast = Baseline Forecast + Shock Impact Correction```

---

## How does the solution work?

+ Baseline-first decomposition (Sybillion + residual modeling)

We treat Sybillion forecasts as a neutral “equilibrium” price path and only model deviations from it. This ensures the regression is learning shock effects, not re-learning the entire price process.

+ Structured shock encoding with interaction effects

Macro drivers (geopolitical, mining/supply-chain, policy) are transformed into continuous indices, and we explicitly include interaction terms (GP, GM, PM) to capture co-occurring shock amplification effects.

+ Interpretable regression layer for attribution

A log-linear OLS model (statsmodels) estimates marginal contributions of each shock component, enabling direct decomposition of forecast deviations into economic drivers.

+ Counterfactual adjustment mechanism

The learned coefficients are applied to future shock scenarios to adjust baseline forecasts, producing “what-if” price trajectories under different macro conditions.

+ Local Python pipeline for reproducibility

The system runs end-to-end in Python (pandas + NumPy + statsmodels), processing Excel-based panel data per metal and outputting coefficients and scenario-based forecasts.

---

## How to run it

See README file

---

## Results


We decompose metal prices into baseline trends and shock effects (geopolitical, mining, policy). Interaction terms improve fit and capture nonlinear stress effects. The model generates interpretable scenario-based forecasts and simple trading signals from macro shocks.

The numbers. This is the section the jury reads most carefully.

- **Headline metric:**
+  The interaction-augmented regression model improves explanatory power over the baseline additive model, increasing R**2 on log metal price dynamics across EV-critical minerals.

- **Baseline comparison:**
+ Compared to a model using only Sybillion forecasts, the full model with  individual shock indices (G, P, M) and interaction terms (GP, GM, PM) reduces unexplained variance and provides more stable attribution of price movements to macroeconomic drivers.

- **Per-domain breakdown (metals):**
+ We focus on four critical EV supply chain metals: cobalt (Co), nickel (Ni), lithium (Li), and manganese (Mn).

* Co / Ni → highly sensitive to geopolitical and mining shocks
* Li → strongly driven by policy and demand-side structural shifts
* Mn → mixed sensitivity across all shock channels with weaker but stable effects

- **Data sources:**

+ Monthly metal price series (2017–2026)
+ EV mineral coverage: Co, Ni, Li, Mn
+ Macro shock indices (geopolitical, mining/supply-chain, policy), constructed from aggregated open-source event and market data
+ External baseline forecasts from Sybillion system
+ All modeling performed in Python using `pandas`, `numpy`, and `statsmodels`


If you used the track's official scoring script (Infineon `eval_metrics.py`), paste the scores here. If you defined your own metrics, explain what they measure and why they are the right metrics for what you built.

---

## What worked

## What didn't work

Two or three things you tried that failed or got abandoned. This counts. Honest engineering reporting is part of what we judge.

---

## What you'd do with another 36 hours

We would extend the system to allow user-controlled scenario inputs, including shock intensities for geopolitical (G), policy (P), and mining (M) factors, as well as a global risk factor slider (0 = no intensity/risk, 1 = extreme intensity/risk). This would enable interactive simulation of how different macro risk environments affect metal price forecasts.

---

## Track-specific deliverables

### 📈 Forecasting AI (Sybilion)
- [X] Working agent or application — not slideware
- [X] Backtest results: at least one historical scenario validating the decision logic
- [X] Driver-importance visualization included in demo
- [X] Agent is ready to adapt to a mid-run assumption shift on Sunday
- [X] Domain choice rationale stated above in "Problem"

---

## Credits & dependencies

- **Open-source libraries used** (with versions): python3 libraries, which counted above and also in README
- **AI coding assistants used during the hackathon**: Claude Code / ChatGPT / Gemini
- **Datasets**:

---

## A note on honesty

In order to adjust the shocks we choose importance ratios of some events (see README) in order to compute the variables G, P and M. Also since we are not expert on the macroeconomic models it is not completely obvious if there is a more natural model than the log-linear regression

---

*Submitted by team while(1):evolve for Zero One Hack_01, 31.05.2026.*
