import json

data = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json', 'r', encoding='utf-8'))
aug30 = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json', 'r', encoding='utf-8'))

state_cashbook = data['cashbook']
baseInd = aug30['individual'] # simulate data.js individual
baseCb = aug30['cashbook'] # simulate data.js cashbook

baseReceiptNos = set([str(r.get("B", "")) for r in baseCb if r.get("B")])
newReceipts = [r for r in state_cashbook if str(r.get("B", "")) and str(r.get("B", "")) not in baseReceiptNos]

print(f"newReceipts length: {len(newReceipts)}")
for r in newReceipts:
    print(f"New receipt: B={r.get('B')}, C={r.get('C')}, E={r.get('E')}")

for itemRow in newReceipts:
    isReceipt = bool(itemRow.get("H") or itemRow.get("I"))
    if not isReceipt: continue
    
    amountStr = str(itemRow.get("H", "") or itemRow.get("I", "") or "0").replace(',', '')
    try:
        amount = float(amountStr)
    except:
        amount = 0
    regNo = str(itemRow.get("C", ""))
    
    if amount > 0 and regNo:
        particulars = str(itemRow.get("E", ""))
        code = str(itemRow.get("F", ""))
        partStr = particulars.strip().lower()
        codeStr = code.strip().upper()
        
        targetColKey = "E"
        headerRow = baseInd[3]
        
        if codeStr in ("RP-3.82", "RP-3.83") or "subscription" in partStr:
            targetColKey = "E"
        else:
            for key, title_val in headerRow.items():
                title = str(title_val).strip().lower()
                if not title: continue
                colLetter = "".join([c for c in key.upper() if c.isalpha()])
                if colLetter in ("A", "B", "C", "D", "AM"): continue
                
                # Check mapping rules
                if ("holy qurbana" in partStr and "qurbana" in title) or \
                   ("donat" in partStr and "donat" in title and "breakfast" not in partStr and "marriage" not in partStr and "cemetry" not in partStr) or \
                   ("breakfast" in partStr and "breakfast" in title) or \
                   (partStr in title if partStr else False) or \
                   (title in partStr if title else False):
                   
                   # Just simulate the specific match for breakfast
                   if "breakfast" in partStr and "breakfast" in title:
                       print(f"MATCHED BREAKFAST for partStr={partStr}, col={colLetter}")
                       targetColKey = colLetter
                       break
        
        print(f"Receipt {itemRow.get('B')}: partStr='{partStr}', targetColKey='{targetColKey}'")
        
        # Find member
        memberRow = None
        memberIdx = -1
        for idx, r in enumerate(baseInd):
            if idx >= 4 and str(r.get("B", "")) == regNo:
                memberRow = r
                memberIdx = idx
                break
                
        if memberRow:
            print(f"  Found member Reg#{regNo} at idx {memberIdx}")
            if targetColKey:
                currentVal = float(str(memberRow.get(targetColKey, 0)).replace(',', '') or 0)
                memberRow[targetColKey] = str(currentVal + amount)
                print(f"  Updated Col {targetColKey} to {memberRow[targetColKey]}")
            
            currentGrand = float(str(memberRow.get("AM", 0)).replace(',', '') or 0)
            memberRow["AM"] = str(currentGrand + amount)

print("\nResult for Reg 65 (Mary Mathew):")
for r in baseInd:
    if str(r.get("B", "")) == "65":
        print(r)

