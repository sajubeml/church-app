import json

data = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json', 'r', encoding='utf-8'))
individual = data['individual']
cashbook = data['cashbook']

# Check header row for column AK title
print("=== Individual Ledger Header Row (Row 3) ===")
header = individual[3]
for k in sorted(header.keys(), key=lambda x: (len(x), x)):
    print(f"  {k}: {header[k]}")

# Check what the first findIndividualColKey would do for "Donation-Breakfast"
# It matches on item.particulars (the account head name) against header titles
print("\n\n=== Receipt #4381 Analysis ===")
print("Account Head: Donation-Breakfast")
print("Code: RP-2.16")

# The first findIndividualColKey (line 1691) does text matching:
# partStr = "donation-breakfast" (lowercase)
# It checks: partStr.includes("breakfast") && title.includes("breakfast")
# So it would match column AK IF the header title contains "breakfast"

ak_title = str(header.get("AK", "")).strip().lower()
print(f"\nColumn AK header title: '{header.get('AK', 'N/A')}'")
print(f"Does 'breakfast' appear in AK title? {'breakfast' in ak_title}")

# Check ALL header titles for "breakfast"
print("\n=== Headers containing 'breakfast' ===")
for k in sorted(header.keys(), key=lambda x: (len(x), x)):
    title = str(header[k]).strip().lower()
    if 'breakfast' in title:
        print(f"  {k}: {header[k]}")

# Check if the code also checks "donat" keyword
print("\n=== Headers containing 'donat' ===")
for k in sorted(header.keys(), key=lambda x: (len(x), x)):
    title = str(header[k]).strip().lower()
    if 'donat' in title:
        print(f"  {k}: {header[k]}")

# Now check: what does findIndividualColKey ACTUALLY return for "Donation-Breakfast"?
# Line 1710: (partStr.includes("donat") && title.includes("donat") && 
#             !partStr.includes("breakfast") && !partStr.includes("marriage") && !partStr.includes("cemetry"))
# 
# For "donation-breakfast":
# - partStr.includes("donat") = TRUE
# - BUT partStr.includes("breakfast") = TRUE  --> THIS EXCLUSION KICKS IN!
# So the "donat" check WON'T match because it excludes "breakfast"
#
# Then it checks:
# Line 1719: (partStr.includes("breakfast") && title.includes("breakfast"))
# This WOULD match if any column header contains "breakfast"

print("\n\n=== SIMULATING findIndividualColKey for 'Donation-Breakfast' ===")
partStr = "donation-breakfast"
codeStr = "RP-2.16"

# Check subscription first
if codeStr == "RP-3.82" or codeStr == "RP-3.83" or "subscription" in partStr:
    print("Would return E (subscription)")
else:
    # Loop through headers
    matched = False
    for k in sorted(header.keys(), key=lambda x: (len(x), x)):
        colLetter = k.upper()
        if colLetter in ("A", "B", "C", "D", "AM"): continue
        title = str(header[k]).strip().lower()
        if not title or title == "grand total": continue
        
        # Check each condition from the code
        if (partStr.find("donat") >= 0 and title.find("donat") >= 0 and 
            partStr.find("breakfast") < 0 and partStr.find("marriage") < 0 and partStr.find("cemetry") < 0):
            print(f"  MATCHED by 'donat' rule -> Col {colLetter}: {header[k]}")
            matched = True
            break
        if partStr.find("breakfast") >= 0 and title.find("breakfast") >= 0:
            print(f"  MATCHED by 'breakfast' rule -> Col {colLetter}: {header[k]}")
            matched = True
            break
        if title.find(partStr) >= 0 or partStr.find(title) >= 0:
            print(f"  MATCHED by title containment -> Col {colLetter}: {header[k]}")
            matched = True
            break
    
    if not matched:
        print("  NO MATCH FOUND -> Would fall through to default Col E")

# Now check Mary Mathew individual record
print("\n\n=== Mary Mathew (Reg 65) - ALL individual ledger values ===")
for i, row in enumerate(individual):
    if i < 4: continue
    if str(row.get('B', '')).strip() == '65':
        for k in sorted(row.keys(), key=lambda x: (len(x), x)):
            v = row.get(k, '')
            if v and str(v).strip() and str(v).strip() != '0':
                print(f"  {k}: {v}")
        print(f"\n  AM (Grand Total) = {row.get('AM', 0)}")
        
        # What SHOULD her AK be?
        print(f"  AK (Donation-Breakfast) = {row.get('AK', 0)}")
        print(f"  E (Subscription) = {row.get('E', 0)}")
        
# Also check: were receipts 4380-4382 created via the form (have all fields)?
print("\n\n=== Receipts #4380-4382 Details ===")
for row in cashbook:
    recNo = str(row.get('B', '')).strip()
    if recNo in ('#4380', '#4381', '#4382', '4380', '4381', '4382'):
        print(f"\nReceipt {recNo}:")
        for k in sorted(row.keys(), key=lambda x: (len(x), x)):
            v = row.get(k, '')
            if v and str(v).strip():
                print(f"  {k}: {v}")
