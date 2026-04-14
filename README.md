# Collections Strategy A/B Testing Engine  
### Model-Driven vs Flat Contact Strategy at 307K Borrower Scale

A Python-based analytics system that operationalizes behavioral models to optimize debt recovery for consumer finance institutions. Built on real-world borrower data from the Home Credit Default Risk dataset (307K+ borrowers).

---

## Results Snapshot

- **Response Rate Lift:** +14.28 percentage points (38.02% → 52.30%)
- **Recovery Uplift:** +27.53%
- **Incremental Recovery:** ₹8.68 Billion
- **Statistical Significance:** p < 0.01 (Chi-square test)
- **Scale:** 307,511 borrowers

Model-driven contact strategy significantly outperforms flat contact strategy across all key metrics.

---

## Business Problem

Debt collection strategies are typically one-size-fits-all, leading to suboptimal recovery rates and wasted contact effort.

Key question:
**Can a model-driven strategy (right channel, timing, and offer) outperform a flat “call everyone” approach in measurable recovery outcomes?**

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

## Key Findings

- Treatment arm achieved **+14.28 pp higher response rate** vs control (52.30% vs 38.02%)
- Total recovery increased by **+27.53%**, generating **₹8.68B incremental recovery**
- Results are statistically significant (**p < 0.01**)
- **DPD 1–30 (Medium/High Risk)** segments drive ~69% of total recovery
- **Email channel** delivers highest recovery per contact, while SMS/Call drive similar response rates
- Trade-off observed: **+27.5% recovery uplift vs -7.3% contact efficiency**, indicating higher recovery comes at increased outreach cost — requiring optimization based on business priorities (growth vs cost control)

---

## Key Results

| Metric | Control (Flat) | Treatment (Model-Driven) | Lift |
|---|---|---|---|
| Response Rate | 38.02% | 52.30% | **+14.28 pp** |
| Avg Recovery / Borrower | ~203K | ~262K | **+29.8%** |
| Statistical Significance | — | — | **p < 0.01** |

**Live Dashboard →** [View on Tableau Public](https://public.tableau.com/app/profile/shubham.singh7575/viz/CollectionsContactStrategyEngine/Dashboard1?publish=yes)

---

## Product Insights

- Personalization (channel + timing + offer) materially improves user response behavior
- Early delinquency segments (DPD 1–30) present highest ROI for intervention
- Channel optimization shows diminishing returns beyond response rate — recovery per contact varies significantly
- Trade-off between scale and efficiency must be optimized based on business goals (max recovery vs cost efficiency)

---

## Real-World Application

This system mirrors how fintech lenders and collections teams:

- Optimize borrower contact strategies
- Run controlled experiments on recovery workflows
- Balance recovery vs operational cost
- Personalize interventions using behavioral signals

Applicable to:
- Lending platforms (collections optimization)
- BNPL / credit products
- Fintech risk & recovery teams

---

## Business Recommendation

- Adopt model-driven contact strategy as default for early delinquency segments (DPD 1–30), where highest recovery lift is observed  
- Prioritize Email as primary channel for high-value segments due to highest recovery per contact  
- Use hybrid strategy: maximize recovery in high-risk segments while optimizing cost efficiency in lower-risk segments  
- Continuously run A/B tests to refine channel mix, timing, and offer strategies  

Net: Favor recovery maximization in early-stage delinquency, with selective efficiency optimization at scale

---

## Design Decisions

**Rule-based offer logic over ML:** Chosen for interpretability and operational deployability. In collections environments, ops teams need to explain offer decisions to compliance and clients — black-box models create friction.

**Stratified random split:** DPD bucket stratification ensures arm balance across delinquency severity, preventing Simpson's Paradox from confounding lift metrics.

**Simulated response rates over synthetic outcomes:** Response probabilities are derived deterministically from real borrower attributes, not randomly assigned — ensuring the behavioral signal in the data drives the outcome.

---

## Limitations

- Results are based on simulated response behavior derived from borrower attributes; real-world performance may vary due to external factors (agent behavior, regulatory constraints, customer sentiment)

---

## Next Steps

- Introduce ML-based uplift modeling to predict individual treatment impact  
- Optimize cost-aware strategy (maximize recovery per ₹ spent)  
- Extend to real-time decisioning using streaming transaction signals  

---

## Technologies
- Python (Pandas, NumPy, SciPy)
- SQL (DuckDB-compatible)
- Tableau (dashboard)
- Home Credit Default Risk dataset (Kaggle)

---

**Author:** Shubham Singh
