---
name: Church Accounting App - Comprehensive Rules & Architecture
description: Complete architectural knowledge, strict RP Code mapping logic, and historical bug fixes for the Church Accounting application (Web and Android).
---

# Church Accounting System Architecture

## 1. Codebase Structure
The user maintains two parallel codebases that must **always be kept in sync**:
1. **Web App (cPanel deployment):** `c:\saju_old pc\Church_App\anti_gravity_v9.2\deployment_files\cpanel\`
   - Core logic file: `app_supabase.js`
2. **Android App:** `c:\saju_old pc\Church_App\anti_gravity_v9.2\android-app\app\src\main\assets\`
   - Core logic file: `app.js`

Whenever a change is made to the core logic (e.g., Ledger calculations, Trial Balance UI, Syncing), it **must be applied to both files simultaneously**.

## 2. Individual Ledger Mapping
The Web App and Android App map Cashbook receipts to the 39 columns of the Individual Ledger using a **strict RP Code matching system**. 
- The legacy "fuzzy string matcher" (which checked `item.head` or `particulars` for text matches) was historically error-prone and has been **completely removed**.
- The `findIndividualColKey(item)` function must STRICTLY use the exact `item.code`.
- If an `RP Code` does NOT have a dedicated column in the 39-column grid (e.g. `RP-3.10` Kanicka Church, `RP-3.18`), it must **NOT** be added to the Individual Ledger. It should return `undefined` or `null`, and should NOT default to Subscription (`E`).

**Complete Mapping Table (`findIndividualColKey`):**
```javascript
'RP-3.82': 'E', 'RP-3.83': 'E',
'RP-2.02': 'F', 'RP-2.02(A)': 'F', // Note: 2.02(A) seamlessly merges into Donation General
'RP-10.04/05': 'G',
'RP-10.08': 'H',
'RP-10.13': 'I',
'RP-10.15': 'J',
'RP-10.10': 'K',
'RP-10.17': 'L',
'RP-3.17': 'M',
'RP-3.16': 'N',
'RP-3.14': 'O',
'RP-3.12': 'P',
'RP-10.14': 'Q',
'RP-3.33': 'R',
'RP-2.12': 'S',
'RP-3.11': 'T',
'RP-3.05': 'U',
'RP-2.13': 'V',
'RP-16.50': 'W',
'RP-3.31': 'X',
'RP-3.32': 'Y',
'RP-3.15(A)': 'Z',
'RP-3.15(B)': 'AA',
'RP-3.15(C)': 'AB',
'RP-3.15(D)': 'AC',
'RP-3.08': 'AD',
'RP-3.17(A)': 'AE',
'RP-2.15(B)': 'AF',
'RP-2.14': 'AG',
'RP-2.15(A)': 'AH',
'RP-3.09': 'AI',
'RP-3.21': 'AJ',
'RP-2.16': 'AK',
'RP-3.22': 'AL',
```

## 3. Trial Balance & Cashbook Data Quirks
When auditing or comparing the Web App Trial Balance against the user's manual Excel Trial Balance, keep these quirks in mind:
- **Opening Balance:** The Web App Trial Balance does **not** include the Opening Balance (e.g. `₹ 4,42,561`) in the bottom Total Receipts figure. The manual Excel sheet *does*.
- **RP-19 vs RP-10 Expense Codes:** The user has historically typed receipts into the Cashbook using expense codes (e.g., `RP-19.xx`). We ran a massive migration fix to map all `RP-19.xx` receipt codes to their proper `RP-10.xx` equivalents to ensure the Trial Balance groups them properly. If the Trial Balance looks split in the future, it means the user manually entered a generic `RP-19` code for a receipt again.
- **Independent Data Source:** The user's Excel file is no longer the required source of truth for the baseline Individual Ledger. The Web App's Cashbook contains the full history, and the Individual Ledger can be 100% mathematically rebuilt strictly from the Cashbook `auto-sync` logic. Do not suggest copy-pasting from Excel unless explicitly requested.

## 4. Known Bugs and Historical Fixes
- **JSON Comma Corruption:** NEVER format numbers with commas (e.g. `"2,000"`) when manually generating or editing JSON backup files via Python scripts. JavaScript's `parseFloat("2,000")` evaluates to `2`, permanently corrupting the entire ledger upon restore. Always use raw floats/integers (e.g. `"2000"`).
- **Hidden Columns:** The UI allows hiding columns with no data to compress the view (logic in `app_supabase.js` and `app.js` around line 2710). However, ensure this does not break CSV exports.
- **Python Utilities:** The `scratch/` directory contains highly useful Python scripts (`rebuild_ledger.py`, `audit_tb.py`, `fix_trial_balance.py`) that can mathematically rebuild the entire Individual Ledger from the Cashbook and audit Trial Balance totals. Use these tools if the user suspects data corruption.
