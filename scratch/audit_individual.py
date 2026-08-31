import json

with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json", "r", encoding="utf-8") as f:
    data = json.load(f)

individual = data.get("individual", [])

# Column mapping from the Excel headers (row index 3 = header row)
# The columns in the individual ledger are:
# A=Sl No, B=Reg No, C=Name of HoF, D=Subscription upto
# E=Subscription (Min 200.00), F=Donation General, G=Catholicate Day & Recessa
# H=Metropolitan Fund, I=Mission Sunday, J=Seminary Day
# K=Priest Welfare Fund, L=Old Cover Collection Dues, M=Wedding Anniversary Offerings
# N=Birthday Offering, O=Baptism, P=Onna Qurbana/Holy Qurbana
# ... and so on up to AM=GRAND TOTAL

print(f"Total rows in individual: {len(individual)}")
print()

# Find the header row and GRAND TOTAL row
for i, row in enumerate(individual):
    b_val = str(row.get("B", "")).strip()
    c_val = str(row.get("C", "")).strip()
    if "GRAND TOTAL" in c_val.upper() or "GRAND TOTAL" in b_val.upper():
        print(f"Row {i}: GRAND TOTAL row found")
        # Print all columns
        for key in sorted(row.keys()):
            val = row[key]
            if val and str(val).strip():
                print(f"  {key}: {val}")
        print()

# Calculate grand total from AM column for all members
total_from_am = 0
member_count = 0
for i, row in enumerate(individual):
    if i < 4:  # Skip header rows
        continue
    am_val = str(row.get("AM", "")).strip()
    c_val = str(row.get("C", "")).strip()
    b_val = str(row.get("B", "")).strip()
    
    if "GRAND TOTAL" in c_val.upper():
        continue
    
    if am_val:
        try:
            val = float(am_val.replace(",", ""))
            total_from_am += val
            member_count += 1
            if val > 0:
                print(f"  Reg#{b_val} {c_val}: AM={val}")
        except:
            pass

print(f"\nTotal members with data: {member_count}")
print(f"Sum of all AM (GRAND TOTAL) columns: {total_from_am}")

# Now calculate column-by-column totals
col_keys = ["E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"]
print("\n\nColumn-by-column totals:")
grand = 0
for col in col_keys:
    total = 0
    for i, row in enumerate(individual):
        if i < 4:
            continue
        c_val = str(row.get("C", "")).strip()
        if "GRAND TOTAL" in c_val.upper():
            continue
        val_str = str(row.get(col, "")).strip()
        if val_str:
            try:
                total += float(val_str.replace(",", ""))
            except:
                pass
    if total > 0:
        print(f"  Col {col}: {total}")
        grand += total

print(f"\nSum of all individual columns: {grand}")

# Now let's check what the web app calculates
# The web shows page 1 of 2 - is this a pagination issue?
print("\n\n=== PAGINATION CHECK ===")
print(f"Total individual rows (including headers): {len(individual)}")
data_rows = [r for i, r in enumerate(individual) if i >= 4 and "GRAND TOTAL" not in str(r.get("C", "")).upper()]
print(f"Data rows (members): {len(data_rows)}")

# Check how many have non-zero AM
non_zero = [r for r in data_rows if float(str(r.get("AM", "0")).replace(",", "") or "0") > 0]
print(f"Members with non-zero GRAND TOTAL: {len(non_zero)}")

# Page 1 vs Page 2 split
page_size = 60  # typical pagination
page1_total = sum(float(str(r.get("AM", "0")).replace(",", "") or "0") for r in data_rows[:page_size])
page2_total = sum(float(str(r.get("AM", "0")).replace(",", "") or "0") for r in data_rows[page_size:])
print(f"\nIf page size = {page_size}:")
print(f"  Page 1 total: {page1_total}")
print(f"  Page 2 total: {page2_total}")

