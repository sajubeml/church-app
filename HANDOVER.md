# St. Gregorios Orthodox Syrian Church Accounting Portal
## Master Handover Document — Current Version: v11.27

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.27** (Android `versionCode 90` / Web / Cloud / Offline PC)  
**Date of Release:** November 10, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  
**Fallback Git Tag:** `v11.26` (Allows 100% instant restoration if needed: `git checkout v11.26`)  

---

## 1. Release Highlights (v11.27) — Dynamic Multi-Item Receipt Density Auto-Scaling for A5 Paper Printing

### A. Perfect Fit on A5 Paper (Strictly 2 Sheets: Original + Copy)
- **Problem Resolved:** In receipts with numerous line items (e.g., 9–13+ particulars like Receipt #4576 which had 12 items plus subtitle details), the total content height exceeded 215mm. Since A5 paper height is 210mm (with 198mm printable area between 6mm margins), the receipt card spilled over onto a 2nd page per copy, turning a 2-page printout (Original + Copy) into a messy 3 or 4 sheets of paper (as seen in user report `media_1794303545961_9b2c3128.jpg`).
- **v11.27 Solution:**
  1. **Dynamic Receipt Density Engine (`getReceiptDensitySettings(items)`):** Automatically analyzes the count of line items and subtitle remarks (calculating an `effectiveCount`).
  2. **Tiered Scaling:**
     - **Normal (<= 5.5 items):** Standard spacious typography (logo 38px, font 11px–12.5px, table padding 4px 6px).
     - **Medium (5.6 – 8.5 items):** Logo 30px, font 10px–11.5px, table padding 2.5px 5px.
     - **Compact (8.6 – 13.5 items, e.g. 12-item Receipt #4576):** Logo 24px, font 8.5px–10px, line height 1.2, table padding 2px 4px, signature line 20px. Content fits cleanly within ~150mm inside the 172mm card box.
     - **Ultra (14+ items):** Logo 20px, font 8px–9px, table padding 1.2px 3px.
  3. **Universal Card Boundary Enforcement:** Receipt cards have `overflow: hidden !important;`, `box-sizing: border-box !important;`, `height: 172mm !important;`, and `break-inside: avoid !important;`.
  4. **Applied Everywhere:** Fully integrated into both initial receipt creation (`showReceiptModal()`), Cash Book reprints (`reprintVoucher()`), and dynamic print popup styling (`printReceiptModal()`).

---

## 2. Release Highlights (v11.26) — Persistent Session Architecture & Silent Auto-Refresh

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
