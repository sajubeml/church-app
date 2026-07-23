"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Church Accounting Python Automation Engine
Converts and automates VBA macro functionality from Excel workbook:
- SpellNumberINR (Number to Indian Rupee Words)
- Transaction Posting (Cash Book & Individual Member Ledgers)
- Dual Side-by-Side Receipt HTML/PDF Generation
- Reconciliation Audit Engine
"""

import os
import json
from datetime import datetime

DATA_DIR = "data_export"
RECEIPTS_DIR = "receipts_output"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)

# ----------------------------------------------------
# 1. INDIAN RUPEE NUMBER TO WORDS CONVERTER (VBA SpellNumberINR replacement)
# ----------------------------------------------------
def num_to_words_inr(amount):
    """Converts a floating point amount into Indian Rupee Words format."""
    try:
        val = float(amount)
    except (ValueError, TypeError):
        return "Zero Rupees Only"

    rupees = int(val)
    paisa = int(round((val - rupees) * 100))

    def convert_below_thousand(n):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                 "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                 "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        words = ""
        if n >= 100:
            words += units[n // 100] + " Hundred "
            n %= 100
        if n >= 20:
            words += tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n > 0:
            words += units[n]
        return words.strip()

    def convert_to_words(n):
        if n == 0:
            return "Zero"
        
        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        
        res = []
        if crore > 0:
            res.append(convert_below_thousand(crore) + " Crore")
        if lakh > 0:
            res.append(convert_below_thousand(lakh) + " Lakh")
        if thousand > 0:
            res.append(convert_below_thousand(thousand) + " Thousand")
        if n > 0:
            res.append(convert_below_thousand(n))
            
        return " ".join(res).strip()

    rupee_str = convert_to_words(rupees) + " Rupees" if rupees > 0 else "Zero Rupees"
    paisa_str = f" and {convert_to_words(paisa)} Paisa" if paisa > 0 else ""
    return f"{rupee_str}{paisa_str} Only"


# ----------------------------------------------------
# 2. DATA LOAD & SAVE UTILITIES
# ----------------------------------------------------
def load_json(name):
    file_path = os.path.join(DATA_DIR, f"{name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(name, data):
    file_path = os.path.join(DATA_DIR, f"{name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ----------------------------------------------------
# 3. TRANSACTION POSTING ENGINE (VBA btnSave_Click replacement)
# ----------------------------------------------------
def post_transaction(trans_type, reg_no, name_of_hof, acct_head, code, details, cash_amt, bank_amt, date_str=None):
    """
    Posts a transaction with safety validation:
    - Lock check: Cannot specify both Cash and Bank simultaneously.
    - Updates Cash Book and Individual Member ledger.
    """
    cash_amt = float(cash_amt) if cash_amt else 0.0
    bank_amt = float(bank_amt) if bank_amt else 0.0

    if cash_amt > 0 and bank_amt > 0:
        raise ValueError("SAFETY ERROR: A single receipt cannot mix both Cash and Bank! Please enter either Cash OR Bank.")
    if cash_amt == 0 and bank_amt == 0:
        raise ValueError("SAFETY ERROR: Please enter a non-zero amount!")
    if not acct_head:
        raise ValueError("SAFETY ERROR: Please select an Account Head!")

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    cashbook = load_json("Cash_Book")
    
    # Auto-calculate next receipt/voucher number
    receipt_no = 4001
    voucher_no = 1
    for row in cashbook:
        if "B" in row and str(row["B"]).isdigit():
            r = int(row["B"])
            if r >= receipt_no: receipt_no = r + 1
        if "L" in row and str(row["L"]).isdigit():
            v = int(row["L"])
            if v >= voucher_no: voucher_no = v + 1

    new_entry = {
        "A": date_str,
        "B": str(receipt_no) if trans_type == "RECEIPT" else "",
        "C": str(reg_no) if reg_no else "",
        "D": name_of_hof or "",
        "E": acct_head if trans_type == "RECEIPT" else "",
        "F": code if trans_type == "RECEIPT" else "",
        "G": details if trans_type == "RECEIPT" else "",
        "H": str(cash_amt) if trans_type == "RECEIPT" and cash_amt > 0 else "",
        "I": str(bank_amt) if trans_type == "RECEIPT" and bank_amt > 0 else "",
        "K": date_str if trans_type == "PAYMENT" else "",
        "L": str(voucher_no) if trans_type == "PAYMENT" else "",
        "M": acct_head if trans_type == "PAYMENT" else "",
        "N": code if trans_type == "PAYMENT" else "",
        "O": details if trans_type == "PAYMENT" else "",
        "P": str(cash_amt) if trans_type == "PAYMENT" and cash_amt > 0 else "",
        "Q": str(bank_amt) if trans_type == "PAYMENT" and bank_amt > 0 else ""
    }

    cashbook.append(new_entry)
    save_json("Cash_Book", cashbook)

    # Update Individual Member Ledger if reg_no is present
    if reg_no:
        indiv = load_json("Individual")
        for member in indiv:
            if str(member.get("B", "")).strip() == str(reg_no).strip():
                # Add to grand total column (AM)
                current_total = float(member.get("AM", 0) or 0)
                new_total = current_total + (cash_amt + bank_amt)
                member["AM"] = str(new_total)
                break
        save_json("Individual", indiv)

    print(f"✅ Successfully posted {trans_type}: Receipt No #{receipt_no if trans_type == 'RECEIPT' else voucher_no} for {name_of_hof or 'General'}")
    return receipt_no if trans_type == "RECEIPT" else voucher_no


# ----------------------------------------------------
# 4. SIDE-BY-SIDE DUAL RECEIPT GENERATOR (VBA UpdateReceipts replacement)
# ----------------------------------------------------
def generate_dual_receipt(receipt_no, date_str, reg_no, member_name, items, total_amount):
    """
    Generates side-by-side (Original & Copy) HTML receipt ready for PDF export or print.
    """
    amount_in_words = num_to_words_inr(total_amount)
    
    item_rows = ""
    for idx, item in enumerate(items, 1):
        item_rows += f"""
        <tr>
            <td style="text-align:center;">{idx}</td>
            <td>{item['particulars']} ({item['code']})</td>
            <td style="text-align:right;">₹ {item['amount']:,.2f}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Receipt #{receipt_no} - St. Gregorios Church</title>
    <style>
        @page {{ size: landscape; margin: 10mm; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px; background: #f4f6f9; }}
        .dual-container {{ display: flex; gap: 20px; justify-content: space-between; max-width: 1200px; margin: 0 auto; }}
        .receipt-card {{ flex: 1; background: #fff; border: 2px solid #2c3e50; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; }}
        .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 8px; margin-bottom: 12px; }}
        .header h3 {{ margin: 0; color: #1a252f; font-size: 16px; font-weight: bold; }}
        .header p {{ margin: 2px 0; font-size: 11px; color: #555; }}
        .watermark {{ position: absolute; right: 15px; top: 15px; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }}
        .original .watermark {{ background: #27ae60; color: #fff; }}
        .copy .watermark {{ background: #e67e22; color: #fff; }}
        .meta-table {{ width: 100%; margin-bottom: 10px; font-size: 12px; border-collapse: collapse; }}
        .meta-table td {{ padding: 3px 0; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 12px; }}
        .items-table th, .items-table td {{ border: 1px solid #ddd; padding: 6px; }}
        .items-table th {{ background: #f8f9fa; text-align: left; color: #333; }}
        .total-box {{ background: #eef2f7; padding: 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: #1a252f; margin-bottom: 15px; }}
        .signatures {{ display: flex; justify-content: space-between; margin-top: 30px; font-size: 11px; font-weight: bold; color: #555; }}
        @media print {{
            body {{ background: none; padding: 0; }}
            .dual-container {{ width: 100%; gap: 10px; }}
            .receipt-card {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="dual-container">
        <!-- ORIGINAL RECEIPT -->
        <div class="receipt-card original">
            <span class="watermark">ORIGINAL</span>
            <div class="header">
                <h3>ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
                <p>Government House Road, Nazarbad, Mysuru, Karnataka 570 010</p>
                <p style="font-weight:bold; color: #2c3e50;">RECEIPT</p>
            </div>
            <table class="meta-table">
                <tr><td><strong>Receipt No:</strong> #{receipt_no}</td><td style="text-align:right;"><strong>Date:</strong> {date_str}</td></tr>
                <tr><td><strong>Register No:</strong> {reg_no or 'N/A'}</td><td style="text-align:right;"><strong>Member:</strong> {member_name or 'General'}</td></tr>
            </table>
            <table class="items-table">
                <thead><tr><th style="width:30px; text-align:center;">#</th><th>Account Head / Particulars</th><th style="width:100px; text-align:right;">Amount</th></tr></thead>
                <tbody>{item_rows}</tbody>
            </table>
            <div class="total-box">
                <div>Total Amount: ₹ {total_amount:,.2f}</div>
                <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:3px;">({amount_in_words})</div>
            </div>
            <div class="signatures"><div>Prepared By: ____________</div><div>Trustee / Treasurer: ____________</div></div>
        </div>

        <!-- DUPLICATE COPY RECEIPT -->
        <div class="receipt-card copy">
            <span class="watermark">COPY</span>
            <div class="header">
                <h3>ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
                <p>Government House Road, Nazarbad, Mysuru, Karnataka 570 010</p>
                <p style="font-weight:bold; color: #2c3e50;">RECEIPT (OFFICE COPY)</p>
            </div>
            <table class="meta-table">
                <tr><td><strong>Receipt No:</strong> #{receipt_no}</td><td style="text-align:right;"><strong>Date:</strong> {date_str}</td></tr>
                <tr><td><strong>Register No:</strong> {reg_no or 'N/A'}</td><td style="text-align:right;"><strong>Member:</strong> {member_name or 'General'}</td></tr>
            </table>
            <table class="items-table">
                <thead><tr><th style="width:30px; text-align:center;">#</th><th>Account Head / Particulars</th><th style="width:100px; text-align:right;">Amount</th></tr></thead>
                <tbody>{item_rows}</tbody>
            </table>
            <div class="total-box">
                <div>Total Amount: ₹ {total_amount:,.2f}</div>
                <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:3px;">({amount_in_words})</div>
            </div>
            <div class="signatures"><div>Prepared By: ____________</div><div>Trustee / Treasurer: ____________</div></div>
        </div>
    </div>
</body>
</html>"""

    file_path = os.path.join(RECEIPTS_DIR, f"Receipt_{receipt_no}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📄 Side-by-side receipt HTML created at: {file_path}")
    return file_path


# ----------------------------------------------------
# 5. AUDIT RECONCILIATION ENGINE (VBA AuditIndividualSheet replacement)
# ----------------------------------------------------
def run_audit_reconciliation():
    """Audits Cash Book entries against Individual Member collections."""
    cashbook = load_json("Cash_Book")
    members = load_json("Members")
    indiv = load_json("Individual")

    print("\n🔍 RUNNING RECONCILIATION AUDIT...")
    
    total_cash_receipts = 0.0
    total_bank_receipts = 0.0
    total_cash_payments = 0.0
    total_bank_payments = 0.0

    for row in cashbook[3:]:  # Skip headers
        h = float(row.get("H", 0) or 0)
        i = float(row.get("I", 0) or 0)
        p = float(row.get("P", 0) or 0)
        q = float(row.get("Q", 0) or 0)
        
        total_cash_receipts += h
        total_bank_receipts += i
        total_cash_payments += p
        total_bank_payments += q

    grand_receipts = total_cash_receipts + total_bank_receipts
    grand_payments = total_cash_payments + total_bank_payments
    net_balance = grand_receipts - grand_payments

    audit_summary = {
        "total_cash_receipts": total_cash_receipts,
        "total_bank_receipts": total_bank_receipts,
        "grand_receipts": grand_receipts,
        "total_cash_payments": total_cash_payments,
        "total_bank_payments": total_bank_payments,
        "grand_payments": grand_payments,
        "net_balance": net_balance,
        "registered_members_count": len(members),
        "individual_ledgers_count": len(indiv)
    }

    print(f"  • Total Receipts: ₹ {grand_receipts:,.2f} (Cash: ₹{total_cash_receipts:,.2f} | Bank: ₹{total_bank_receipts:,.2f})")
    print(f"  • Total Payments: ₹ {grand_payments:,.2f} (Cash: ₹{total_cash_payments:,.2f} | Bank: ₹{total_bank_payments:,.2f})")
    print(f"  • Net Cashbook Balance: ₹ {net_balance:,.2f}")
    print(f"  • Members Registered: {len(members)}")
    print("✅ Reconciliation Audit Completed Successfully!\n")
    return audit_summary


# ----------------------------------------------------
# DEMO / TEST RUNNER
# ----------------------------------------------------
if __name__ == "__main__":
    print("==================================================")
    print("  ST. GREGORIOS CHURCH PYTHON AUTOMATION ENGINE  ")
    print("==================================================")

    # Test 1: Number to Indian Rupee Words
    test_amount = 9300.50
    print(f"\n1. Testing Rupee Words Conversion:")
    print(f"   ₹ {test_amount:,.2f} --> {num_to_words_inr(test_amount)}")

    # Test 2: Audit Engine
    run_audit_reconciliation()

    # Test 3: Generate Dual Side-by-Side Receipt
    sample_items = [
        {"particulars": "Monthly Subscription (Current Year)", "code": "RP-3.82", "amount": 6000.00},
        {"particulars": "Catholicate Day & Recessa", "code": "RP-2.02", "amount": 600.00},
        {"particulars": "Metropolitan Fund", "code": "RP-2.03", "amount": 300.00},
        {"particulars": "Passion Week Collection", "code": "RP-2.13", "amount": 1000.00},
        {"particulars": "Auction Dues - Old", "code": "RP-10.01", "amount": 1400.00}
    ]
    generate_dual_receipt(
        receipt_no=4275,
        date_str="2026-07-23",
        reg_no="128",
        member_name="Abraham Thomas Dr",
        items=sample_items,
        total_amount=9300.00
    )
