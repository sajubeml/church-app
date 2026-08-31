import re
import json

with open(r"c:\saju_old pc\Church_App\anti_gravity_v9.2\data.js", "r", encoding="utf-8") as f:
    content = f.read()

# find cashbook array
match = re.search(r'cashbook:\s*(\[.*?\]),\s*customAccountHeads', content, re.DOTALL)
if match:
    cashbook_json = match.group(1)
    cashbook = json.loads(cashbook_json)

    def getColVal(row, colKey):
        if not row: return ""
        val = str(row.get(colKey, ""))
        if val == "None": val = ""
        return val.strip()

    openingCash = 0.0
    openingBank = 0.0
    totalCashR = 0.0
    totalBankR = 0.0
    totalCashP = 0.0
    totalBankP = 0.0

    def parse_float(val):
        if not val: return float('nan')
        try:
            return float(val.replace(',', ''))
        except:
            return float('nan')

    for row in cashbook:
        dtRaw = getColVal(row, 'A')
        recNo = getColVal(row, 'B')
        voucherNo = getColVal(row, 'L')
        regNo = getColVal(row, 'C')
        hof = getColVal(row, 'D')
        head = getColVal(row, 'E')
        details = getColVal(row, 'G')
        cashR = getColVal(row, 'H')
        bankR = getColVal(row, 'I')
        payHead = getColVal(row, 'M')
        payCode = getColVal(row, 'N')
        payDetails = getColVal(row, 'O')
        cashP = getColVal(row, 'P')
        bankP = getColVal(row, 'Q')

        dtLower = dtRaw.lower()
        recLower = recNo.lower()
        headLower = head.lower()
        payLower = payHead.lower()

        if ("cash book" in dtLower or "receipts" in dtLower or dtLower == "date" or
            recLower.startswith("receipt") or headLower == "accounts head" or payLower == "accounts head"):
            continue

        isOpening = False
        if ("opening balance" in details.lower() or cashR == "9879" or bankR == "651682" or
            ("opening" in headLower and (cashR or bankR))):
            isOpening = True

        isValidReceipt = isOpening or bool(recNo) or bool(head) or bool(hof)
        
        if isOpening:
            if openingCash == 0 and cashR:
                v = parse_float(cashR)
                if not v != v: openingCash = v
            if openingBank == 0 and bankR:
                v = parse_float(bankR)
                if not v != v: openingBank = v
        elif isValidReceipt:
            if cashR:
                v = parse_float(cashR)
                if not v != v: totalCashR += v
            if bankR:
                v = parse_float(bankR)
                if not v != v: totalBankR += v

        isValidPayment = bool(voucherNo) or bool(payHead) or bool(payCode) or bool(payDetails)
        if isValidPayment:
            if cashP:
                v = parse_float(cashP)
                if not v != v: totalCashP += v
            if bankP:
                v = parse_float(bankP)
                if not v != v: totalBankP += v

    closingCash = openingCash + totalCashR - totalCashP
    closingBank = openingBank + totalBankR - totalBankP

    print(f"data.js Calc: Cash={closingCash}, Bank={closingBank}")
else:
    print("Could not parse data.js")
