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

## 1. Release Highlights (v11.27) — Dynamic Receipt Density Auto-Scaling (A5 Single-Sheet Fit)

### A. Problem Resolved: Multi-Item Receipts Spilling Over Onto 3–4 Sheets
- In receipts with many items (e.g., 9–12+ items like subscription arrears, feast contributions, funds, and harvest collections), fixed font sizes (11px–12.5px), fixed table paddings (4px–6px), and fixed header logo/signature heights caused the total vertical content to exceed 220mm.
- Because A5 paper height is 210mm (with printable height of ~198mm after margins), the receipt card contents overflowed past the bottom border.
- The printer pushed overflowing items (e.g., items 11, 12, Total bar, and Signature) onto Page 2, and the Office Copy onto Pages 2 and 3 ("Total: 3 sheets of paper").

### B. v11.27 Solution: Dynamic Content Density Engine (`getReceiptDensitySettings`)
- Implemented a smart density calculator in `app_supabase.js` and `app.js` that evaluates the number of cart items and secondary subtitle details (`effectiveCount`):
  1. **Normal Density (1–5 items):** Standard spacious layout (Logo 38px, font 11px–12.5px, table cell padding 4px 6px).
  2. **Medium Density (6–8 items):** Compact layout (Logo 30px, font 10px–11.5px, table cell padding 2.5px 5px).
  3. **Compact Density (9–13 items):** High-density layout tailored for 10–13 items (Logo 24px, font 8.5px–10.5px, table cell padding 2px 4px, signature 20px). Fits all 12 items, subtitles, totals, and signatures cleanly inside 155mm, leaving 17mm cushion inside the 172mm card.
  4. **Ultra Density (14+ items):** Ultra-compact layout (Logo 20px, font 8px–9.5px, table cell padding 1.2px 3px) fitting up to 18 items without page breaks.
- Added matching CSS classes (`.dense-medium`, `.dense-compact`, `.dense-ultra`) with `overflow: hidden !important;` in `styles.css` and the print popup styles to strictly eliminate border bleeding.
- Applied symmetrically across both **New Voucher / Receipt generation** (`showReceiptModal`) and **Historical Cash Book Reprints** (`reprintVoucher`).
- **Guaranteed Result:** Page 1 = ORIGINAL strictly on 1 A5 sheet; Page 2 = COPY strictly on 1 A5 sheet. Total print is strictly **2 sheets of paper** with zero trailing spillover.

---

## 2. Updated Deliverables in v11.27

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
| :--- | :--- | :--- | :--- | :--- |
| **Online (GitHub Pages)** | Repository root & `deployment_files/github-supabase/` | `index.html`, `app_supabase.js?v=11.27`, `styles.css` | Supabase Cloud Database (`cashbook` table) | `git push origin main` and `git push church-app main` |
| **Online (cPanel)** | `deployment_files/cpanel/` & `cpanel_update_v11.27.zip` | `index.html`, `app_supabase.js?v=11.27`, `styles.css` | Supabase Cloud Database | Upload `cpanel_update_v11.27.zip` to cPanel File Manager & extract |
| **Offline PC** | `index_offline.html` | `app.js?v=11.27`, `data.js` | LocalStorage + SQLite bridge | Open in browser or local Python server |
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.27.apk` | Standalone Offline Build (`versionCode 90`) | Embedded SQLite + LocalStorage | `py build_all_releases.py` |
| **Android APK (Fresh)** | `St_Gregorios_Church_Accounting_Fresh_v11.27.apk` | Fresh Start Build (`versionCode 90`) | Clean Slate SQLite | `py build_all_releases.py` |

---

## 3. Fallback Instructions
If you ever need to revert to v11.26:
```bash
git checkout v11.26
```
Or to return to this release:
```bash
git checkout main
```

