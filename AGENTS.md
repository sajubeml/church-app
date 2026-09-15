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

## 5. Subscription Upto Date — Automatic Sync (Updated Sep 2026)
- The app scans the Cash Book for all subscription receipts (`RP-3.82` and `RP-3.83`) plus initial `rawSubUpto` (Col D) for each member.
- Extracts all validity periods across full 3-part dates (`DD-MM-YYYY`, `YYYY-MM-DD`), hyphenated or spaced month names (e.g. `oct-25`, `march-26`, `apr 26 to june 26`), and 2-part dates (`MM/YYYY`).
- Always computes and displays the absolute MAXIMUM (latest) paid month and year (e.g., `10/2026`).
- Fixes the bug where 3-part dates like `01-10-2026` were mistakenly parsed as `01/2010`.
- If a member has NO subscription receipts or validity dates, the app displays `-`. NM non-members always display `-`.


## 6. Deployment Architecture
The app is deployed to multiple targets:
- **Offline (local):** `index_supabase.html` + `app_supabase.js` in the project root.
- **Online cPanel:** Files in `deployment_files/cpanel/` — manually upload via cPanel File Manager.
- **Online GitHub Pages:** Files in `deployment_files/github-supabase/` — push to `church-app` remote. Live at `https://sajubeml.github.io/church-app/` (username is `sajubeml`, NOT `sajubeiml`).
- **Android APK:** 
  - Assets are populated using `py copy_assets_to_android.py full` (or `fresh`), which copies `index_offline.html` -> `index.html`, `data.js`, and `app.js`. **Never** package `index_supabase.html` into Android assets.
  - Build APKs using `.\gradlew.bat assembleFullRelease assembleFreshRelease` from inside the `android-app/` folder.
  - The `full` flavor is the offline standalone version. The `fresh` flavor is the fresh-start version.
  - **Built APK output:** `android-app\app\build\outputs\apk\full\release\app-full-release.apk` — copied to project root as `St_Gregorios_Church_Accounting_v10.0.apk`, `St_Gregorios_Church_Accounting_v9.9.apk`, and `St_Gregorios_Church_Accounting.apk`.

## 7. Android APK Data Management & Backup Restore
- **Admin Backup Import:** In the standalone Android APK, the in-app **Administration** panel (`tabAdmin`) allows restoring/patching the latest monolithic JSON backup file (`St_Gregorios_Church_Backup_YYYY-MM-DD.json`).
- Importing a backup writes directly to the WebView `localStorage` and memory `state`, instantly restoring all members, dropdown options, voucher sequences, and cashbook history.

## 8. GitHub Remote Configuration
The local repository has TWO remotes:
- `origin` → `https://github.com/sajubeml/Church_account.git` (main codebase backup)
- `church-app` → `https://github.com/sajubeml/church-app.git` (GitHub Pages live site)
- Always push to BOTH: `git push origin main` AND `git push church-app main`.

