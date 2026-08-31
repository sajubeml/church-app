# St. Gregorios Church App Accounting Rules & Knowledge

When working on this project or auditing its database backups, you must adhere to the following learned knowledge about the system architecture and its common data entry bugs:

## 1. Database Architecture
The application primarily exports and imports state via a monolithic JSON backup file (e.g., `St_Gregorios_Church_Backup_YYYY-MM-DD.json`).
- The **Cash Book** (`cashbook` array) is the **absolute single source of truth** for EVERYTHING — Trial Balance, Individual Ledger amounts, and Subscription Upto dates.
- The **Individual Member Ledger** (`individual` array) is used ONLY for member name/reg no identity (columns `A`, `B`, `C`) and the header row (row index 3). All financial amounts are now dynamically aggregated from the Cash Book at render time. **Do NOT manually edit ledger financial cells — they are ignored by the app.**

## 2. Master Accounting Codes
The source of truth for all accounting codes is hardcoded in `app_supabase.js` (`MASTER_RECEIPT_HEADS` and `MASTER_PAYMENT_HEADS`).
- **Receipt Codes** (Left Side) generally start with `RP-10.xx`, `RP-2.xx`, `RP-3.xx`. (e.g., `RP-3.32` is St. Mary's Feast Receipt).
- **Payment Codes** (Right Side) generally start with `RP-12.xx`, `RP-14.xx`, `RP-16.xx`, `RP-19.xx`. (e.g., `RP-16.47` is St. Mary's Feast Expense).
- **Key subscription codes:** `RP-3.82` = Monthly Subscription (Current Year), `RP-3.83` = Monthly Subscription (Previous Year).

## 3. Cash Book Validation (Common Bugs)
When auditing the cashbook, operators frequently swap codes between sides when entering multi-entry receipts.
- **Receipts (Left):** Stored in columns `A` to `I`. Date is `A`, Receipt number is `B`, Reg No is `C`, Name is `D`, Account Head is `E`, Code is `F`, Remarks is `G`, Amount is `H` or `I`.
- **Payments (Right):** Stored in columns `K` to `P`. Voucher number is `L`, Account Head is `M`, Code is `N`.
- **CRITICAL AUDIT RULE:** You must ensure that `F` NEVER contains a code from `MASTER_PAYMENT_HEADS`, and `N` NEVER contains a code from `MASTER_RECEIPT_HEADS`. If they do, the Trial Balance will silently break.

## 4. Individual Member Ledger — Cashbook-Brain Architecture (Updated Aug 2026)
The `individual` array's header row (index 3) defines the column layout. Financial data is now 100% computed from the Cash Book.
- `B` = Register No. (used to match cashbook `C` column)
- `C` = Member Name
- `D` = Subscription Upto Validity (manual override only — app now ignores this and reads from Cash Book remarks automatically)
- The app function `findIndividualColKey({ head, code })` maps each Cash Book Account Head/Code to its ledger column key.
- The app function `getLatestSubscriptionRemark(regNo)` reads the Cash Book to find the latest subscription remarks for the member and auto-calculates their Subscription Upto date.
- **CRITICAL:** If the Individual Ledger shows wrong totals, the bug is in the **Cash Book** entries (wrong Reg No, wrong code, wrong Account Head spelling) — NOT in the Individual Ledger grid.

## 5. Subscription Upto Date — Automatic Sync (Updated Aug 2026)
- The app now automatically scans the Cash Book for each member's latest receipt with code `RP-3.82` or `RP-3.83` and extracts the validity date from the **Remarks** column (e.g., "Apr 25 to Sept 26" displays as `09/2026`).
- If a member has NO subscription receipts in the Cash Book, the app displays `-`.
- The old bug where a blank `D` column showed `03/2027` by default has been permanently fixed by correcting the check from `colValues["F"]` to `colValues["E"]` in `getCleanSubUptoLive()`.

## 6. Deployment Architecture
The app is deployed to multiple targets. All targets must be kept in sync using the deploy script at `scratch/deploy_cashbook_brain.py`:
- **Offline (local):** `index_supabase.html` + `app_supabase.js` in the project root.
- **Online cPanel:** Files in `deployment_files/cpanel/` — manually upload via cPanel File Manager.
- **Online GitHub Pages:** Files in `deployment_files/github-supabase/` — push to `church-app` remote. Live at `https://sajubeml.github.io/church-app/` (username is `sajubeml`, NOT `sajubeiml`).
- **Android APK:** Source at `android-app/app/src/main/assets/app.js`. Build using `.\gradlew.bat assembleFullRelease` from inside the `android-app/` folder. The `full` flavor is the offline standalone version. The `fresh` flavor is the fresh-start version.
- **Built APK output:** `android-app\app\build\outputs\apk\full\release\app-full-release.apk` — copy to project root and rename as `St_Gregorios_Church_Accounting_v9.9.apk`.

## 7. GitHub Remote Configuration
The local repository has TWO remotes:
- `origin` → `https://github.com/sajubeml/Church_account.git` (main codebase backup)
- `church-app` → `https://github.com/sajubeml/church-app.git` (GitHub Pages live site)
- Always push to BOTH: `git push origin main` AND `git push church-app main`.
