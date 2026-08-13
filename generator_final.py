"""
Generate app_cloud_final.js from the original app.js.
This script makes ONLY the following targeted changes:

1. Replace the entire loadAllData() function with a web-only version
   that fetches JSON files directly (no AndroidBridge, no /api/data).
2. Wrap all localStorage calls in try/catch for private browsing safety.
3. Add cloud data loading (loadCloudData) at the bottom.
4. Add a global error handler for debugging.

Everything else in app.js is left UNTOUCHED.
"""
import re

# Read original app.js
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, "app.js"), "r", encoding="utf-8") as f:
    content = f.read()

# ===== 1. Replace loadAllData() entirely =====
# Find and replace the entire loadAllData function
old_func_pattern = re.compile(
    r'async function loadAllData\(\) \{.*?\n\}',
    re.DOTALL
)

new_loadAllData = r'''async function loadAllData() {
  try {
    // === WEB-ONLY DATA LOADING ===
    // Fetch JSON files directly from data_export folder
    const fetchJson = async (name) => {
      try {
        const res = await fetch('./data_export/' + name + '.json');
        if (res.ok) {
          const arr = await res.json();
          if (Array.isArray(arr) && arr.length > 0) return arr;
        }
      } catch (e) { console.warn("fetchJson error for " + name + ":", e); }
      return [];
    };

    // Fetch all JSON data files in parallel
    const [m, ind, tb, c, bu] = await Promise.all([
      fetchJson("Members"),
      fetchJson("Individual"),
      fetchJson("Trial_Balance"),
      fetchJson("Codes"),
      fetchJson("Budget")
    ]);

    // Assign to state (fetched data takes priority, fallback to INITIAL_*)
    state.members = m.length ? m : (window.INITIAL_MEMBERS || []);
    state.individual = ind.length ? ind : (window.INITIAL_INDIVIDUAL || []);
    state.trialBalance = tb.length ? tb : (window.INITIAL_TRIAL_BALANCE || []);
    state.codes = c.length ? c : (window.INITIAL_CODES || []);
    state.budget = bu.length ? bu : (window.INITIAL_BUDGET || []);
    state.cashbook = [];

    // Load App State from Cloud (Individual Ledgers, Custom Heads, Members Directory, etc.)
    try {
      const stateRes = await fetch('./api.php?_t=' + Date.now(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'get_app_state' })
      });
      const stateData = await stateRes.json();
      if (stateData.success && stateData.data) {
        if (stateData.data.CHURCH_MEMBERS) state.individual = stateData.data.CHURCH_MEMBERS;
        if (stateData.data.CHURCH_ACCOUNT_HEADS) state.customAccountHeads = stateData.data.CHURCH_ACCOUNT_HEADS;
        if (stateData.data.CHURCH_DELETED_HEADS) state.deletedAccountHeads = stateData.data.CHURCH_DELETED_HEADS;
        if (stateData.data.CHURCH_DELETED_MEMBERS) state.deletedMembers = stateData.data.CHURCH_DELETED_MEMBERS;
        if (stateData.data.CHURCH_MASTER_MEMBERS) state.members = stateData.data.CHURCH_MASTER_MEMBERS;
        console.log("App state loaded from MySQL cloud!");
      }
    } catch(e) {
      console.warn("Cloud state fetch failed, falling back to LocalStorage.");
    }

    console.log("Loaded all JSON data! Members:", state.members.length, "Individual:", state.individual.length);

    // 3. Load LocalStorage Overrides (with safety wrappers)
    try {
      const savedMembers = localStorage.getItem("CHURCH_MEMBERS");
      if (savedMembers) {
        try { state.individual = JSON.parse(savedMembers); } catch (e) { }
      }
    } catch(e) { }

    try {
      const savedHeads = localStorage.getItem("CHURCH_ACCOUNT_HEADS");
      if (savedHeads) {
        try { state.customAccountHeads = JSON.parse(savedHeads); } catch (e) { }
      }
    } catch(e) { }

    try {
      const savedDeletedHeads = localStorage.getItem("CHURCH_DELETED_HEADS");
      if (savedDeletedHeads) {
        try { state.deletedAccountHeads = JSON.parse(savedDeletedHeads); } catch (e) { }
      }
    } catch(e) { }
    if (!Array.isArray(state.deletedAccountHeads)) state.deletedAccountHeads = [];

    // Purge any master receipt codes from deleted list to guarantee they always appear
    const masterCodes = ["CD", "RP-3.61", "RP-10.14", "RP-1.01", "RP-1.02", "RP-1.03", "RP-2.02", "RP-2.14", "RP-3.12", "RP-3.16", "RP-3.17", "RP-3.82", "RP-3.83"];
    state.deletedAccountHeads = state.deletedAccountHeads.filter(c => !masterCodes.includes(c));
    try { localStorage.setItem("CHURCH_DELETED_HEADS", JSON.stringify(state.deletedAccountHeads)); } catch(e) { }

    try {
      const savedDeletedMembers = localStorage.getItem("CHURCH_DELETED_MEMBERS");
      if (savedDeletedMembers) {
        try { state.deletedMembers = JSON.parse(savedDeletedMembers); } catch (e) { }
      }
    } catch(e) { }
    if (!Array.isArray(state.deletedMembers)) state.deletedMembers = [];

    // If Fresh Start Build: Purge any old full-data localStorage caches
    if (window.isFreshStartBuild) {
      try {
        if (!localStorage.getItem("CHURCH_FRESH_START_INITIALIZED")) {
          localStorage.removeItem("CHURCH_CASHBOOK");
          localStorage.removeItem("CHURCH_MEMBERS");
          localStorage.removeItem("CHURCH_ACCOUNT_HEADS");
          localStorage.removeItem("CHURCH_DELETED_HEADS");
          localStorage.removeItem("CHURCH_DELETED_MEMBERS");
          localStorage.setItem("CHURCH_FRESH_START_INITIALIZED", "true");
        }
      } catch(e) { }
      state.cashbook = [];
      state.trialBalance = [];
      state.auction = [];
      state.budget = [];
    }

    try {
      const savedCashbook = localStorage.getItem("CHURCH_CASHBOOK");
      if (savedCashbook) {
        try { state.cashbook = JSON.parse(savedCashbook); } catch (e) { }
      }
    } catch(e) { }

    try {
      const savedPass = localStorage.getItem("CHURCH_ADMIN_PASS");
      if (savedPass) { state.adminPassword = savedPass; }
    } catch(e) { }

    try {
      const savedRecNo = localStorage.getItem("CHURCH_RECEIPT_NO");
      if (savedRecNo) {
        const parsedRec = parseInt(savedRecNo, 10);
        if (!isNaN(parsedRec)) state.currentReceiptNo = parsedRec;
      }
    } catch(e) { }

    try {
      const savedVouNo = localStorage.getItem("CHURCH_VOUCHER_NO");
      if (savedVouNo) {
        const parsedVou = parseInt(savedVouNo, 10);
        if (!isNaN(parsedVou)) state.currentVoucherNo = parsedVou;
      }
    } catch(e) { }

    calculateNextNumbers();
    populateMemberDropdown();
    checkTrialLicenseGuard();
  } catch (err) {
    alert("LOAD ERROR: " + err.message);
    console.error("Data load error:", err);
  }
}'''

