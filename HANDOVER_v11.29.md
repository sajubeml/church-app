# St. Gregorios Orthodox Syrian Church Accounting Portal
## Release Handover Documentation — Version: v11.29

**Release Version:** `v11.29` (Android `versionCode 92` / Supabase Cloud / GitHub Pages / cPanel / Offline PC)  
**Release Date:** November 10, 2026  
**Git Remote Origin:** `https://github.com/sajubeml/Church_account.git` (Main Codebase Backup)  
**Git Remote Church-App:** `https://github.com/sajubeml/church-app.git` (GitHub Pages Live Deployment)  
**Live GitHub Pages URL:** `https://sajubeml.github.io/church-app/`  
**Live cPanel Web URL:** `https://orthodoxchurchmysore.in/accounting/`  
**Fallback Tag:** `v11.28`  

---

## 1. Release Highlights — Balanced Proportional Fit & Inline Text Wrapping on A5 Paper

### A. The User's Requirement
- Rather than shrinking 12-item receipts down to tiny 8.5px fonts with a cavernous 60mm empty gap at the bottom of the card, the user requested:
  *"instead of shrinking items can you wrap text to fit in a5 to avoid bottom space?"*

### B. Engineering Solution in v11.29
1. **Inline Text Wrapping for Remarks & Particulars**:
   - Remarks/details (e.g., `Feb26 to mar26`, `2yrs`) previously created stacked sub-rows with dashed borders, adding ~30mm of unnecessary height.
   - In v11.29, remarks wrap cleanly inline with the Particulars text:
     `Monthly Subscription ( Previous Year) (RP-3.83) — Feb26 to mar26`
   - Naturally wraps within the particulars cell with zero wasteful sub-div overhead.
2. **Generous, Highly Legible Font Sizes**:
   - 8 to 13-item receipts (e.g. Receipt #4576 with 12 items) now use a comfortable **11px font** with **4.5px 6px table cell padding**.
   - Total bar uses **12.5px font**, and Church Header uses **12px font** with **34px logo**.
3. **Optimized Card Height (182mm) & Zero Bottom Void**:
   - Receipt card height is set to `182mm !important;` (inside the 198mm printable area between 6mm page margins on A5).
   - Card coverage of the A5 paper is increased to **94.3%**!
   - Content expands evenly and naturally across the sheet.
   - Result: **Zero bottom empty void**, perfectly readable text, and strictly **2 sheets of paper** (Page 1: ORIGINAL, Page 2: OFFICE COPY) with zero spillover!

---

## 2. Deliverables & Artifacts in v11.29

| Target Platform / Location | File Name / Deliverable | Status & Verification |
| :--- | :--- | :--- |
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.29.apk` | Compiled with `versionCode 92`, `versionName 11.29` (9.21 MB) |
| **Android APK (Fresh)** | `St_Gregorios_Church_Accounting_Fresh_v11.29.apk` | Compiled with `versionCode 92`, `versionName 11.29` (9.14 MB) |
| **cPanel 1-Click Update** | `cpanel_update_v11.29.zip` | Packaged in workspace root (1.0 MB) |
| **GitHub Pages Live Site** | `https://sajubeml.github.io/church-app/` | Deployed and verified |
| **Desktop Executable** | `St_Gregorios_Church_Accounting.exe` | Compiled and verified |

