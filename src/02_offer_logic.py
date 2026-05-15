"""
Module 2: Offer Logic Engine
==============================
Assigns a recovery offer to each borrower based on DPD bucket,
risk tier, and outstanding balance.

This operationalizes the "offer logic" layer referenced in
collections strategy frameworks - turning borrower segmentation
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


def channel_examples(row: pd.Series) -> pd.Series:
    if row["risk_tier"] == "High" or row["dpd_bucket"] in {"DPD_31_60", "DPD_61_90"}:
        whatsapp_action = (
            "Send empathetic escalation note with repayment link, settlement option, "
            "and callback path to a collections specialist."
        )
        sms_action = "Urgent: your account needs attention. Review repayment options or request a callback today."
        message_timing = "Morning follow-up plus same-day evening reminder"
    elif row["offer_type"] == "Settlement Offer":
        whatsapp_action = "Send settlement explanation with amount, expiry date, and self-serve payment link."
        sms_action = "Limited settlement option available. Check your repayment link before it expires."
        message_timing = row["optimal_contact_window"]
    else:
        whatsapp_action = "Send friendly reminder with due amount, payment link, and support contact."
        sms_action = "Reminder: payment is due. Use your secure repayment link or contact support."
        message_timing = row["optimal_contact_window"]

    primary_channel = "WHATSAPP" if row["urgency_flag"] else row["preferred_channel"]
    if primary_channel == "SMS":
        primary_channel_action = sms_action
    elif primary_channel == "WHATSAPP":
        primary_channel_action = whatsapp_action
    else:
        primary_channel_action = f"Use {primary_channel} with the same offer context."

    return pd.Series(
        {
            "primary_message_channel": primary_channel,
            "message_timing": message_timing,
            "whatsapp_action": whatsapp_action,
            "sms_action": sms_action,
            "primary_channel_action": primary_channel_action,
        }
    )


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

    df[[
        "primary_message_channel",
        "message_timing",
        "whatsapp_action",
        "sms_action",
        "primary_channel_action",
    ]] = df.apply(channel_examples, axis=1)

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
