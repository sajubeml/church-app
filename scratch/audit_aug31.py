"""
Audit the difference between Excel individual ledger totals and web app totals
from the Aug 31 backup. READ-ONLY analysis, no code changes.
"""
import json

INPUT_FILE = r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

cashbook = data.get("cashbook", [])
individual = data.get("individual", [])

# Amount columns
amount_cols = ["E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
               "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", 
               "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"]

# ---- STEP 1: Current individual ledger totals (what the web shows) ----
print("=" * 90)
print("STEP 1: CURRENT INDIVIDUAL LEDGER TOTALS (from backup JSON)")
print("=" * 90)

web_totals = {}
member_count = 0
for i, row in enumerate(individual):
    if i < 4: continue
    c = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c.upper(): continue
    member_count += 1
    for col in amount_cols + ["AM"]:
        val = float(str(row.get(col, "0")).replace(",", "") or "0")
        web_totals[col] = web_totals.get(col, 0) + val

print(f"Members: {member_count}")
for col in amount_cols:
    if web_totals.get(col, 0) > 0:
        print(f"  Col {col}: {web_totals[col]:>12,.0f}")
print(f"  GRAND TOTAL (AM): {web_totals.get('AM', 0):>12,.0f}")

# ---- STEP 2: Recalculate from cashbook ----
print("\n" + "=" * 90)
print("STEP 2: RECALCULATED FROM CASHBOOK")
print("=" * 90)

def get_col_key(head, code):
    head = (head or "").lower().strip()
    code = (code or "").upper().strip()
    if "subscription" in head or code in ("RP-3.82", "RP-3.83"): return "E"
    if "donation general" in head or code in ("RP-2.02", "RP-2.02(A)"): return "F"
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
    if "st. mary's feast" in head or "st. mary" in head or code == "RP-3.32": return "Y"
    if "marriage bann" in head or code == "RP-3.15(A)": return "Z"
    if "marriage celebration" in head or code == "RP-3.15(B)": return "AA"
    if "donations-marriage" in head or code == "RP-3.15(C)": return "AB"
    if "marriage kaimuthu" in head or code == "RP-3.15(D)": return "AC"
    if "donation - cemetry" in head or "donation cemetry" in head or code == "RP-3.08": return "AD"
    if "house blessing" in head or code == "RP-3.17(A)": return "AE"
    if "petty auction" in head or code == "RP-2.15(B)": return "AF"
    if "auction current" in head or code == "RP-2.14": return "AG"
    if "auction dues" in head or code == "RP-2.15(A)": return "AH"
    if "cemetry receipt" in head or code == "RP-3.09": return "AI"
    if "certificate fee" in head or code == "RP-3.21": return "AJ"
    if "donation-breakfast" in head or "donation breakfast" in head or code == "RP-2.16": return "AK"
    if "miscellaneous income" in head or code == "RP-3.22": return "AL"
    return "E"

# Build member index
member_index = {}
for i, row in enumerate(individual):
    if i < 4: continue
    c = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c.upper(): continue
    reg = str(row.get("B", "")).strip()
    if reg: member_index[reg] = i

# Recalculate
recalc = {col: 0 for col in amount_cols}
for row in cashbook:
    dt = str(row.get("A", "")).strip().lower()
    recNo = str(row.get("B", "")).strip().lower()
    reg = str(row.get("C", "")).strip()
    head = str(row.get("E", "")).strip()
    code = str(row.get("F", "")).strip()
    headLower = head.lower()
    cashR = float(row.get("H", 0) or 0)
    bankR = float(row.get("I", 0) or 0)
    total_amt = cashR + bankR
    if total_amt <= 0: continue
    if not reg: continue
    if "cash book" in dt or "receipts" in dt or dt == "date" or recNo.startswith("receipt") or headLower == "accounts head":
        continue
    details = str(row.get("G", "")).strip().lower()
    if "opening balance" in details or cashR == 9879 or bankR == 651682:
        continue
    col_key = get_col_key(head, code)
    if reg in member_index:
        recalc[col_key] += total_amt

recalc_total = sum(recalc.values())
for col in amount_cols:
    if recalc[col] > 0:
        print(f"  Col {col}: {recalc[col]:>12,.0f}")
print(f"  RECALC TOTAL: {recalc_total:>12,.0f}")

