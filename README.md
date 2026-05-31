*The project has been created as part of the Zero One Hack: Vienna's Supercompute AI Hackathon by Asma Lehiany, Oliver Pacheco Montero, Anton Dudnik and Shokhrukh Kholmatov, team "while (1): evolve"


# Commodity Price Forecasting and Decision Support System

## Overview

This project forecasts future prices of some critical EV metals and evaluates the impact of geopolitical, policy, and mining-related shocks on market dynamics.

The system combines:

- Historical metal price data
- Geopolitical indicators
- Policy indicators
- Mining and supply-chain indicators
- Time-series forecasting
- Econometric shock modeling
- Risk-adjusted decision support

The goal is to help analysts, investors, producers, and policymakers understand how external events may affect future metal prices and identify appropriate strategic actions.

---

## Metals Covered

- Lithium
- Nickel
- Cobalt
- Manganese


## Data

For each metal, the dataset contains Date (monthly) and  Historical market price. Moreover, we used some of main geopolitical events, policy changes and mining/supply issues which affected the price

# Cobalt (Co)

## Geopolitics

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| DRC political instability baseline phase | 2016-01 → ongoing | 0.30 | Structural supply risk (dominant factor) |
| Ethical sourcing / ESG scrutiny rise | 2018-01 → ongoing | 0.20 | Demand-side structural shift |
| COVID supply chain disruption | 2020-03 → 2021-12 | 0.15 | Temporary but global shock |
| Africa logistics and DRC instability spike | 2022-01 → ongoing | 0.25 | Amplifies supply disruption |
| Resource nationalism in Africa | 2024-01 → ongoing | 0.10 | Emerging but secondary factor |

##  Mining & Supply

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| EV-driven cobalt demand surge | 2017-01 → 2021-12 | 0.35 | Primary demand driver |
| Battery chemistry shift (reduced cobalt use) | 2021-01 → ongoing | 0.25 | Structural downward pressure |
| Artisanal mining disruption cycles | 2019-01 → ongoing | 0.15 | Persistent but noisy supply effect |
| Recycling and substitution expansion | 2023-01 → ongoing | 0.15 | Medium-term structural effect |
| Cobalt price spike cycle | 2021-06 → 2022-06 | 0.10 | Short-term volatility factor |

## Policy

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| OECD cobalt sourcing guidelines | 2018-05 → ongoing | 0.20 | ESG-driven market constraint |
| Corporate ESG cobalt reduction initiatives | 2021-01 → ongoing | 0.15 | Indirect but significant demand effect |
| US Inflation Reduction Act (IRA) sourcing requirements | 2022-08 → ongoing | 0.30 | Major supply-chain restructuring |
| EU Battery Regulation enforcement | 2023-01 → ongoing | 0.25 | Binding structural regulation |
| DRC export quota discussions | 2025-01 → ongoing | 0.10 | Emerging and uncertain policy factor |

---

#  Lithium (Li)

## 🌍 Geopolitics

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| US–China trade war escalation | 2018-03 → 2020-12 | 0.20 | Foundational supply-chain disruption |
| COVID global disruption | 2020-03 → 2021-12 | 0.10 | Temporary global shock |
| Russia–Ukraine war spillover | 2022-02 → ongoing | 0.35 | Energy and inflation shock |
| Red Sea / Middle East shipping instability | 2023-10 → ongoing | 0.10 | Logistics disruption |
| US–China EV technology rivalry | 2023-01 → ongoing | 0.25 | Structural supply-chain fragmentation |

##  Mining & Supply

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| Lithium supercycle demand expansion | 2017-01 → 2022-12 | 0.35 | Long-term demand driver |
| China EV battery manufacturing boom | 2020-01 → 2022-12 | 0.25 | Demand concentration effect |
| Lithium price bubble peak phase | 2021-06 → 2022-06 | 0.10 | Short-term speculative cycle |
| Oversupply (Australia and Chile expansion) | 2023-01 → ongoing | 0.20 | Major correction force |
| Price correction / bear market cycle | 2023-06 → 2025-06 | 0.10 | Lagged adjustment process |

## Policy

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| China EV subsidy expansion | 2015-01 → 2022-12 | 0.35 | Demand creation engine |
| EU Green Deal acceleration | 2020-12 → ongoing | 0.15 | Long-term demand support |
| US Inflation Reduction Act (IRA) | 2022-08 → ongoing | 0.25 | Global supply-chain restructuring |
| EU Critical Raw Materials Act | 2023-03 → ongoing | 0.15 | Strategic supply diversification |
| China battery export tightening | 2024-01 → ongoing | 0.10 | Emerging supply constraint |

---

#  Nickel (Ni)

## Geopolitics

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| Indonesia resource nationalism escalation | 2014-01 → ongoing | 0.20 | Direct supply-chain influence |
| Russia–Ukraine war | 2022-02 → ongoing | 0.45 | Major nickel and energy shock |
| Red Sea shipping disruption | 2023-10 → ongoing | 0.20 | Logistics and shipping cost increase |
| China–Indonesia industrial alignment | 2020-01 → ongoing | 0.15 | Structural trade reshaping |

## Mining & Supply

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| EV nickel demand emergence | 2017-01 → 2021-12 | 0.20 | Demand-side structural driver |
| Indonesia HPAL capacity expansion | 2020-01 → ongoing | 0.40 | Structural supply expansion |
| LME nickel short squeeze crisis | 2022-03 → 2022-03 | 0.15 | Extreme but short-lived shock |
| Indonesia oversupply phase | 2023-01 → ongoing | 0.25 | Major price-determining factor |

