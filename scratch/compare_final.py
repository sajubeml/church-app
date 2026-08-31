
# Compare recalculated vs Excel
excel = {
    "E": 195700, "F": 255720, "G": 34250, "H": 15250, "I": 19150,
    "J": 7050, "K": 7900, "L": 8100, "M": 8500, "N": 21350,
    "O": 2500, "P": 3520, "Q": 5250, "U": 3400, "V": 78000,
    "W": 15000, "X": 600, "Y": 56400, "AE": 1500, "AF": 1500,
    "AH": 92500, "AK": 118300,
}

recalc = {
    "E": 208140, "F": 255720, "G": 34250, "H": 15250, "I": 10150,
    "J": 7050, "K": 7900, "L": 8100, "M": 8500, "N": 21350,
    "O": 2500, "P": 3520, "Q": 2750, "U": 3400, "V": 81006,
    "W": 15000, "X": 600, "Y": 56400, "AE": 1500, "AF": 1500,
    "AH": 92500, "AK": 118800,
}

old_web = {
    "E": 193300, "F": 61400, "G": 34250, "H": 15250, "I": 9650,
    "J": 7050, "K": 7900, "L": 8100, "M": 8500, "N": 21350,
    "O": 2500, "P": 2520, "Q": 5250, "U": 3400, "V": 55305,
    "W": 14000, "X": 600, "Y": 54900, "AE": 1500, "AF": 1500,
    "AH": 92500, "AK": 118800,
}

all_cols = sorted(set(list(excel.keys()) + list(recalc.keys()) + list(old_web.keys())),
                  key=lambda x: (len(x), x))

print(f"{'Col':<6} {'Excel':>10} {'Old Web':>10} {'Recalc':>10} {'Excel-Recalc':>12}  Status")
print("=" * 70)
for col in all_cols:
    e = excel.get(col, 0)
    o = old_web.get(col, 0)
    r = recalc.get(col, 0)
    diff = e - r
    status = "OK MATCH" if diff == 0 else f"!! Diff {diff:+,}"
    print(f"  {col:<4} {e:>10,} {o:>10,} {r:>10,} {diff:>+12,}  {status}")

e_total = sum(excel.values())
o_total = sum(old_web.values())
r_total = sum(recalc.values())
print("=" * 70)
print(f"  {'TOT':<4} {e_total:>10,} {o_total:>10,} {r_total:>10,} {e_total-r_total:>+12,}")
print(f"\nOLD discrepancy:  {e_total - o_total:,} (HUGE)")
print(f"NEW discrepancy:  {e_total - r_total:,} (mostly subscription timing differences)")
