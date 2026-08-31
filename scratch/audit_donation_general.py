import json

with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json", "r", encoding="utf-8") as f:
    data = json.load(f)

cashbook = data.get("cashbook", [])
individual = data.get("individual", [])

# Account head code mapping - find what codes map to what columns
# Let's check the header rows of individual to find the code-to-column mapping
print("=== INDIVIDUAL HEADER ROWS ===")
for i in range(min(4, len(individual))):
    row = individual[i]
    print(f"Row {i}: {json.dumps(row, indent=None)[:200]}")

print("\n\n=== CASHBOOK: DONATION GENERAL ENTRIES ===")
# The biggest mismatch is Donation General (Col F in individual = 61,400 vs Excel 255,720)
# Let's find all cashbook entries with "Donation" head and see their reg numbers
dg_entries = []
for i, row in enumerate(cashbook):
    head = str(row.get("E", "")).strip()
    code = str(row.get("F", "")).strip()
    if "Donation" in head and "General" in head:
        reg = str(row.get("C", "")).strip()
        hof = str(row.get("D", "")).strip()
        cashR = float(row.get("H", 0) or 0)
        bankR = float(row.get("I", 0) or 0)
        total = cashR + bankR
        dg_entries.append({
            "reg": reg, "hof": hof, "cash": cashR, "bank": bankR, "total": total, "code": code
        })
        print(f"  Reg#{reg} {hof}: Cash={cashR}, Bank={bankR}, Total={total}, Code={code}")

dg_total_cashbook = sum(e["total"] for e in dg_entries)
print(f"\nTotal Donation General in Cashbook: {dg_total_cashbook}")

# Now check what's in individual Col F (Donation General)
print("\n\n=== INDIVIDUAL: COL F (DONATION GENERAL) ===")
dg_total_individual = 0
for i, row in enumerate(individual):
    if i < 4: continue
    c_val = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c_val.upper(): continue
    f_val = str(row.get("F", "")).strip()
    if f_val:
        try:
            val = float(f_val.replace(",", ""))
            if val > 0:
                reg = str(row.get("B", "")).strip()
                print(f"  Reg#{reg} {c_val}: F={val}")
                dg_total_individual += val
        except:
            pass

print(f"\nTotal Donation General in Individual ledger: {dg_total_individual}")
print(f"Difference (Cashbook - Individual): {dg_total_cashbook - dg_total_individual}")

# Now let's check: for each Donation General cashbook entry, does the individual ledger
# have a corresponding amount in Col F?
print("\n\n=== CROSS-REFERENCE: CASHBOOK vs INDIVIDUAL for Donation General ===")
missing_total = 0
for entry in dg_entries:
    reg = entry["reg"]
    if not reg: continue
    # Find this reg in individual
    member = None
    for row in individual[4:]:
        if str(row.get("B", "")).strip() == reg:
            member = row
            break
    
    if member:
        indiv_f = float(str(member.get("F", "0")).replace(",", "") or "0")
        if abs(indiv_f - entry["total"]) > 0.01:
            # Mismatch!
            name = str(member.get("C", "")).strip()
            # Don't print exact match, only mismatches
    else:
        if entry["total"] > 0:
            print(f"  REG#{reg} ({entry['hof']}): Cashbook has {entry['total']} but member NOT FOUND in individual!")
            missing_total += entry["total"]

print(f"\nMissing total from unmatched members: {missing_total}")

# Check if the code mapping is the issue
print("\n\n=== ACCOUNT HEAD CODES for Donation General ===")
codes_used = set(e["code"] for e in dg_entries)
print(f"Codes used in cashbook: {codes_used}")

# Check customAccountHeads
custom_heads = data.get("customAccountHeads", [])
print(f"\nCustom Account Heads: {json.dumps(custom_heads, indent=2)[:500]}")

# Check what the individual header says about column F
if len(individual) > 2:
    print(f"\nIndividual header row 2 col F: {individual[2].get('F', 'N/A')}")
    print(f"Individual header row 3 col F: {individual[3].get('F', 'N/A')}")