## Policy

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| Indonesia raw ore export ban | 2014-01 → ongoing | 0.35 | Direct supply restriction |
| Full enforcement of export restrictions | 2020-01 → ongoing | 0.05 | Incremental effect |
| US Inflation Reduction Act (IRA) | 2022-08 → ongoing | 0.25 | Supply-chain restructuring |
| EU critical raw materials diversification | 2023-03 → ongoing | 0.15 | Long-term strategic demand shift |
| Indonesia mining quota tightening | 2024-01 → ongoing | 0.20 | Supply-control mechanism |

---

# Manganese (Mn)

## Geopolitics

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| US–China trade war | 2018-03 → 2020-12 | 0.20 | Steel and battery-material tension |
| COVID global disruption | 2020-03 → 2021-12 | 0.10 | Temporary global shock |
| Russia–Ukraine war | 2022-02 → ongoing | 0.35 | Metals and energy inflation |
| Red Sea shipping disruption | 2023-10 → ongoing | 0.15 | Logistics shock |
| China–Africa resource competition | 2021-01 → ongoing | 0.20 | Supply-chain influence |

## Mining & Supply

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| China steel demand supercycle | 2016-01 → 2018-12 | 0.10 | Early structural demand phase |
| Global steel expansion cycle | 2017-01 → 2021-12 | 0.30 | Core demand driver |
| Post-COVID steel rebound | 2021-01 → 2022-06 | 0.25 | Cyclical demand surge |
| South African electricity crisis | 2022-01 → ongoing | 0.20 | Supply constraint |
| Battery-grade manganese investment surge | 2022-01 → ongoing | 0.15 | Emerging EV demand source |

## Policy

| Event | Timeline | Weight | Rationale |
|---------|---------|---------|---------|
| China infrastructure stimulus cycles | 2015-01 → 2019-12 | 0.10 | Historical demand support |
| China environmental restrictions | 2017-01 → 2020-12 | 0.20 | Supply constraint |
| EU carbon border adjustment planning | 2021-07 → ongoing | 0.00 | Background policy factor |
| US Inflation Reduction Act (IRA) | 2022-08 → ongoing | 0.30 | EV-material market reshaping |
| Critical minerals diversification policies (EU + US) | 2023-01 → ongoing | 0.25 | Structural supply diversification |
| South Africa mining and electricity policy stress | 2021-01 → ongoing | 0.15 | Regional supply impact |


The weights are chosen apprximately according with the effect of the event on the price.
Using the wieghts we create variables

G --- Aggregated geopolitical score
P ---  Aggregated policy score
M --- Aggregated mining score

in the data and their interactions.


The data spans approximately January 2017 to April 2026.

---

## Methodology

### 1. Baseline Forecasting

Future prices are obtained from a forecasting model/API of Sybilion.

For each future horizon, the system receives:

- predicted price
- confidence interval
- forecast uncertainty

---

### 2. Shock Modeling

The influence of external shocks is modeled using the log-linear regression:

```\text
log(P_t) = β₀ + β_G·G_t + β_P·P_t + β_M·M_t + β_GP·GP_t + β_GM·GM_t + β_PM·PM_t
```
where:

- \(G_t\) represents geopolitical effects,
- \(P_t\) represents policy effects,
- \(M_t\) represents mining/supply effects.

Interaction terms capture combined effects of simultaneous events. The β_i are computed according the log-linear regression coefficients.


### 3. Expected Return Estimation

Let
```\text
P_0
```
denote the current price (in April 2026) and
```\text
P_t'
```
the forecasted future price.

The expected log-return is computed as
```\text
r_t = \log(P_t') - \log(P_0).
```

Shock effects are incorporated through the estimated regression coefficients.

---

### 4. Risk Estimation

Forecast confidence intervals are converted into volatility estimates.

The uncertainty measure is used to evaluate forecast reliability and downside risk.

---

### 5. Utility Function

The project evaluates opportunities using a risk-adjusted utility function:
```\text
U = E[r] - \lambda \, Var(r),
```
where

- \(E[r]\) is the expected return,
- \(Var(r)\) is the forecast variance,
- \(\lambda\) is a risk-aversion parameter.

---

### 6. Decision Agent

Based on expected return, uncertainty, and shock effects, the system generates recommendations such as:

- Increase inventory
- Reduce inventory
- Accelerate procurement
- Delay procurement
- Increase production
- Reduce production
- Hedge exposure
- Maintain current strategy

Each recommendation is accompanied by a quantitative explanation.

---

## Project Structure

```text
EXANTE/
│
├── data/
├── models/
│   ├── shock_model.py
│   ├── forecast_model.py
│
├── engine/
│   ├── decision_engine.py
│   ├── scenario_engine.py
│
├── api/
│   ├── sybilion_client.py
│
├── ui/
│   ├── js/
│   ├── css/
│   ├── index.html
│
├── utils/
│   ├── helpers.py
│
├── results/
│   ├── betas.json
│
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd forecasting-project

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

### Run regression analysis

```bash
python regression.py
```

### Generate forecasts

```bash
python forecast.py
```

### Run decision agent

```bash
python decision_agent.py
```

---

## Example Output

```text
Metal: Lithium

Expected Return: 7.8%
Volatility: 3.2%
Shock Score: +1.5%
Utility: 6.8%

Recommendations:

✓ Increase inventory
✓ Accelerate procurement
✓ Increase production
✓ No hedge required

Reason:
Positive expected return and favorable macro conditions
outweigh forecast uncertainty.
```

---

## Limitations

- Regression coefficients do not imply causality.
- Historical relationships may change over time.
- Forecast quality depends on the accuracy of external data sources.
- Interaction effects may be sensitive to model specification.


## Authors

Developed as part of a commodity forecasting and decision-support project focused on critical minerals and battery supply chains.
