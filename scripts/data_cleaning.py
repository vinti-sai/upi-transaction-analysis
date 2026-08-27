"""
data_cleaning.py
----------------
Loads the raw UPI transactions CSV, performs cleaning & validation,
and saves a processed version ready for EDA and SQL loading.
"""

import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
RAW_PATH      = os.path.join(BASE_DIR, "..", "data", "raw", "upi_transactions.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "data", "processed")
PROCESSED_PATH = os.path.join(PROCESSED_DIR, "upi_transactions_clean.csv")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_data(path: str) -> pd.DataFrame:
    log.info(f"Loading raw data from: {path}")
    df = pd.read_csv(path)
    log.info(f"  Shape: {df.shape}")
    return df


def audit(df: pd.DataFrame, stage: str):
    log.info(f"\n{'='*50}")
    log.info(f"AUDIT → {stage}")
    log.info(f"  Rows        : {len(df):,}")
    log.info(f"  Columns     : {list(df.columns)}")
    log.info(f"  Nulls       :\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    log.info(f"  Duplicates  : {df.duplicated(subset='transaction_id').sum()}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    audit(df, "Before Cleaning")

    # ── 1. Parse datetimes ────────────────────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"]      = pd.to_datetime(df["date"])

    # ── 2. Drop duplicate transaction_ids ─────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset="transaction_id", keep="first")
    log.info(f"  Dropped {before - len(df)} duplicate transactions")

    # ── 3. Validate amount ────────────────────────────────────────────────────
    before = len(df)
    df = df[df["amount_inr"] > 0]
    log.info(f"  Dropped {before - len(df)} rows with amount ≤ 0")

    # ── 4. Standardise string columns ─────────────────────────────────────────
    str_cols = ["payment_app", "bank_name", "state", "category",
                "transaction_type", "status", "device_type"]
    for col in str_cols:
        df[col] = df[col].str.strip().str.title()

    # ── 5. Fill null failure_reason ───────────────────────────────────────────
    df["failure_reason"] = df["failure_reason"].fillna("N/A")

    # ── 6. Add derived features ───────────────────────────────────────────────
    df["is_success"]    = (df["status"] == "Success").astype(int)
    df["is_failed"]     = (df["status"] == "Failed").astype(int)
    df["quarter"]       = df["timestamp"].dt.quarter.map(
                              {1:"Q1", 2:"Q2", 3:"Q3", 4:"Q4"})
    df["week_number"]   = df["timestamp"].dt.isocalendar().week.astype(int)
    df["is_weekend"]    = df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
    df["amount_bucket"] = pd.cut(
        df["amount_inr"],
        bins=[0, 100, 500, 1_000, 5_000, 10_000, np.inf],
        labels=["<₹100", "₹100–500", "₹500–1K", "₹1K–5K", "₹5K–10K", ">₹10K"],
    )

    # ── 7. Sort by timestamp ──────────────────────────────────────────────────
    df = df.sort_values("timestamp").reset_index(drop=True)

    audit(df, "After Cleaning")
    return df


def save(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    log.info(f"\n[OK] Cleaned data saved -> {path}")
    log.info(f"   Final shape: {df.shape}")


if __name__ == "__main__":
    df = load_data(RAW_PATH)
    df = clean(df)
    save(df, PROCESSED_PATH)

    # Quick summary stats
    print("\nQuick Summary")
    print("-" * 40)
    print(f"Total Transactions : {len(df):,}")
    print(f"Total Volume (INR) : Rs.{df['amount_inr'].sum():,.2f}")
    print(f"Avg Transaction    : Rs.{df['amount_inr'].mean():,.2f}")
    print(f"Success Rate       : {df['is_success'].mean() * 100:.1f}%")
    print(f"Failure Rate       : {df['is_failed'].mean() * 100:.1f}%")
    print(f"Date Range         : {df['date'].min().date()} -> {df['date'].max().date()}")
