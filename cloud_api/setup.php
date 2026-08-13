<?php
// setup.php - Run this once in your browser to create tables
require 'db_config.php';

$sql = "
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    status VARCHAR(50)
);
";
if ($conn->query($sql) === TRUE) { echo "Table members created successfully<br>"; } else { echo "Error: " . $conn->error . "<br>"; }

$sql = "
CREATE TABLE IF NOT EXISTS cashbook (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    receipt_no VARCHAR(100),
    reg_no VARCHAR(255),
    name_of_hof VARCHAR(255),
    receipt_acct_head VARCHAR(255),
    receipt_code VARCHAR(100),
    receipt_details TEXT,
    receipt_cash DECIMAL(10,2),
    receipt_bank DECIMAL(10,2),
    payment_date DATE,
    payment_voucher_no VARCHAR(100),
    payment_acct_head VARCHAR(255),
    payment_code VARCHAR(100),
    payment_details TEXT,
    payment_cash DECIMAL(10,2),
    payment_bank DECIMAL(10,2)
);
";
if ($conn->query($sql) === TRUE) { echo "Table cashbook created successfully<br>"; } else { echo "Error: " . $conn->error . "<br>"; }

$sql = "
CREATE TABLE IF NOT EXISTS individual_ledgers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    receipt_no VARCHAR(100),
    reg_no VARCHAR(255),
    name_of_hof VARCHAR(255),
    acct_head VARCHAR(255),
    code VARCHAR(100),
    details TEXT,
    cash_amount DECIMAL(10,2),
    bank_amount DECIMAL(10,2)
);
";
if ($conn->query($sql) === TRUE) { echo "Table individual_ledgers created successfully<br>"; } else { echo "Error: " . $conn->error . "<br>"; }

$sql = "
CREATE TABLE IF NOT EXISTS account_heads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(100) UNIQUE,
    title VARCHAR(255),
    category VARCHAR(50)
);
";
if ($conn->query($sql) === TRUE) { echo "Table account_heads created successfully<br>"; } else { echo "Error: " . $conn->error . "<br>"; }

$conn->close();
echo "Setup complete!";
?>
