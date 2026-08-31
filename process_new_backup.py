import json
import re

def parse_currency(val):
    if not val: return 0.0
    val_str = str(val).replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

def normalize_code(c):
    if not c: return ""
    c = str(c).strip()
    c = re.sub(r'(?i)^RP[-\s]*', 'RP-', c)
    c = re.sub(r'\s+', '', c)
    return c.upper()

def format_currency(val):
    if val == 0: return ""
    return str(int(val)) if val.is_integer() else str(val)

def main():
    input_file = r'C:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (4).json'
    output_file = r'C:\Users\sajub\Downloads\St_Gregorios_Church_Backup_Fixed.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cashbook = data.get("cashbook", [])
    
    # 1. ADD OPENING BALANCE
    has_ob = any("OPENING BALANCE" in str(r.get("E", "")).upper() for r in cashbook)
    if not has_ob:
        cashbook.insert(0, {
            "A": "01-04-2026",
            "B": "",
            "C": "Opening Balance",
            "E": "OPENING BALANCE",
            "F": "",
            "G": "1657803",
            "J": "2000"
        })
        print("Added Opening Balance without Receipt Number.")
    else:
        # Check if receipt number is empty, if not, empty it
        for r in cashbook:
            if "OPENING BALANCE" in str(r.get("E", "")).upper():
                if r.get("B"):
                    r["B"] = ""
                    print("Removed Receipt Number from Opening Balance.")

    data["cashbook"] = cashbook
    
    # 2. RECALCULATE INDIVIDUAL LEDGERS
    current_indiv = data.get("individual", [])
    new_indiv = current_indiv[:4]
    
    income_cols = []
    header_row = new_indiv[3]
    for key, val in header_row.items():
        if key in ["A", "B", "C", "D", "AM"]: continue
        title = str(val).strip()
        if title and title.lower() != "grand total":
            income_cols.append({"key": key, "title": title})
            
    def find_col_key(head_title, code_ref):
        head = str(head_title).strip().lower()
        code = normalize_code(code_ref)
        for col in income_cols:
            if head and head == col["title"].lower(): return col["key"]
        
        if "subscription ( current year)" in head or code == "RP-3.82": return "E"
        if "donation general" in head or code == "RP-2.02" or code == "RP-2.02(A)": return "F"
        if "catholicate day" in head or code == "RP-19.03&.04": return "G"
        if "metropolitan fund" in head or code == "RP-19.11": return "H"
        if "mission sunday" in head or code == "RP-19.21": return "I"
        if "seminary day" in head or code == "RP-19.23": return "J"
        if "priest welfare" in head or code == "RP-19.15": return "K"
        if "old cover collection" in head or code == "RP-10.17": return "L"
        if "wedding anniversary" in head or code == "RP-3.17": return "M"
        if "birthday offering" in head or code == "RP-3.16": return "N"
        if "baptism" in head or code == "RP-3.14": return "O"
        if "orma qurbana" in head or "holy qurbana" in head or code == "RP-3.12": return "P"
        if "sunday school day collection" in head or code == "RP-19.22": return "Q"
        if "st.gregorios feast" in head or code == "RP-3.33": return "R"
        if "parish day" in head or code == "RP-2.12": return "S"
        if "christmas" in head or "new year" in head or code == "RP-3.11": return "T"
        if "perunnal vanchika" in head or "house offertory box" in head or code == "RP-3.05": return "U"
        if "passion week" in head or code == "RP-2.13": return "V"
        if "st. george feast" in head or code == "RP-16.50": return "W"
        if "st. thomas feast" in head or code == "RP-3.31": return "X"
        if "st. mary's feast" in head or code == "RP-3.32": return "Y"
        if "marriage bann" in head or code == "RP-3.15(A)": return "Z"
        if "marriage celebration" in head or code == "RP-3.15(B)": return "AA"
        if "donations-marriage" in head or code == "RP-3.15(C)": return "AB"
        if "marriage kaimuthu" in head or code == "RP-3.15(D)": return "AC"
        if "donation - cemetry" in head or code == "RP-3.08": return "AD"
        if "house blessing" in head or code == "RP-3.17(A)": return "AE"
        if "petty auction" in head or code == "RP-2.15(B)": return "AF"
        if "auction current" in head or code == "RP-2.14": return "AG"
        if "auction dues - old" in head or code == "RP-2.15(A)": return "AH"
        if "cemetry receipt" in head or code == "RP-3.09": return "AI"
        if "certificate fee" in head or code == "RP-3.21": return "AJ"
        if "donation-breakfast" in head or code == "RP-2.16": return "AK"
        if "miscellaneous income" in head or code == "RP-3.22": return "AL"
        if "monthly subscription ( pervious year)" in head or code == "RP-3.83": return "E" 
        
        return "E"

    member_rows = {}
    for row in current_indiv[4:]:
        reg_no = str(row.get("B", "")).strip()
        if not reg_no or "GRAND TOTAL" in str(row.get("C", "")).upper(): continue
        new_row = {"A": row.get("A", ""), "B": reg_no, "C": row.get("C", ""), "D": row.get("D", "")}
        member_rows[reg_no] = new_row
        new_indiv.append(new_row)
        
    for row in cashbook:
        head = row.get("E", "")
        code = row.get("F", "")
        reg_no = str(row.get("C", "")).strip()
        cash = parse_currency(row.get("H", 0))
        bank = parse_currency(row.get("I", 0))
        total = cash + bank
        
        # Fix typo
        if code == "RP- 16.47":
            code = "RP-3.32"
            row["F"] = "RP-3.32"
        elif code == "RP-16.47":
            code = "RP-3.32"
            row["F"] = "RP-3.32"

        is_receipt = bool(row.get("F", "") or row.get("E", "") or row.get("H", "") or row.get("I", ""))
        if "cash deposit" in head.lower() or "bank withdrawal" in head.lower() or code.upper() in ["RP-17.02", "RP-13.01", "RP-17.01", "RP-13.01"]:
            is_receipt = False
            
        if is_receipt and total > 0 and reg_no and reg_no in member_rows:
            col_key = find_col_key(head, code)
            mem_row = member_rows[reg_no]
            mem_row[col_key] = mem_row.get(col_key, 0.0) + total

    overall_grand_total = 0
    for row in new_indiv[4:]:
        reg_no = str(row.get("B", "")).strip()
        if not reg_no or reg_no == "NM": continue
        
        grand_total = 0
        for col in income_cols:
            val = row.get(col["key"], 0.0)
            if val > 0:
                grand_total += val
                row[col["key"]] = format_currency(val)
            else:
                row.pop(col["key"], None)
        
        if grand_total > 0:
            row["AM"] = format_currency(grand_total)
            overall_grand_total += grand_total
            
    filtered_indiv = []
    for row in new_indiv:
        c_val = str(row.get("C", "")).strip().upper()
        if "GRAND TOTAL" in c_val: continue
        filtered_indiv.append(row)
        
    gt_row = {"C": "GRAND TOTAL"}
    col_totals = {}
    for row in filtered_indiv[4:]:
        for col in income_cols:
            val = parse_currency(row.get(col["key"], 0))
            col_totals[col["key"]] = col_totals.get(col["key"], 0) + val
            
    for col in income_cols:
        if col_totals[col["key"]] > 0:
            gt_row[col["key"]] = format_currency(col_totals[col["key"]])
            
    gt_row["AM"] = format_currency(overall_grand_total)
    filtered_indiv.append(gt_row)
    data["individual"] = filtered_indiv

    # 3. FIX TRIAL BALANCE
    trial_balance = data.get("trial_balance", [])
    if len(trial_balance) >= 2:
        new_tb = trial_balance[:2]
        
        # Collect unique heads
        tb_dict = {}
        for row in trial_balance[2:]:
            head = row.get("A", "").strip()
            if not head or "Total" in head: continue
            tb_dict[head] = {"receipts": 0.0, "payments": 0.0}
            
        for row in cashbook:
            head = str(row.get("E", "")).strip()
            code = str(row.get("F", "")).strip()
            details = str(row.get("G", "")).strip()
            r_cash = parse_currency(row.get("H", 0))
            r_bank = parse_currency(row.get("I", 0))
            p_head = str(row.get("L", "")).strip()
            p_details = str(row.get("N", "")).strip()
            p_cash = parse_currency(row.get("O", 0))
            p_bank = parse_currency(row.get("P", 0))
            
            is_receipt = bool(code or head or r_cash > 0 or r_bank > 0)
            is_payment = bool(p_head or p_cash > 0 or p_bank > 0)
            
            if is_receipt:
                if head not in tb_dict: tb_dict[head] = {"receipts": 0.0, "payments": 0.0}
                tb_dict[head]["receipts"] += (r_cash + r_bank)
            if is_payment:
                if p_head not in tb_dict: tb_dict[p_head] = {"receipts": 0.0, "payments": 0.0}
                tb_dict[p_head]["payments"] += (p_cash + p_bank)
                
        # Rebuild TB
        for head, vals in tb_dict.items():
            if vals["receipts"] > 0 or vals["payments"] > 0:
                new_tb.append({
                    "A": head,
                    "B": "", # Opening balance
                    "C": format_currency(vals["receipts"]) if vals["receipts"] > 0 else "",
                    "D": format_currency(vals["payments"]) if vals["payments"] > 0 else "",
                    "E": ""  # Closing balance
                })
        
        data["trial_balance"] = new_tb

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully processed {input_file} and saved to {output_file}")

if __name__ == "__main__":
    main()