## 9. Print Engine & HTML Script Parsing Rules (Updated Sep 2026)
- **Nested Script Escaping:** When generating dynamic HTML windows inside string literals (e.g. `printWin.document.write(...)`), NEVER write unescaped literal `</script>` tags or inner backticks (`` ` ``). In HTML specifications, ANY literal `</script>` string inside a JS file immediately terminates the outer script tag. Always escape closing script tags inside JS string literals as `<\/script>`.
- **A5 Portrait Dimensions (Zero Spillover):** Set `@page { size: A5 portrait; margin: 6mm; }` with receipt card `height: 172mm !important;`, `padding: 4mm 6mm !important;`, and `margin: 0 !important;`. This leaves ~17mm physical margin cushion for laser printer hardware unprintable boundaries (e.g. Canon LBP2900 / HP LaserJet), guaranteeing Page 1 (ORIGINAL) and Page 2 (OFFICE COPY) fit strictly across 2 sheets of paper without spilling over onto 3 or 4 pages.
- **Trailing Page Break Avoidance:** Always ensure `.receipt-card:last-child` has `page-break-after: avoid !important;` and `break-after: avoid !important;`. Never leave conflicting landscape `@page` declarations in `styles.css`.

## 10. Print Engine Modal Bleed Isolation (Updated Sep 2026)
- **Strict Modal Suppression in Print CSS:** When native Android print (`window.AndroidBridge.printPage()`) or browser `window.print()` triggers, the WebView captures the active DOM. All backdrops (`.modal-backdrop`, `#memberCrudModal`, `#passwordModal`, `#editMemberModal`, `#editCashbookModal`, `#addMemberModal`, `#addAccountHeadModal`, `#trialActivationModal`) must be strictly set to `display: none !important;` in `@media print`. Only `#receiptModal.active` should be permitted to display, preventing empty/unrelated modal forms from bleeding across 3-4 printed pages.

## 11. Cashbook Mobile Responsiveness & Android SQLite Sync (Updated Sep 2026)
- **Cashbook Table Layout:** Never use `table-layout: fixed; width: 100%;` with proportional percentages for `#cashbookTable`. On mobile devices (360px–420px width), 16 accounting columns will crush to 15px–25px, breaking words vertically letter-by-letter. Always use `table-layout: auto; width: max-content; min-width: 100%;` with individual column minimum widths (`min-width: 40px` to `200px`) inside `.table-container { overflow-x: auto; }` for smooth horizontal panning.
## 13. Mandatory Automatic Version Bumping Rule (Updated Sep 2026)
- **EVERY single update, patch, fix, or build release MUST increment the version string and versionCode** across the entire project before building (e.g., `v11.3` -> `v11.4`, `versionCode 67` -> `versionCode 68`).
- Update version in:
  1. `android-app/app/build.gradle.kts` (`versionCode = XX`, `versionName = "11.X"`)
  2. `build_all_releases.py` (`full_apk_v11`, `fresh_apk_v11`)
  3. `index_supabase.html` (`app_supabase.js?v=11.X`)
  4. `index_offline.html` (`app.js?v=11.X`)
  5. `HANDOVER.md` and `HANDOVER_v11.X.md`

## 14. Sequential Twin Asset Copy & APK Build Pipeline (Updated Sep 2026)
- **Environment Variables**:
  - `JAVA_HOME` = `C:\Users\sajub\AppData\Local\JDK17\jdk-17.0.10+7`
  - `ANDROID_HOME` = `C:\Users\sajub\AppData\Local\Android\Sdk`
- **Package Name Alignment (CRITICAL)**:
  - `namespace` and `applicationId` in `build.gradle.kts` MUST be `com.stgregorios.churchaccounting`.
  - `AndroidManifest.xml` activity MUST be `android:name="com.stgregorios.churchaccounting.MainActivity"`. Never use relative `.MainActivity` with a different namespace, or Android will throw `ClassNotFoundException` and auto-close the app on tap.
- **Build Sequence**:
  - Always run `py build_all_releases.py` or the sequential steps:
    1. `py build_data_js.py` & `py build_fresh_start_data.py`
    2. `py build_executable.py` (Desktop .exe)
    3. `py copy_assets_to_android.py full` ➔ `.\gradlew.bat assembleFullRelease`
    4. `py copy_assets_to_android.py fresh` ➔ `.\gradlew.bat assembleFreshRelease`
  - **CRITICAL:** NEVER combine `assembleFullRelease` and `assembleFreshRelease` into a single Gradle invocation without executing `copy_assets_to_android.py fresh` in between, or the `fresh` release will get contaminated with `full` data.

## 15. Fresh Start Build User Data Flag (`CHURCH_FRESH_START_HAS_USER_DATA`)
- In `data_fresh.js`, `window.isFreshStartBuild = true`.
- On initial launch, `loadAllData()` purges native SQLite (`window.AndroidBridge.bulkSync("[]")`) and resets `localStorage` to start with 0 transactions and ₹ 0.00 balances.
- Whenever a user restores a JSON backup (`processBackupRestoreData`) or creates a transaction (`showReceiptModal`), the app sets `localStorage.setItem("CHURCH_FRESH_START_HAS_USER_DATA", "true")`.
- This ensures `loadAllData()` permanently retains all imported/entered records across app restarts without wiping them.


