import os
import re

with open(r"c:\saju_old pc\Church_App\anti_gravity\app.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add global error handler at the very top
error_handler = """
window.onerror = function(message, source, lineno, colno, error) {
    alert("CRITICAL JS ERROR:\\n" + message + "\\nLine: " + lineno);
    return false;
};
window.addEventListener('unhandledrejection', function(event) {
    alert("UNHANDLED PROMISE REJECTION:\\n" + event.reason);
});

// MAP CHURCH_DATA TO INITIAL_* variables for the web
if (window.CHURCH_DATA) {
  window.INITIAL_MEMBERS = window.CHURCH_DATA.members || [];
  window.INITIAL_INDIVIDUAL = window.CHURCH_DATA.individual || [];
  window.INITIAL_TRIAL_BALANCE = window.CHURCH_DATA.trialBalance || [];
  window.INITIAL_CODES = window.CHURCH_DATA.codes || [];
  window.INITIAL_BUDGET = window.CHURCH_DATA.budget || [];
}

const safeLocalStorage = {
  getItem: function(key) {
    try { return localStorage.getItem(key); } catch(e) { return null; }
  },
  setItem: function(key, val) {
    try { localStorage.setItem(key, val); } catch(e) { }
  },
  removeItem: function(key) {
    try { localStorage.removeItem(key); } catch(e) { }
  }
};
"""
content = error_handler + "\n" + content

# 2. Replace all localStorage with safeLocalStorage
content = content.replace("localStorage.getItem", "safeLocalStorage.getItem")
content = content.replace("localStorage.setItem", "safeLocalStorage.setItem")
content = content.replace("localStorage.removeItem", "safeLocalStorage.removeItem")

# 3. Completely rewrite loadAllData to be 100% hardwired for web
load_all_data_regex = re.compile(r'async function loadAllData\(\) \{.*?\n\}', re.DOTALL)
def get_load_all_data_replacement():
    return """async function loadAllData() {
  try {
    state.cashbook = [];
    state.members = window.INITIAL_MEMBERS || [];
    state.individual = window.INITIAL_INDIVIDUAL || [];
    state.trialBalance = window.INITIAL_TRIAL_BALANCE || [];
    state.codes = window.INITIAL_CODES || [];
    state.budget = window.INITIAL_BUDGET || [];
    
    // Ignore master list overrides from localStorage to prevent corruption on web
    
    const savedHeads = safeLocalStorage.getItem("CHURCH_ACCOUNT_HEADS");
    if (savedHeads) {
      try { state.customAccountHeads = JSON.parse(savedHeads); } catch (e) { }
    }

    const savedDeletedHeads = safeLocalStorage.getItem("CHURCH_DELETED_HEADS");
    if (savedDeletedHeads) {
      try { state.deletedAccountHeads = JSON.parse(savedDeletedHeads); } catch (e) { }
    }
    if (!Array.isArray(state.deletedAccountHeads)) state.deletedAccountHeads = [];

    const masterCodes = ["CD", "RP-3.61", "RP-10.14", "RP-1.01", "RP-1.02", "RP-1.03", "RP-2.02", "RP-2.14", "RP-3.12", "RP-3.16", "RP-3.17", "RP-3.82", "RP-3.83"];
    state.deletedAccountHeads = state.deletedAccountHeads.filter(c => !masterCodes.includes(c));

    calculateNextNumbers();
    populateMemberDropdown();
    checkTrialLicenseGuard();
  } catch (error) {
    alert("CRITICAL ERROR inside loadAllData: " + error.message);
  }
}"""

content = load_all_data_regex.sub(get_load_all_data_replacement(), content)

# 4. Strip out AndroidBridge checks in DOMContentLoaded just in case
content = content.replace('if (!window.AndroidBridge && typeof window.AndroidBridge !== "object") {', '')
content = content.replace('      setupPwaPrompt();\n    }', '      setupPwaPrompt();')

# 5. Fix loadCloudData API fallback
# (It's not called loadCloudData in app.js, it's just missing. I will inject it at the bottom)
cloud_data_func = """
window.loadCloudData = async function() {
    try {
        const response = await fetch('https://orthodoxchurchmysore.in/api/api.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'action=get_cashbook'
        });
        const result = await response.json();
        if (result.success && result.data) {
            state.cashbook = result.data;
            renderAllViews();
        }
    } catch (e) {
        console.error("Cloud fetch error:", e);
    }
};
"""
content += "\n" + cloud_data_func

# Inject window.loadCloudData() call in DOMContentLoaded
content = content.replace('await loadAllData();\n  setupNavigation();', 'await loadAllData();\n  if(window.loadCloudData) await window.loadCloudData();\n  setupNavigation();')

with open(r"c:\saju_old pc\Church_App\anti_gravity\app_cloud_v7.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Created pristine app_cloud_v7.js")