# ---- STEP 3: Compare ----
# Excel totals from screenshot (reading the GRAND TOTAL row)
# Updated for Aug 31 Excel screenshot
excel_totals = {
    "E": 195700, "F": 255720, "G": 34250, "H": 15250, "I": 19150,
    "J": 7050, "K": 7900, "L": 8100, "M": 8500, "N": 21350,
    "O": 2500, "P": 3520, "Q": 5250, "U": 3400, "V": 78000,
    "W": 15000, "X": 600, "Y": 56400, "AE": 1500, "AF": 1500,
    "AH": 92500, "AK": 133800,
}
excel_grand = sum(excel_totals.values())

print("\n" + "=" * 90)
print("STEP 3: COMPARISON - Excel vs Web (current) vs Recalculated")
print("=" * 90)
print(f"{'Col':<6} {'Excel':>12} {'Web Now':>12} {'Recalc':>12} {'Exc-Web':>10} {'Exc-Rec':>10}")
print("-" * 74)

all_cols = sorted(set(list(excel_totals.keys()) + [c for c in amount_cols if web_totals.get(c, 0) > 0 or recalc.get(c, 0) > 0]),
                  key=lambda x: (len(x), x))

for col in all_cols:
    e = excel_totals.get(col, 0)
    w = web_totals.get(col, 0)
    r = recalc.get(col, 0)
    d1 = e - w
    d2 = e - r
    flag = ""
    if d1 != 0: flag += " [Web!=Excel]"
    if d2 != 0 and abs(d2) > 100: flag += " [Recalc!=Excel]"
    print(f"  {col:<4} {e:>12,.0f} {w:>12,.0f} {r:>12,.0f} {d1:>+10,.0f} {d2:>+10,.0f}{flag}")

w_total = sum(web_totals.get(c, 0) for c in amount_cols)
print("-" * 74)
print(f"  {'TOT':<4} {excel_grand:>12,} {w_total:>12,.0f} {recalc_total:>12,.0f} {excel_grand-w_total:>+10,.0f} {excel_grand-recalc_total:>+10,.0f}")

print(f"\nExcel GRAND TOTAL:       {excel_grand:>10,}")
print(f"Web GRAND TOTAL:         {w_total:>10,.0f}")
print(f"Recalculated TOTAL:      {recalc_total:>10,.0f}")
print(f"Excel - Web gap:         {excel_grand - w_total:>+10,.0f}")
print(f"Excel - Recalc gap:      {excel_grand - recalc_total:>+10,.0f}")

# ---- STEP 4: Identify specific member-level gaps for top mismatched columns ----
print("\n" + "=" * 90)
print("STEP 4: TOP MISMATCHED COLUMNS - Member-level detail")
print("=" * 90)

# For each mismatched column, show members where cashbook has data but individual doesn't
for col in all_cols:
    e = excel_totals.get(col, 0)
    w = web_totals.get(col, 0)
    diff = e - w
    if abs(diff) < 500: continue
    
    print(f"\n--- Col {col}: Excel={e:,.0f}, Web={w:,.0f}, Diff={diff:+,.0f} ---")
    
    # Find members with cashbook receipts for this column but missing/less in individual
    member_cb = {}
    for row in cashbook:
        reg = str(row.get("C", "")).strip()
        head = str(row.get("E", "")).strip()
        code = str(row.get("F", "")).strip()
        cashR = float(row.get("H", 0) or 0)
        bankR = float(row.get("I", 0) or 0)
        total_amt = cashR + bankR
        if total_amt <= 0 or not reg: continue
        dt = str(row.get("A", "")).strip().lower()
        recNo = str(row.get("B", "")).strip().lower()
        headLower = head.lower()
        if "cash book" in dt or "receipts" in dt or dt == "date" or recNo.startswith("receipt") or headLower == "accounts head":
            continue
        details = str(row.get("G", "")).strip().lower()
        if "opening balance" in details: continue
        
        ck = get_col_key(head, code)
        if ck == col:
            member_cb[reg] = member_cb.get(reg, 0) + total_amt
    
    missing_count = 0
    for reg, cb_total in sorted(member_cb.items(), key=lambda x: -x[1]):
        if reg not in member_index: continue
        idx = member_index[reg]
        indiv_val = float(str(individual[idx].get(col, "0")).replace(",", "") or "0")
        gap = cb_total - indiv_val
        if abs(gap) > 0.01:
            name = str(individual[idx].get("C", "")).strip()
            print(f"  Reg#{reg} {name}: CB={cb_total:,.0f}, Indiv={indiv_val:,.0f}, Gap={gap:+,.0f}")
            missing_count += 1
    if missing_count == 0:
        print("  (No member-level gaps found)")
