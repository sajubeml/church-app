import json

with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json", "r", encoding="utf-8") as f:
    data = json.load(f)

individual = data.get("individual", [])

# Compare web JSON individual totals vs Excel totals from screenshots
# Excel GRAND TOTAL row: 195700, 2,55,720, 34,250, 15,250, 19,150, 7,050, 7,900, 8,100, 8,500, 21,350, 2,500, 3,520, 5,250, 3,400, 78,000, 15,000, 600, 56,400, 1,500, 1,500, 92,500, 1,18,300 = 9,43,546

# Excel totals (from screenshot, reading left to right):
excel_totals = {
    "E": 195700,   # Subscription
    "F": 255720,   # Donation General
    "G": 34250,    # Catholicate Day & Recessa
    "H": 15250,    # Metropolitan Fund
    "I": 19150,    # Mission Sunday
    "J": 7050,     # Seminary Day
    "K": 7900,     # Priest Welfare Fund
    "L": 8100,     # Old Cover Collection Dues
    "M": 8500,     # Wedding Anniversary Offerings
    "N": 21350,    # Birthday Offering
    "O": 2500,     # Baptism
    "P": 3520,     # Onna Qurbana/Holy Qurbana
    "Q": 5250,     # Sunday School/Day Qurbana
    "U": 3400,     # Personal/Offertory Collection
    "V": 78000,    # St. George Feast (or similar)
    "W": 15000,    # St. Thomas Feast
    "X": 600,      # St. Mary's Feast
    "Y": 56400,    # House Blessing
    "AE": 1500,    # Petty Auction
    "AF": 1500,    # Auction Dues Oil
    "AH": 92500,   # Donation/Breakfast
    "AK": 118300,  # Donation Breakfast?
}
excel_grand = 943546

# Web/JSON totals (from our calculation)
json_totals = {
    "E": 193300.0,
    "F": 61400.0,
    "G": 34250.0,
    "H": 15250.0,
    "I": 9650.0,
    "J": 7050.0,
    "K": 7900.0,
    "L": 8100.0,
    "M": 8500.0,
    "N": 21350.0,
    "O": 2500.0,
    "P": 2520.0,
    "Q": 5250.0,
    "U": 3400.0,
    "V": 55305.0,
    "W": 14000.0,
    "X": 600.0,
    "Y": 54900.0,
    "AE": 1500.0,
    "AF": 1500.0,
    "AH": 92500.0,
    "AK": 118800.0,
}
json_grand = 719525

print("=" * 80)
print(f"{'Column':<8} {'Excel':>12} {'Web/JSON':>12} {'Difference':>12}  Notes")
print("=" * 80)

all_cols = sorted(set(list(excel_totals.keys()) + list(json_totals.keys())), 
                  key=lambda x: (len(x), x))

total_diff = 0
for col in all_cols:
    e = excel_totals.get(col, 0)
    j = json_totals.get(col, 0)
    diff = e - j
    total_diff += diff
    flag = " <<<< MISMATCH" if diff != 0 else ""
    print(f"  {col:<6} {e:>12,.0f} {j:>12,.0f} {diff:>+12,.0f}{flag}")

print("=" * 80)
print(f"  {'TOTAL':<6} {excel_grand:>12,} {json_grand:>12,} {excel_grand - json_grand:>+12,}")
print(f"\nTotal difference: {excel_grand - json_grand:,}")
print(f"Sum of column diffs: {total_diff:,}")
