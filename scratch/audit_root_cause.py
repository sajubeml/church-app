import json

with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json", "r", encoding="utf-8") as f:
    data = json.load(f)

cashbook = data.get("cashbook", [])
individual = data.get("individual", [])

# The key bug: code "RP-2.02(a)" (lowercase) does NOT match "RP-2.02(A)" (uppercase) in the mapping!
# Line 2816: if (head.includes("donation general") || code === "RP-2.02" || code === "RP-2.02(A)") return "F";
# But cashbook entries use code "RP-2.02(a)" (lowercase 'a')!

print("=== BUG ANALYSIS: Case sensitivity in code matching ===")
print()
rp202_total = 0
rp202a_lower_total = 0
rp202A_upper_total = 0

for row in cashbook:
    code = str(row.get("F", "")).strip()
    head = str(row.get("E", "")).strip()
    if "Donation" in head and "General" in head:
        cashR = float(row.get("H", 0) or 0)
        bankR = float(row.get("I", 0) or 0)
        total = cashR + bankR
        if code == "RP-2.02":
            rp202_total += total
        elif code == "RP-2.02(a)":
            rp202a_lower_total += total
        elif code == "RP-2.02(A)":
            rp202A_upper_total += total

print(f"Code 'RP-2.02'   total: {rp202_total}  (MATCHED by app)")
print(f"Code 'RP-2.02(a)' total: {rp202a_lower_total}  (NOT MATCHED - lowercase 'a')")
print(f"Code 'RP-2.02(A)' total: {rp202A_upper_total}  (Would be MATCHED - uppercase 'A')")
print()
print(f"Total correctly mapped:  {rp202_total + rp202A_upper_total}")
print(f"Total MISSED (case bug): {rp202a_lower_total}")
print()

# Now let's check ALL mismatched columns similarly
# Check if the individual ledger is just not being updated when receipts are created via the app
# vs the Excel which was manually maintained

# Let's look at how receipts update individual ledger
print("\n=== DEEPER ANALYSIS: What happens when a receipt is saved? ===")
print()

# Check if the issue is that individual ledger entries come from the ORIGINAL Excel data
# and don't get updated when new cashbook entries are added via the web app

# Count entries in individual that have Col F > 0
indiv_f_members = {}
for row in individual[4:]:
    c = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c.upper(): continue
    f = float(str(row.get("F", "0")).replace(",", "") or "0")
    if f > 0:
        indiv_f_members[str(row.get("B", "")).strip()] = f

print(f"Members with Donation General in individual ledger: {len(indiv_f_members)}")

# Count unique members with Donation General in cashbook
cb_dg_members = {}
for row in cashbook:
    head = str(row.get("E", "")).strip()
    if "Donation" in head and "General" in head:
        reg = str(row.get("C", "")).strip()
        if not reg: continue
        cashR = float(row.get("H", 0) or 0)
        bankR = float(row.get("I", 0) or 0)
        cb_dg_members.setdefault(reg, 0)
        cb_dg_members[reg] += cashR + bankR

print(f"Unique members with Donation General in cashbook: {len(cb_dg_members)}")

# Members in cashbook but NOT in individual for Donation General
print("\n=== Members with Donation General in CASHBOOK but MISSING/LESS in INDIVIDUAL ===")
missing_total = 0
for reg, cb_total in sorted(cb_dg_members.items()):
    indiv_total = indiv_f_members.get(reg, 0)
    diff = cb_total - indiv_total
    if diff > 0.01:
        # Find member name
        name = reg
        for row in individual[4:]:
            if str(row.get("B", "")).strip() == reg:
                name = str(row.get("C", "")).strip()
                break
        print(f"  Reg#{reg} {name}: Cashbook={cb_total}, Individual={indiv_total}, Missing={diff}")
        missing_total += diff

print(f"\nTotal missing from individual ledger: {missing_total}")

# Now check the entire flow: does saving a new receipt update the individual ledger?
print("\n\n=== ROOT CAUSE SUMMARY ===")
print(f"Cashbook Donation General total: 267,540")
print(f"Individual Donation General total: 61,400")
print(f"Difference: 206,140")
print(f"  - Due to RP-2.02(a) case mismatch: {rp202a_lower_total}")
print(f"  - Due to entries not updating individual: {missing_total - rp202a_lower_total}")
