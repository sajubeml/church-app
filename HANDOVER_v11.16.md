# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Document — Version 11.16

**Church:** St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru  
**Workspace Root:** `C:\CASHBOOK_APP`  
**Current Active Version:** **v11.16** (Android `versionCode 79` / Web / Cloud / Offline PC)  
**Date of Release:** October 17, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Site)  
**Live GitHub Pages Site:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  

---

## 1. Release Highlights (v11.16)

### A. Digital Signature Integration into Receipts and Payment Vouchers
- **Background:** The church requested adding the official handwritten signature directly into receipts without affecting any other calculation, layout, or print features.
- **Image Processing & Asset Preparation:**
  - The uploaded signature was processed to extract the handwritten ink strokes while eliminating paper background noise, shadows, and dust flecks.
  - Converted to a clean, crisp 480x281 transparent PNG (`signature.png`, ~43 KB).
  - Synchronously embedded as a Base64 data URI (`window.CHURCH_SIGNATURE_BASE64`) into `logo_data.js` (~57 KB).
- **Zero Spillover & Strict A5 Preservation:**
  - Formatted inside the signatory block above `Vicar / Trustee` with `height: 34px; max-width: 120px; object-fit: contain;`.
  - The existing `<div style="flex: 1;"></div>` absorbing spacer seamlessly adjusts, preserving the exact `172mm` card height and zero-spillover constraint for standard laser printers (Canon LBP2900 / HP LaserJet).
- **Multi-Target Offline & Online Support:**
  - Embedded base64 prevents any `Tainted canvases may not be exported SecurityError` when `html2pdf.js` generates PDFs offline in file:// contexts (Desktop .exe or Android WebView).
  - Bundled into Android assets (`android-app/app/src/main/assets/signature.png`), distribution zips (`create_offline_zip.py`, `package_distributable.py`), and all cloud deployment targets (`prepare_deployments.py`).

---

## 2. Updated Deliverables in v11.16

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
|---|---|---|---|---|
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.16.apk` | `app.js?v=11.16`, `signature.png`, `logo_data.js?v=11.16` | Standalone SQLite & LocalStorage | Install APK onto Android phones / tablets |
| **Android APK (Fresh Start)** | `St_Gregorios_Church_Accounting_Fresh_v11.16.apk` | `app.js?v=11.16`, `signature.png`, `logo_data.js?v=11.16` | Fresh dataset with 7-day trial mode | Install fresh-start APK for blank ledger testing |
| **Windows Desktop Launcher** | `St_Gregorios_Church_Accounting.exe` | `index_offline.html`, `app.js?v=11.16`, `signature.png` | Local JSON files in `data_export/` | Double-click .exe to launch local Edge app window |
| **GitHub Pages** | `deployment_files/github-supabase/` | `app_supabase.js?v=11.16`, `signature.png`, `logo_data.js?v=11.16` | Supabase Cloud PostgreSQL | `git push church-app main` |
| **cPanel Production** | `deployment_files/cpanel/` | `app_supabase.js?v=11.16`, `signature.png`, `logo_data.js?v=11.16` | Supabase Cloud PostgreSQL | Upload via cPanel File Manager to `public_html/accounting/` |
| **Offline Portable ZIP** | `dist/St_Gregorios_Church_Accounting_Offline_Package.zip` | Bundled standalone distribution suite | Embedded JSON | Unzip and run on offline PC |

---

## 3. Verification & Safety Checks
- **No Function Disruption:** All cashbook calculations, multi-split items, voucher sequences, ledger balances, trial balance sums, and subscription upto computations remain 100% untouched.
- **Self-Contained Saved Receipts:** Auto-saved HTML files in `Receipts/` contain the signature and church logo embedded inline as base64, guaranteeing that archived receipts view and print with high fidelity anywhere without external network dependencies.
