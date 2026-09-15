-- SQLite Database Schema for St. Gregorios Church Accounting
-- Replaces JSON files from data_export

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no TEXT UNIQUE,
    name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    status TEXT
);

CREATE TABLE IF NOT EXISTS cashbook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    receipt_no TEXT,
    reg_no TEXT,
    name_of_hof TEXT,
    receipt_acct_head TEXT,
    receipt_code TEXT,
    receipt_details TEXT,
    receipt_cash REAL,
    receipt_bank REAL,
    payment_date TEXT,
    payment_voucher_no TEXT,
    payment_acct_head TEXT,
    payment_code TEXT,
    payment_details TEXT,
    payment_cash REAL,
    payment_bank REAL
);

CREATE TABLE IF NOT EXISTS individual_ledgers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    receipt_no TEXT,
    reg_no TEXT,
    name_of_hof TEXT,
    acct_head TEXT,
    code TEXT,
    details TEXT,
    cash_amount REAL,
    bank_amount REAL
);

CREATE TABLE IF NOT EXISTS account_heads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    title TEXT,
    category TEXT -- 'RECEIPT' or 'PAYMENT'
);
