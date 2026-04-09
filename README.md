# Collections Contact Strategy Engine
### A/B Test: Model-Driven vs Flat Contact Strategy

A Python-based analytics system that operationalizes behavioral models to optimize debt recovery for consumer finance institutions. Built on real-world borrower data from the Home Credit Default Risk dataset (307K+ borrowers).

---

## Business Problem

Loan servicers and debt collection agencies contact borrowers using flat, one-size-fits-all strategies — same channel, same timing, same message for everyone. This results in:

- Low response rates from mismatched channel preferences
- Revenue leakage from avoidable missed contacts
- Operational inefficiency: high contact volume, low conversion

This project answers: **does a model-driven contact strategy — right channel, right time, right offer — produce measurably better recovery outcomes than a flat strategy?**

---

## What This Project Demonstrates

| Capability | Implementation |
|---|---|
| Behavioral model operationalization | Channel affinity scores, contact timing models |
| Offer logic design | DPD bucket × Risk tier offer matrix |
| A/B test framework | Stratified random split, response simulation, lift measurement |
| Statistical validation | Chi-square significance test on response rates |
| Analytics & BI export | Pareto analysis, channel performance, Tableau-ready datasets |

---

## Project Architecture

```
collections-strategy-engine/
│
├── data/
│   ├── raw/               ← Place application_train.csv here
│   └── processed/         ← Intermediate outputs (auto-generated)
│
├── src/
│   ├── main.py                  ← Pipeline runner
│   ├── 01_load_and_profile.py   ← Borrower profiling + DPD segmentation
│   ├── 02_offer_logic.py        ← Offer assignment via matrix
│   ├── 03_ab_test.py            ← A/B test simulation + lift metrics
│   └── 04_analytics.py          ← Deep analytics + BI exports
│
├── sql/
│   └── analytics_queries.sql    ← DuckDB/SQL analytical queries
│
├── outputs/                     ← Tableau-ready CSVs (auto-generated)
│   ├── tableau_master.csv
│   ├── recovery_by_dpd.csv
│   ├── channel_performance.csv
│   ├── offer_effectiveness.csv
│   ├── pareto_segments.csv
│   └── timing_analysis.csv
│
├── dashboard/                   ← Tableau workbook + screenshots
├── requirements.txt
└── README.md
```

---

## Experiment Design

### Hypothesis
A model-driven contact strategy — using channel affinity scores, optimal contact windows, and DPD-based offer logic — will produce a statistically significant lift in borrower response rate and total amount recovered versus a flat call-everyone approach.

### Arms

| | Control (Arm A) | Treatment (Arm B) |
|---|---|---|
| **Channel** | Call (everyone) | Model-predicted preferred channel |
| **Timing** | 10 AM (flat) | Borrower-optimal window |
| **Offer** | Payment Reminder (flat) | DPD bucket × Risk tier offer |
| **Split** | 50% random stratified | 50% random stratified |

### Success Metrics
- **Primary:** Response rate lift (percentage points)
- **Secondary:** Total recovery lift (%), contact efficiency (recovery per contact)
- **Validation:** Chi-square significance test (p < 0.05)

---

## Model Design

### Channel Affinity Scoring
Each borrower receives a normalized affinity score for Call, SMS, and Email based on:
- Age (proxy for digital channel comfort)
- External credit score (proxy for financial literacy)
- Debt-to-income ratio
- Employment tenure

### Contact Timing
Optimal window (Morning / Afternoon / Evening) derived from:
- Employment status and tenure
- Regional rating (urban vs rural)

### Offer Logic Matrix

| DPD Bucket | Low Risk | Medium Risk | High Risk |
|---|---|---|---|
| Current | Payment Reminder | Payment Reminder | Early Intervention |
| DPD 1-30 | Payment Reminder | Settlement Offer (5%) | Settlement Offer (8%) |
| DPD 31-60 | Settlement Offer (5%) | Settlement Offer (10%) | Restructuring Proposal |
| DPD 61-90 | Settlement Offer (12%) | Restructuring Proposal | Legal Warning + Offer (15%) |

---

## Setup & Usage

### 1. Get the data
Download `application_train.csv` from [Home Credit Default Risk on Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data) and place it in `data/raw/`.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the full pipeline
```bash
python src/main.py
```

### 4. View analytics in Tableau
Load `outputs/tableau_master.csv` into Tableau. Dashboard covers:
- A/B lift summary
- Recovery by DPD bucket
- Channel performance heatmap
- Pareto: top segments driving 80% of recovery
- Offer effectiveness breakdown

---

## Key Results

| Metric | Control (Flat) | Treatment (Model-Driven) | Lift |
|---|---|---|---|
| Response Rate | 38.02% | 52.30% | **+14.28 pp** |
| Avg Recovery / Borrower | ~203K | ~262K | **+29.8%** |
| Statistical Significance | — | — | **p < 0.01** |

**Live Dashboard →** [View on Tableau Public](https://public.tableau.com/app/profile/shubham.singh7575/viz/CollectionsContactStrategyEngine/Dashboard1?publish=yes)
---

## Design Decisions

**Rule-based offer logic over ML:** Chosen for interpretability and operational deployability. In collections environments, ops teams need to explain offer decisions to compliance and clients — black-box models create friction.

**Stratified random split:** DPD bucket stratification ensures arm balance across delinquency severity, preventing Simpson's Paradox from confounding lift metrics.

**Simulated response rates over synthetic outcomes:** Response probabilities are derived deterministically from real borrower attributes, not randomly assigned — ensuring the behavioral signal in the data drives the outcome.

---

## Technologies
- Python (Pandas, NumPy, SciPy)
- SQL (DuckDB-compatible)
- Tableau (dashboard)
- Home Credit Default Risk dataset (Kaggle)

---

**Author:** Shubham Singh
