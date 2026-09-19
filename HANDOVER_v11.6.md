# Handover Document - St. Gregorios Church Accounting App (v11.6)

**Date:** September 19, 2026  
**Version:** v11.6 (`versionCode 70`)  
**Targets Deployed:** 
- Online GitHub Pages (`https://sajubeml.github.io/church-app/`)
- Online cPanel Server (`/home/orthodox/public_html/accounting`)
- Offline Desktop Executable (`St_Gregorios_Church_Accounting.exe`)
- Standalone Android Release APK (`St_Gregorios_Church_Accounting_v11.6.apk`)
- Fresh Start Android Release APK (`St_Gregorios_Church_Accounting_Fresh_v11.6.apk`)

---

## 🚀 Key Improvements & Feature Additions in v11.6

### 1. Member Contact Directory — "Amount Promised" Column Integration
- Added a dedicated **Amount Promised** column placed immediately after **Name of HoF** in the Member Contact Directory grid:
  - Table Header Order: `Reg No` | `Name of HoF` | `Amount Promised` | `Mobile` | `Address` | `Actions`
- Added the **Amount Promised (₹)** input field inside both **Add New Member** and **Edit Member** modals.
- **Data Mapping:** Stored safely in **Column `F`** of `state.members`. This ensures `state.individual` (used strictly for financial ledger identity matching) is left 100% untouched.
- **Formatting:** Values automatically format with Indian currency notation (e.g. `₹ 25,000`), or display `-` if left blank.

### 2. Layout Width Spacing Optimization
- Reduced wide empty side padding on desktop screens by constraining the directory card container to `max-width: 1250px; margin: 0 auto;`.
- Enabled clean horizontal scrolling (`overflow-x: auto`) for mobile viewports.

### 3. CSV Import & Export Capabilities
- `exportMemberDirectoryCSV()` exports `"Register No.","Name","Amount Promised","Mobile","Address"`.
- `importMemberDirectoryCSV()` dynamically matches column headers containing `"promise"`, `"pledge"`, or `"amount"`, automatically updating or creating member records with Column `F`.

---

## 📌 Architecture & Column Mapping Reference

| Member Array (`state.members`) | Field Name | Description |
|---|---|---|
| **Column A** | `Sl No` | Serial Number |
| **Column B** | `Register No.` | Register Number (Used for 2-Way Sync) |
| **Column C** | `Name of HoF` | Head of Family / Member Name |
| **Column D** | `Mobile / Phone` | Contact Phone Number |
| **Column E** | `Address` | Resident Address |
| **Column F** | `Amount Promised` | Promised / Pledged Subscription Amount |

---

## 🛠️ Build & Deployment Instructions

1. **Rebuilding Data & Bundles**:
   ```cmd
   py build_data_js.py
   py build_fresh_start_data.py
   ```

2. **Full Automated Twin Release Compile**:
   ```cmd
   py build_all_releases.py
   ```

3. **cPanel Deployment**:
   ```cmd
   py prepare_deployments.py
   ```
   Upload `index.html` (or `index_supabase.html` renamed to `index.html`) and `app_supabase.js` to `/public_html/accounting`.

4. **GitHub Deployment**:
   ```cmd
   git add .
   git commit -m "v11.6: Add Amount Promised column to Member Directory"
   git push origin main
   git push church-app main
   ```

---

## ✅ Verification & Status
- **Financial Ledger & Cash Book Integrity:** 100% preserved. No existing calculation, subscription date algorithm, or trial balance module was altered.
- **GitHub Pages:** Verified live at `https://sajubeml.github.io/church-app/`.
- **cPanel Production Site:** Uploaded and verified live at `https://orthodoxchurchmysore.in/accounting/`.
- **Android APKs:** Built successfully (`v11.6`, `versionCode 70`).
