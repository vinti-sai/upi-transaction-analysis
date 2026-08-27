-- ============================================================
-- create_tables.sql
-- Schema for loading UPI transactions into a relational DB
-- Compatible with: SQLite, PostgreSQL, MySQL
-- ============================================================

-- Drop if exists
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS dim_payment_app;
DROP TABLE IF EXISTS dim_bank;
DROP TABLE IF EXISTS dim_state;
DROP TABLE IF EXISTS dim_category;

-- ── Dimension: Payment Apps ───────────────────────────────────
CREATE TABLE dim_payment_app (
    app_id   INTEGER PRIMARY KEY,
    app_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO dim_payment_app (app_id, app_name) VALUES
    (1, 'PhonePe'),
    (2, 'GPay'),
    (3, 'Paytm'),
    (4, 'BHIM'),
    (5, 'Amazon Pay');

-- ── Dimension: Banks ──────────────────────────────────────────
CREATE TABLE dim_bank (
    bank_id   INTEGER PRIMARY KEY,
    bank_name VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO dim_bank (bank_id, bank_name) VALUES
    (1,  'SBI'),
    (2,  'HDFC'),
    (3,  'ICICI'),
    (4,  'Axis Bank'),
    (5,  'Kotak Mahindra'),
    (6,  'Punjab National Bank'),
    (7,  'Bank Of Baroda'),
    (8,  'Canara Bank'),
    (9,  'Union Bank'),
    (10, 'Indusind Bank');

-- ── Dimension: States ─────────────────────────────────────────
CREATE TABLE dim_state (
    state_id   INTEGER PRIMARY KEY,
    state_name VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO dim_state (state_id, state_name) VALUES
    (1,  'Maharashtra'),
    (2,  'Karnataka'),
    (3,  'Tamil Nadu'),
    (4,  'Delhi'),
    (5,  'Telangana'),
    (6,  'Gujarat'),
    (7,  'West Bengal'),
    (8,  'Rajasthan'),
    (9,  'Uttar Pradesh'),
    (10, 'Kerala'),
    (11, 'Madhya Pradesh'),
    (12, 'Punjab'),
    (13, 'Haryana'),
    (14, 'Bihar'),
    (15, 'Andhra Pradesh');

-- ── Dimension: Categories ─────────────────────────────────────
CREATE TABLE dim_category (
    category_id   INTEGER PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO dim_category (category_id, category_name) VALUES
    (1, 'Food & Dining'),
    (2, 'Shopping'),
    (3, 'Utilities'),
    (4, 'Transport'),
    (5, 'Entertainment'),
    (6, 'Healthcare'),
    (7, 'Education'),
    (8, 'Recharge'),
    (9, 'Groceries');

-- ── Fact: Transactions ────────────────────────────────────────
CREATE TABLE transactions (
    transaction_id   VARCHAR(36)    PRIMARY KEY,
    timestamp        DATETIME       NOT NULL,
    date             DATE           NOT NULL,
    year             INTEGER        NOT NULL,
    month            INTEGER        NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name       VARCHAR(15)    NOT NULL,
    day_of_week      VARCHAR(15)    NOT NULL,
    hour             INTEGER        NOT NULL CHECK (hour BETWEEN 0 AND 23),
    quarter          VARCHAR(2)     NOT NULL,
    week_number      INTEGER        NOT NULL,
    is_weekend       INTEGER        NOT NULL DEFAULT 0,
    sender_upi_id    VARCHAR(100)   NOT NULL,
    receiver_upi_id  VARCHAR(100)   NOT NULL,
    amount_inr       DECIMAL(12, 2) NOT NULL CHECK (amount_inr > 0),
    amount_bucket    VARCHAR(20),
    transaction_type VARCHAR(10)    NOT NULL CHECK (transaction_type IN ('P2P', 'P2M')),
    category         VARCHAR(100)   NOT NULL,
    payment_app      VARCHAR(50)    NOT NULL,
    bank_name        VARCHAR(100)   NOT NULL,
    state            VARCHAR(100)   NOT NULL,
    device_type      VARCHAR(20)    NOT NULL,
    status           VARCHAR(20)    NOT NULL CHECK (status IN ('Success','Failed','Pending')),
    is_success       INTEGER        NOT NULL DEFAULT 0,
    is_failed        INTEGER        NOT NULL DEFAULT 0,
    failure_reason   VARCHAR(100)   DEFAULT 'N/A'
);

-- ── Indexes for query performance ─────────────────────────────
CREATE INDEX idx_txn_date        ON transactions (date);
CREATE INDEX idx_txn_status      ON transactions (status);
CREATE INDEX idx_txn_app         ON transactions (payment_app);
CREATE INDEX idx_txn_state       ON transactions (state);
CREATE INDEX idx_txn_category    ON transactions (category);
CREATE INDEX idx_txn_bank        ON transactions (bank_name);
CREATE INDEX idx_txn_type        ON transactions (transaction_type);
