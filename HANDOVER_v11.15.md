# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Notes & Handover Guide (v11.15)

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.15** (Android `versionCode 78` / Web / Cloud / Offline PC)  
**Date of Release:** October 14, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. What's New in v11.15

### A. Dedicated Balance Sheet / Audited Financial Statement Tab (`tabBalanceSheet`)
* Added a dedicated **Balance Sheet** tab next to Trial Balance, presenting a clean 2-column audited financial statement:
  - **Left Column: Receipts / Inflows**
    - Opening Balances (Cash in Hand & Bank Balance as of start date)
    - Revenue & Capital Receipts grouped by Master Account Heads
  - **Right Column: Payments / Outflows**
    - Revenue & Capital Expenses grouped by Master Account Heads
    - Closing Balances (Cash in Hand & Bank Balance as of end date)
  - **Double-Entry Reconciliation Banner:**
    - Displays `Total Debit = Total Credit` and confirms `Variance = ₹0.00` in real-time.
  - **Print & PDF Export:** One-click print or save to PDF with clean official formatting.

### B. Statement Period & Date Range Filter Toolbar
* Users can filter the Balance Sheet by any financial period:
  - **⭐ Half-Yearly (Apr-Sep):** Preset for `01/04/2026` to `30/09/2026`.
  - **Full Year:** Entire financial year from `01/04/2026` to `31/03/2027`.
  - **Q1 (Apr-Jun):** First quarter `01/04/2026` to `30/06/2026`.
  - **Q2 (Jul-Sep):** Second quarter `01/07/2026` to `30/09/2026`.
  - **Custom Date Range:** Input fields for `From Date` and `To Date` (`DD/MM/YYYY` or `YYYY-MM-DD`) with an instant `Apply Filter` button.
* When filtered to a sub-period (e.g. Half-Yearly):
  - Dynamic Opening Balances automatically incorporate prior cashbook receipts and subtract prior payments.
  - Receipts and payments strictly include only transactions falling within the selected date window.
  - Contra transactions (bank deposits) are excluded from operational income/expense heads and correctly reflected in closing cash and bank balances.
  - Closing balances accurately reflect cash in hand and bank balance as of the closing date.
  - Perfect double-entry balance is maintained with `Variance = ₹0.00`.

### C. Cash & Bank Balance Reconciliation (14-Oct-2026)
* Traced and resolved the ₹660 difference between old workbooks and portal data:
  - In the old workbook, Receipt #4451 on 27-09-2026 had been entered as a duplicate candle/oil sale (₹810) instead of Daniel J's ₹150 receipt.
  - Correcting #4451 brought the portal and workbook into 100% agreement:
    - **Closing Cash in Hand:** ₹15,869.00
    - **Closing Bank Balance:** ₹20,48,637.00
    - **Total Net Liquidity:** ₹20,64,506.00
* Ingested monolithic backup `St_Gregorios_Church_Backup_2026-10-14.json` (1,079 rows) into all data bundles.

---

## 2. Half-Yearly Balance Sheet Summary (01-04-2026 to 30-09-2026)

| Particulars | Receipts (Debit) (₹) | Payments (Credit) (₹) |
| :--- | :---: | :---: |
| **Opening Balance (01-04-2026)** | | |
| - Cash in Hand | ₹9,879.00 | — |
| - SB Account | ₹6,51,682.00 | — |
| **Operational Transactions (Apr - Sep 2026)** | | |
| - Total Receipts (Net of Contra) | ₹33,99,894.00 | — |
| - Total Payments (Net of Contra) | — | ₹20,30,425.29 |
| **Closing Balance (as of 30-09-2026)** | | |
| - Cash in Hand | — | ₹1,493.01 |
| - SB Account | — | ₹20,29,536.70 |
| **GRAND TOTAL** | **₹40,61,455.00** | **₹40,61,455.00** |
| **VARIANCE** | **₹0.00** | **₹0.00** |

---

## 3. How to Access the Half-Yearly Balance Sheet

1. Open the application (Web, Android APK, or Offline Desktop).
2. Click on the **Balance Sheet** tab in the top navigation bar.
3. Click the preset button: **"⭐ Half-Yearly (Apr-Sep)"**.
4. The Balance Sheet immediately re-renders with:
   - Statement Period header: `From: 01/04/2026 To: 30/09/2026`
   - Opening cash & bank balances as of 01/04/2026
   - All receipts and payments for the first half of the financial year
   - Closing cash (₹1,493.01) and bank (₹20,29,536.70) as of 30/09/2026
   - Balanced grand totals: ₹40,61,455.00 (Variance: ₹0.00)
5. Click **"🖨️ Print Balance Sheet"** to print or export to PDF.
