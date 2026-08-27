"""
kpi_dashboard.py
----------------
Runs all KPI queries against the SQLite database and prints a formatted
console report. Also exports results to Excel for Power BI consumption.
"""

import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "..", "data", "processed", "upi_transactions.db")
CSV_PATH   = os.path.join(BASE_DIR, "..", "data", "processed", "upi_transactions_clean.csv")
EXCEL_PATH = os.path.join(BASE_DIR, "..", "reports", "kpi_report.xlsx")
os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)


def init_db(conn: sqlite3.Connection):
    """Load cleaned CSV into SQLite."""
    log.info("Loading CSV → SQLite…")
    df = pd.read_csv(CSV_PATH)
    df.to_sql("transactions", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app    ON transactions(payment_app)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_state  ON transactions(state)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date   ON transactions(date)")
    conn.commit()
    log.info(f"  {len(df):,} rows loaded into SQLite")


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


# ── KPI Queries ───────────────────────────────────────────────────────────────
QUERIES = {
    "Overall KPIs": """
        SELECT
            COUNT(*)                                            AS total_transactions,
            ROUND(SUM(amount_inr), 2)                          AS total_volume_inr,
            ROUND(AVG(amount_inr), 2)                          AS avg_transaction_value,
            ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)      AS success_rate_pct,
            ROUND(SUM(is_failed)  * 100.0 / COUNT(*), 2)      AS failure_rate_pct,
            ROUND(SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END)
                  * 100.0 / COUNT(*), 2)                       AS pending_rate_pct
        FROM transactions
    """,

    "Monthly Volume": """
        SELECT year, month, month_name, quarter,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct
        FROM transactions
        GROUP BY year, month, month_name, quarter
        ORDER BY year, month
    """,

    "Payment App Performance": """
        SELECT payment_app,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(AVG(amount_inr), 2) AS avg_value,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct,
               ROUND(SUM(is_failed)*100.0/COUNT(*), 2) AS failure_rate_pct
        FROM transactions
        GROUP BY payment_app
        ORDER BY transactions DESC
    """,

    "Category Spend": """
        SELECT category,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS total_spend_millions,
               ROUND(AVG(amount_inr), 2) AS avg_spend
        FROM transactions
        WHERE status = 'Success'
        GROUP BY category
        ORDER BY total_spend_millions DESC
    """,

    "State Performance": """
        SELECT state,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct
        FROM transactions
        GROUP BY state
        ORDER BY volume_millions DESC
    """,

    "Failure Analysis": """
        SELECT failure_reason,
               COUNT(*) AS occurrences,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM transactions WHERE status='Failed'), 2)
                   AS share_pct
        FROM transactions
        WHERE status = 'Failed'
        GROUP BY failure_reason
        ORDER BY occurrences DESC
    """,

    "Hourly Peak Usage": """
        SELECT hour,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct
        FROM transactions
        GROUP BY hour
        ORDER BY hour
    """,

    "Device Type Stats": """
        SELECT device_type,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(AVG(amount_inr), 2) AS avg_value,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct
        FROM transactions
        GROUP BY device_type
    """,

    "Bank Failure Rates": """
        SELECT bank_name,
               COUNT(*) AS total,
               SUM(is_failed) AS failures,
               ROUND(SUM(is_failed)*100.0/COUNT(*), 2) AS failure_rate_pct
        FROM transactions
        GROUP BY bank_name
        ORDER BY failure_rate_pct DESC
    """,

    "P2P vs P2M": """
        SELECT transaction_type,
               COUNT(*) AS transactions,
               ROUND(SUM(amount_inr)/1e6, 2) AS volume_millions,
               ROUND(AVG(amount_inr), 2) AS avg_value,
               ROUND(SUM(is_success)*100.0/COUNT(*), 2) AS success_rate_pct
        FROM transactions
        GROUP BY transaction_type
    """,
}


def print_banner(title: str):
    print(f"\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def run_dashboard():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    results = {}
    for name, sql in QUERIES.items():
        df = run_query(conn, sql)
        results[name] = df

    conn.close()

    # ── Console Output ─────────────────────────────────────────
    for name, df in results.items():
        print_banner(name)
        print(df.to_string(index=False))

    # ── Export to Excel ────────────────────────────────────────
    log.info(f"\nExporting KPI report to Excel → {EXCEL_PATH}")
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        for name, df in results.items():
            sheet = name[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=sheet, index=False)

    log.info(f"\n[OK] KPI report exported -> {EXCEL_PATH}")
    print(f"\n[OK] KPI report exported -> {EXCEL_PATH}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Sheets   : {len(results)}")


if __name__ == "__main__":
    run_dashboard()
