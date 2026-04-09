"""
Smoke test — generates a small synthetic application_train.csv
to verify the full pipeline runs before the real Kaggle data arrives.

Usage:
    python src/smoke_test.py
"""

import pandas as pd
import numpy as np
import os, subprocess, sys

SEED = 42
np.random.seed(SEED)
N = 5000

def generate_synthetic():
    os.makedirs("data/raw", exist_ok=True)
    df = pd.DataFrame({
        "SK_ID_CURR":           range(1, N+1),
        "TARGET":               np.random.choice([0,1], N, p=[0.92, 0.08]),
        "AMT_CREDIT":           np.random.uniform(50000, 1500000, N).round(2),
        "AMT_ANNUITY":          np.random.uniform(5000, 80000, N).round(2),
        "AMT_INCOME_TOTAL":     np.random.uniform(40000, 500000, N).round(2),
        "DAYS_BIRTH":           np.random.randint(-25000, -6000, N),
        "DAYS_EMPLOYED":        np.random.randint(-15000, 365, N),
        "CODE_GENDER":          np.random.choice(["M","F"], N),
        "NAME_CONTRACT_TYPE":   np.random.choice(["Cash loans","Revolving loans"], N),
        "AMT_GOODS_PRICE":      np.random.uniform(40000, 1400000, N).round(2),
        "CNT_FAM_MEMBERS":      np.random.randint(1, 7, N).astype(float),
        "REGION_RATING_CLIENT": np.random.choice([1,2,3], N),
        "EXT_SOURCE_1":         np.random.uniform(0.1, 0.9, N).round(4),
        "EXT_SOURCE_2":         np.random.uniform(0.1, 0.9, N).round(4),
        "EXT_SOURCE_3":         np.random.uniform(0.1, 0.9, N).round(4),
    })
    df.to_csv("data/raw/application_train.csv", index=False)
    print(f"Synthetic dataset written: {N} rows → data/raw/application_train.csv")

if __name__ == "__main__":
    print("── Smoke Test ──────────────────────────────────────────────")
    generate_synthetic()
    modules = [
        "src/01_load_and_profile.py",
        "src/02_offer_logic.py",
        "src/03_ab_test.py",
        "src/04_analytics.py",
    ]
    for m in modules:
        print(f"\nRunning {m}...")
        r = subprocess.run([sys.executable, m])
        if r.returncode != 0:
            print(f"FAILED at {m}")
            sys.exit(1)
    print("\n── Smoke test passed. All modules ran successfully. ────────")
