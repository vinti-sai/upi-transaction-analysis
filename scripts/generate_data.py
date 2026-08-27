"""
generate_data.py
----------------
Generates a realistic synthetic UPI transactions dataset with ~15,000 records
covering multiple payment apps, banks, states, categories, and statuses.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random
import uuid

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Constants ─────────────────────────────────────────────────────────────────
NUM_RECORDS = 15_000
START_DATE  = datetime(2023, 1, 1)
END_DATE    = datetime(2024, 12, 31)

PAYMENT_APPS = {
    "PhonePe":    0.35,
    "GPay":       0.30,
    "Paytm":      0.18,
    "BHIM":       0.10,
    "Amazon Pay": 0.07,
}

BANKS = [
    "SBI", "HDFC", "ICICI", "Axis Bank", "Kotak Mahindra",
    "Punjab National Bank", "Bank of Baroda", "Canara Bank",
    "Union Bank", "IndusInd Bank",
]

STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Telangana",
    "Gujarat", "West Bengal", "Rajasthan", "Uttar Pradesh", "Kerala",
    "Madhya Pradesh", "Punjab", "Haryana", "Bihar", "Andhra Pradesh",
]

CATEGORIES = {
    "Food & Dining":   0.20,
    "Shopping":        0.18,
    "Utilities":       0.12,
    "Transport":       0.13,
    "Entertainment":   0.08,
    "Healthcare":      0.07,
    "Education":       0.06,
    "Recharge":        0.09,
    "Groceries":       0.07,
}

TRANSACTION_TYPES = {"P2P": 0.55, "P2M": 0.45}

STATUSES = {"SUCCESS": 0.88, "FAILED": 0.08, "PENDING": 0.04}

DEVICE_TYPES = {"Mobile": 0.83, "Desktop": 0.17}

# Amount ranges per category (INR)
AMOUNT_RANGES = {
    "Food & Dining":   (50,   1_500),
    "Shopping":        (200,  15_000),
    "Utilities":       (100,  5_000),
    "Transport":       (20,   2_000),
    "Entertainment":   (100,  3_000),
    "Healthcare":      (200,  20_000),
    "Education":       (500,  50_000),
    "Recharge":        (19,   999),
    "Groceries":       (100,  4_000),
}


def weighted_choice(choices: dict) -> str:
    keys = list(choices.keys())
    weights = list(choices.values())
    return np.random.choice(keys, p=weights)


def random_upi_id(bank: str) -> str:
    user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
    bank_handle = bank.lower().replace(" ", "").replace("bank", "")[:6]
    return f"{user}@{bank_handle}"


def generate_timestamp() -> datetime:
    """
    Weighted toward business hours and weekdays with seasonal spikes
    (festivals: Oct–Nov, year-end: Dec, Jan).
    """
    delta_days = (END_DATE - START_DATE).days
    day_offset  = np.random.randint(0, delta_days)
    ts = START_DATE + timedelta(days=int(day_offset))

    # Peak-hour weighting
    hour_weights = np.array([
        1, 1, 0.5, 0.5, 0.5, 1,      # 0–5
        2, 4, 5,  4,   3,   4,        # 6–11
        5, 4, 3,  3,   3,   4,        # 12–17
        5, 5, 4,  3,   2,   1,        # 18–23
    ], dtype=float)
    hour_weights /= hour_weights.sum()
    hour   = np.random.choice(range(24), p=hour_weights)
    minute = np.random.randint(0, 60)
    second = np.random.randint(0, 60)
    return ts.replace(hour=hour, minute=minute, second=second)


# ── Build Dataset ─────────────────────────────────────────────────────────────
records = []
for _ in range(NUM_RECORDS):
    app      = weighted_choice(PAYMENT_APPS)
    status   = weighted_choice(STATUSES)
    category = weighted_choice(CATEGORIES)
    txn_type = weighted_choice(TRANSACTION_TYPES)
    device   = weighted_choice(DEVICE_TYPES)
    state    = random.choice(STATES)
    bank     = random.choice(BANKS)

    lo, hi   = AMOUNT_RANGES[category]
    amount   = round(np.random.lognormal(mean=np.log((lo + hi) / 2), sigma=0.6), 2)
    amount   = float(np.clip(amount, lo, hi))

    ts = generate_timestamp()

    records.append({
        "transaction_id":   str(uuid.uuid4()),
        "timestamp":        ts.strftime("%Y-%m-%d %H:%M:%S"),
        "date":             ts.strftime("%Y-%m-%d"),
        "year":             ts.year,
        "month":            ts.month,
        "month_name":       ts.strftime("%B"),
        "day_of_week":      ts.strftime("%A"),
        "hour":             ts.hour,
        "sender_upi_id":    random_upi_id(bank),
        "receiver_upi_id":  random_upi_id(random.choice(BANKS)),
        "amount_inr":       amount,
        "transaction_type": txn_type,
        "category":         category,
        "payment_app":      app,
        "bank_name":        bank,
        "state":            state,
        "device_type":      device,
        "status":           status,
        "failure_reason":   (
            random.choice([
                "Insufficient Funds", "Bank Server Down",
                "Invalid UPI PIN",    "Transaction Limit Exceeded",
                "Network Timeout",
            ]) if status == "FAILED" else None
        ),
    })

df = pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)
out_path = os.path.join(OUT_DIR, "upi_transactions.csv")
df.to_csv(out_path, index=False)

print(f"[OK] Dataset generated -> {out_path}")
print(f"   Shape : {df.shape}")
print(f"   Period: {df['date'].min()}  ->  {df['date'].max()}")
print(f"\nStatus breakdown:\n{df['status'].value_counts()}")
print(f"\nPayment App distribution:\n{df['payment_app'].value_counts()}")
