"""
Module 4: Analytics & Statistical Validation
==============================================
Deep-dives into A/B test results:
  - Statistical significance (chi-square on response rates)
  - Recovery breakdown by DPD bucket and offer type
  - Channel performance analysis
  - Pareto: which borrower segments drive most recovery
  - Exports Tableau-ready BI datasets

Input:  data/processed/ab_test_results.csv
Output: outputs/ (multiple analytics CSVs for Tableau)
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

IN_PATH = "data/processed/ab_test_results.csv"
os.makedirs("outputs", exist_ok=True)


# ── 1. Statistical Significance ───────────────────────────────────────────────
def test_significance(df: pd.DataFrame) -> dict:
    """
    Chi-square test on response rates between arms.
    H0: Response rate is the same in Control and Treatment.
    """
    ctrl  = df[df["arm"] == "Control"]
    treat = df[df["arm"] == "Treatment"]

    c_responded  = ctrl["responded"].sum()
    c_total      = len(ctrl)
    t_responded  = treat["responded"].sum()
    t_total      = len(treat)

    contingency = np.array([
        [c_responded,  c_total  - c_responded],
        [t_responded,  t_total  - t_responded]
    ])

    chi2, p_value, dof, _ = stats.chi2_contingency(contingency)

    result = {
        "chi2_statistic":      round(chi2, 4),
        "p_value":             round(p_value, 6),
        "degrees_of_freedom":  dof,
        "significant_at_95":   p_value < 0.05,
        "significant_at_99":   p_value < 0.01,
        "control_response_rate_pct":   round(c_responded / c_total * 100, 2),
        "treatment_response_rate_pct": round(t_responded / t_total * 100, 2),
    }

    print("\n── STATISTICAL SIGNIFICANCE ────────────────────────────")
    for k, v in result.items():
        print(f"  {k:<40} {v}")

    return result


# ── 2. Recovery by DPD Bucket ─────────────────────────────────────────────────
def recovery_by_dpd(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby(["arm","dpd_bucket"]).agg(
        borrowers        = ("SK_ID_CURR",       "count"),
        responded        = ("responded",         "sum"),
        amount_recovered = ("amount_recovered",  "sum"),
    ).reset_index()

    out["response_rate_pct"] = (out["responded"] / out["borrowers"] * 100).round(2)
    out["avg_recovered"]     = (out["amount_recovered"] / out["borrowers"]).round(2)

    out.to_csv("outputs/recovery_by_dpd.csv", index=False)
    print("\n── RECOVERY BY DPD BUCKET ──────────────────────────────")
    print(out.to_string(index=False))
    return out


# ── 3. Channel Performance ────────────────────────────────────────────────────
def channel_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Only Treatment arm has meaningful channel variation."""
    treat = df[df["arm"] == "Treatment"]
    out = treat.groupby("strategy_channel").agg(
        borrowers        = ("SK_ID_CURR",      "count"),
        responded        = ("responded",        "sum"),
        amount_recovered = ("amount_recovered", "sum"),
    ).reset_index()

    out["response_rate_pct"]  = (out["responded"] / out["borrowers"] * 100).round(2)
    out["recovery_per_contact"] = (out["amount_recovered"] / out["borrowers"]).round(2)

    out.to_csv("outputs/channel_performance.csv", index=False)
    print("\n── CHANNEL PERFORMANCE (Treatment Arm) ─────────────────")
    print(out.to_string(index=False))
    return out


# ── 4. Offer Effectiveness ────────────────────────────────────────────────────
def offer_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby(["arm","strategy_offer"]).agg(
        borrowers        = ("SK_ID_CURR",      "count"),
        responded        = ("responded",        "sum"),
        amount_recovered = ("amount_recovered", "sum"),
    ).reset_index()

    out["response_rate_pct"]  = (out["responded"] / out["borrowers"] * 100).round(2)
    out["recovery_per_contact"] = (out["amount_recovered"] / out["borrowers"]).round(2)

    out.to_csv("outputs/offer_effectiveness.csv", index=False)
    print("\n── OFFER EFFECTIVENESS ─────────────────────────────────")
    print(out.to_string(index=False))
    return out


# ── 5. Pareto: Which Segments Drive Recovery ──────────────────────────────────
def pareto_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify the borrower segments (DPD x Risk Tier) that contribute
    disproportionately to total recovery — the 20% driving 80%.
    """
    treat = df[df["arm"] == "Treatment"]
    out = treat.groupby(["dpd_bucket","risk_tier"]).agg(
        borrowers        = ("SK_ID_CURR",      "count"),
        amount_recovered = ("amount_recovered", "sum"),
    ).reset_index().sort_values("amount_recovered", ascending=False)

    total_recovery = out["amount_recovered"].sum()
    out["recovery_share_pct"] = (out["amount_recovered"] / total_recovery * 100).round(2)
    out["cumulative_pct"]     = out["recovery_share_pct"].cumsum().round(2)

    out.to_csv("outputs/pareto_segments.csv", index=False)
    print("\n── PARETO: TOP RECOVERY SEGMENTS (Treatment) ───────────")
    print(out.head(10).to_string(index=False))
    return out


# ── 6. Timing Window Analysis ─────────────────────────────────────────────────
def timing_analysis(df: pd.DataFrame) -> pd.DataFrame:
    treat = df[df["arm"] == "Treatment"]
    out = treat.groupby("strategy_window").agg(
        borrowers        = ("SK_ID_CURR",      "count"),
        responded        = ("responded",        "sum"),
        amount_recovered = ("amount_recovered", "sum"),
    ).reset_index()

    out["response_rate_pct"]    = (out["responded"] / out["borrowers"] * 100).round(2)
    out["recovery_per_contact"] = (out["amount_recovered"] / out["borrowers"]).round(2)

    out.to_csv("outputs/timing_analysis.csv", index=False)
    print("\n── TIMING WINDOW ANALYSIS (Treatment) ──────────────────")
    print(out.to_string(index=False))
    return out


# ── 7. Tableau Master Export ──────────────────────────────────────────────────
def tableau_export(df: pd.DataFrame):
    """
    Single flat file with all fields needed for Tableau dashboard.
    """
    export_cols = [
        "SK_ID_CURR", "arm", "dpd_bucket", "risk_tier",
        "preferred_channel", "optimal_contact_window",
        "offer_type", "discount_pct", "urgency_flag",
        "strategy_channel", "strategy_window", "strategy_offer",
        "strategy_response_rate", "responded",
        "AMT_CREDIT", "amount_recovered", "expected_recovery_amt",
        "age_years", "employment_years", "dti", "ext_score_avg",
        "CODE_GENDER", "NAME_CONTRACT_TYPE", "REGION_RATING_CLIENT"
    ]
    available = [c for c in export_cols if c in df.columns]
    df[available].to_csv("outputs/tableau_master.csv", index=False)
    print(f"\nTableau master export: outputs/tableau_master.csv  ({len(df):,} rows)")


def run():
    assert os.path.exists(IN_PATH), f"Run 03_ab_test.py first. Missing: {IN_PATH}"

    df = pd.read_csv(IN_PATH)

    sig    = test_significance(df)
    dpd    = recovery_by_dpd(df)
    ch     = channel_performance(df)
    offers = offer_effectiveness(df)
    pareto = pareto_analysis(df)
    timing = timing_analysis(df)
    tableau_export(df)

    print("\n── ALL OUTPUTS SAVED TO outputs/ ───────────────────────")

if __name__ == "__main__":
    run()
