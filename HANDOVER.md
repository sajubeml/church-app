# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document — Current Version: v11.23

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.23** (Android `versionCode 86` / Web / Cloud / Offline PC)  
**Date of Release:** November 03, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.23) — Individual Account Heading Date Customization & Unified Print Alignment

### A. Dynamic Heading Configuration for Individual Member Accounts
1. **Report Heading Dropdown (`cmbIndivHeadingMode`):**
   - Added to the Individual Member Ledgers toolbar with 5 flexible modes:
     - `Period: 01-04-2026 to Month End` *(Default)*: `Individual Account for the Period 01-04-2026 to 30-11-2026`
     - `Period: 01-04-2026 to Today`: `Individual Account for the Period 01-04-2026 to [Current Date]`
     - `Updated Upto Month End`: `Individual Account updated upto 30-11-2026` *(previous format)*
     - `Updated Upto Today`: `Individual Account updated upto [Current Date]`
     - `Custom Date Range...`: Reveals inline `From` and `To` date pickers for custom date generation.
2. **Real-Time Header Preview:**
   - Embedded directly below the tab title:
     `All Parish Member Contributions & Grand Totals | Individual Account for the Period 01-04-2026 to 30-11-2026`
   - Dynamically updates upon changing dropdown selection or date inputs.
   - User preference persists in `localStorage` under `CHURCH_INDIV_HEADING_MODE`.
3. **Synchronized PDF & Excel Exports:**
   - **PDF Print / Export:** Prepend block inside `<thead>` embeds the dynamically chosen heading on every repeated page.
   - **Excel Export:** Row 3 of the `.xlsx` spreadsheet embeds the exact chosen heading text.

---

### B. Print Engine Alignment & Output Preservation
1. **Strict 2-Page Landscape Output:**
   - Unified `@page { size: A4 landscape; margin: 4mm 5mm; }` with `zoom: 0.62` across all targets.
2. **Preserved High-Fidelity Table Styling:**
   - **Subscription Columns Highlight:** Golden background `#fff2cc !important;` preserved on columns 4 through 10 (*Subscription Upto, Subscription, Donation General, Catholicate Day, Metropolitan Fund, Mission Sunday, Seminary Day*).
   - **Cell Borders:** Dotted borders `1px dotted #888 !important;` across all table data cells.
   - **Grand Total Row:** Highlighted `#e2e8f0` background with bold text and solid top/bottom borders.
3. **Zero Accounting Code Disruption:**
   - 100% preservation of `state.cashbook` single source of truth, dynamic `cbAgg` mapping, sorting algorithms, and member contact directory.

---

## 2. Updated Deliverables in v11.23

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.23.apk` | `app.js?v=11.23`, `data.js`, `logo_data.js?v=11.23` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.23.apk` | `app.js?v=11.23`, `data_fresh.js` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.23` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.23`, `logo_data.js?v=11.23` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.23`, `logo_data.js?v=11.23` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **cPanel Update ZIP** | `cpanel_update_v11.23.zip` | Bundled cPanel web assets | Supabase Cloud PostgreSQL | Extract directly into `public_html/accounting/` |
| **Offline Portable ZIP** | `St_Gregorios_Church_Accounting_Offline_PC_v11.23.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Verification & Safety Checks
- [x] Heading dropdown allows switching between Generation Date Range, Updated Upto Date, and Custom Date Range.
- [x] Live preview accurately reflects current heading selection.
- [x] PDF export Line 3 header displays the dynamic heading and matches previous 2-page landscape styling with `#fff2cc` column highlights and dotted borders.
- [x] Excel export (.xlsx) includes the dynamic heading in Row 3.
- [x] Android `versionCode 86` / `versionName 11.23` aligned across build configurations.
