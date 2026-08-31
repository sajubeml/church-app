"""
Recalculate individual member ledger totals from cashbook data.
This fixes the discrepancy between the Excel (manually maintained) and the app
(which only updates individual ledger on NEW receipt creation, not on backup restore).
"""
import json
import copy

INPUT_FILE = r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json"
OUTPUT_FILE = r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30_FIXED.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

cashbook = data.get("cashbook", [])
individual = data.get("individual", [])

# Account code -> individual column mapping (matching the app's logic exactly)
def get_col_key(head, code):
    head = (head or "").lower().strip()
    code = (code or "").upper().strip()
    
    if "subscription" in head or code in ("RP-3.82", "RP-3.83"):
        return "E"
    if "donation general" in head or code in ("RP-2.02", "RP-2.02(A)"):
        return "F"
    if "catholicate day" in head or code == "RP-19.03&.04":
        return "G"
    if "metropolitan fund" in head or code == "RP-19.11":
        return "H"
    if "mission sunday" in head or code == "RP-19.21":
        return "I"
    if "seminary day" in head or code == "RP-19.23":
        return "J"
    if "priest welfare" in head or code == "RP-19.15":
        return "K"
    if "old cover collection" in head or code == "RP-10.17":
        return "L"
    if "wedding anniversary" in head or code == "RP-3.17":
        return "M"
    if "birthday offering" in head or code == "RP-3.16":
        return "N"
    if "baptism" in head or code == "RP-3.14":
        return "O"
    if "orma qurbana" in head or "holy qurbana" in head or code == "RP-3.12":
        return "P"
    if "sunday school day collection" in head or code == "RP-19.22":
        return "Q"
    if "st.gregorios feast" in head or code == "RP-3.33":
        return "R"
    if "parish day" in head or code == "RP-2.12":
        return "S"
    if "christmas" in head or "new year" in head or code == "RP-3.11":
        return "T"
    if "perunnal vanchika" in head or "house offertory box" in head or code == "RP-3.05":
        return "U"
    if "passion week" in head or code == "RP-2.13":
        return "V"
    if "st. george feast" in head or code == "RP-16.50":
        return "W"
    if "st. thomas feast" in head or code == "RP-3.31":
        return "X"
    if "st. mary's feast" in head or "st. mary" in head or code == "RP-3.32":
        return "Y"
    if "marriage bann" in head or code == "RP-3.15(A)":
        return "Z"
    if "marriage celebration" in head or code == "RP-3.15(B)":
        return "AA"
    if "donations-marriage" in head or code == "RP-3.15(C)":
        return "AB"
    if "marriage kaimuthu" in head or code == "RP-3.15(D)":
        return "AC"
    if "donation - cemetry" in head or "donation cemetry" in head or code == "RP-3.08":
        return "AD"
    if "house blessing" in head or code == "RP-3.17(A)":
        return "AE"
    if "petty auction" in head or code == "RP-2.15(B)":
        return "AF"
    if "auction current" in head or code == "RP-2.14":
        return "AG"
    if "auction dues" in head or code == "RP-2.15(A)":
        return "AH"
    if "cemetry receipt" in head or code == "RP-3.09":
        return "AI"
    if "certificate fee" in head or code == "RP-3.21":
        return "AJ"
    if "donation-breakfast" in head or "donation breakfast" in head or code == "RP-2.16":
        return "AK"
    if "miscellaneous income" in head or code == "RP-3.22":
        return "AL"
    
    return "E"  # Default fallback

# Data columns that hold amounts (E through AL)
amount_cols = ["E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
               "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", 
               "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"]

# Step 1: Build a member registry from individual ledger (reg -> row index)
member_index = {}
for i, row in enumerate(individual):
    if i < 4: continue
    c = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c.upper(): continue
    reg = str(row.get("B", "")).strip()
    if reg:
        member_index[reg] = i

print(f"Found {len(member_index)} members in individual ledger")

# Step 2: Zero out all amount columns for all members (we'll recalculate from cashbook)
for reg, idx in member_index.items():
    for col in amount_cols:
        individual[idx][col] = 0

# Step 3: Process each cashbook receipt entry and accumulate into individual ledger
receipts_processed = 0
receipts_skipped = 0
unmapped_heads = {}

for row in cashbook:
    dt = str(row.get("A", "")).strip()
    recNo = str(row.get("B", "")).strip()
    reg = str(row.get("C", "")).strip()
    hof = str(row.get("D", "")).strip()
    head = str(row.get("E", "")).strip()
    code = str(row.get("F", "")).strip()
    cashR = float(row.get("H", 0) or 0)
    bankR = float(row.get("I", 0) or 0)
    
    total_amt = cashR + bankR
    if total_amt <= 0: continue
    if not reg: continue
    
    # Skip header rows
    dtLower = dt.lower()
    recLower = recNo.lower()
    headLower = head.lower()
    if ("cash book" in dtLower or "receipts" in dtLower or dtLower == "date" or
        recLower.startswith("receipt") or headLower == "accounts head"):
        continue
    
    # Skip opening balance
    details = str(row.get("G", "")).strip().lower()
    if "opening balance" in details or cashR == 9879 or bankR == 651682:
        continue
    
    # Find column
    col_key = get_col_key(head, code)
    
    # Find member
    if reg in member_index:
        idx = member_index[reg]
        current = float(individual[idx].get(col_key, 0) or 0)
        individual[idx][col_key] = current + total_amt
        receipts_processed += 1
    else:
        receipts_skipped += 1

# Step 4: Recalculate AM (GRAND TOTAL) for each member
for reg, idx in member_index.items():
    grand = 0
    for col in amount_cols:
        grand += float(individual[idx].get(col, 0) or 0)
    individual[idx]["AM"] = round(grand, 2)

# Step 5: Update GRAND TOTAL row
for i, row in enumerate(individual):
    c = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c.upper():
        for col in amount_cols + ["AM"]:
            total = 0
            for reg, idx in member_index.items():
                total += float(individual[idx].get(col, 0) or 0)
            individual[i][col] = round(total, 2)
        break

# Step 6: Save fixed backup
data["individual"] = individual
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nReceipts processed: {receipts_processed}")
print(f"Receipts skipped (no reg match): {receipts_skipped}")

# Print new totals
print("\n=== RECALCULATED INDIVIDUAL TOTALS ===")
grand_total = 0
for col in amount_cols:
    total = 0
    for reg, idx in member_index.items():
        total += float(individual[idx].get(col, 0) or 0)
    if total > 0:
        print(f"  Col {col}: {total:,.0f}")
    grand_total += total
print(f"\nNEW GRAND TOTAL: {grand_total:,.0f}")
print(f"\nFixed backup saved to: {OUTPUT_FILE}")
