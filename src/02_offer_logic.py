"""
Module 2: Offer Logic Engine
==============================
Assigns a recovery offer to each borrower based on DPD bucket,
risk tier, and outstanding balance.

This operationalizes the "offer logic" layer referenced in
collections strategy frameworks — turning borrower segmentation
into concrete, actionable recovery offers.

Input:  data/processed/borrower_profiles.csv
Output: data/processed/borrower_with_offers.csv
"""

import pandas as pd
import numpy as np
import os

IN_PATH  = "data/processed/borrower_profiles.csv"
OUT_PATH = "data/processed/borrower_with_offers.csv"

# ── Offer Matrix ──────────────────────────────────────────────────────────────
# Rows = DPD bucket | Cols = Risk tier
# Format: (offer_type, discount_pct, urgency_flag)
OFFER_MATRIX = {
    ("Current",   "Low"):    ("Payment Reminder",        0,    False),
    ("Current",   "Medium"): ("Payment Reminder",        0,    False),
    ("Current",   "High"):   ("Early Intervention",      0,    True),
    ("DPD_1_30",  "Low"):    ("Payment Reminder",        0,    False),
    ("DPD_1_30",  "Medium"): ("Settlement Offer",        5,    False),
    ("DPD_1_30",  "High"):   ("Settlement Offer",        8,    True),
    ("DPD_31_60", "Low"):    ("Settlement Offer",        5,    False),
    ("DPD_31_60", "Medium"): ("Settlement Offer",       10,    True),
    ("DPD_31_60", "High"):   ("Restructuring Proposal",  0,    True),
    ("DPD_61_90", "Low"):    ("Settlement Offer",       12,    True),
    ("DPD_61_90", "Medium"): ("Restructuring Proposal",  0,    True),
    ("DPD_61_90", "High"):   ("Legal Warning + Offer",  15,    True),
}

# Base response rate by offer type (used in simulation)
OFFER_BASE_RESPONSE = {
    "Payment Reminder":       0.45,
    "Early Intervention":     0.55,
    "Settlement Offer":       0.38,
    "Restructuring Proposal": 0.30,
    "Legal Warning + Offer":  0.22,
}

# Expected recovery rate (% of outstanding) if borrower responds
OFFER_RECOVERY_RATE = {
    "Payment Reminder":       1.00,   # full payment
    "Early Intervention":     0.90,
    "Settlement Offer":       0.85,
    "Restructuring Proposal": 0.60,
    "Legal Warning + Offer":  0.50,
}


def assign_offers(df: pd.DataFrame) -> pd.DataFrame:
    def lookup(row):
        key = (row["dpd_bucket"], row["risk_tier"])
        return OFFER_MATRIX.get(key, ("Payment Reminder", 0, False))

    df[["offer_type", "discount_pct", "urgency_flag"]] = df.apply(
        lookup, axis=1, result_type="expand"
    )

    df["base_response_rate"] = df["offer_type"].map(OFFER_BASE_RESPONSE)
    df["recovery_rate_if_responded"] = df["offer_type"].map(OFFER_RECOVERY_RATE)

    # Net recovery amount (after discount)
    df["expected_recovery_amt"] = (
        df["AMT_CREDIT"] *
        df["recovery_rate_if_responded"] *
        (1 - df["discount_pct"] / 100)
    ).round(2)

    return df


def run():
    assert os.path.exists(IN_PATH), f"Run 01_load_and_profile.py first. Missing: {IN_PATH}"

    df = pd.read_csv(IN_PATH)
    df = assign_offers(df)

    print("Offer Distribution:")
    print(df.groupby(["dpd_bucket","offer_type"]).size().reset_index(name="count").to_string(index=False))

    df.to_csv(OUT_PATH, index=False)
    print(f"\nSaved to {OUT_PATH}  |  Shape: {df.shape}")

if __name__ == "__main__":
    run()
