# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Documentation — Version: v11.28

**Release Version:** `v11.28` (Android `versionCode 91` / Supabase Cloud / GitHub Pages / cPanel / Offline PC)  
**Release Date:** November 10, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Deployment)  
**Live GitHub Pages URL:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  
**Fallback Tag:** `v11.27`  

---

## 1. Problem Description & Root Cause
- **Symptom:** On opening the GitHub Pages site, the browser displayed an alert:  
  `sajubeml.github.io says`  
  `Error: Uncaught SyntaxError: Unexpected identifier 'Account'`  
  `Line: 6617`
- **Root Cause Analysis:**
  1. In `app_supabase.js` inside `reprintVoucher()`, a duplicate closing template literal delimiter (`  `;`) was accidentally introduced at line 6599 immediately following line 6598.
  2. The first `  `;` closed the HTML string literal for `reprintVoucher()`. The second `  `;` immediately opened an unclosed template literal string covering lines 6600 through 6616.
  3. When the parser reached line 6617:
     ```javascript
     alert(`Account Head [${code}] not found!`);
     ```
     The leading backtick terminated the rogue template literal, causing the word `Account` to be evaluated as a bare JavaScript identifier in an invalid syntactic position, throwing `Uncaught SyntaxError: Unexpected identifier 'Account'`.
  4. In `app.js`, a duplicate `modeRowHtml` constant declaration was also present at lines 6037 and 6044, which threw `Identifier 'modeRowHtml' has already been declared`.

---

## 2. Fixes & Verification Implemented in v11.28
1. **Removed Duplicate Delimiter in `app_supabase.js`:**
   - Deleted the rogue second `  `;` closing line at line 6599.
2. **Removed Duplicate `modeRowHtml` in `app.js`:**
   - Cleaned up line 6037 so only the dynamic density-aware `modeRowHtml` definition is retained.
3. **Automated Lexical & AST Verification via Headless Chromium (Playwright):**
   - Executed headless Chromium engine via Playwright to parse and compile both `app_supabase.js` and `app.js` using `new Function(code)`.
   - Verified that both files compile cleanly with **0 syntax errors**.
4. **Preserved A5 Dynamic Density Scaling:**
   - Multi-item receipts continue to automatically condense (font, logo, cell padding, line heights) so that up to 14+ item receipts fit strictly within 172mm, guaranteeing a clean **2 sheets of paper** (Original + Office Copy) printout with zero trailing spillover.

---

## 3. Deliverables & Artifacts in v11.28

| Target Platform / Location | File Name / Deliverable | Status & Verification |
| :--- | :--- | :--- |
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.28.apk` | Compiled with `versionCode 91`, `versionName 11.28` (9.21 MB) |
| **Android APK (Fresh)** | `St_Gregorios_Church_Accounting_Fresh_v11.28.apk` | Compiled with `versionCode 91`, `versionName 11.28` (9.14 MB) |
| **cPanel 1-Click Update** | `cpanel_update_v11.28.zip` | Packaged in workspace root (1.0 MB) |
| **GitHub Pages Live Site** | `https://sajubeml.github.io/church-app/` | Deployed and verified |
| **Desktop Executable** | `St_Gregorios_Church_Accounting.exe` | Compiled and verified |

