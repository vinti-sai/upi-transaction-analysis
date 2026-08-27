# -*- coding: utf-8 -*-
"""
run_pipeline.py
---------------
Master pipeline script - runs all steps end-to-end:
  1. Generate synthetic dataset
  2. Clean & validate data
  3. Run EDA and save charts
  4. Build KPI dashboard & export Excel

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("[1/4] Generating synthetic UPI dataset",      "scripts/generate_data.py"),
    ("[2/4] Cleaning & validating data",            "scripts/data_cleaning.py"),
    ("[3/4] Running EDA (charts saved to reports/)","scripts/eda_analysis.py"),
    ("[4/4] Building KPI Dashboard & Excel export", "scripts/kpi_dashboard.py"),
]


def run_step(label: str, script: str):
    print(f"\n" + "-"*60)
    print(f"  {label}")
    print("-"*60)
    path = os.path.join(BASE, script)
    t0 = time.time()
    result = subprocess.run([sys.executable, path], capture_output=False, text=True)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\nFAILED: {script}")
        sys.exit(1)
    print(f"  Done in {elapsed:.1f}s")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  UPI TRANSACTIONS ANALYSIS - FULL PIPELINE")
    print("="*60)
    total_start = time.time()

    for label, script in STEPS:
        run_step(label, script)

    total = time.time() - total_start
    print("\n" + "="*60)
    print(f"  Pipeline complete in {total:.1f}s")
    print(f"  Outputs:")
    print(f"     data/raw/upi_transactions.csv")
    print(f"     data/processed/upi_transactions_clean.csv")
    print(f"     data/processed/upi_transactions.db")
    print(f"     reports/figures/  (10 charts)")
    print(f"     reports/kpi_report.xlsx")
    print("="*60)
