"""
Module 1: Load and Profile Borrowers
=====================================
Loads Home Credit Default Risk data and engineers borrower profiles
with delinquency buckets, risk tiers, and behavioral signals.

Input:  data/raw/application_train.csv  (Home Credit Kaggle dataset)
Output: data/processed/borrower_profiles.csv
"""

import pandas as pd
import numpy as np
import os

RAW_PATH   = "data/raw/application_train.csv"
OUT_PATH   = "data/processed/borrower_profiles.csv"

SEED = 42
np.random.seed(SEED)


# ── 1. Load ───────────────────────────────────────────────────────────────────
def load_raw(path: str) -> pd.DataFrame:
    required_cols = [
        "SK_ID_CURR", "TARGET", "AMT_CREDIT", "AMT_ANNUITY",
        "AMT_INCOME_TOTAL", "DAYS_BIRTH", "DAYS_EMPLOYED",
        "CODE_GENDER", "NAME_CONTRACT_TYPE",
        "AMT_GOODS_PRICE", "CNT_FAM_MEMBERS",
        "REGION_RATING_CLIENT", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"
    ]
    df = pd.read_csv(path, usecols=lambda c: c in required_cols)
    print(f"Loaded {len(df):,} borrowers from Home Credit dataset.")
    return df


# ── 2. Clean ──────────────────────────────────────────────────────────────────
def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Convert days to positive years/months
    df["age_years"]         = (-df["DAYS_BIRTH"] / 365).round(1)
    df["employment_years"]  = np.where(
        df["DAYS_EMPLOYED"] > 0, 0, (-df["DAYS_EMPLOYED"] / 365).round(1)
    )

    # Impute external credit scores with median
    for col in ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]:
        df[col] = df[col].fillna(df[col].median())

    # Composite external score (proxy for creditworthiness)
    df["ext_score_avg"] = df[["EXT_SOURCE_1","EXT_SOURCE_2","EXT_SOURCE_3"]].mean(axis=1)

    # Debt-to-income ratio
    df["dti"] = (df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]).round(4)

    # Fill remaining numerics
    df["CNT_FAM_MEMBERS"] = df["CNT_FAM_MEMBERS"].fillna(df["CNT_FAM_MEMBERS"].median())
    df["AMT_GOODS_PRICE"] = df["AMT_GOODS_PRICE"].fillna(df["AMT_GOODS_PRICE"].median())

    return df


# ── 3. Engineer DPD Bucket ────────────────────────────────────────────────────
def assign_dpd_bucket(df: pd.DataFrame) -> pd.DataFrame:
    """
    Home Credit's TARGET = 1 means payment difficulties.
    We simulate a DPD (Days Past Due) bucket using TARGET + risk signals
    to create realistic delinquency segmentation.

    Bucket logic:
      Current (0 DPD)   : TARGET=0, high ext_score
      Early (1-30 DPD)  : TARGET=0, low ext_score OR TARGET=1, high ext_score
      Mid (31-60 DPD)   : TARGET=1, mid ext_score
      Late (61-90 DPD)  : TARGET=1, low ext_score, high DTI
    """
    conditions = [
        (df["TARGET"] == 0) & (df["ext_score_avg"] >= 0.60),
        (df["TARGET"] == 0) & (df["ext_score_avg"] <  0.60),
        (df["TARGET"] == 1) & (df["ext_score_avg"] >= 0.50),
        (df["TARGET"] == 1) & (df["ext_score_avg"] <  0.50) & (df["dti"] <= 0.35),
        (df["TARGET"] == 1) & (df["ext_score_avg"] <  0.50) & (df["dti"] >  0.35),
    ]
    buckets = ["Current", "DPD_1_30", "DPD_1_30", "DPD_31_60", "DPD_61_90"]
    df["dpd_bucket"] = np.select(conditions, buckets, default="DPD_1_30")

    print("\nDPD Bucket Distribution:")
    print(df["dpd_bucket"].value_counts())
    return df