content = old_func_pattern.sub(new_loadAllData, content, count=1)

# ===== 2. Add cloud database sync and loader at the bottom =====
cloud_code = '''

// === CLOUD DATABASE SYNC ===
window._syncStateTimeout = null;
window.syncAppStateToCloud = function() {
    if (window._syncStateTimeout) clearTimeout(window._syncStateTimeout);
    window._syncStateTimeout = setTimeout(() => {
        const stateData = {
            "CHURCH_MEMBERS": state.individual || [],
            "CHURCH_ACCOUNT_HEADS": state.customAccountHeads || [],
            "CHURCH_DELETED_HEADS": state.deletedAccountHeads || [],
            "CHURCH_DELETED_MEMBERS": state.deletedMembers || [],
            "CHURCH_MASTER_MEMBERS": state.members || []
        };
        
        fetch('./api.php?_t=' + Date.now(), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'save_app_state', state_data: stateData })
        }).then(r => r.json()).then(r => {
            if (r.success) console.log('App state successfully synced to cloud MySQL:', r.message);
            else console.warn('Failed to sync app state:', r.message);
        }).catch(err => console.warn('App state cloud sync skipped:', err.message));
    }, 500); // 500ms debounce
};

window.loadCloudData = async function() {
    console.log("Loading cashbook from cloud database...");
    try {
        const response = await fetch('./api.php?_t=' + Date.now(), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'get_cashbook' })
        });
        const result = await response.json();
        if (result.success && result.data && result.data.length > 0) {
            state.cashbook = result.data;
            calculateNextNumbers();
            renderAllViews();
            console.log("Cloud cashbook loaded successfully!");
        }
    } catch (e) {
        console.warn("Cloud fetch skipped (api.php not available):", e.message);
    }
};
'''
content += cloud_code

# ===== 3. Add global error handler at the very top =====
error_handler = '''window.onerror = function(message, source, lineno, colno, error) {
    alert("JS ERROR:\\n" + message + "\\nLine: " + lineno);
    return false;
};
'''
content = error_handler + content

# ===== 4. Inject loadCloudData call in DOMContentLoaded =====
content = content.replace(
    'await loadAllData();\n  setupNavigation();',
    'await loadAllData();\n  try { if(window.loadCloudData) await window.loadCloudData(); } catch(e) { console.warn("Cloud sync skipped"); }\n  setupNavigation();'
)

# ===== 5. Inject syncAppStateToCloud in CRUD actions =====
content = content.replace(
    'localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members));',
    'localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();'
)
content = content.replace(
    'localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads));',
    'localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();'
)

# ===== 6. Unified local / cloud transaction save handler =====
unified_save_handler = """      const isLocalServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.');
      if (isLocalServer) {
        const endpoint = isReceipt ? '/api/save_receipt' : '/api/save_payment';
        return fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        const payloadWithAction = {
          action: isReceipt ? 'save_receipt' : 'save_payment',
          ...payload
        };
        return fetch('./api.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payloadWithAction)
        });
      }"""

