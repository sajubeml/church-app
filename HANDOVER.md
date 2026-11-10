# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document — Current Version: v11.26

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.26** (Android `versionCode 89` / Web / Cloud / Offline PC)  
**Date of Release:** November 10, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  
**Fallback Git Tag:** `v11.25` (Allows 100% instant restoration if needed: `git checkout v11.25`)  

---

## 1. Release Highlights (v11.26) — Persistent Session Architecture & Silent Auto-Refresh

### A. Root Cause of Inactivity Logouts Eliminated
- **Problem Resolved:** Previously, `window.SUPABASE_ACCESS_TOKEN` was stored purely in volatile in-memory JavaScript variables. When mobile browsers (Chrome, Samsung Internet) or desktop browsers put idle tabs to sleep or discarded them to save RAM (which commonly happens after 5 to 15 minutes of inactivity), switching back to the tab reloaded the page from scratch. Because the in-memory variable was reset to `null`, the app showed the `#login-overlay` modal and forced the user to manually re-enter their credentials. Furthermore, Supabase access tokens naturally expire after 60 minutes with no refresh mechanism.
- **v11.26 Solution:**
  1. **Persistent Session Storage:** Secure session tokens (`access_token`, `refresh_token`, and calculated expiry timestamp `expires_at`) are saved to `localStorage.setItem('CHURCH_SUPABASE_SESSION', ...)`.
  2. **Zero-Flicker Instant Startup:** An inline script right at `<div id="login-overlay">` checks for an existing session and immediately suppresses the login card before initial paint, preventing any visible flash of the login screen.
  3. **Silent Background Token Refresh (`window.refreshSupabaseToken`):** Connects to `${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token`. Whenever the access token approaches expiration, it is refreshed silently in the background without interrupting the user.
  4. **Proactive Keep-Alive & Wakeup Listeners:** A 10-minute interval timer, along with `visibilitychange` and `focus` event listeners, monitors session freshness and silently updates tokens whenever the user returns to an inactive tab or unlocks their phone.
  5. **Transparent 401 Auto-Recovery:** All Supabase REST and Storage requests route through `fetchWithAuth()`. If Supabase ever returns HTTP 401 Unauthorized, the app silently refreshes the token and transparently retries the request once.

### B. Explicit Red "🚪 Logout" Button
- Added a dedicated, highly visible `🚪 Logout` button next to `🔄 Sync Cloud` in the top navigation bar.
- Clicking the button prompts the user for confirmation, clears the stored session tokens from `localStorage`, resets memory variables, and presents the Secure Gateway login card with the last-used email address conveniently pre-filled.

### C. In-Place Cloud Sync Without Page Reload
- The "🔄 Sync Cloud" button updates data in-place without triggering full page reloads or session disconnections, keeping the current document and entry forms intact.
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
