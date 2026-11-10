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

---

## 2. Updated Deliverables in v11.26

| Target Platform | Location / Artifact | Core Code / Asset | Data Source / Connectivity | Deployment Command / Action |
| :--- | :--- | :--- | :--- | :--- |
| **Online (GitHub Pages)** | Repository root & `deployment_files/github-supabase/` | `index.html`, `app_supabase.js?v=11.26`, `styles.css` | Supabase Cloud Database (`cashbook` table) | `git push origin main` and `git push church-app main` |
| **Online (cPanel)** | `deployment_files/cpanel/` & `cpanel_update_v11.26.zip` | `index.html`, `app_supabase.js?v=11.26`, `styles.css` | Supabase Cloud Database | Upload `cpanel_update_v11.26.zip` to cPanel File Manager & extract |
| **Offline PC** | `index_offline.html` | `app.js?v=11.26`, `data.js` | LocalStorage + SQLite bridge | Open in browser or local Python server |
| **Android APK (Full)** | `St_Gregorios_Church_Accounting_v11.26.apk` | Standalone Offline Build (`versionCode 89`) | Embedded SQLite + LocalStorage | `py build_all_releases.py` |
| **Android APK (Fresh)** | `St_Gregorios_Church_Accounting_Fresh_v11.26.apk` | Fresh Start Build (`versionCode 89`) | Clean Slate SQLite | `py build_all_releases.py` |

---

## 3. Fallback Instructions
If you ever need to revert to v11.25:
```bash
git checkout v11.25
```
Or to return to this release:
```bash
git checkout main
```

