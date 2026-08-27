-- ============================================================
-- kpi_queries.sql
-- Key Performance Indicator queries for UPI transaction data
-- ============================================================


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 1 — OVERALL KPIs                               ║
-- ╚══════════════════════════════════════════════════════════╝

-- 1.1 Total transactions, volume, and overall success rate
SELECT
    COUNT(*)                                               AS total_transactions,
    ROUND(SUM(amount_inr), 2)                              AS total_volume_inr,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount_inr ELSE 0 END), 2)
                                                           AS successful_volume_inr,
    ROUND(AVG(amount_inr), 2)                              AS avg_transaction_value,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)          AS success_rate_pct,
    ROUND(SUM(is_failed)  * 100.0 / COUNT(*), 2)          AS failure_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
                                                           AS pending_rate_pct
FROM transactions;


-- 1.2 KPI breakdown by year
SELECT
    year,
    COUNT(*)                                          AS total_transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                  AS total_volume_millions,
    ROUND(AVG(amount_inr), 2)                         AS avg_value,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)     AS success_rate_pct,
    ROUND(SUM(is_failed)  * 100.0 / COUNT(*), 2)     AS failure_rate_pct
FROM transactions
GROUP BY year
ORDER BY year;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 2 — PAYMENT APP PERFORMANCE                    ║
-- ╚══════════════════════════════════════════════════════════╝

-- 2.1 Transactions, volume and success rate per app
SELECT
    payment_app,
    COUNT(*)                                               AS total_transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                       AS total_volume_millions,
    ROUND(AVG(amount_inr), 2)                              AS avg_transaction_value,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)          AS success_rate_pct,
    ROUND(SUM(is_failed)  * 100.0 / COUNT(*), 2)          AS failure_rate_pct,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)    AS market_share_pct
FROM transactions
GROUP BY payment_app
ORDER BY total_transactions DESC;


-- 2.2 Month-over-month growth by app (Year 2024)
SELECT
    payment_app,
    month_name,
    month,
    COUNT(*)                                         AS transactions,
    LAG(COUNT(*)) OVER (PARTITION BY payment_app ORDER BY month)
                                                     AS prev_month_txns,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY payment_app ORDER BY month))
        * 100.0
        / NULLIF(LAG(COUNT(*)) OVER (PARTITION BY payment_app ORDER BY month), 0),
    2)                                               AS mom_growth_pct
FROM transactions
WHERE year = 2024
GROUP BY payment_app, month, month_name
ORDER BY payment_app, month;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 3 — TEMPORAL ANALYSIS                          ║
-- ╚══════════════════════════════════════════════════════════╝

-- 3.1 Monthly transaction summary
SELECT
    year,
    month,
    month_name,
    quarter,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct,
    ROUND(AVG(amount_inr), 2)                             AS avg_value
FROM transactions
GROUP BY year, month, month_name, quarter
ORDER BY year, month;


-- 3.2 Peak hours analysis
SELECT
    hour,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct
FROM transactions
GROUP BY hour
ORDER BY transactions DESC
LIMIT 10;


-- 3.3 Day-of-week patterns
SELECT
    day_of_week,
    is_weekend,
    COUNT(*)                                              AS transactions,
    ROUND(AVG(amount_inr), 2)                             AS avg_amount,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct
FROM transactions
GROUP BY day_of_week, is_weekend
ORDER BY transactions DESC;


-- 3.4 Quarterly performance comparison
SELECT
    year,
    quarter,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct
FROM transactions
GROUP BY year, quarter
ORDER BY year, quarter;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 4 — CATEGORY & SPEND ANALYSIS                  ║
-- ╚══════════════════════════════════════════════════════════╝

-- 4.1 Category-level spend for successful transactions
SELECT
    category,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS total_spend_millions,
    ROUND(AVG(amount_inr), 2)                             AS avg_spend,
    ROUND(MAX(amount_inr), 2)                             AS max_transaction,
    ROUND(MIN(amount_inr), 2)                             AS min_transaction,
    ROUND(SUM(amount_inr) * 100.0 / SUM(SUM(amount_inr)) OVER (), 2)
                                                          AS spend_share_pct
FROM transactions
WHERE status = 'Success'
GROUP BY category
ORDER BY total_spend_millions DESC;


-- 4.2 P2P vs P2M breakdown per category
SELECT
    category,
    transaction_type,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(AVG(amount_inr), 2)                             AS avg_value
FROM transactions
GROUP BY category, transaction_type
ORDER BY category, transaction_type;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 5 — GEOGRAPHIC ANALYSIS                        ║
-- ╚══════════════════════════════════════════════════════════╝

-- 5.1 State-level KPIs
SELECT
    state,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(AVG(amount_inr), 2)                             AS avg_value,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct,
    ROUND(SUM(is_failed)  * 100.0 / COUNT(*), 2)         AS failure_rate_pct
FROM transactions
GROUP BY state
ORDER BY volume_millions DESC;


-- 5.2 State × App cross-analysis (market penetration)
SELECT
    state,
    payment_app,
    COUNT(*)                                              AS transactions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY state), 2)
                                                          AS app_share_in_state_pct
FROM transactions
GROUP BY state, payment_app
ORDER BY state, transactions DESC;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 6 — FAILURE ANALYSIS                           ║
-- ╚══════════════════════════════════════════════════════════╝

-- 6.1 Failure reason breakdown
SELECT
    failure_reason,
    COUNT(*)                                              AS occurrences,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)   AS share_pct
FROM transactions
WHERE status = 'Failed'
GROUP BY failure_reason
ORDER BY occurrences DESC;


-- 6.2 Failure rate by bank
SELECT
    bank_name,
    COUNT(*)                                              AS total_transactions,
    SUM(is_failed)                                        AS failures,
    ROUND(SUM(is_failed) * 100.0 / COUNT(*), 2)          AS failure_rate_pct
FROM transactions
GROUP BY bank_name
ORDER BY failure_rate_pct DESC;


-- 6.3 High-value failed transactions (amount > ₹5,000)
SELECT
    transaction_id,
    timestamp,
    sender_upi_id,
    receiver_upi_id,
    amount_inr,
    payment_app,
    bank_name,
    failure_reason
FROM transactions
WHERE status = 'Failed'
  AND amount_inr > 5000
ORDER BY amount_inr DESC
LIMIT 20;


-- ╔══════════════════════════════════════════════════════════╗
-- ║  SECTION 7 — DEVICE & USER BEHAVIOUR                    ║
-- ╚══════════════════════════════════════════════════════════╝

-- 7.1 Device type usage and performance
SELECT
    device_type,
    COUNT(*)                                              AS transactions,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions,
    ROUND(AVG(amount_inr), 2)                             AS avg_value,
    ROUND(SUM(is_success) * 100.0 / COUNT(*), 2)         AS success_rate_pct
FROM transactions
GROUP BY device_type
ORDER BY transactions DESC;


-- 7.2 Amount bucket distribution
SELECT
    amount_bucket,
    COUNT(*)                                              AS transactions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)   AS share_pct,
    ROUND(SUM(amount_inr) / 1e6, 2)                      AS volume_millions
FROM transactions
GROUP BY amount_bucket
ORDER BY transactions DESC;
