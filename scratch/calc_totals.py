import json

with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json", "r", encoding="utf-8") as f:
    data = json.load(f)

cashbook = data.get("cashbook", [])

openingCash = 0
openingBank = 0
totalCashR = 0
totalBankR = 0
totalCashP = 0
totalBankP = 0

for row in cashbook:
    cashR_str = row.get("H", "")
    bankR_str = row.get("I", "")
    cashP_str = row.get("P", "")
    bankP_str = row.get("Q", "")
    details = str(row.get("G", "")).lower()
    head = str(row.get("E", "")).lower()
    
    cashR = float(cashR_str) if cashR_str and str(cashR_str).strip() != "" else 0.0
    bankR = float(bankR_str) if bankR_str and str(bankR_str).strip() != "" else 0.0
    cashP = float(cashP_str) if cashP_str and str(cashP_str).strip() != "" else 0.0
    bankP = float(bankP_str) if bankP_str and str(bankP_str).strip() != "" else 0.0

    if "opening balance" in details or str(cashR_str).strip() == "9879" or str(bankR_str).strip() == "651682" or ("opening" in head and (cashR > 0 or bankR > 0)):
        if openingCash == 0 and cashR > 0:
            openingCash = cashR
        if openingBank == 0 and bankR > 0:
            openingBank = bankR
    else:
        totalCashR += cashR
        totalBankR += bankR
        
    totalCashP += cashP
    totalBankP += bankP

closingCash = openingCash + totalCashR - totalCashP
closingBank = openingBank + totalBankR - totalBankP

print(f"Calculated from JSON:")
print(f"Opening Cash: {openingCash}, Opening Bank: {openingBank}")
print(f"Total Cash R: {totalCashR}, Total Bank R: {totalBankR}")
print(f"Total Cash P: {totalCashP}, Total Bank P: {totalBankP}")
print(f"Net Cash Balance: {closingCash}")
print(f"Net Bank Balance: {closingBank}")
print(f"Total Liquidity: {closingCash + closingBank}")

