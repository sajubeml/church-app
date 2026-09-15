# St. Gregorios Church Accounting Portal - System Architecture (v9.2)

This document outlines the current state of the St. Gregorios Church Accounting application architecture, detailing its evolution from a local python server to a fully serverless cloud-hosted application.

## 1. Overview

The application has successfully migrated from a local Python-based backend using SQLite to a modern, serverless architecture.
- **Frontend Hosting**: GitHub Pages (`https://sajubeml.github.io/church-app/`)
- **Backend Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (JWT)

This architecture ensures the application is highly available, accessible from both mobile and desktop browsers over the internet, and completely secure from unauthorized access.

## 2. Security & Authentication (RLS)

To transition from an open web application to a secure portal, we implemented military-grade database security:

### Supabase Row Level Security (RLS)
- RLS was enabled on the `cashbook` and `app_state` tables.
- **Policies**: We created `SELECT`, `INSERT`, `UPDATE`, and `DELETE` policies for both tables.
- **Target Role**: All policies are restricted to the `authenticated` role. This means that anonymous (unauthenticated) web requests attempting to read or write data will be instantly rejected by the Supabase server with a `401 Unauthorized` or return empty data.

### Frontend Authentication Flow (`attemptLogin`)
1. **Login Overlay**: A glassmorphism-style secure login overlay blocks access to the application UI until the user authenticates.
2. **Credential Verification**: When the user enters their email and password, the app makes an API call to `${SUPABASE_URL}/auth/v1/token?grant_type=password`.
3. **Token Injection**: If successful, Supabase returns an `access_token` (a secure JSON Web Token). We store this in memory (`window.SUPABASE_ACCESS_TOKEN`).
4. **Data Hydration**: The app hides the login screen and instantly fetches the secured data from the cloud using the newly acquired token.

## 3. The Interceptor Architecture

A core design decision in v9.2 was to avoid completely rewriting the thousands of lines of frontend application logic (`app_cloud_final.js`) which originally expected a local `api.php` or Python backend. 

Instead, we built a **Fetch Interceptor** in `app_supabase.js`:

```javascript
const originalFetch = window.fetch;
window.fetch = async function(url, options) {
  // If the legacy app code tries to call the old local API
  if (url && typeof url === 'string' && url.includes('api.php')) {
      const body = JSON.parse(options.body);
      
      // We catch the request, and route it to Supabase instead!
      if (body.action === 'get_app_state') {
          return await originalFetch(`${SUPABASE_URL}/rest/v1/app_state...`, {
              headers: {
                  // We inject the secure Auth token here!
                  'Authorization': window.SUPABASE_ACCESS_TOKEN 
                                   ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN 
                                   : 'Bearer ' + SUPABASE_ANON_KEY
              }
          });
      }
      // ... (handles get_cashbook, save_transaction, import_cashbook, etc.)
  }
  // Let normal requests pass through
  return originalFetch(url, options);
}
```

This acts as a "middleman", translating legacy `api.php` requests into secure Supabase REST API requests seamlessly.

## 4. GitHub Deployment Structure

The application is deployed using GitHub Pages. The repository requires the following files to function correctly:

- `index.html` (Renamed from `index_supabase.html`) - The main entry point containing the UI structure and the login overlay.
- `app_supabase.js` - Contains the fetch interceptor, authentication logic, and the core application logic (merged from `app_cloud_final.js`).
- `styles.css` - Custom styling, CSS grid layouts, and glassmorphism effects.
- `church_logo.png` - Assets for the UI and login screen.
- `data_export/` (Folder) - Contains static JSON fallback files (`Members.json`, `Codes.json`, etc.) used to populate dropdowns in case the cloud state is empty or initializing.

## 5. Recent Fixes (The Desktop Loading Bug)

During testing, we discovered a bug where the application loaded perfectly on Mobile but failed to load the Cashbook data on Desktop InPrivate mode. 

**The Cause**: The `attemptLogin()` function was correctly triggering a background reload of the `app_state` (members & settings) after a successful login, but it forgot to call the separate `window.loadCloudData()` function which is responsible for fetching the `cashbook` and re-rendering the UI. 
- (On mobile, it worked because the user had tapped the manual "Refresh" button which explicitly fetched the cashbook).

**The Solution**: We updated `attemptLogin()` in `app_supabase.js` to await both data loading pipelines once the secure token is acquired:
```javascript
// Trigger data reload now that we have the secure token!
if (typeof loadAllData === 'function') {
    await loadAllData();
}
if (typeof window.loadCloudData === 'function') {
    await window.loadCloudData(false);
}
```

## Conclusion
The v9.2 application is robust, highly secure, and correctly handles state synchronization between the static GitHub Pages host and the dynamic Supabase PostgreSQL backend.
