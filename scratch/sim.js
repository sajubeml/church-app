
const fs = require('fs');

const dataStr = fs.readFileSync('c:/Users/sajub/Downloads/St_Gregorios_Church_Backup_2026-08-31.json', 'utf-8');
const data = JSON.parse(dataStr);

const stateCashbook = data.cashbook;

// Fake baseInd to be the Aug 30 data
const aug30Str = fs.readFileSync('c:/Users/sajub/Downloads/St_Gregorios_Church_Backup_2026-08-30 (5).json', 'utf-8');
const aug30 = JSON.parse(aug30Str);

let baseInd = aug30.individual;
let baseCb = aug30.cashbook;

const baseReceiptNos = new Set();
baseCb.forEach(r => { const no = String(r["B"] || ""); if (no) baseReceiptNos.add(no); });

const newReceipts = stateCashbook.filter(r => {
    const no = String(r["B"] || "");
    return no && !baseReceiptNos.has(no);
});

console.log("New receipts count:", newReceipts.length);

function getColVal(rowObj, colLetter) {
  if (!rowObj) return "";
  const targetCol = String(colLetter).toUpperCase().replace(/[^A-Z]/g, '');
  if (!targetCol) return "";
  const targetKey = Object.keys(rowObj).find(k => k.toUpperCase().replace(/[^A-Z]/g, '') === targetCol);
  return (targetKey && rowObj[targetKey] !== undefined && rowObj[targetKey] !== null) ? String(rowObj[targetKey]).trim() : "";
}

function setColVal(rowObj, colLetter, val) {
  if (!rowObj) return;
  const targetCol = String(colLetter).toUpperCase().replace(/[^A-Z]/g, '');
  if (!targetCol) return;
  const targetKey = Object.keys(rowObj).find(k => k.toUpperCase().replace(/[^A-Z]/g, '') === targetCol);
  if (targetKey) {
    rowObj[targetKey] = String(val);
  } else {
    rowObj[targetCol] = String(val);
  }
}

newReceipts.forEach(itemRow => {
    const isReceipt = !!(getColVal(itemRow, "H") || getColVal(itemRow, "I"));
    if (!isReceipt) return;
    const amountStr = getColVal(itemRow, "H");
    const amountBank = getColVal(itemRow, "I");
    const amount = parseFloat((amountStr || amountBank || "0").toString().replace(/,/g, '')) || 0;
    const regNo = getColVal(itemRow, "C");
    
    if (amount > 0 && regNo) {
        const item = { particulars: getColVal(itemRow, "E"), code: getColVal(itemRow, "F") };
        let targetColKey = "E";
        const headerRow = baseInd[3] || {};
        const partStr = String(item.particulars || "").trim().toLowerCase();
        const codeStr = String(item.code || "").trim().toUpperCase();
        
        if (codeStr === "RP-3.82" || codeStr === "RP-3.83" || partStr.includes("subscription")) {
            targetColKey = "E";
        } else {
            for (let key in headerRow) {
                const title = String(headerRow[key] || "").trim().toLowerCase();
                if (!title) continue;
                const colLetter = key.replace(/[^A-Za-z]/g, '').toUpperCase();
                if (["A", "B", "C", "D", "AM"].includes(colLetter)) continue;
                
                if (
                    (partStr.includes("holy qurbana") && title.includes("qurbana")) ||
                    (partStr.includes("donat") && title.includes("donat") && !partStr.includes("breakfast") && !partStr.includes("marriage") && !partStr.includes("cemetry")) ||
                    (partStr.includes("perunnal") && title.includes("perunnal")) ||
                    (partStr.includes("passion") && title.includes("passion")) ||
                    (partStr.includes("george") && title.includes("george")) ||
                    (partStr.includes("thomas") && title.includes("thomas")) ||
                    (partStr.includes("mary") && title.includes("mary")) ||
                    (partStr.includes("blessing") && title.includes("blessing")) ||
                    (partStr.includes("auction") && title.includes("auction")) ||
                    (partStr.includes("cemetry") && title.includes("cemetry")) ||
                    (partStr.includes("breakfast") && title.includes("breakfast")) ||
                    (partStr.includes("birthday") && title.includes("birthday")) ||
                    (partStr.includes("anniversary") && title.includes("anniversary")) ||
                    (partStr.includes("baptism") && title.includes("baptism")) ||
                    (partStr.includes("bann") && title.includes("bann")) ||
                    (partStr.includes("catholicate") && title.includes("catholicate")) ||
                    (partStr.includes("metropolitan") && title.includes("metropolitan")) ||
                    (partStr.includes("mission") && title.includes("mission")) ||
                    (partStr.includes("seminary") && title.includes("seminary")) ||
                    (partStr.includes("priest") && title.includes("priest")) ||
                    (partStr.includes("sunday school") && title.includes("sunday school")) ||
                    (partStr.includes("harvest") && title.includes("harvest")) ||
                    (partStr.includes("christmas") && title.includes("christmas")) ||
                    title.includes(partStr) || partStr.includes(title)
                ) {
                    targetColKey = colLetter;
                    break;
                }
            }
        }
        
        console.log(`Receipt ${itemRow["B"]}: partStr=${partStr}, targetColKey=${targetColKey}`);
        
        const memberRow = baseInd.find((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);
        if (memberRow) {
            if (targetColKey) {
                const currentVal = parseFloat(getColVal(memberRow, targetColKey)) || 0;
                setColVal(memberRow, targetColKey, (currentVal + amount).toString());
            }
            const currentGrand = parseFloat(getColVal(memberRow, "AM")) || 0;
            setColVal(memberRow, "AM", (currentGrand + amount).toString());
        }
    }
});

const mary = baseInd.find(r => getColVal(r, "B") === "65");
console.log("Mary Mathew in baseInd:", mary);