content = content.replace(
    '''      const endpoint = isReceipt ? '/api/save_receipt' : '/api/save_payment';
      return fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });''',
    unified_save_handler
)

# ===== 7. Unified local / cloud bulk import handler for edits/deletions =====
bulk_edit_cloud = """    if (!window.AndroidBridge) {
      const isLocalServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.');
      if (isLocalServer) {
        fetch('/api/bulk_import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(state.cashbook)
        }).then(() => console.log("Cashbook edit synced to DB!")).catch(err => {
          console.error("[SYNC ERROR] Failed to sync cashbook edit to server:", err);
        });
      } else {
        fetch('./api.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'import_cashbook', rows: state.cashbook })
        }).then(r => r.json()).then(r => {
          if (r.success) console.log("Cashbook edit synced to cloud MySQL!");
          else console.error("Cloud MySQL sync failed:", r.message);
        }).catch(err => console.error("[SYNC ERROR] Failed to sync cashbook edit to cloud server:", err));
      }
    }"""

bulk_delete_cloud = """    if (!window.AndroidBridge) {
      const isLocalServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.');
      if (isLocalServer) {
        fetch('/api/bulk_import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(state.cashbook)
        }).then(() => console.log("Cashbook deletion synced to DB!")).catch(err => {
          console.error("[SYNC ERROR] Failed to sync cashbook deletion to server:", err);
        });
      } else {
        fetch('./api.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'import_cashbook', rows: state.cashbook })
        }).then(r => r.json()).then(r => {
          if (r.success) console.log("Cashbook deletion synced to cloud MySQL!");
          else console.error("Cloud MySQL sync failed:", r.message);
        }).catch(err => console.error("[SYNC ERROR] Failed to sync cashbook deletion to cloud server:", err));
      }
    }"""

content = content.replace(
    '''    if (!window.AndroidBridge) {
      fetch('/api/bulk_import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state.cashbook)
      }).then(() => console.log("Cashbook edit synced to DB!")).catch(err => {
        console.error("[SYNC ERROR] Failed to sync cashbook edit to server:", err);
      });
    }''',
    bulk_edit_cloud
)

content = content.replace(
    '''    if (!window.AndroidBridge) {
      fetch('/api/bulk_import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state.cashbook)
      }).then(() => console.log("Cashbook deletion synced to DB!")).catch(err => {
        console.error("[SYNC ERROR] Failed to sync cashbook deletion to server:", err);
      });
    }''',
    bulk_delete_cloud
)

# Write output
with open(os.path.join(script_dir, "app_cloud_final.js"), "w", encoding="utf-8") as f:
    f.write(content)

# Generate app_cloud_v10.js with offline local storage fallback for Android APK / Desktop EXE
offline_fallback = """
    // Offline Fallback for Cashbook (Android APK / Desktop EXE)
    if (window.location.protocol === 'file:') {
      try {
        const savedCashbook = localStorage.getItem("CHURCH_CASHBOOK");
        if (savedCashbook) {
          const parsedCb = JSON.parse(savedCashbook);
          if (parsedCb && parsedCb.length > 0) {
            state.cashbook = parsedCb;
            console.log("Offline Mode: Loaded cashbook from LocalStorage!");
          }
        }
      } catch (e) { }
    }
"""
content_v10 = content.replace(
    'try {\n      const savedPass = localStorage.getItem("CHURCH_ADMIN_PASS");',
    offline_fallback + '\n    try {\n      const savedPass = localStorage.getItem("CHURCH_ADMIN_PASS");'
)
with open(os.path.join(script_dir, "app_cloud_v10.js"), "w", encoding="utf-8") as f:
    f.write(content_v10)

# Verify
with open(os.path.join(script_dir, "app_cloud_final.js"), "r", encoding="utf-8") as f:
    verify = f.read()

# Sanity checks
assert "async function loadAllData()" in verify, "loadAllData not found!"
assert "await Promise.all" in verify, "Promise.all not found - replacement failed!"
assert "window.loadCloudData" in verify, "Cloud loader not found!"
assert "window.onerror" in verify, "Error handler not found!"
# Make sure AndroidBridge is NOT in loadAllData anymore
load_func_match = re.search(r'async function loadAllData\(\) \{.*?\n\}', verify, re.DOTALL)
assert load_func_match, "Could not find loadAllData in output"
load_func_body = load_func_match.group(0)
assert "AndroidBridge" not in load_func_body, "AndroidBridge still in loadAllData!"
assert "api/data" not in load_func_body, "/api/data still in loadAllData!"

print("SUCCESS! app_cloud_final.js created and verified.")
print(f"  File size: {len(verify)} bytes")
print(f"  loadAllData function: {len(load_func_body)} chars")
print(f"  Contains AndroidBridge in loadAllData: {'AndroidBridge' in load_func_body}")
print(f"  Contains /api/data in loadAllData: {'api/data' in load_func_body}")
