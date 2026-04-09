"""
Main Pipeline Runner
=====================
Executes all modules in sequence.

Usage:
    python src/main.py

Prerequisites:
    Place application_train.csv in data/raw/
    Download from: https://www.kaggle.com/competitions/home-credit-default-risk/data
"""

import subprocess
import sys
import os

MODULES = [
    ("01_load_and_profile.py", "Loading and profiling borrowers"),
    ("02_offer_logic.py",      "Assigning offers via offer matrix"),
    ("03_ab_test.py",          "Running A/B test simulation"),
    ("04_analytics.py",        "Computing analytics and exporting BI data"),
]

def run():
    print("=" * 60)
    print("  Collections Contact Strategy Engine")
    print("  A/B Test: Model-Driven vs Flat Contact Strategy")
    print("=" * 60)

    for module, description in MODULES:
        print(f"\n{'─'*60}")
        print(f"  STEP: {description}")
        print(f"{'─'*60}")
        result = subprocess.run(
            [sys.executable, os.path.join("src", module)],
            capture_output=False
        )
        if result.returncode != 0:
            print(f"\nERROR in {module}. Stopping pipeline.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print("  Outputs saved to: outputs/")
    print("  Load outputs/tableau_master.csv into Tableau for dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    run()
