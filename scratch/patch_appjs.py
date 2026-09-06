import re

filepath = r'c:\saju_old pc\Church_App\anti_gravity_v9.2\android-app\app\src\main\assets\app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update callers
content = content.replace('findIndividualColKey({ head: oldHead, code: oldCode })', 'findIndividualColKey({ particulars: oldHead, code: oldCode })')
content = content.replace('findIndividualColKey({ head: head, code: code })', 'findIndividualColKey({ particulars: head, code: code })')

# 2. Fix the second findIndividualColKey definition
old_def = """function findIndividualColKey({ head, code }) {
  if (!state.individual || state.individual.length < 4) return null;
  const headerRow = state.individual[3];
  
  head = (head || "").toLowerCase().trim();
  code = (code || "").toUpperCase().trim();"""

new_def = """function findIndividualColKey(item) {
  if (!state.individual || state.individual.length < 4) return null;
  const headerRow = state.individual[3];
  
  let head = (item.particulars || "").toLowerCase().trim();
  let code = (item.code || "").toUpperCase().trim();"""

content = content.replace(old_def, new_def)

# 3. Fix auto-sync logic
auto_sync_old = """             const item = { particulars: getColVal(itemRow, "E"), code: getColVal(itemRow, "F") };
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
             }"""

auto_sync_new = """             const item = { particulars: getColVal(itemRow, "E"), code: getColVal(itemRow, "F") };
             let targetColKey = findIndividualColKey(item) || "E";"""

content = content.replace(auto_sync_old, auto_sync_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done updating app.js')
