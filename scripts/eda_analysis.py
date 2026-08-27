"""
eda_analysis.py
---------------
Performs full Exploratory Data Analysis on the cleaned UPI transactions dataset.
Generates publication-quality charts saved to reports/figures/.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":        150,
    "figure.facecolor":  "#0f172a",
    "axes.facecolor":    "#1e293b",
    "axes.edgecolor":    "#334155",
    "axes.labelcolor":   "#e2e8f0",
    "axes.titlecolor":   "#f1f5f9",
    "xtick.color":       "#94a3b8",
    "ytick.color":       "#94a3b8",
    "text.color":        "#e2e8f0",
    "grid.color":        "#334155",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "legend.facecolor":  "#1e293b",
    "legend.edgecolor":  "#334155",
    "font.family":       "DejaVu Sans",
})

PALETTE   = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#f43f5e",
             "#a78bfa", "#fb923c", "#34d399", "#818cf8", "#38bdf8"]
HIGHLIGHT = "#6366f1"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, "..", "data", "processed", "upi_transactions_clean.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "..", "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def save_fig(name: str):
    path = os.path.join(FIGURES_DIR, name)
    plt.savefig(path, bbox_inches="tight", facecolor=plt.rcParams["figure.facecolor"])
    plt.close()
    print(f"  Saved -> {name}")


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data…")
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp", "date"])
print(f"  {len(df):,} records loaded\n")


# ══════════════════════════════════════════════════════════════════════════════
# 1. TRANSACTION VOLUME OVER TIME (monthly)
# ══════════════════════════════════════════════════════════════════════════════
print("1. Monthly transaction volume…")
monthly = (df.groupby(df["timestamp"].dt.to_period("M"))
             .agg(count=("transaction_id", "count"),
                  volume=("amount_inr", "sum"))
             .reset_index())
monthly["period_str"] = monthly["timestamp"].dt.strftime("%b %Y")

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig.suptitle("UPI Transaction Volume & Payment Value — Monthly Trend",
             fontsize=14, fontweight="bold", y=1.01)

axes[0].bar(range(len(monthly)), monthly["count"], color=HIGHLIGHT, alpha=0.85)
axes[0].set_ylabel("No. of Transactions")
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{int(x):,}"))

axes[1].fill_between(range(len(monthly)), monthly["volume"], color="#22d3ee", alpha=0.6)
axes[1].plot(range(len(monthly)), monthly["volume"], color="#22d3ee", linewidth=2)
axes[1].set_ylabel("Total Volume (INR)")
axes[1].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"Rs.{x/1e6:.1f}M"))
axes[1].set_xticks(range(len(monthly)))
axes[1].set_xticklabels(monthly["period_str"], rotation=45, ha="right", fontsize=7)

for ax in axes:
    ax.grid(axis="y")

fig.tight_layout()
save_fig("01_monthly_volume.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. SUCCESS vs FAILURE vs PENDING (overall)
# ══════════════════════════════════════════════════════════════════════════════
print("2. Transaction status breakdown…")
status_counts = df["status"].value_counts()
colors = {"Success": "#10b981", "Failed": "#f43f5e", "Pending": "#f59e0b"}
clr = [colors.get(s, HIGHLIGHT) for s in status_counts.index]

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    status_counts, labels=None, autopct="%1.1f%%",
    colors=clr, startangle=90,
    wedgeprops={"linewidth": 2, "edgecolor": "#0f172a"},
    pctdistance=0.75,
)
for at in autotexts:
    at.set(fontsize=12, fontweight="bold", color="white")
ax.legend(wedges, [f"{k}  ({v:,})" for k, v in status_counts.items()],
          loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08))
ax.set_title("Transaction Status Distribution", fontsize=13, fontweight="bold")
save_fig("02_status_pie.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. SUCCESS RATE BY PAYMENT APP
# ══════════════════════════════════════════════════════════════════════════════
print("3. Success rate by payment app…")
app_stats = (df.groupby("payment_app")
               .agg(total=("transaction_id","count"),
                    success=("is_success","sum"))
               .assign(success_rate=lambda d: d["success"]/d["total"]*100)
               .sort_values("success_rate", ascending=True))

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(app_stats.index, app_stats["success_rate"],
               color=PALETTE[:len(app_stats)], edgecolor="#0f172a", height=0.5)
for bar, val in zip(bars, app_stats["success_rate"]):
    ax.text(val - 1.5, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=10, fontweight="bold", color="white")
ax.set_xlabel("Success Rate (%)")
ax.set_title("Success Rate by Payment App", fontsize=13, fontweight="bold")
ax.set_xlim(80, 100)
ax.grid(axis="x")
save_fig("03_success_rate_by_app.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. CATEGORY SPEND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("4. Category spend…")
cat_stats = (df[df["status"] == "Success"]
               .groupby("category")
               .agg(txn_count=("transaction_id","count"),
                    total_spend=("amount_inr","sum"),
                    avg_spend=("amount_inr","mean"))
               .sort_values("total_spend", ascending=False))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Spending Analysis by Category", fontsize=13, fontweight="bold")

axes[0].barh(cat_stats.index, cat_stats["total_spend"]/1e6,
             color=PALETTE[:len(cat_stats)], edgecolor="#0f172a", height=0.6)
axes[0].set_xlabel("Total Spend (INR Millions)")
axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"Rs.{x:.1f}M"))
axes[0].set_title("Total Spend")
axes[0].grid(axis="x")

axes[1].barh(cat_stats.index, cat_stats["avg_spend"],
             color=PALETTE[:len(cat_stats)], edgecolor="#0f172a", height=0.6)
axes[1].set_xlabel("Average Transaction (INR)")
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"Rs.{int(x):,}"))
axes[1].set_title("Avg Transaction Value")
axes[1].grid(axis="x")

fig.tight_layout()
save_fig("04_category_spend.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. HOURLY TRANSACTION HEATMAP (Day × Hour)
# ══════════════════════════════════════════════════════════════════════════════
print("5. Hourly heatmap…")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heatmap_data = (df.groupby(["day_of_week","hour"])
                  .size()
                  .unstack(fill_value=0)
                  .reindex(day_order))

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(heatmap_data, cmap="YlOrRd", ax=ax,
            linewidths=0.4, linecolor="#0f172a",
            cbar_kws={"label": "Transaction Count"})
ax.set_title("Peak Usage Heatmap — Day of Week × Hour of Day",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("")
save_fig("05_peak_usage_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. TOP 10 STATES BY TRANSACTION VOLUME
# ══════════════════════════════════════════════════════════════════════════════
print("6. State-wise volume…")
state_stats = (df.groupby("state")
                 .agg(count=("transaction_id","count"),
                      volume=("amount_inr","sum"))
                 .sort_values("count", ascending=False)
                 .head(10))

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(state_stats.index, state_stats["count"],
              color=PALETTE[:10], edgecolor="#0f172a")
for bar, val in zip(bars, state_stats["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f"{val:,}", ha="center", fontsize=8, color="#e2e8f0")
ax.set_title("Top 10 States by Transaction Count", fontsize=13, fontweight="bold")
ax.set_ylabel("No. of Transactions")
ax.set_xticklabels(state_stats.index, rotation=30, ha="right")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(axis="y")
save_fig("06_top_states.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. FAILURE REASON BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
print("7. Failure reasons…")
failure_df = df[df["status"] == "Failed"]
fail_reasons = failure_df["failure_reason"].value_counts()

fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(fail_reasons.index, fail_reasons.values,
        color="#f43f5e", alpha=0.85, edgecolor="#0f172a", height=0.5)
for i, val in enumerate(fail_reasons.values):
    ax.text(val + 5, i, f"{val:,}", va="center", fontsize=9)
ax.set_title("Failed Transaction — Reason Breakdown", fontsize=13, fontweight="bold")
ax.set_xlabel("Count")
ax.grid(axis="x")
save_fig("07_failure_reasons.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. AMOUNT DISTRIBUTION (log scale)
# ══════════════════════════════════════════════════════════════════════════════
print("8. Amount distribution…")
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle("Transaction Amount Distribution", fontsize=13, fontweight="bold")

success_amounts = df[df["status"] == "Success"]["amount_inr"]
axes[0].hist(success_amounts, bins=50, color=HIGHLIGHT, edgecolor="#0f172a", alpha=0.85)
axes[0].set_xlabel("Amount (INR)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Histogram (Normal Scale)")
axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"Rs.{int(x):,}"))
axes[0].grid(axis="y")

axes[1].hist(np.log1p(success_amounts), bins=50, color="#22d3ee", edgecolor="#0f172a", alpha=0.85)
axes[1].set_xlabel("log(Amount + 1)")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Histogram (Log Scale)")
axes[1].grid(axis="y")

fig.tight_layout()
save_fig("08_amount_distribution.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. P2P vs P2M by APP
# ══════════════════════════════════════════════════════════════════════════════
print("9. P2P vs P2M by app…")
type_app = (df.groupby(["payment_app","transaction_type"])
              .size()
              .unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(9, 5))
type_app.plot(kind="bar", ax=ax, color=["#6366f1","#22d3ee"],
              edgecolor="#0f172a", width=0.6)
ax.set_title("P2P vs P2M Transactions by Payment App", fontsize=13, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("No. of Transactions")
ax.set_xticklabels(type_app.index, rotation=30, ha="right")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.legend(title="Type")
ax.grid(axis="y")
save_fig("09_p2p_vs_p2m.png")


# ══════════════════════════════════════════════════════════════════════════════
# 10. KPI DASHBOARD SUMMARY (text card style)
# ══════════════════════════════════════════════════════════════════════════════
print("10. KPI summary dashboard…")
total_txn    = len(df)
success_df   = df[df["status"] == "Success"]
total_vol    = success_df["amount_inr"].sum()
success_rate = len(success_df) / total_txn * 100
fail_rate    = df["is_failed"].mean() * 100
avg_txn      = success_df["amount_inr"].mean()
top_app      = df["payment_app"].value_counts().idxmax()
top_cat      = df["category"].value_counts().idxmax()
top_state    = df["state"].value_counts().idxmax()

kpis = [
    ("Total Transactions",    f"{total_txn:,}",          "#6366f1"),
    ("Total Volume",          f"₹{total_vol/1e6:.2f}M",  "#22d3ee"),
    ("Success Rate",          f"{success_rate:.1f}%",    "#10b981"),
    ("Failure Rate",          f"{fail_rate:.1f}%",       "#f43f5e"),
    ("Avg Transaction Value", f"₹{avg_txn:,.0f}",        "#f59e0b"),
    ("Top Payment App",       top_app,                   "#a78bfa"),
    ("Top Category",          top_cat,                   "#fb923c"),
    ("Top State",             top_state,                 "#34d399"),
]

fig, axes = plt.subplots(2, 4, figsize=(16, 6))
fig.suptitle("UPI Transactions — KPI Dashboard", fontsize=16, fontweight="bold", y=1.02)
axes_flat = axes.flatten()

for ax, (label, value, color) in zip(axes_flat, kpis):
    ax.set_facecolor(color + "22")
    ax.text(0.5, 0.60, value, ha="center", va="center",
            fontsize=20, fontweight="bold", color=color,
            transform=ax.transAxes)
    ax.text(0.5, 0.25, label, ha="center", va="center",
            fontsize=9, color="#94a3b8",
            transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax.set_xticks([])
    ax.set_yticks([])

fig.tight_layout()
save_fig("10_kpi_dashboard.png")

print("\n[OK] All charts saved to reports/figures/")
