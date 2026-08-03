import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data_export/Individual.json', 'r', encoding='utf-8') as f:
    indiv = json.load(f)

print("=== BEFORE FIX ===")
print("Row 5 (Reg #51):", indiv[4])
print("Row 90 (Reg #150):", indiv[89])
print("Row 115 (Grand Total):", indiv[114])
