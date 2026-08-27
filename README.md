# UPI Transactions Data Analysis 💳📊

> **Python · SQL · Excel · Power BI**  
> An end-to-end data analysis project on a large synthetic UPI payments dataset, extracting trends in payment volume, success rates, user behaviour, and seasonal patterns.

---

## 🗂 Project Structure

```
upi-transactions-analysis/
├── data/
│   ├── raw/                    # Raw generated CSV (git-ignored)
│   └── processed/              # Cleaned CSV + SQLite DB (git-ignored)
├── scripts/
│   ├── generate_data.py        # Synthetic dataset generator (15 K records)
│   ├── data_cleaning.py        # Data cleaning & feature engineering
│   ├── eda_analysis.py         # EDA with 10 publication-quality charts
│   └── kpi_dashboard.py        # SQL KPI runner → Excel export
├── sql/
│   ├── create_tables.sql       # Schema (fact + dimension tables)
│   └── kpi_queries.sql         # 20+ KPI queries across 7 sections
├── reports/
│   ├── figures/                # Auto-generated PNG charts (git-ignored)
│   └── kpi_report.xlsx         # Auto-generated Excel report (git-ignored)
├── run_pipeline.py             # 🚀 One-command pipeline runner
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/upi-transactions-analysis.git
cd upi-transactions-analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the full pipeline
```bash
python run_pipeline.py
```

This single command will:
- ✅ Generate 15,000 synthetic UPI transaction records
- ✅ Clean and validate the dataset
- ✅ Run EDA and save 10 charts to `reports/figures/`
- ✅ Build the KPI dashboard and export to `reports/kpi_report.xlsx`

---

## 📊 Key KPIs Tracked

| KPI | Description |
|-----|-------------|
| **Transaction Volume** | Monthly and quarterly count of transactions |
| **Payment Value** | Total and average transaction amount (INR) |
| **Success Rate** | % of transactions completed successfully |
| **Failure Rate** | % of failed transactions + root-cause breakdown |
| **App Market Share** | PhonePe vs GPay vs Paytm vs BHIM vs Amazon Pay |
| **Peak Usage Periods** | Hour-of-day and day-of-week heatmaps |
| **Category Spend** | Spend distribution across 9 categories |
| **State-wise Analysis** | Geographic transaction and volume distribution |
| **Device Adoption** | Mobile vs Desktop usage patterns |
| **MoM Growth** | Month-over-month transaction growth per app |

---

## 📈 Charts Generated

| # | Chart | Insight |
|---|-------|---------|
| 1 | Monthly Transaction Volume | Trend and seasonality over 2 years |
| 2 | Status Pie Chart | Success / Failed / Pending breakdown |
| 3 | Success Rate by App | App reliability comparison |
| 4 | Category Spend Analysis | Total & average spend per category |
| 5 | Peak Usage Heatmap | Day × Hour transaction density |
| 6 | Top 10 States | State-wise transaction leaders |
| 7 | Failure Reason Breakdown | Why transactions fail |
| 8 | Amount Distribution | Normal and log-scale histograms |
| 9 | P2P vs P2M by App | Transaction type mix per app |
| 10 | KPI Dashboard | 8-card summary dashboard |

---

## 🗄️ SQL Highlights

The `sql/kpi_queries.sql` file contains **20+ queries** across 7 analysis sections:

1. **Overall KPIs** — aggregate success/failure rates
2. **Payment App Performance** — market share, MoM growth
3. **Temporal Analysis** — monthly, quarterly, hourly, weekly patterns
4. **Category & Spend** — top categories, P2P vs P2M breakdown
5. **Geographic Analysis** — state × app cross-analysis
6. **Failure Analysis** — root cause, high-value failures, bank-level rates
7. **Device & User Behaviour** — mobile vs desktop, amount buckets

---

## 📦 Dataset Description

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | UUID | Unique identifier |
| `timestamp` | DateTime | Transaction date & time |
| `amount_inr` | Float | Transaction amount in INR |
| `payment_app` | String | PhonePe / GPay / Paytm / BHIM / Amazon Pay |
| `bank_name` | String | Sender's bank |
| `state` | String | Geographic state (15 states) |
| `category` | String | Spending category (9 categories) |
| `transaction_type` | String | P2P (peer-to-peer) or P2M (peer-to-merchant) |
| `status` | String | Success / Failed / Pending |
| `failure_reason` | String | Reason for failure (if any) |
| `device_type` | String | Mobile or Desktop |
| `is_weekend` | Integer | 1 if weekend, 0 if weekday |
| `quarter` | String | Q1 / Q2 / Q3 / Q4 |

---

## 🔧 Power BI Integration

1. Run the pipeline to generate `reports/kpi_report.xlsx`
2. Open **Power BI Desktop**
3. **Get Data → Excel Workbook** → select `kpi_report.xlsx`
4. Each sheet maps to a separate table (Monthly Volume, App Performance, etc.)
5. Build visuals using the pre-aggregated KPI data

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Data generation, cleaning, EDA, visualization |
| **Pandas / NumPy** | Data manipulation and analysis |
| **Matplotlib / Seaborn** | Chart generation |
| **SQLite** | Embedded SQL database for KPI queries |
| **SQL** | KPI aggregation, window functions, cross-analysis |
| **openpyxl** | Excel report generation |
| **Power BI** | Interactive dashboard consumption |

---

## 📌 Key Findings

- **PhonePe** leads with ~35% market share, followed by GPay (~30%)
- **Success rate** across all apps exceeds **88%**
- **Peak transaction hours**: 12 PM – 8 PM, with highest activity on weekdays
- **Shopping** and **Food & Dining** are the top spending categories
- **Insufficient Funds** is the leading cause of transaction failures (~30%)
- **Maharashtra, Karnataka, and Tamil Nadu** are the top 3 states by transaction volume
- Significant **seasonal spikes** in October–November (festive season) and December

---