# ── 4. Engineer Behavioral Signals ────────────────────────────────────────────
def engineer_behavioral_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Proxy behavioral signals for channel affinity and contact timing.
    In a real system these come from interaction logs; here we derive
    them deterministically from available borrower attributes.
    """

    # -- Channel affinity proxies --
    # Older borrowers respond better to calls (lower digital comfort)
    # Younger borrowers respond better to SMS/app
    # High-income borrowers respond better to email (business hours)
    df["call_affinity_score"] = (
        0.40 * (df["age_years"] / 70) +
        0.30 * (1 - df["ext_score_avg"]) +
        0.30 * np.clip(df["dti"], 0, 1)
    ).round(4)

    df["sms_affinity_score"] = (
        0.50 * (1 - df["age_years"] / 70) +
        0.30 * df["ext_score_avg"] +
        0.20 * (1 - np.clip(df["dti"], 0, 1))
    ).round(4)

    df["email_affinity_score"] = (
        0.40 * np.clip(df["AMT_INCOME_TOTAL"] / 200000, 0, 1) +
        0.40 * df["ext_score_avg"] +
        0.20 * (df["employment_years"] / 20).clip(0, 1)
    ).round(4)

    # Normalize so scores sum to 1 per borrower
    total = df[["call_affinity_score","sms_affinity_score","email_affinity_score"]].sum(axis=1)
    df["call_affinity_score"]  = (df["call_affinity_score"]  / total).round(4)
    df["sms_affinity_score"]   = (df["sms_affinity_score"]   / total).round(4)
    df["email_affinity_score"] = (df["email_affinity_score"] / total).round(4)

    # Preferred channel = highest affinity
    df["preferred_channel"] = df[
        ["call_affinity_score","sms_affinity_score","email_affinity_score"]
    ].idxmax(axis=1).str.replace("_affinity_score","").str.upper()

    # -- Contact timing proxy --
    # Employed full-time → responsive in evening (after work)
    # Unemployed / self-employed → responsive in morning
    # Region rating 3 (rural) → morning; 1 (urban) → evening
    conditions = [
        (df["employment_years"] > 3) & (df["REGION_RATING_CLIENT"] <= 2),
        (df["employment_years"] <= 3) | (df["REGION_RATING_CLIENT"] == 3),
    ]
    df["optimal_contact_window"] = np.select(
        conditions, ["Evening (6-8 PM)", "Morning (9-11 AM)"], default="Afternoon (2-4 PM)"
    )

    return df


# ── 5. Assign Risk Tier ───────────────────────────────────────────────────────
def assign_risk_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Three-tier risk segmentation used to drive offer logic downstream.
    """
    conditions = [
        df["ext_score_avg"] >= 0.65,
        (df["ext_score_avg"] >= 0.45) & (df["ext_score_avg"] < 0.65),
        df["ext_score_avg"] <  0.45,
    ]
    df["risk_tier"] = np.select(conditions, ["Low", "Medium", "High"], default="Medium")
    return df


# ── 6. Select & Export ────────────────────────────────────────────────────────
FINAL_COLS = [
    "SK_ID_CURR", "TARGET", "AMT_CREDIT", "AMT_ANNUITY", "AMT_INCOME_TOTAL",
    "age_years", "employment_years", "CODE_GENDER", "NAME_CONTRACT_TYPE",
    "ext_score_avg", "dti", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT",
    "dpd_bucket", "risk_tier",
    "call_affinity_score", "sms_affinity_score", "email_affinity_score",
    "preferred_channel", "optimal_contact_window"
]

def run():
    assert os.path.exists(RAW_PATH), (
        f"\nFile not found: {RAW_PATH}\n"
        "Download from: https://www.kaggle.com/competitions/home-credit-default-risk/data\n"
        "Place application_train.csv in data/raw/"
    )

    df = load_raw(RAW_PATH)
    df = clean(df)
    df = assign_dpd_bucket(df)
    df = engineer_behavioral_signals(df)
    df = assign_risk_tier(df)

    df = df[FINAL_COLS]
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"\nBorrower profiles saved to {OUT_PATH}")
    print(f"Shape: {df.shape}")
    print("\nSample:")
    print(df.head(3).T)

if __name__ == "__main__":
    run()
