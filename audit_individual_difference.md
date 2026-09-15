# Individual Ledger Discrepancy Audit

This audit report identifies the root causes of the differences between your manual Excel spreadsheet totals and the Web App's Individual Member Ledgers totals. 

**Grand Total Difference:**
- Excel Spreadsheet: ₹ 9,59,646
- Web App: ₹ 9,56,046
- **Difference: ₹ 3,600**

## 1. Massive Column Value Shifts (The Shifted Baseline)

If you look closely at the Web App footer totals compared to the Excel footer totals, the numbers for the columns on the right side are completely jumbled:
- **Web App Passion Week Collection:** ₹ 80,306 *(Excel is ₹ 15,000)*
- **Web App St. Mary's Feast:** ₹ 55,100 *(Excel is ₹ 1,500)*
- **Web App Perunnal Vanchika:** ₹ 2,400 *(Excel is ₹ 78,606)*

### Root Cause: Hidden Columns in Excel during Copy-Paste
When you imported your initial data into the Web App using the **"Paste Excel Data"** feature, you copied data from your `.xlsm` file. However, your Excel spreadsheet has several **Hidden Columns**.

If you look at the column letters at the top of your Excel screenshot, they jump:
- From `Q` directly to `U` (columns `R, S, T` are hidden or deleted)
- From `V` directly to `X` (column `W` is hidden)
- From `Y` to `AE` (columns `Z, AA, AB, AC, AD` are hidden)

When you copy and paste this into the Web App, Excel only copies the **visible** columns. 
The Web App expects a rigid 39-column format (Columns `A` through `AM`). Because the hidden columns were skipped, the Web App shifted all the following data to the left to fill the gaps.

**Example of the shift:**
- Excel Column `P` is **Perunnal Vanchika**. It was pasted into Web App Column `P`, which is **Orma Qurbana**.
- Excel Column `V` is **Petty Auction**. It was pasted into Web App Column `R`, which is **St. Gregorios Feast**.
- Excel Column `X` is **Donation-Breakfast**. It was pasted into Web App Column `T`, which is **Christmas / New Year**.

This completely corrupted the "baseline" data (`data.js` / `INITIAL_INDIVIDUAL`), which is why the Web App starts with completely wrong base numbers for all the feast and auction columns.

## 2. The "Auction Dues - Old" Mapping Bug

You may have noticed that **Petty Auction** in the Web App is **₹ 16,000**, but in Excel it is **₹ 0**.

### Root Cause: Fuzzy Matching Priority
When you enter a receipt in the Cashbook for "Auction Dues - Old", the Web App tries to find the matching column by looking for the word "auction". 

Since **Petty Auction (Column AF)** comes before **Auction Dues - Old (Column AH)** in the database, the system matches "Petty" first and stops looking. This means **every new receipt you entered for Auction Dues went into the Petty Auction column instead!**

## 3. The Remaining ₹ 3,600 Difference

Because the baseline data was pasted with shifted columns, and new receipts were added on top of that broken baseline using fuzzy matching, the Grand Total difference of ₹ 3,600 is a result of a combination of:
1. Missing hidden column values that were left out during the copy-paste.
2. Receipts mapped to the wrong columns.
3. Potentially missing cashbook entries that were added manually to Excel but not to the Web App.

## How to Fix This

Because you explicitly requested not to touch any functioning features, I have not made any code changes to fix this. However, if you wish to resolve these discrepancies in the future:
1. **Fix the Copy-Paste:** Unhide all columns in your Excel spreadsheet so that it matches columns `A` through `AM` perfectly before copying and pasting into the Web App.
2. **Fix the Fuzzy Match:** We can adjust the Web App's `app_supabase.js` to prioritize exact matches for "Auction Dues" before checking for "Auction".
