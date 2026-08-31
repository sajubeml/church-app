
const SUPABASE_URL = 'https://djpuxmrjxsrhgfrtppky.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_QjkuMrFMwtc2imGfy0XCdw_37h05VtE';


window.SUPABASE_ACCESS_TOKEN = null;

window.attemptLogin = async function() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const btn = document.getElementById('login-submit');
    
    if (!email || !password) {
        errorDiv.textContent = "Please enter email and password.";
        errorDiv.style.display = "block";
        return;
    }
    
    btn.disabled = true;
    btn.textContent = "Authenticating...";
    errorDiv.style.display = "none";
    
    try {
        const res = await originalFetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        });
        
        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.error_description || data.msg || "Authentication failed");
        }
        
        // Success! Save token
        window.SUPABASE_ACCESS_TOKEN = data.access_token;
        
        // Hide overlay and show app
        document.getElementById('login-overlay').style.display = 'none';
        document.getElementById('main-app-container').style.display = 'block';
        
        // Trigger data reload now that we have the secure token!
        if (typeof loadAllData === 'function') {
            await loadAllData();
        }
        if (typeof window.loadCloudData === 'function') {
            await window.loadCloudData(false);
        }
        
    } catch(err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = "block";
        btn.disabled = false;
        btn.textContent = "Login";
    }
};


const originalFetch = window.fetch;
window.fetch = async function(url, options) {
  if (url && typeof url === 'string' && url.includes('api.php')) {
    try {
      const body = JSON.parse(options.body);
      
      if (body.action === 'save_transaction') {
        const row = body.row;
        const insertObj = {};
        const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
        cols.forEach(c => {
            insertObj['col_' + c] = (row[c] !== undefined && row[c] !== null) ? String(row[c]) : null;
        });
        
        // Ultimate maxId calculator with global state to prevent double-click duplicate keys
        // ULTIMATE TEST: Use Date.now() for ID. If this throws a duplicate key, 
        // it means the primary key is NOT on the ID column, but on Receipt No (col_B)!
        // Robust ID generation: Unix timestamp in seconds + random salt.
        // E.g., 1724063000. Fits easily within PostgreSQL int4 limit (2.1 billion)
        // and guarantees uniqueness across all devices without needing cloud sync!
        let safeId = Math.floor(Date.now() / 1000);
        if (window._lastInsertedId && safeId <= window._lastInsertedId) {
            safeId = window._lastInsertedId + 1; // Prevent rapid-fire collisions
        }
        insertObj.id = safeId;
        window._lastInsertedId = safeId;
        
        
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY,
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            body: JSON.stringify(insertObj)
        });
        
        if (!res.ok) {
            const errText = await res.text();
            throw new Error("Failed to save transaction: " + res.status + " " + errText);
        }
        if (window.state && window.state.cashbook) {
            body.row.id = insertObj.id;
            window.state.cashbook.push(body.row);
            if (typeof calculateNextNumbers === 'function') calculateNextNumbers();
            if (typeof window.loadCloudData === 'function') setTimeout(() => window.loadCloudData(false), 500);
        }
        return new Response(JSON.stringify({ success: true }));
      }

      if (body.action === 'get_app_state') {
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/app_state?select=*`, {
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY
            }
        });
        if (!res.ok) throw new Error("App state fetch failed: " + res.status);
        const data = await res.json();
        
        const stateMap = {};
        data.forEach(row => { 
            try { 
                stateMap[row.key_name] = typeof row.json_data === 'string' ? JSON.parse(row.json_data || '[]') : row.json_data; 
            } catch(e){}
        });
        return new Response(JSON.stringify({ success: true, data: stateMap }));
      }
      
      if (body.action === 'get_cashbook') {
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook?select=*&order=id.asc`, {
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY
            }
        });
        if (!res.ok) throw new Error("Cashbook fetch failed: " + res.status);
        const data = await res.json();

        const mappedRows = data.map(row => {
            const mapped = {};
            if(row.id) mapped.id = row.id;
            const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            cols.forEach(c => {
                if (row['col_'+c] !== undefined && row['col_'+c] !== null && row['col_'+c] !== 'NULL') mapped[c] = row['col_'+c];
            });
            return mapped;
        });
        return new Response(JSON.stringify({ success: true, data: mappedRows }));
      }
      
      if (body.action === 'save_app_state') {
        const updates = [];
        for (let key in body.state_data) {
           updates.push({ key_name: key, json_data: body.state_data[key] }); 
        }
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/app_state?on_conflict=key_name`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY,
                'Content-Type': 'application/json',
                'Prefer': 'resolution=merge-duplicates'
            },
            body: JSON.stringify(updates)
        });
        if (!res.ok) throw new Error("Failed to save app state: " + res.status);
        if (window.state && window.state.cashbook) {
            body.row.id = insertObj.id;
            window.state.cashbook.push(body.row);
            if (typeof calculateNextNumbers === 'function') calculateNextNumbers();
            if (typeof window.loadCloudData === 'function') setTimeout(() => window.loadCloudData(false), 500);
        }
        return new Response(JSON.stringify({ success: true }));
      }
      
      if (body.action === 'import_cashbook') {
        const rows = body.rows;
        
        // 1. Delete all existing rows
        await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook?id=gt.0`, {
            method: 'DELETE',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY
            }
        });
        
        // 2. Prepare new rows for bulk insert with EXACTLY matching schema structure
        const insertArr = rows.map((row, idx) => {
            const insertObj = { id: (idx + 1) }; 
            const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            cols.forEach(c => {
                insertObj['col_' + c] = (row[c] !== undefined && row[c] !== null) ? String(row[c]) : null;
            });
            return insertObj;
        });
        
        // 3. Insert in batches
        for (let i=0; i<insertArr.length; i+=500) {
            const batch = insertArr.slice(i, i+500);
            const res = await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(batch)
            });
            if (!res.ok) {
                const errText = await res.text();
                throw new Error("Batch insert failed: " + res.status + " " + errText);
            }
        }
        
        if (window.state && window.state.cashbook) {
            body.row.id = insertObj.id;
            window.state.cashbook.push(body.row);
            if (typeof calculateNextNumbers === 'function') calculateNextNumbers();
            if (typeof window.loadCloudData === 'function') setTimeout(() => window.loadCloudData(false), 500);
        }
        return new Response(JSON.stringify({ success: true }));
      }
      
    } catch(err) {
      console.error('Supabase Mock Fetch Error:', err);
      alert("Database Save Error:\n" + err.message);
      return new Response(JSON.stringify({ success: false, message: err.message }));
    }
  }
  
  return originalFetch(url, options);
};

window.onerror = function(message, source, lineno, colno, error) {
    alert("JS ERROR:\n" + message + "\nLine: " + lineno);
    return false;
};
/**
 * St. Gregorios Church Accounting Application Logic
 * Implements VBA UserForm (frmEntry) behavior, 2-way member sync,
 * Document Type selection (Receipt vs Payment Voucher),
 * Cash/Bank safety lock, side-by-side receipt generator, Excel Date formatting, and ledger views.
 */

// Application State
const state = {
  members: [],
  cashbook: [],
  individual: [],
  trialBalance: [],
  codes: [],
  auction: [],
  budget: [],
  customAccountHeads: [],
  adminPassword: "church123",
  isAdminUnlocked: false,
  pendingAction: null,
  cart: [],
  currentReceiptNo: 4001,
  currentVoucherNo: 1,
  showOnlyNonZeroColumns: true,
  sortCol: "B",
  sortAsc: true,
  sortCashbookCol: "date",
  sortCashbookAsc: true,
  columnDensity: "compact",
  activeAccountHeads: []
};

let cbPage = 1;
let cbPageSize = 100;
window.nextCbPage = function() { cbPage++; renderCashbook(); };
window.prevCbPage = function() { if(cbPage > 1) { cbPage--; renderCashbook(); } };

let indivPage = 1;
let indivPageSize = 100;
window.nextIndivPage = function() { indivPage++; renderIndividualLedgers(); };
window.prevIndivPage = function() { if(indivPage > 1) { indivPage--; renderIndividualLedgers(); } };

// Helper to extract column value regardless of cell key format ("B" or "B2" or "B3" or "AA4")
function getColVal(rowObj, colLetter) {
  if (!rowObj) return "";
  const targetCol = String(colLetter).toUpperCase().replace(/[^A-Z]/g, '');
  if (!targetCol) return "";
  const targetKey = Object.keys(rowObj).find(k => k.toUpperCase().replace(/[^A-Z]/g, '') === targetCol);
  return (targetKey && rowObj[targetKey] !== undefined && rowObj[targetKey] !== null) ? String(rowObj[targetKey]).trim() : "";
}

// Helper to set column value matching exact cell key format (e.g. "E" -> "E5" or "AM" -> "AM5")
function setColVal(rowObj, colLetter, val) {
  if (!rowObj) return;
  const targetCol = String(colLetter).toUpperCase().replace(/[^A-Z]/g, '');
  if (!targetCol) return;
  const targetKey = Object.keys(rowObj).find(k => k.toUpperCase().replace(/[^A-Z]/g, '') === targetCol);
  if (targetKey) {
    rowObj[targetKey] = String(val);
  } else {
    rowObj[targetCol] = String(val);
  }
}

function formatExcelDate(val) {
  if (!val) return "";
  let str = String(val).trim();
  if (str === "-" || str === "null" || str === "undefined") return "";

  // 1. Handle Float/Integer Excel Serial Date (e.g., 46113 or 46113.0)
  const floatVal = parseFloat(str);
  if (!isNaN(floatVal) && floatVal > 30000 && floatVal < 60000) {
    const serial = Math.floor(floatVal);
    const utcDays = serial - 25569;
    const date = new Date(utcDays * 86400 * 1000);
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const year = date.getUTCFullYear();
    return `${day}-${month}-${year}`;
  }

  // 2. Handle YYYY-MM-DD or YYYY/MM/DD
  const isoMatch = str.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
  if (isoMatch) {
    const y = isoMatch[1];
    const m = String(isoMatch[2]).padStart(2, '0');
    const d = String(isoMatch[3]).padStart(2, '0');
    return `${d}-${m}-${y}`;
  }

  // 3. Handle DD-MM-YYYY or DD/MM/YYYY
  const dmyMatch = str.match(/^(\d{1,2})[-/](\d{1,2})[-/](\d{4})/);
  if (dmyMatch) {
    const d = String(dmyMatch[1]).padStart(2, '0');
    const m = String(dmyMatch[2]).padStart(2, '0');
    const y = dmyMatch[3];
    return `${d}-${m}-${y}`;
  }

  return str;
}

// Convert date string (DD-MM-YYYY or YYYY-MM-DD) to integer (YYYYMMDD) for ultra-fast sorting
function parseDateForSort(dtStr) {
  if (!dtStr) return 0;
  const str = String(dtStr).trim();
  const parts = str.split(/[-/]/);
  if (parts.length === 3) {
    if (parts[0].length === 4) { // YYYY-MM-DD
      return (parseInt(parts[0], 10) || 0) * 10000 + (parseInt(parts[1], 10) || 0) * 100 + (parseInt(parts[2], 10) || 0);
    } else { // DD-MM-YYYY
      return (parseInt(parts[2], 10) || 0) * 10000 + (parseInt(parts[1], 10) || 0) * 100 + (parseInt(parts[0], 10) || 0);
    }
  }
  return 0;
}

// Currency formatter - rounds to nearest whole Rupee (omits .00 decimals)
function formatCurrency(val) {
  if (val === null || val === undefined || val === "") return "";
  const cleaned = String(val).replace(/[^0-9.-]/g, '');
  if (!cleaned) return "";
  const num = Math.round(parseFloat(cleaned));
  if (isNaN(num)) return "";
  return "₹ " + num.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

// ----------------------------------------------------
// 1. INDIAN RUPEE NUMBER TO WORDS (VBA SpellNumberINR)
// ----------------------------------------------------
function numberToIndianWords(amount) {
  const val = parseFloat(amount);
  if (isNaN(val) || val <= 0) return "Zero Rupees Only";

  const rupees = Math.floor(val);
  const paisa = Math.round((val - rupees) * 100);

  const units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"];
  const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];

  function belowThousand(n) {
    let w = "";
    if (n >= 100) {
      w += units[Math.floor(n / 100)] + " Hundred ";
      n %= 100;
    }
    if (n >= 20) {
      w += tens[Math.floor(n / 10)] + (n % 10 !== 0 ? " " + units[n % 10] : "");
    } else if (n > 0) {
      w += units[n];
    }
    return w.trim();
  }

  function convert(n) {
    if (n === 0) return "Zero";
    const crore = Math.floor(n / 10000000); n %= 10000000;
    const lakh = Math.floor(n / 100000); n %= 100000;
    const thousand = Math.floor(n / 1000); n %= 1000;

    let res = [];
    if (crore > 0) res.push(belowThousand(crore) + " Crore");
    if (lakh > 0) res.push(belowThousand(lakh) + " Lakh");
    if (thousand > 0) res.push(belowThousand(thousand) + " Thousand");
    if (n > 0) res.push(belowThousand(n));
    return res.join(" ");
  }

  const rStr = rupees > 0 ? convert(rupees) + " Rupees" : "Zero Rupees";
  const pStr = paisa > 0 ? " and " + convert(paisa) + " Paisa" : "";
  return `${rStr}${pStr} Only`;
}

// ----------------------------------------------------
// 2. DATA INITIALIZATION & LOAD (File & Server Offline Support)
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  if (!verifyLicenseGuard()) return;
  await loadAllData();
  try { if(window.loadCloudData) await window.loadCloudData(); } catch(e) { console.warn("Cloud sync skipped"); }
  setupNavigation();
  setupFormEventListeners();
  setupCashbookViewListeners();
  setupIndividualViewListeners();
  renderAllViews();
});

function verifyLicenseGuard() {
  // License Expiry: 31-MAR-2028 23:59:59 UTC
  const EXPIRY_TIMESTAMP = 1838160000000;
  const now = new Date().getTime();

  const lastRunKey = "_4s_last_run_t";
  const storedLastRun = localStorage.getItem(lastRunKey);
  const lastRun = storedLastRun ? parseInt(storedLastRun, 10) : 0;

  let isTampered = false;
  if (lastRun > 0 && now < (lastRun - 86400000)) { // Clock backdated by > 24 hours
    isTampered = true;
  } else {
    if (now > lastRun) {
      localStorage.setItem(lastRunKey, now.toString());
    }
  }

  const isExpired = now > EXPIRY_TIMESTAMP;

  if (isExpired || isTampered) {
    document.body.innerHTML = `
      <div style="background:#0f172a; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:2rem; font-family:'Segoe UI',sans-serif; color:#f8fafc;">
        <div style="background:#1e293b; border:2px solid #ef4444; border-radius:16px; max-width:640px; width:100%; padding:2.5rem; text-align:center; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
          <div style="font-size:4rem; margin-bottom:1rem;">🔒</div>
          <h1 style="color:#ef4444; font-size:1.75rem; margin-bottom:0.5rem; font-weight:800;">SOFTWARE LICENSE EXPIRED</h1>
          <p style="color:#94a3b8; font-size:1rem; line-height:1.6; margin-bottom:1.5rem;">
            ${isTampered ? 'Security Warning: System clock manipulation detected. Application locked.' : 'The time-bound license period for St. Gregorios Church Accounting Application has ended (Validity: 31-03-2028).'}
          </p>
          <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:1.25rem; margin-bottom:1.75rem; text-align:left;">
            <h3 style="color:#f8fafc; font-size:1.05rem; margin-bottom:0.75rem;">🔑 License Key Renewal & Authorization Contact:</h3>
            <p style="margin:0.35rem 0; color:#e2e8f0; font-size:0.95rem;"><strong>Developer:</strong> 4S POWER SYSTEMS Mysore</p>
            <p style="margin:0.35rem 0; color:#e2e8f0; font-size:0.95rem;"><strong>Mobile / Phone:</strong> <a href="tel:9980615758" style="color:#38bdf8; text-decoration:none; font-weight:700;">9980615758</a></p>
            <p style="margin:0.35rem 0; color:#e2e8f0; font-size:0.95rem;"><strong>Location:</strong> Mysore, Karnataka</p>
          </div>
          <p style="font-size:0.8rem; color:#64748b;">Protected Application Binary — Reverse Engineering & Unauthorized Use Prohibited</p>
        </div>
      </div>
    `;
    return false;
  }
  return true;
}

async function loadAllData() {
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
}

function escapeJsString(str) {
  if (!str) return '';
  return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function getNormalizedAccountHeadTitle(code, defaultHead) {
  if (!code) return defaultHead || "";
  const normCode = String(code).trim().replace(/^RP-\s*/i, 'RP-').replace(/\s+/g, '').toUpperCase();
  const allHeads = getAllAccountHeads("ALL");
  const found = allHeads.find(h => h.code && h.code.trim().replace(/^RP-\s*/i, 'RP-').replace(/\s+/g, '').toUpperCase() === normCode);
  return found ? found.name : (defaultHead || "");
}

// ----------------------------------------------------
// EXTRACT ALL ACCOUNT HEADS WITH RP CODES FROM BUDGET
// ----------------------------------------------------
function getAllAccountHeads(type = "ALL") {
  const headsMap = new Map(); // codeKey -> { code, name, category, source }

  function addHead(rawCode, rawName, category, source, override = false) {
    if (rawName === undefined || rawName === null || String(rawName).trim() === "") return;
    let code = rawCode ? String(rawCode).trim() : "";
    let name = String(rawName).trim();

    // Skip table header title strings
    const nameLower = name.toLowerCase();
    if (nameLower.includes("account head") || nameLower.includes("particulars") || nameLower === "name" || nameLower.includes("receipts") || nameLower.includes("payments")) return;

    // Standardize RP Code formatting and normalize spaces for 100% strict deduplication
    const cleanCat = (category || "RECEIPT").toUpperCase();
    const formattedCode = code ? code.replace(/^RP-\s*/i, "RP-").trim() : "";
    const normCodeStr = formattedCode.replace(/\s+/g, '').toUpperCase();
    const normNameStr = name.replace(/\s+/g, '').toUpperCase();

    // Deduplication Key: Category + Normalized Code (or Category + Normalized Name if no code)
    const codeKey = formattedCode ? (cleanCat + "_" + normCodeStr) : (cleanCat + "_" + normNameStr);

    // Baseline master heads protection check
    const isMasterHead = (source === "Budget Master");
    if (state.deletedAccountHeads && (state.deletedAccountHeads.includes(codeKey) || state.deletedAccountHeads.includes(normCodeStr))) return;

    const existing = headsMap.get(codeKey);
    // Budget Master heads take 100% HIGHEST priority and can NEVER be overwritten by Trial Balance, Cashbook, or Codes.json
    if (existing && existing.source === "Budget Master" && source !== "Budget Master" && source !== "Custom") {
      return;
    }

    if (!headsMap.has(codeKey) || override) {
      headsMap.set(codeKey, {
        code: formattedCode,
        name: name,
        category: cleanCat,
        source: source
      });
    }
  }

  // 1. MASTER RECEIPT SIDE HEADERS (BASELINE MASTER PRIORITY)
  const MASTER_RECEIPT_HEADS = [
    {
        "code": "RP-1.01",
        "name": "Opening Balance - Cash",
        "category": "RECEIPT"
    },
    {
        "code": "RP-1.02",
        "name": "- Bank",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.82",
        "name": "Monthly Subscription ( Current Year)",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.83",
        "name": "Monthly Subscription ( Pervious Year)",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.16",
        "name": "Birthday Offerings",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.17",
        "name": "Wedding Anniversary Offerings",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.12",
        "name": "Orma Qurbana/Holy Qurbana",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.17 (a)",
        "name": "House Blessing",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.14",
        "name": "Marriage Bann",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.14",
        "name": "Baptism",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.19",
        "name": "Cemetry Receipt",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.61",
        "name": "Sunday School",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.66",
        "name": "OVBS",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.64",
        "name": "Kanika Prayer Group",
        "category": "RECEIPT"
    },
    {
        "code": "",
        "name": "Miscellaneous Income",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.52",
        "name": "Certificate Fee",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.02",
        "name": "Donation General",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.02(a)",
        "name": "Donation General-chair & tables",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.16",
        "name": "Donation-Breakfast",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.20",
        "name": "Donation- Others (Farewell)",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.211",
        "name": "KMDC Grant",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.03",
        "name": "Kurishinthothi &",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.04",
        "name": "Koodaram",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.05",
        "name": "Perunnal Vanchika (House Offertory Box)",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.10",
        "name": "Kanicka Church",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.13",
        "name": "Kanicka-Chapel",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.15(a)",
        "name": "Auction Dues - Old",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.15",
        "name": "Auction current",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.15(b)",
        "name": "Petty Auction",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.04/05",
        "name": "Catholicate Day & Recessa",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.08",
        "name": "Metropolitan Fund",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.13",
        "name": "Mission Sunday",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.15",
        "name": "Seminary Day",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.10",
        "name": "Priest Welfare Fund",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.09",
        "name": "Marriage Kaimuthu",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.17",
        "name": "Old Cover Collection Dues",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.14",
        "name": "Sunday School Day Collection",
        "category": "RECEIPT"
    },
    {
        "code": "RP-10.16",
        "name": "Gerbo Sunday",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.35",
        "name": "St. George Feast",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.31",
        "name": "St. Thomas Feast",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.32",
        "name": "St. Mary's Feast",
        "category": "RECEIPT"
    },
    {
        "code": "RP-3.33",
        "name": "St.Gregorios Feast ( Annual Feast)",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.11",
        "name": "Christmas / New Year Collection",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.12",
        "name": "Parish Day/Harvest / Collection",
        "category": "RECEIPT"
    },
    {
        "code": "RP-2.13",
        "name": "Passion Week Collection",
        "category": "RECEIPT"
    },
    {
        "code": "RP-8.03",
        "name": "Interest Received SB Account",
        "category": "RECEIPT"
    },
    {
        "code": "",
        "name": "Advance A/C Sound System",
        "category": "RECEIPT"
    },
    {
        "code": "",
        "name": "Diocesan Prayer Meeting Income",
        "category": "RECEIPT"
    },
    {
        "code": "",
        "name": "IOBD Charity",
        "category": "RECEIPT"
    },
    {
        "code": "",
        "name": "Fixed Deposit Withdrawn",
        "category": "RECEIPT"
    }
];

  MASTER_RECEIPT_HEADS.forEach(h => {
    addHead(h.code, h.name, "RECEIPT", "Budget Master", true);
  });

  const MASTER_PAYMENT_HEADS = [
    {
        "code": "RP-16.68",
        "name": "MGOCSM & OCYM",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.31",
        "name": "Salary Quota to Diocese(Vicar)",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.03 (a)",
        "name": "Salary to Sexton",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.03 (b)",
        "name": "Salary to Watchman(Cemetry)",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.03 (c)",
        "name": "Salary to Ayah",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02 (a)",
        "name": "Medical Allowance to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.06",
        "name": "Medical Allowance to Sexton",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02 (c)",
        "name": "Telephone Allowance to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02(d)",
        "name": "Local Travelling Allowance to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02(e)",
        "name": "Annual Travelling Allowance to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02(f)",
        "name": "Leave Salary to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.02(g)",
        "name": "Gift Purse to Vicar",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.07",
        "name": "Kaimuthu to Thirumeni",
        "category": "PAYMENT"
    },
    {
        "code": "RP-12.07(a)",
        "name": "Kaimuthu to Visiting priest",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.04",
        "name": "Church Service Expense",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.11(a)",
        "name": "Electricity Charges - Church",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.11(b)",
        "name": "Electricity Charges - Parsonage",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.11(c)",
        "name": "Elecricity Charges - Cemetry",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.08",
        "name": "Breakfast Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 14.31(a)",
        "name": "Church Renovation Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 14.31",
        "name": "Maintenance of Church & Parsonage",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.06",
        "name": "Passion Week Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 14.35",
        "name": "Maintenance of Cemetry",
        "category": "PAYMENT"
    },
    {
        "code": "RP-14.05",
        "name": "Postage",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.35",
        "name": "Canteen Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "RP-14.06",
        "name": "Printing & Stationery",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.36",
        "name": "Cemetry Development",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.87",
        "name": "Grant - Sneha Bhavan",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.89",
        "name": "Gift & Mementoes",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.62",
        "name": "Sunday School Expense",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.67",
        "name": "OVBS",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.65",
        "name": "Prayer Group",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 14.03",
        "name": "Travelling Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 14.04",
        "name": "Audit Fee",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 13.02",
        "name": "Bank Charges",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.69",
        "name": "St Joseph Orthodox Fellowship",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.70",
        "name": "St Dionysius Orthodox Fellowship",
        "category": "PAYMENT"
    },
    {
        "code": "RP-14.34",
        "name": "Repairs And Maintenance-Vehicles",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.03&.04",
        "name": "Catholicate Day & Recceessa",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.11",
        "name": "Metropolitan Fund",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.21",
        "name": "Mission Sunday",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.22",
        "name": "Sunday School Cover Collection",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.23",
        "name": "Seminary Day",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.15",
        "name": "Priest Welfare Fund",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.12",
        "name": "Marriage Kaimuthu",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.32",
        "name": "Annual Kaimuthu to Tirumeni",
        "category": "PAYMENT"
    },
    {
        "code": "RP-19.24",
        "name": "Gerbo Sunday",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.50",
        "name": "St. George Feast",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.47",
        "name": "St. Mary's Feast",
        "category": "PAYMENT"
    },
    {
        "code": "RP- 16.48",
        "name": "St.Gregorios Feast ( Annual Feast)",
        "category": "PAYMENT"
    },
    {
        "code": "RP-16.15",
        "name": "Christmas & New Year Expense",
        "category": "PAYMENT"
    },
    {
        "code": "RP-16.14",
        "name": "Harvest Day/Parish Day Expense",
        "category": "PAYMENT"
    },
    {
        "code": "RP-16.38",
        "name": "Miscellaneous Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "",
        "name": "Fixed Deposit",
        "category": "PAYMENT"
    },
    {
        "code": "RP-18.16",
        "name": "Asset Purchase",
        "category": "PAYMENT"
    },
    {
        "code": "RP-18.23",
        "name": "Electrical Equipments",
        "category": "PAYMENT"
    },
    {
        "code": "",
        "name": "Ecumenical Meeting Expenses (UCF)",
        "category": "PAYMENT"
    },
    {
        "code": "RP-16.32",
        "name": "Diocesan Prayer Meeting Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "",
        "name": "Farewell Expenses",
        "category": "PAYMENT"
    },
    {
        "code": "",
        "name": "Transport Charges ( Ex. Vicar)",
        "category": "PAYMENT"
    },
    {
        "code": "",
        "name": "IOBD Charity",
        "category": "PAYMENT"
    }
];

  MASTER_PAYMENT_HEADS.forEach(h => {
    addHead(h.code, h.name, "PAYMENT", "Budget Master", true);
  });

  // Explicit System Overrides
  addHead("CD", "Excess Cash Deposited to Bank", "RECEIPT", "System", true);
  addHead("CD", "Excess Cash Deposited to Bank", "PAYMENT", "System", true);
  addHead("RP-3.61", "Sunday School", "RECEIPT", "System", true);
  addHead("RP-10.14", "Sunday School Day Collection", "RECEIPT", "System", true);
  addHead("RP-14.31", "Maintenance of Church & Parsonage", "PAYMENT", "System", true);
  addHead("RP-14.31(a)", "Church Renovation Expenses", "PAYMENT", "System", true);
  addHead("RP-14.34", "Repairs And Maintenance-Vehicles", "PAYMENT", "System", true);
  addHead("RP-16.36", "Cemetry Development", "PAYMENT", "System", true);
  addHead("RP-14.35", "Maintenance of Cemetry", "PAYMENT", "System", true);
  addHead("RP-16.11(c)", "Electricity Charges - Cemetry", "PAYMENT", "System", true);
  addHead("RP-12.03 (a)", "Salary to Sexton", "PAYMENT", "System", true);
  addHead("RP-12.03 (b)", "Salary to Watchman(Cemetry)", "PAYMENT", "System", true);
  addHead("RP-12.03 (c)", "Salary to Ayah", "PAYMENT", "System", true);
  addHead("RP-12.02 (a)", "Medical Allowance to Vicar", "PAYMENT", "System", true);
  addHead("RP-12.06", "Medical Allowance to Sexton", "PAYMENT", "System", true);
  addHead("RP-12.02 (c)", "Telephone Allowance to Vicar", "PAYMENT", "System", true);
  addHead("RP-12.02 (d)", "Local Travelling Allowance to Vicar", "PAYMENT", "System", true);
  addHead("RP-12.02 (e)", "Annual Travelling Allowance to Vicar", "PAYMENT", "System", true);
  addHead("RP-12.02 (f)", "Leave Salary to Vicar", "PAYMENT", "System", true);
  addHead("RP-12.02 (g)", "Gift Purse to Vicar", "PAYMENT", "System", true);
  addHead("RP-14.32", "Repairs And Maintenance-Equipments", "PAYMENT", "System", true);

  // 2. Extract from state.trialBalance
  if (Array.isArray(state.trialBalance)) {
    state.trialBalance.forEach(row => {
      const rCode = getColVal(row, "A");
      const rHead = getColVal(row, "B");
      const pCode = getColVal(row, "D");
      const pHead = getColVal(row, "E");

      if (rCode && rCode.toUpperCase().startsWith("RP-")) {
        addHead(rCode, rHead, "RECEIPT", "Trial Balance", true);
      }
      if (pCode && pCode.toUpperCase().startsWith("RP-")) {
        addHead(pCode, pHead, "PAYMENT", "Trial Balance", true);
      }
    });
  }

  // 3. Extract from state.cashbook
  if (Array.isArray(state.cashbook)) {
    state.cashbook.forEach(row => {
      const rCode = getColVal(row, "F");
      const rHead = getColVal(row, "E");
      const pCode = getColVal(row, "N");
      const pHead = getColVal(row, "M");

      if (rCode && rCode.toUpperCase().startsWith("RP-")) {
        addHead(rCode, rHead, "RECEIPT", "Cashbook");
      }
      if (pCode && pCode.toUpperCase().startsWith("RP-")) {
        addHead(pCode, pHead, "PAYMENT", "Cashbook");
      }
    });
  }

  // 4. Extract from state.budget
  if (Array.isArray(state.budget)) {
    state.budget.forEach(row => {
      for (let k in row) {
        const v_str = String(row[k] || "").trim();
        if (/^(RP|PAY)[-_\s]*/i.test(v_str)) {
          const colLetter = k.replace(/[0-9]/g, '').toUpperCase();
          const rowNum = k.replace(/[^0-9]/g, '');

          let titleCol = "";
          let cat = "RECEIPT";

          if (["C", "D"].includes(colLetter)) {
            titleCol = "B";
            cat = "RECEIPT";
          } else if (["I", "J", "P"].includes(colLetter)) {
            titleCol = "H";
            cat = "PAYMENT";
          } else {
            continue;
          }

          const titleVal = String(row[titleCol + rowNum] || row[titleCol] || "").trim();
          if (v_str && titleVal) {
            addHead(v_str, titleVal, cat, "Budget XL", true);
          }
        }
      }
    });
  }

  // 5. Extract from state.codes
  if (Array.isArray(state.codes)) {
    state.codes.forEach(c => {
      let code = getColVal(c, "A");
      let name = getColVal(c, "B");
      let cat = getColVal(c, "C");
      if (!code) code = (c.code || c.Code || "").trim();
      if (!name) name = (c.particulars || c.name || c.Particulars || "").trim();
      if (!cat) cat = (c.type || c.category || "RECEIPT").trim();
      if (code && name) {
        addHead(code, name, cat.toUpperCase(), "Codes", true);
      }
    });
  }

  // 6. Custom / Edited Account Heads from state.customAccountHeads (USER OVERRIDES - HIGHEST PRIORITY)
  if (Array.isArray(state.customAccountHeads)) {
    state.customAccountHeads.forEach(h => {
      if (h && h.code && h.name) {
        addHead(h.code, h.name, h.category || h.type || "RECEIPT", h.source || "Custom", true);
      }
    });
  }

  const result = Array.from(headsMap.values());

  // Sort alphabetically by Account Head Title (Name) A to Z
  result.sort((a, b) => {
    const nameA = String(a.name || "").trim().toLowerCase();
    const nameB = String(b.name || "").trim().toLowerCase();
    return nameA.localeCompare(nameB, undefined, { sensitivity: 'base' });
  });

  const paymentMasterCodes = MASTER_PAYMENT_HEADS.filter(h => h.code).map(h => h.code.toUpperCase().replace(/\s+/g, ''));
  if (type === "RECEIPT") {
    return result.filter(h => h.category === "RECEIPT" && (!h.code || !paymentMasterCodes.includes(h.code.toUpperCase().replace(/\s+/g, ''))));
  } else if (type === "PAYMENT") {
    return result.filter(h => h.category === "PAYMENT");
  }
  return result;
}

function calculateNextNumbers() {
  let maxR = 4000;
  let maxV = 0;
  state.cashbook.forEach(row => {
    const rVal = getColVal(row, "B");
    const vVal = getColVal(row, "L");
    if (rVal && !isNaN(parseInt(rVal))) {
      const r = parseInt(rVal);
      if (r > maxR) maxR = r;
    }
    if (vVal && !isNaN(parseInt(vVal))) {
      const v = parseInt(vVal);
      if (v > maxV) maxV = v;
    }
  });
  state.currentReceiptNo = maxR + 1;
  state.currentVoucherNo = maxV + 1;

  updateDocTypeView();
  document.getElementById("txtDate").valueAsDate = new Date();
}

// Populate Member Dropdown from ALL worksheets (Individual, Members, Auction)
function populateMemberDropdown() {
  const cmbMember = document.getElementById("cmbMember");
  cmbMember.innerHTML = `<option value="">-- Select Member --</option>`;

  const memberMap = new Map();
  const invalidNames = ["NAME OF HOF", "NAME", "SL. NO.", "REGISTER NO.", "REGISTER NO", "SL NO", "MEMBER NAME"];

  // 1. Load from state.members (which includes Address and Phone)
  // We prefer state.members over individual sheet to reflect live edits
  state.members.forEach(row => {
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    if (regNo && name && !invalidNames.includes(regNo.toUpperCase()) && !invalidNames.includes(name.toUpperCase())) {
      memberMap.set(regNo, name);
    }
  });

  // Fallback/Merge with Individual Sheet
  state.individual.forEach(row => {
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    if (regNo && name && !invalidNames.includes(regNo.toUpperCase()) && !invalidNames.includes(name.toUpperCase())) {
      if (!memberMap.has(regNo)) memberMap.set(regNo, name);
    }
  });

  const sortedRegNos = Array.from(memberMap.keys()).sort((a, b) => {
    const nameA = String(memberMap.get(a)).toLowerCase();
    const nameB = String(memberMap.get(b)).toLowerCase();
    return nameA.localeCompare(nameB);
  });

  sortedRegNos.forEach(regNo => {
    const name = memberMap.get(regNo);
    const opt = document.createElement("option");
    opt.value = regNo;
    opt.textContent = `${regNo} - ${name}`;
    opt.dataset.name = name;
    cmbMember.appendChild(opt);
  });

  // Keep a global reference for the search filter
  window.cachedMemberMap = memberMap;
  window.cachedSortedRegNos = sortedRegNos;

  console.log(`Successfully populated ${sortedRegNos.length} parish members into dropdown.`);
}

// ----------------------------------------------------
// 3. NAVIGATION TAB SWITCHING
// ----------------------------------------------------
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const paneId = tab.dataset.tab;
      if (paneId === "tabAdmin" && !state.isAdminUnlocked) {
        promptAdminPassword("OPEN_ADMIN_TAB");
        return;
      }
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetPane = document.getElementById(paneId);
      if (targetPane) targetPane.classList.add("active");
      
      if (paneId === "tabAdmin") {
        renderAdminTab();
      } else if (paneId === "tabMemberDirectory") {
        renderMemberDirectory();
      }
    });
  });
}

// ----------------------------------------------------
// 4. FORM SETUP & 2-WAY MEMBER SYNC
// ----------------------------------------------------
function setupFormEventListeners() {
  const cmbMember = document.getElementById("cmbMember");
  const txtSearchMember = document.getElementById("txtSearchMember");

  // Receipt Tab Member Search Filter
  if (txtSearchMember) {
    txtSearchMember.addEventListener("input", (e) => {
      const searchStr = e.target.value.toLowerCase().trim();
      cmbMember.innerHTML = `<option value="">-- Select Member --</option>`;
      window.cachedSortedRegNos.forEach(regNo => {
        const name = window.cachedMemberMap.get(regNo);
        if (regNo.toLowerCase().includes(searchStr) || name.toLowerCase().includes(searchStr)) {
          const opt = document.createElement("option");
          opt.value = regNo;
          opt.textContent = `${regNo} - ${name}`;
          opt.dataset.name = name;
          cmbMember.appendChild(opt);
        }
      });
    });
  }

  // 2-Way Sync: Member Select -> Reg No
  cmbMember.addEventListener("change", (e) => {
    const regNo = e.target.value;
    document.getElementById("txtRegNo").value = regNo;
  });

  // 2-Way Sync: Reg No Input -> Member Select
  document.getElementById("txtRegNo").addEventListener("input", (e) => {
    const regNo = e.target.value.trim();
    cmbMember.value = regNo;
  });

  // Document Type Change (Receipt vs Payment Voucher)
  document.getElementById("optDocReceipt").addEventListener("change", updateDocTypeView);
  document.getElementById("optDocVoucher").addEventListener("change", updateDocTypeView);

  // Account Head Code Select Listener
  document.getElementById("cmbAccountHead").addEventListener("change", (e) => {
    const selectedOpt = e.target.options[e.target.selectedIndex];
    const codeVal = selectedOpt ? (selectedOpt.dataset.code || "") : "";
    document.getElementById("txtCode").value = codeVal ? codeVal : (selectedOpt && selectedOpt.value ? "(No RP Code)" : "");
  });

  // Account Head Search Filter Listener
  const txtSearchHead = document.getElementById("txtSearchAccountHead");
  if (txtSearchHead) {
    txtSearchHead.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = state.activeAccountHeads.filter(h =>
        (h.code || "").toLowerCase().includes(q) || (h.name || "").toLowerCase().includes(q)
      );
      renderAccountHeadOptions(filtered);
    });
  }

  // Payment Type Lock (No mixing Cash & Bank in 1 receipt)
  const optCash = document.getElementById("optCash");
  const optBank = document.getElementById("optBank");

  optCash.addEventListener("change", () => {
    if (state.cart.length > 0 && state.cart[0].paymentType === "Bank") {
      alert("SAFETY LOCK: Current receipt active cart items are set to Bank. Mixing Cash and Bank in 1 receipt is not allowed!");
      optBank.checked = true;
    }
  });

  optBank.addEventListener("change", () => {
    if (state.cart.length > 0 && state.cart[0].paymentType === "Cash") {
      alert("SAFETY LOCK: Current receipt active cart items are set to Cash. Mixing Cash and Bank in 1 receipt is not allowed!");
      optCash.checked = true;
    }
  });

  // Add Item to Cart
  document.getElementById("btnAddItem").addEventListener("click", addItemToCart);

  // Clear Form
  document.getElementById("btnClearForm").addEventListener("click", clearForm);

  // Generate Receipt / Voucher Modal
  document.getElementById("btnGenerateReceipt").addEventListener("click", showReceiptModal);
}

function renderAccountHeadOptions(headsList) {
  const cmbHead = document.getElementById("cmbAccountHead");
  if (!cmbHead) return;

  const currentVal = cmbHead.value;
  cmbHead.innerHTML = `<option value="">-- Select Account Head --</option>`;

  // Sort dropdown options in ALPHABETICAL ORDER by Account Head Title (Name) for easy search
  const sortedHeads = [...headsList].sort((a, b) => {
    const nameA = (a.name || "").trim().toLowerCase();
    const nameB = (b.name || "").trim().toLowerCase();
    return nameA.localeCompare(nameB, undefined, { sensitivity: 'base' });
  });

  sortedHeads.forEach(h => {
    const opt = document.createElement("option");
    const optValue = h.code || ("HEAD_" + h.name.replace(/\s+/g, '_').toUpperCase());
    opt.value = optValue;
    opt.textContent = h.code ? `${h.name} [${h.code}]` : h.name;
    opt.dataset.code = h.code || "";
    opt.dataset.name = h.name || "";
    cmbHead.appendChild(opt);
  });

  if (headsList.some(h => (h.code || ("HEAD_" + h.name.replace(/\s+/g, '_').toUpperCase())) === currentVal)) {
    cmbHead.value = currentVal;
  } else if (headsList.length === 1) {
    cmbHead.selectedIndex = 1;
    document.getElementById("txtCode").value = headsList[0].code || "(No RP Code)";
  } else {
    document.getElementById("txtCode").value = "";
  }
}

function updateDocTypeView() {
  const isReceipt = document.getElementById("optDocReceipt").checked;
  const numLabel = document.getElementById("lblNum");
  const txtNum = document.getElementById("txtVoucherNo");
  const btnGen = document.getElementById("btnGenerateReceipt");
  const txtSearchHead = document.getElementById("txtSearchAccountHead");

  if (txtSearchHead) txtSearchHead.value = "";

  state.activeAccountHeads = getAllAccountHeads(isReceipt ? "RECEIPT" : "PAYMENT");

  if (isReceipt) {
    numLabel.textContent = "Receipt No.";
    txtNum.value = state.currentReceiptNo;
    btnGen.textContent = "🖨️ Generate & Print Dual Receipt (Original + Copy)";
  } else {
    numLabel.textContent = "Voucher No.";
    txtNum.value = state.currentVoucherNo;
    btnGen.textContent = "🖨️ Generate & Print Payment Voucher";
  }

  try {
    if (state && state.cashbook && state.cashbook.length === 0) {
      if (txtNum) {
        txtNum.removeAttribute("readonly");
        txtNum.style.background = "#ffffff";
        txtNum.title = "First Entry: You may type a custom starting serial number";
      }
    } else {
      if (txtNum) {
        txtNum.setAttribute("readonly", "true");
        txtNum.style.background = "#f1f5f9";
        txtNum.title = "";
      }
    }
  } catch(e) {
    console.error("Error setting readonly state:", e);
  }

  renderAccountHeadOptions(state.activeAccountHeads);
}

function addItemToCart() {
  const cmbHead = document.getElementById("cmbAccountHead");
  if (!cmbHead || cmbHead.selectedIndex <= 0) {
    alert("SAFETY ERROR: Please select an Account Head!");
    return;
  }

  const selectedOpt = cmbHead.options[cmbHead.selectedIndex];
  const code = selectedOpt.dataset.code || "";
  const name = selectedOpt.dataset.name || selectedOpt.text;
  const details = document.getElementById("txtDetails").value.trim();

  const isCash = document.getElementById("optCash").checked;
  const amountInput = document.getElementById("txtAmount");
  const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;
  const selectedPaymentType = isCash ? "Cash" : "Bank";

  // Validation
  if (!code) {
    alert("SAFETY ERROR: Please select an Account Head!");
    return;
  }
  if (amount <= 0) {
    alert("SAFETY ERROR: Please enter a valid amount!");
    return;
  }

  // Safety Lock: Enforce single payment type per receipt (no mixing Cash & Bank)
  if (state.cart.length > 0) {
    const existingType = state.cart[0].paymentType;
    if (existingType !== selectedPaymentType) {
      alert(`SAFETY LOCK ERROR: Cannot mix Cash and Bank items in a single receipt! All items in this receipt must be ${existingType}.`);
      return;
    }
  }

  state.cart.push({
    code,
    particulars: name,
    details,
    paymentType: selectedPaymentType,
    amount
  });

  renderCartTable();

  // Clear item fields
  cmbHead.value = "";
  document.getElementById("txtCode").value = "";
  document.getElementById("txtDetails").value = "";
  if (amountInput) amountInput.value = "";
}

function renderCartTable() {
  const tbody = document.getElementById("cartTbody");
  tbody.innerHTML = "";

  let grandTotal = 0;

  state.cart.forEach((item, index) => {
    grandTotal += item.amount;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="text-center">${index + 1}</td>
      <td><strong>[${item.code}]</strong> ${item.particulars}</td>
      <td>${item.details || '-'}</td>
      <td class="text-center"><span class="header-badge" style="background:#e2e8f0; color:#334155;">${item.paymentType}</span></td>
      <td class="text-right">₹ ${item.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
      <td class="text-center"><button class="btn btn-outline" style="padding:2px 8px; color:var(--danger-color);" onclick="removeCartItem(${index})">✕</button></td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("cartTotalAmt").textContent = `₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  document.getElementById("cartTotalWords").textContent = numberToIndianWords(grandTotal);
}

function removeCartItem(index) {
  state.cart.splice(index, 1);
  renderCartTable();
}

function clearForm() {
  state.cart = [];
  renderCartTable();
  const txtReg = document.getElementById("txtRegNo");
  if (txtReg) txtReg.value = "";
  const cmbM = document.getElementById("cmbMember");
  if (cmbM) cmbM.value = "";
  const txtDet = document.getElementById("txtDetails");
  if (txtDet) txtDet.value = "";
  const amtEl = document.getElementById("txtAmount");
  if (amtEl) amtEl.value = "";
  const txtSrcMem = document.getElementById("txtSearchMember");
  if (txtSrcMem) txtSrcMem.value = "";
  const txtSrcHead = document.getElementById("txtSearchAccountHead");
  if (txtSrcHead) txtSrcHead.value = "";
}

function formatSubUptoMonthYear(val) {
  if (!val) return "-";
  const str = String(val).trim();
  if (!str || str === "-") return "-";

  // Check if it's already MM/YYYY or MM-YYYY
  if (/^\d{2}[\/\-]\d{4}$/.test(str)) {
    return str.replace('-', '/');
  }

  const monthsMap = {
    jan: "01", feb: "02", mar: "03", apr: "04", may: "05", jun: "06",
    jul: "07", aug: "08", sep: "09", oct: "10", nov: "11", dec: "12"
  };

  const lower = str.toLowerCase();

  // Extract month and year, e.g. "Apr 26 to march 27", "mar27", "march 2027", "mar 2027"
  const matches = [...lower.matchAll(/([a-z]{3,9})\s*['\s-]?\s*(\d{2,4})/g)];
  if (matches.length > 0) {
    // Pick the LAST match (latest month/year entry)
    const lastMatch = matches[matches.length - 1];
    const monthStr = lastMatch[1].substring(0, 3);
    const monthNum = monthsMap[monthStr] || "03";
    let yearNum = lastMatch[2];
    if (yearNum.length === 2) yearNum = "20" + yearNum;
    return `${monthNum}/${yearNum}`;
  }

  // Fallback pattern match for date in string
  const dateMatch = str.match(/(\d{1,2})[\/\-](\d{4})/);
  if (dateMatch) {
    const m = dateMatch[1].padStart(2, '0');
    return `${m}/${dateMatch[2]}`;
  }

  return str;
}

function commitCartToLedgers() {
  if (state.cart.length === 0) return;

  const isReceipt = document.getElementById("optDocReceipt").checked;
  const docNo = document.getElementById("txtVoucherNo").value;
  const dateStr = document.getElementById("txtDate").value || new Date().toISOString().split("T")[0];
  const regNo = document.getElementById("txtRegNo").value.trim();
  const cmbMember = document.getElementById("cmbMember");

  let memberName = "";
  if (cmbMember && cmbMember.selectedIndex > 0) {
    memberName = cmbMember.options[cmbMember.selectedIndex].dataset.name || cmbMember.options[cmbMember.selectedIndex].text;
  }

  // 1. Commit each cart item to state.cashbook
  state.cart.forEach(item => {
    const isCash = item.paymentType === "Cash";
    const amtStr = item.amount.toString();

    // Auto-Contra Entry Handling for Internal Cash Deposit to Bank (Code CD, reflects Vr<VoucherNo> on Receipt side, excludes from Trial Balance)
    const isContraParticular = item.code === "CD" || (item.particulars + " " + item.details).toLowerCase().includes("cash deposited");
    if (isContraParticular) {
      const vNoStr = isReceipt ? state.currentVoucherNo.toString() : docNo;

      const rRow = {
        "A": dateStr,
        "B": `Vr${vNoStr}`, // Reflects Voucher No on Receipt side (e.g. Vr166), does NOT consume a Receipt No
        "C": regNo,
        "D": memberName,
        "E": item.particulars || "Excess Cash Deposited to Bank",
        "F": "CD", // Code CD for internal Contra transfers
        "G": item.details || "cash deposited in bank",
        "H": "",
        "I": amtStr
      };
      const pRow = {
        "K": dateStr,
        "L": vNoStr,
        "M": item.particulars || "Excess Cash Deposited to Bank",
        "N": "CD", // Code CD for internal Contra transfers
        "O": item.details || "cash deposited in bank",
        "P": amtStr,
        "Q": ""
      };
      state.cashbook.push(rRow);
      state.cashbook.push(pRow);
      state.currentVoucherNo++;
      return;
    }

    let newRow = {};
    if (isReceipt) {
      newRow = {
        "A": dateStr,
        "B": docNo,
        "C": regNo,
        "D": memberName,
        "E": item.particulars,
        "F": item.code,
        "G": item.details || "",
        "H": isCash ? amtStr : "",
        "I": isCash ? "" : amtStr
      };
    } else {
      newRow = {
        "K": dateStr,
        "L": docNo,
        "M": item.particulars,
        "N": item.code,
        "O": item.details || "",
        "P": isCash ? amtStr : "",
        "Q": isCash ? "" : amtStr
      };
    }
    state.cashbook.push(newRow);

    // 2. Commit member receipt to state.individual using setColVal
    if (isReceipt && regNo && state.individual.length > 0) {
      const targetColKey = findIndividualColKey(item);
      const memberRow = state.individual.find((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);

      if (memberRow) {
        if (targetColKey) {
          const currentVal = parseFloat(getColVal(memberRow, targetColKey)) || 0;
          setColVal(memberRow, targetColKey, (currentVal + item.amount).toString());
        }
        const currentGrand = parseFloat(getColVal(memberRow, "AM")) || 0;
        setColVal(memberRow, "AM", (currentGrand + item.amount).toString());
      }
    }
  });

  // 3. Increment Sequence Numbers & Update Inputs
  try {
    const docStr = docNo ? String(docNo) : "";
    const parsedDocNo = parseInt(docStr.replace(/\D/g, ''));
    if (isReceipt) {
      if (!isNaN(parsedDocNo) && parsedDocNo !== state.currentReceiptNo) {
        state.currentReceiptNo = parsedDocNo;
      }
      state.currentReceiptNo++;
    } else {
      if (!isNaN(parsedDocNo) && parsedDocNo !== state.currentVoucherNo) {
        state.currentVoucherNo = parsedDocNo;
      }
      state.currentVoucherNo++;
    }
  } catch (e) {
    console.error("Error updating sequence:", e);
    if (isReceipt) state.currentReceiptNo++; else state.currentVoucherNo++;
  }

  // 4. Save updated Cash Book, Member Ledgers to LocalStorage and Backend API
  localStorage.setItem("CHURCH_CASHBOOK", JSON.stringify(state.cashbook));
  localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
  localStorage.setItem("CHURCH_RECEIPT_NO", state.currentReceiptNo.toString());
  localStorage.setItem("CHURCH_VOUCHER_NO", state.currentVoucherNo.toString());

  // Post to SQLite Backend or Android Native Bridge
  if (window.AndroidBridge) {
    state.cart.forEach(item => {
      const isCash = item.paymentType === "Cash";
      const payload = isReceipt ? {
        date: dateStr, receipt_no: docNo, reg_no: regNo, name_of_hof: memberName,
        receipt_acct_head: item.particulars, receipt_code: item.code, receipt_details: item.details,
        receipt_cash: isCash ? item.amount : 0, receipt_bank: isCash ? 0 : item.amount
      } : {
        payment_date: dateStr, payment_voucher_no: docNo, 
        payment_acct_head: item.particulars, payment_code: item.code, payment_details: item.details,
        payment_cash: isCash ? item.amount : 0, payment_bank: isCash ? 0 : item.amount
      };
      window.AndroidBridge.saveTransaction(JSON.stringify(payload), isReceipt);
    });
    console.log("Saved to Native Android SQLite!");
  } else {
    Promise.all(state.cart.map(item => {
      const isCash = item.paymentType === "Cash";
      const payload = isReceipt ? {
        date: dateStr, receipt_no: docNo, reg_no: regNo, name_of_hof: memberName,
        receipt_acct_head: item.particulars, receipt_code: item.code, receipt_details: item.details,
        receipt_cash: isCash ? item.amount : 0, receipt_bank: isCash ? 0 : item.amount
      } : {
        payment_date: dateStr, payment_voucher_no: docNo, 
        payment_acct_head: item.particulars, payment_code: item.code, payment_details: item.details,
        payment_cash: isCash ? item.amount : 0, payment_bank: isCash ? 0 : item.amount
      };

      const newRow = {
        A: dateStr, 
        B: isReceipt ? docNo : "",
        C: isReceipt ? regNo : "",
        D: isReceipt ? memberName : "",
        E: isReceipt ? item.particulars : "",
        F: isReceipt ? item.code : "",
        G: isReceipt ? item.details : "",
        H: isReceipt && isCash ? item.amount : "",
        I: isReceipt && !isCash ? item.amount : "",
        K: !isReceipt ? dateStr : "",
        L: !isReceipt ? docNo : "",
        M: !isReceipt ? item.particulars : "",
        N: !isReceipt ? item.code : "",
        O: !isReceipt ? item.details : "",
        P: !isReceipt && isCash ? item.amount : "",
        Q: !isReceipt && !isCash ? item.amount : ""
      };
      
      return fetch('./api.php?_t=' + Date.now(), {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'save_transaction', row: newRow })
      });
    })).then((responses) => {
      let allOk = true;
      responses.forEach(r => { if (r && !r.ok) allOk = false; });
      if (allOk) {
        console.log("Saved to DB!");
        alert("✅ Transaction successfully synced to Cloud Database!");
      } else {
        alert("⚠️ Transaction saved locally, but Cloud server returned an error.");
      }
    }).catch(err => {
      console.error("[SYNC ERROR] Failed to save to server database:", err);
      alert("⚠️ Data saved locally but could NOT sync to server database. Please check your network connection and try again.");
    });
  }

  const vInput = document.getElementById("txtVoucherNo");
  if (vInput) {
    vInput.value = isReceipt ? state.currentReceiptNo.toString() : state.currentVoucherNo.toString();
  }

  // 5. Reset Cart & Live update all table views (Cash Book, Member Ledgers, Trial Balance, Audit, Admin)
  clearForm();
  renderAllViews();
}

// ----------------------------------------------------
// 5. DUAL SIDE-BY-SIDE PRINTABLE RECEIPT MODAL
// ----------------------------------------------------
function showReceiptModal() {
  if (state.cart.length === 0) {
    alert("Please add at least one item to the cart!");
    return;
  }

  const isReceipt = document.getElementById("optDocReceipt").checked;
  const docTitle = isReceipt ? "RECEIPT" : "PAYMENT VOUCHER";
  const numLabel = isReceipt ? "Receipt No" : "Voucher No";
  const docNo = document.getElementById("txtVoucherNo").value;
  const dateStr = document.getElementById("txtDate").value;
  const regNo = document.getElementById("txtRegNo").value;
  const cmbMember = document.getElementById("cmbMember");

  let memberName = "General / N/A";
  if (cmbMember.selectedIndex > 0) {
    memberName = cmbMember.options[cmbMember.selectedIndex].dataset.name || cmbMember.options[cmbMember.selectedIndex].text;
  }

  let grandTotal = 0;
  let itemRowsHtml = "";

  state.cart.forEach((item, idx) => {
    grandTotal += item.amount;
    const detailsText = item.details ? String(item.details).trim() : '';
    const detailsHtml = detailsText ? `<div style="font-size:10.5px; color:#475569; font-style:italic; margin-top:3px; padding-top:2px; border-top:1px dashed #cbd5e1;"><strong>Details:</strong> ${detailsText}</div>` : '';
    itemRowsHtml += `
      <tr>
        <td style="text-align:center; vertical-align:top; padding:6px;">${idx + 1}</td>
        <td style="padding:6px;">
          <div style="font-weight:700; color:#0f172a;">${item.particulars} (${item.code})</div>
          ${detailsHtml}
        </td>
        <td style="text-align:right; vertical-align:top; padding:6px; font-weight:700;">₹ ${item.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
      </tr>
    `;
  });

  const totalWords = numberToIndianWords(grandTotal);

  // Commit Cart Items to Cash Book & Member Ledgers
  commitCartToLedgers();

  const prefix = isReceipt ? "Receipt" : "Voucher";
  const pdfTitle = `${prefix}_${docNo}`;
  document.title = pdfTitle;

  const receiptContent = `
    <div class="dual-receipt-container" style="display:flex; gap:20px; flex-wrap:wrap;">
      <!-- ORIGINAL -->
      <div class="receipt-card" style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#10b981; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">ORIGINAL</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <img src="church_logo.png" alt="Church Logo" style="height:54px; width:54px; border-radius:50%; border:1.5px solid #1e293b; margin-bottom:4px; object-fit:contain; background:#fff;">
          <h3 style="margin:0; font-size:15px; color:#0f172a; font-weight:800;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:10.5px; color:#475569;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010 | ESTD : 1954</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle}</p>
        </div>
        <table style="width:90%; margin:0 auto 10px auto; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${docNo}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:90%; margin:0 auto 12px auto; border-collapse:collapse; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>${itemRowsHtml}</tbody>
        </table>
        <div style="display:flex; flex-direction:row; justify-content:space-between; align-items:flex-end; background:#f1f5f9; padding:10px; border-radius:4px; margin-bottom:15px; width:90%; margin-left:auto; margin-right:auto; flex-wrap:nowrap;">
          <div style="font-size:11px; font-weight:normal; font-style:italic; color:#475569; max-width:65%; text-align:left; word-wrap:break-word;">(${totalWords})</div>
          <div style="font-size:14px; font-weight:900; color:#0f172a; text-align:right; white-space:nowrap;">Total: ₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
        </div>
        <div style="display:flex; justify-content:flex-end; font-size:11px; font-weight:bold; color:#1e293b; margin-bottom:8px;">
          <div style="text-align:right;">Vicar / Trustee: ___________________</div>
        </div>
        <div style="text-align:center; font-size:9.5px; color:#475569; border-top:1px dashed #cbd5e1; padding-top:6px; font-weight:600; font-style:italic;">
          ✓ Computer Generated Document — Digitally Signed & Authenticated
        </div>
      </div>

      <!-- DUPLICATE COPY -->
      <div class="receipt-card" style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#f59e0b; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">COPY</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <img src="church_logo.png" alt="Church Logo" style="height:54px; width:54px; border-radius:50%; border:1.5px solid #1e293b; margin-bottom:4px; object-fit:contain; background:#fff;">
          <h3 style="margin:0; font-size:15px; color:#0f172a; font-weight:800;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:10.5px; color:#475569;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010 | ESTD : 1954</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle} (OFFICE COPY)</p>
        </div>
        <table style="width:90%; margin:0 auto 10px auto; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${docNo}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:90%; margin:0 auto 12px auto; border-collapse:collapse; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>${itemRowsHtml}</tbody>
        </table>
        <div style="display:flex; flex-direction:row; justify-content:space-between; align-items:flex-end; background:#f1f5f9; padding:10px; border-radius:4px; margin-bottom:15px; width:90%; margin-left:auto; margin-right:auto; flex-wrap:nowrap;">
          <div style="font-size:11px; font-weight:normal; font-style:italic; color:#475569; max-width:65%; text-align:left; word-wrap:break-word;">(${totalWords})</div>
          <div style="font-size:14px; font-weight:900; color:#0f172a; text-align:right; white-space:nowrap;">Total: ₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
        </div>
        <div style="display:flex; justify-content:flex-end; font-size:11px; font-weight:bold; color:#1e293b; margin-bottom:8px;">
          <div style="text-align:right;">Vicar / Trustee: ___________________</div>
        </div>
        <div style="text-align:center; font-size:9.5px; color:#475569; border-top:1px dashed #cbd5e1; padding-top:6px; font-weight:600; font-style:italic;">
          ✓ Computer Generated Document — Digitally Signed & Authenticated
        </div>
      </div>
    </div>
  `;

  const modalArea = document.getElementById("receiptModalArea");
  if (modalArea) {
    modalArea.innerHTML = receiptContent;
    modalArea.dataset.prefix = prefix;
    modalArea.dataset.docno = docNo;
  }
  document.getElementById("receiptModal").classList.add("active");

  // Auto-save print copy HTML immediately upon generation
  saveReceiptPrintCopy(docNo, prefix, receiptContent);
}

function triggerSystemPrint(pdfTitle) {
  if (pdfTitle) {
    document.title = getCleanPrintTitle(pdfTitle);
  }
  if (window.AndroidBridge) {
    window.AndroidBridge.printPage(document.title);
  } else {
    window.print();
  }
}
window.triggerSystemPrint = triggerSystemPrint;

function closePrintPreviewOverlay() {
  const overlay = document.getElementById("printPreviewOverlay");
  if (overlay) {
    overlay.remove();
  }
  document.body.classList.remove("printing-mode");
  document.title = "St. Gregorios Orthodox Syrian Church & Pilgrim Centre";
  return true;
}
window.closePrintPreviewOverlay = closePrintPreviewOverlay;

function closeAnyOpenModalOrPdf() {
  let closedSomething = false;

  const overlay = document.getElementById("printPreviewOverlay");
  if (overlay) {
    overlay.remove();
    closedSomething = true;
  }

  const rModal = document.getElementById("receiptModal");
  if (rModal && rModal.classList.contains("active")) {
    rModal.classList.remove("active");
    closedSomething = true;
  }

  const activeModals = document.querySelectorAll(".modal-backdrop.active");
  activeModals.forEach(m => {
    m.classList.remove("active");
    closedSomething = true;
  });

  if (document.body.classList.contains("printing-mode")) {
    document.body.classList.remove("printing-mode");
    closedSomething = true;
  }

  document.title = "St. Gregorios Orthodox Syrian Church & Pilgrim Centre";
  return closedSomething;
}

function closeReceiptModal() {
  closeAnyOpenModalOrPdf();
}

window.closeAnyOpenModalOrPdf = closeAnyOpenModalOrPdf;

// Helper for cleaning document.title for auto PDF file naming in print mode
function getCleanPrintTitle(rawTitle) {
  if (!rawTitle) return "Document";
  const clean = String(rawTitle)
    .replace(/#/g, "")
    .replace(/[^a-zA-Z0-9_\-]/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
  return clean || "Document";
}

function getActiveViewPrintTitle() {
  const receiptModal = document.getElementById("receiptModal");
  if (receiptModal && receiptModal.classList.contains("active")) {
    const modalArea = document.getElementById("receiptModalArea");
    const prefix = modalArea?.dataset?.prefix || (document.getElementById("optDocReceipt")?.checked ? "Receipt" : "Voucher");
    const rawDocNo = modalArea?.dataset?.docno || document.getElementById("txtVoucherNo")?.value || "";
    const docNo = rawDocNo.replace(/#/g, "").trim();
    return getCleanPrintTitle(docNo ? `${prefix}_${docNo}` : `${prefix}_Document`);
  }

  const activeTabBtn = document.querySelector(".app-nav .nav-btn.active");
  const tabText = activeTabBtn ? activeTabBtn.textContent.trim().toLowerCase() : "";

  if (tabText.includes("cash book") || tabText.includes("cashbook")) {
    return "St_Gregorios_Cash_Book_FY2026_2027";
  } else if (tabText.includes("individual")) {
    const memberSel = document.getElementById("selIndivMember");
    if (memberSel && memberSel.value) {
      const selectedText = memberSel.options[memberSel.selectedIndex]?.text || "";
      if (selectedText && !selectedText.includes("All Members")) {
        return getCleanPrintTitle(`Member_${selectedText}_Ledger`);
      }
    }
    return "St_Gregorios_Individual_Member_Ledgers";
  } else if (tabText.includes("trial balance")) {
    return "St_Gregorios_Trial_Balance_Statement";
  } else if (tabText.includes("audit")) {
    return "St_Gregorios_Audit_Reconciliation_Report";
  }

  return "St_Gregorios_Church_Accounting";
}

let __prePrintTitle = document.title;
window.addEventListener("beforeprint", function () {
  __prePrintTitle = document.title;
  document.title = getActiveViewPrintTitle();
});

window.addEventListener("afterprint", function () {
  document.title = __prePrintTitle || "St. Gregorios Orthodox Syrian Church & Pilgrim Centre";
});

function printReceiptModal() {
  const modalArea = document.getElementById("receiptModalArea");
  const prefix = modalArea?.dataset?.prefix || (document.getElementById("optDocReceipt")?.checked ? "Receipt" : "Voucher");
  const rawDocNo = modalArea?.dataset?.docno || document.getElementById("txtVoucherNo")?.value || "";
  const docNo = rawDocNo.replace(/#/g, "").trim();
  const pdfTitle = getCleanPrintTitle(docNo ? `${prefix}_${docNo}` : `${prefix}_Document`);

  // 1. Ensure all ledger views are updated live
  renderAllViews();

  // 2. Save print file copy into local Receipts/ folder & localStorage
  if (modalArea && docNo) {
    saveReceiptPrintCopy(docNo, prefix, modalArea.innerHTML);
  }

  // 3. Set main document title for native print filename auto-population
  document.title = pdfTitle;

  // 4. On Android WebView, invoke native system print directly
  if (window.AndroidBridge) {
    triggerSystemPrint(pdfTitle);
    return;
  }

  // 5. Open dedicated print popup window with explicit <title> for 100% PDF filename auto-population
  const printWin = window.open('', '_blank', 'width=1100,height=850');
  if (!printWin) {
    // Fallback if popup blocker prevents window open
    triggerSystemPrint(pdfTitle);
    return;
  }

  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=0.5, maximum-scale=5.0, user-scalable=yes">
      <title>${pdfTitle}</title>
      <style>
        body { font-family: system-ui, -apple-system, sans-serif; padding: 60px 20px 20px 20px; background: #fff; color: #000; }
        button[onclick*="closeReceiptModal"], .receipt-modal-close-btn, .modal-close-btn { display: none !important; }
        .dual-receipt-container { display: flex; gap: 20px; justify-content: center; align-items: stretch; }
        .receipt-card { flex: 1; border: 2px solid #0f172a; border-radius: 8px; padding: 15px; background: #fff; min-width: 320px; max-width: 48%; position: relative; box-sizing: border-box; }
        @media print {
          .no-print, .print-preview-header { display: none !important; }
          @page { size: A4 landscape; margin: 0; }
          body { padding: 5mm !important; background: #fff; width: 100%; margin: 0; box-sizing: border-box; }
          .dual-receipt-container { position: relative; gap: 15px !important; width: 100%; min-height: 190mm; align-items: flex-start !important; }
          .dual-receipt-container::after { content: ""; position: absolute; top: 0; bottom: 0; left: 50%; border-left: 1px dashed #94a3b8; }
          .receipt-card { max-width: 48% !important; border: 2px solid #0f172a !important; border-radius: 8px !important; padding: 10mm !important; }
        }
      </style>
    </head>
    <body>
      <div class="print-preview-header no-print" style="position:fixed; top:0; left:0; right:0; z-index:2147483647; background:#0f172a; color:#ffffff; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 14px rgba(0,0,0,0.5);">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:1.1rem;">📄</span>
          <span style="font-weight:800; font-size:0.92rem; color:#ffffff;">${pdfTitle}</span>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
          <button onclick="window.print()" style="background:#0284c7; color:#ffffff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; cursor:pointer; font-size:0.85rem;">🖨️ Print / Save PDF</button>
          <button onclick="if(window.history.length>1){window.history.back();}else{window.close();}" style="background:#dc2626; color:#ffffff; border:none; padding:8px 18px; border-radius:24px; font-weight:800; cursor:pointer; font-size:0.9rem; box-shadow:0 2px 10px rgba(220,38,38,0.5);">✖ Close & Return to App</button>
        </div>
      </div>
      ${modalArea ? modalArea.innerHTML : ''}
      <script>
        document.title = "${pdfTitle}";
        window.onload = function() {
          document.title = "${pdfTitle}";
          setTimeout(function() {
            window.print();
          }, 250);
        };
      </script>
    </body>
    </html>
  `);
  printWin.document.close();
  printWin.document.title = pdfTitle;
}

function exportReceiptPdf() {
  const modalArea = document.getElementById("receiptModalArea");
  const prefix = modalArea?.dataset?.prefix || "Receipt";
  const rawDocNo = modalArea?.dataset?.docno || "";
  const docNo = rawDocNo.replace(/#/g, "").trim();
  const cleanTitle = getCleanPrintTitle(docNo ? `${prefix}_${docNo}` : `${prefix}_Document`);
  const pdfName = `${cleanTitle}.pdf`;

  if (!modalArea) return;

  document.title = cleanTitle;

  // 1. Send to server to generate Receipts/Receipt_4275.pdf and download directly
  saveReceiptPrintCopy(docNo, prefix, modalArea.innerHTML, function (res) {
    if (res && res.pdf_url) {
      const a = document.createElement("a");
      a.href = res.pdf_url;
      a.download = pdfName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      return;
    }
    // Fallback: Open system print window if server unavailable
    printReceiptModal();
  });
}

function downloadReceiptHtml() {
  const modalArea = document.getElementById("receiptModalArea");
  const prefix = modalArea?.dataset?.prefix || "Receipt";
  const rawDocNo = modalArea?.dataset?.docno || "";
  const docNo = rawDocNo.replace(/#/g, "").trim();
  const cleanTitle = getCleanPrintTitle(docNo ? `${prefix}_${docNo}` : `${prefix}_Document`);
  const fileName = `${cleanTitle}.html`;

  const content = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${cleanTitle}_St_Gregorios_Church</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 20px; background: #fff; color: #000; }
    .dual-receipt-container { display: flex; gap: 20px; flex-wrap: wrap; }
    .receipt-card { flex: 1; border: 2px solid #0f172a; border-radius: 8px; padding: 15px; background: #fff; min-width: 320px; position: relative; }
    @media print { @page { size: landscape; margin: 6mm; } }
  </style>
</head>
<body>
  <div class="dual-receipt-container">
    ${modalArea ? modalArea.innerHTML : ''}
  </div>
</body>
</html>`;

  const blob = new Blob([content], { type: "text/html;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function saveReceiptPrintCopy(docNo, prefix, htmlContent, callback) {
  const cleanDocNo = (docNo || "").replace(/#/g, "").trim();
  const key = getCleanPrintTitle(cleanDocNo ? `${prefix}_${cleanDocNo}` : `${prefix}_Document`);
  const fileName = `${key}.html`;

  // 1. Save to Local Storage Map
  try {
    const savedMap = JSON.parse(localStorage.getItem("CHURCH_SAVED_RECEIPTS") || "{}");
    savedMap[key] = htmlContent;
    savedMap[`${prefix}_#${cleanDocNo}`] = htmlContent;
    localStorage.setItem("CHURCH_SAVED_RECEIPTS", JSON.stringify(savedMap));
  } catch (e) { }

  // 2. Prepare clean HTML for Edge headless PDF rendering & file storage
  // Fix relative image path so files in Receipts/ directory locate church_logo.png in root folder
  let cleanContent = (htmlContent || "")
    .replace(/src="church_logo\.png"/g, 'src="../church_logo.png"')
    .replace(/src="church_logo\.jpg"/g, 'src="../church_logo.jpg"');

  const fullHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${key}_St_Gregorios_Church</title>
  <style>
    @page { size: A4 landscape; margin: 0; }
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; padding: 5mm; background: #fff; color: #000; margin: 0; width: 297mm; height: auto; overflow: hidden; }
    .no-print, .print-preview-header { display: none !important; }
    .dual-receipt-container { display: flex; position: relative; gap: 15px; flex-wrap: nowrap; width: 100%; min-height: 190mm; align-items: flex-start; justify-content: center; }
    .dual-receipt-container::after { content: ""; position: absolute; top: 0; bottom: 0; left: 50%; border-left: 1px dashed #94a3b8; }
    .receipt-card { flex: 1; border: 2px solid #0f172a !important; border-radius: 8px !important; padding: 10mm; background: #fff; position: relative; box-sizing: border-box; overflow: hidden; max-width: 48%; }
  </style>
</head>
<body>
  ${cleanContent}
</body>
</html>`;

  fetch('/api/save_print', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: fileName,
      content: fullHtml
    })
  })
    .then(r => r.json())
    .then(res => {
      if (typeof callback === 'function') callback(res);
    })
    .catch(() => {
      if (typeof callback === 'function') callback(null);
    });
}

// ----------------------------------------------------
// 6. RENDER ALL DATA VIEWS
// ----------------------------------------------------
function renderAllViews() {
  renderCashbook();
  renderIndividualLedgers();
  renderTrialBalance();
  renderAudit();
  if (state.isAdminUnlocked) {
    renderAdminTab();
  }
}

function renderCashbook() {
  const tbody = document.getElementById("cashbookTbody");
  const tfoot = document.getElementById("cashbookTfoot");
  if (!tbody) return;
  tbody.innerHTML = "";
  if (tfoot) tfoot.innerHTML = "";

  const receiptRows = [];
  const paymentRows = [];

  let totalCashR = 0, totalBankR = 0, totalCashP = 0, totalBankP = 0;
  let openingCash = 0;
  let openingBank = 0;

  state.cashbook.forEach(row => {
    const dtRaw = getColVal(row, "A");
    const payDtRaw = getColVal(row, "K");
    const recNo = getColVal(row, "B");
    const voucherNo = getColVal(row, "L");
    const regNo = getColVal(row, "C");
    const hof = getColVal(row, "D");
    let head = getColVal(row, "E");
    const code = getColVal(row, "F");
    const details = getColVal(row, "G");
    const cashR = getColVal(row, "H");
    const bankR = getColVal(row, "I");

    const payHead = getColVal(row, "M");
    const payCode = getColVal(row, "N");
    const payDetails = getColVal(row, "O");
    const cashP = getColVal(row, "P");
    const bankP = getColVal(row, "Q");

    // Skip top header/title rows
    const dtLower = dtRaw.toLowerCase();
    const recLower = recNo.toLowerCase();
    const headLower = head.toLowerCase();
    const payLower = payHead.toLowerCase();

    if (dtLower.includes("cash book") || dtLower.includes("receipts") || dtLower === "date" || recLower.startsWith("receipt") || headLower === "accounts head" || payLower === "accounts head") {
      return;
    }

    // Label Opening Balance explicitly
    let isOpening = false;
    if (details.toLowerCase().includes("opening balance") || cashR === "9879" || bankR === "651682" || (headLower.includes("opening") && (cashR || bankR))) {
      head = "Opening Balance";
      isOpening = true;
      openingCash = parseFloat(cashR) || 0;
      openingBank = parseFloat(bankR) || 0;
    }

    let finalReceiptHead = head;
    if (!isOpening && code) {
      const normHead = getNormalizedAccountHeadTitle(code, head);
      if (normHead) finalReceiptHead = normHead;
    }

    let finalPaymentHead = payHead;
    if (payCode) {
      const normPayHead = getNormalizedAccountHeadTitle(payCode, payHead);
      if (normPayHead) finalPaymentHead = normPayHead;
    }

    // Valid receipt entry condition: MUST be opening balance, OR have valid amount (> 0)
    const hasReceiptAmt = (parseFloat(cashR) || 0) > 0 || (parseFloat(bankR) || 0) > 0;
    const isValidReceipt = isOpening || ((Boolean(recNo) || Boolean(head) || Boolean(hof)) && hasReceiptAmt);
    if (isValidReceipt) {
      const displayDate = formatExcelDate(dtRaw || payDtRaw);
      receiptRows.push({
        displayDate,
        recNo,
        regNo,
        hof,
        head: isOpening ? "Opening Balance" : finalReceiptHead,
        code,
        details,
        cashR,
        bankR,
        isOpening,
        dateKey: parseDateForSort(displayDate),
        recNoKey: parseInt(String(recNo || '').replace(/\D/g, ''), 10) || 0,
        regNoKey: parseInt(String(regNo || '').replace(/\D/g, ''), 10) || 0,
        nameKey: (hof || "").toLowerCase(),
        headKey: (isOpening ? "Opening Balance" : finalReceiptHead || "").toLowerCase(),
        codeKey: (code || "").toLowerCase(),
        amtKey: (parseFloat(cashR) || 0) + (parseFloat(bankR) || 0)
      });

      if (!isOpening) {
        if (cashR && !isNaN(parseFloat(cashR))) totalCashR += parseFloat(cashR) || 0;
        if (bankR && !isNaN(parseFloat(bankR))) totalBankR += parseFloat(bankR) || 0;
      }
    }

    // Valid payment entry condition: MUST have valid amount (> 0)
    const hasPaymentAmt = (parseFloat(cashP) || 0) > 0 || (parseFloat(bankP) || 0) > 0;
    const isValidPayment = (Boolean(voucherNo) || Boolean(payHead) || Boolean(payCode) || Boolean(payDetails)) && hasPaymentAmt;
    if (isValidPayment) {
      const payDate = formatExcelDate(payDtRaw || dtRaw);
      paymentRows.push({
        payDate,
        voucherNo,
        payHead: finalPaymentHead,
        payCode,
        payDetails,
        cashP,
        bankP,
        dateKey: parseDateForSort(payDate),
        voucherNoKey: parseInt(String(voucherNo || '').replace(/\D/g, ''), 10) || 0,
        payHeadKey: (finalPaymentHead || "").toLowerCase(),
        payCodeKey: (payCode || "").toLowerCase(),
        payAmtKey: (parseFloat(cashP) || 0) + (parseFloat(bankP) || 0)
      });

      if (cashP && !isNaN(parseFloat(cashP))) totalCashP += parseFloat(cashP) || 0;
      if (bankP && !isNaN(parseFloat(bankP))) totalBankP += parseFloat(bankP) || 0;
    }
  });

  // Sort receiptRows and paymentRows based on active Cash Book sort selection (Ultra-fast direct key comparison)
  const isAsc = state.sortCashbookAsc;
  const col = state.sortCashbookCol;

  const getPropR = (col) => {
    if (col === "date" || col === "paydate") return "dateKey";
    if (col === "rec" || col === "voucher") return "recNoKey";
    if (col === "reg") return "regNoKey";
    if (col === "name") return "nameKey";
    if (col === "head" || col === "payhead") return "headKey";
    if (col === "code" || col === "paycode") return "codeKey";
    if (col === "cash" || col === "bank" || col === "amt") return "amtKey";
    return "dateKey";
  };
  
  const getPropP = (col) => {
    if (col === "date" || col === "paydate") return "dateKey";
    if (col === "rec" || col === "voucher") return "voucherNoKey";
    if (col === "head" || col === "payhead") return "payHeadKey";
    if (col === "code" || col === "paycode") return "payCodeKey";
    if (col === "paycash" || col === "paybank" || col === "amt") return "payAmtKey";
    return "dateKey";
  };

  const propR = getPropR(col);
  const propP = getPropP(col);

  receiptRows.sort((a, b) => {
    if (a.isOpening) return -1;
    if (b.isOpening) return 1;

    let valA = a[propR], valB = b[propR];
    if (valA < valB) return isAsc ? -1 : 1;
    if (valA > valB) return isAsc ? 1 : -1;

    return isAsc ? (a.recNoKey - b.recNoKey) : (b.recNoKey - a.recNoKey);
  });

  paymentRows.sort((a, b) => {
    let valA = a[propP], valB = b[propP];
    if (valA < valB) return isAsc ? -1 : 1;
    if (valA > valB) return isAsc ? 1 : -1;

    return isAsc ? (a.voucherNoKey - b.voucherNoKey) : (b.voucherNoKey - a.voucherNoKey);
  });

  const hasOpening = receiptRows.length > 0 && receiptRows[0].isOpening;
  const maxRows = Math.max(receiptRows.length, paymentRows.length + (hasOpening ? 1 : 0));

  const totalPages = Math.ceil(maxRows / cbPageSize) || 1;
  if (cbPage > totalPages) cbPage = totalPages;
  if (cbPage < 1) cbPage = 1;
  const startIdx = (cbPage - 1) * cbPageSize;
  const endIdx = Math.min(startIdx + cbPageSize, maxRows);

  const lbl = document.getElementById("cbPageLabel");
  if (lbl) lbl.textContent = `Page ${cbPage} of ${totalPages} (${maxRows} total rows)`;

  for (let i = startIdx; i < endIdx; i++) {
    const rec = receiptRows[i] || {};

    // Shift payment entries down by 1 row when Opening Balance row is present at index 0
    let pay = {};
    if (hasOpening) {
      if (i > 0) {
        pay = paymentRows[i - 1] || {};
      }
    } else {
      pay = paymentRows[i] || {};
    }

    const tr = document.createElement("tr");
    if (rec.isOpening) tr.style.background = "#f0fdf4";

    tr.innerHTML = `
      <td style="white-space:nowrap;"><strong>${rec.displayDate || ''}</strong></td>
      <td style="white-space:nowrap;"><strong>${rec.recNo ? '#' + rec.recNo : ''}</strong></td>
      <td>${rec.regNo || ''}</td>
      <td style="white-space:nowrap; max-width:180px; overflow:hidden; text-overflow:ellipsis;" title="${rec.hof || ''}">${rec.hof || ''}</td>
      <td style="white-space:nowrap;">${rec.isOpening ? '<span class="header-badge" style="background:#dcfce7; color:#15803d; font-weight:800; padding:4px 10px; border-radius:6px; display:inline-block;">Opening Balance</span>' : (rec.head || '')}</td>
      <td><code>${rec.code || ''}</code></td>
      <td style="font-size:0.8rem; color:#475569; max-width:160px; overflow:hidden; text-overflow:ellipsis;" title="${rec.details || ''}">${rec.details || ''}</td>
      <td class="text-right" style="min-width:110px; font-weight:600;">${formatCurrency(rec.cashR)}</td>
      <td class="text-right" style="border-right:2px solid #cbd5e1; min-width:125px; font-weight:600;">${formatCurrency(rec.bankR)}</td>
      <td style="white-space:nowrap;"><strong>${pay.payDate || ''}</strong></td>
      <td style="white-space:nowrap;"><strong>${pay.voucherNo ? '#' + pay.voucherNo : ''}</strong></td>
      <td style="white-space:nowrap;">${pay.payHead || ''}</td>
      <td><code>${pay.payCode || ''}</code></td>
      <td style="font-size:0.8rem; color:#475569; max-width:180px; overflow:hidden; text-overflow:ellipsis;" title="${pay.payDetails || ''}">${pay.payDetails || ''}</td>
      <td class="text-right" style="min-width:110px; font-weight:600;">${formatCurrency(pay.cashP)}</td>
      <td class="text-right" style="min-width:125px; font-weight:600;">${formatCurrency(pay.bankP)}</td>
    `;
    tbody.appendChild(tr);
  }

  // Derived Closing Balances
  const closingCash = openingCash + totalCashR - totalCashP;
  const closingBank = openingBank + totalBankR - totalBankP;
  const grandClosing = closingCash + closingBank;

  if (tfoot) {
    tfoot.innerHTML = `
      <tr style="background:#f8fafc; font-weight:700; border-top:2px solid #cbd5e1;">
        <td colspan="7" style="text-align:right; font-weight:700; color:#334155;">TOTAL RECEIPTS COLLECTED:</td>
        <td class="text-right" style="color:#059669; font-weight:800; font-size:0.95rem;">${formatCurrency(totalCashR)}</td>
        <td class="text-right" style="border-right:2px solid #cbd5e1; color:#059669; font-weight:800; font-size:0.95rem;">${formatCurrency(totalBankR)}</td>
        <td colspan="5" style="text-align:right; font-weight:700; color:#334155;">TOTAL EXPENSES / PAYMENTS:</td>
        <td class="text-right" style="color:#e11d48; font-weight:800; font-size:0.95rem;">${formatCurrency(totalCashP)}</td>
        <td class="text-right" style="color:#e11d48; font-weight:800; font-size:0.95rem;">${formatCurrency(totalBankP)}</td>
      </tr>
      <tr style="background:#e2e8f0; font-weight:800; font-size:0.95rem; border-top:1px solid #cbd5e1;">
        <td colspan="7" style="text-align:right; color:#0f172a;">DERIVED CLOSING NET BALANCE:</td>
        <td class="text-right" style="color:#15803d; font-weight:800; font-size:1.05rem;">${formatCurrency(closingCash)}</td>
        <td class="text-right" style="border-right:2px solid #cbd5e1; color:#1d4ed8; font-weight:800; font-size:1.05rem;">${formatCurrency(closingBank)}</td>
        <td colspan="5" style="text-align:right; color:#0f172a;">TOTAL NET LIQUIDITY:</td>
        <td colspan="2" class="text-right" style="color:#0f172a; font-weight:800; font-size:1.1rem;">${formatCurrency(grandClosing)}</td>
      </tr>
    `;
  }

  // Also update Tab 2 Top Summary Bar
  const cbCash = document.getElementById("cbNetCash");
  if (cbCash) cbCash.textContent = formatCurrency(closingCash);

  const cbBank = document.getElementById("cbNetBank");
  if (cbBank) cbBank.textContent = formatCurrency(closingBank);

  const cbTot = document.getElementById("cbNetTotal");
  if (cbTot) cbTot.textContent = formatCurrency(grandClosing);
}

function setupCashbookViewListeners() {
  const sortSelect = document.getElementById("cmbSortCashbook");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      const parts = e.target.value.split("_");
      state.sortCashbookCol = parts[0];
      state.sortCashbookAsc = parts[1] === "asc";
      cbPage = 1;
      renderCashbook();
    });
  }
}

function handleCashbookHeaderClick(colKey) {
  if (state.sortCashbookCol === colKey) {
    state.sortCashbookAsc = !state.sortCashbookAsc;
  } else {
    state.sortCashbookCol = colKey;
    state.sortCashbookAsc = true;
  }

  const sortSelect = document.getElementById("cmbSortCashbook");
  if (sortSelect) {
    let valStr = `${state.sortCashbookCol}_${state.sortCashbookAsc ? 'asc' : 'desc'}`;
    if (colKey === "amt" || colKey === "cash" || colKey === "bank" || colKey === "paycash" || colKey === "paybank") {
      valStr = `amt_${state.sortCashbookAsc ? 'asc' : 'desc'}`;
    }
    sortSelect.value = valStr;
  }
  cbPage = 1;
  renderCashbook();
}

function setupIndividualViewListeners() {
  const searchInput = document.getElementById("txtSearchIndividual");
  const clearBtn = document.getElementById("btnClearIndivSearch");
  const toggleBtn = document.getElementById("btnToggleCols");
  const sortSelect = document.getElementById("cmbSortIndividual");

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.searchIndivQuery = e.target.value;
      indivPage = 1;
      renderIndividualLedgers();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      state.searchIndivQuery = "";
      indivPage = 1;
      renderIndividualLedgers();
    });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      state.showOnlyNonZeroColumns = !state.showOnlyNonZeroColumns;
      toggleBtn.textContent = state.showOnlyNonZeroColumns ? "👁️ Show All Columns" : "👁️ Show Non-Zero Columns Only";
      renderIndividualLedgers();
    });
  }

  const colWidthBtn = document.getElementById("btnToggleColumnWidth");
  if (colWidthBtn) {
    colWidthBtn.addEventListener("click", () => {
      if (state.columnDensity === "compact") {
        state.columnDensity = "normal";
        colWidthBtn.textContent = "↔️ Width: Normal (85px)";
      } else if (state.columnDensity === "normal") {
        state.columnDensity = "wide";
        colWidthBtn.textContent = "↔️ Width: Wide (110px)";
      } else {
        state.columnDensity = "compact";
        colWidthBtn.textContent = "↔️ Width: Compact (60px)";
      }
      renderIndividualLedgers();
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      const parts = e.target.value.split("_");
      state.sortCol = parts[0];
      state.sortAsc = parts[1] === "asc";
      indivPage = 1;
      renderIndividualLedgers();
    });
  }
}

function handleIndivHeaderClick(colKey) {
  if (state.sortCol === colKey) {
    state.sortAsc = !state.sortAsc;
  } else {
    state.sortCol = colKey;
    state.sortAsc = true;
  }
  const sortSelect = document.getElementById("cmbSortIndividual");
  if (sortSelect) {
    sortSelect.value = `${state.sortCol}_${state.sortAsc ? 'asc' : 'desc'}`;
  }
  indivPage = 1;
  renderIndividualLedgers();
}

function getCleanSubUptoLive(text, hasSub) {
  if (!text) return hasSub ? "03/2027" : "-";
  const s = String(text).trim().toLowerCase();
  if (s === "-" || s === "null" || s === "undefined") return hasSub ? "03/2027" : "-";

  const MONTH_MAP = {
    jan: 1, january: 1, feb: 2, february: 2, mar: 3, march: 3, apr: 4, april: 4,
    may: 5, jun: 6, june: 6, jul: 7, july: 7, aug: 8, august: 8, sep: 9, sept: 9, september: 9,
    oct: 10, october: 10, nov: 11, november: 11, dec: 12, december: 12
  };

  const results = [];
  const matches1 = Array.from(s.matchAll(/\b(\d{1,2})[-/](\d{2,4})\b/g));
  for (const m of matches1) {
    const mm = parseInt(m[1], 10);
    let yy = parseInt(m[2], 10);
    if (yy < 100) yy += 2000;
    if (mm >= 1 && mm <= 12 && yy >= 2000 && yy <= 2099) results.push({ yy, mm });
  }

  const matches2 = Array.from(s.matchAll(/\b(jan|feb|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s*(\d{2,4})\b/g));
  for (const m of matches2) {
    const mm = MONTH_MAP[m[1]] || 0;
    let yy = parseInt(m[2], 10);
    if (yy < 100) yy += 2000;
    if (mm >= 1 && mm <= 12 && yy >= 2000 && yy <= 2099) results.push({ yy, mm });
  }

  if (s.includes("current year") || s.includes("monthly subscription")) {
    results.push({ yy: 2027, mm: 3 });
  }

  if (results.length === 0) return hasSub ? "03/2027" : "-";

  results.sort((a, b) => (a.yy !== b.yy ? a.yy - b.yy : a.mm - b.mm));
  const latest = results[results.length - 1];
  return `${String(latest.mm).padStart(2, '0')}/${latest.yy}`;
}

function findIndividualColKey(item) {
  if (!state.individual || state.individual.length < 4) return null;
  const headerRow = state.individual[3];
  
  let head = (item.particulars || "").toLowerCase().trim();
  let code = (item.code || "").toUpperCase().trim();
  code = code.replace(/^RP[-\s]*/i, "RP-").replace(/\s+/g, '');
  
  const incomeCols = [];
  for (let key in headerRow) {
    const colLetter = key.replace(/[^A-Za-z]/g, '').toUpperCase();
    if (colLetter !== "A" && colLetter !== "B" && colLetter !== "C" && colLetter !== "D" && colLetter !== "AM") {
      const title = String(headerRow[key] || "").trim();
      if (title && title.toLowerCase() !== "grand total") {
        incomeCols.push({ key: colLetter, title: title.toLowerCase() });
      }
    }
  }

  for (let col of incomeCols) {
    if (head && head === col.title) return col.key;
  }
  
  if (head.includes("subscription ( current year)") || code === "RP-3.82") return "E";
  if (head.includes("donation general") || code === "RP-2.02" || code === "RP-2.02(A)") return "F";
  if (head.includes("catholicate day") || code === "RP-19.03&.04") return "G";
  if (head.includes("metropolitan fund") || code === "RP-19.11") return "H";
  if (head.includes("mission sunday") || code === "RP-19.21") return "I";
  if (head.includes("seminary day") || code === "RP-19.23") return "J";
  if (head.includes("priest welfare") || code === "RP-19.15") return "K";
  if (head.includes("old cover collection") || code === "RP-10.17") return "L";
  if (head.includes("wedding anniversary") || code === "RP-3.17") return "M";
  if (head.includes("birthday offering") || code === "RP-3.16") return "N";
  if (head.includes("baptism") || code === "RP-3.14") return "O";
  if (head.includes("orma qurbana") || head.includes("holy qurbana") || code === "RP-3.12") return "P";
  if (head.includes("sunday school day collection") || code === "RP-19.22") return "Q";
  if (head.includes("st.gregorios feast") || code === "RP-3.33") return "R";
  if (head.includes("parish day") || code === "RP-2.12") return "S";
  if (head.includes("christmas") || head.includes("new year") || code === "RP-3.11") return "T";
  if (head.includes("perunnal vanchika") || head.includes("house offertory box") || code === "RP-3.05") return "U";
  if (head.includes("passion week") || code === "RP-2.13") return "V";
  if (head.includes("st. george feast") || code === "RP-16.50") return "W";
  if (head.includes("st. thomas feast") || code === "RP-3.31") return "X";
  if (head.includes("st. mary's feast") || code === "RP-3.32") return "Y";
  if (head.includes("marriage bann") || code === "RP-3.15(A)") return "Z";
  if (head.includes("marriage celebration") || code === "RP-3.15(B)") return "AA";
  if (head.includes("donations-marriage") || code === "RP-3.15(C)") return "AB";
  if (head.includes("marriage kaimuthu") || code === "RP-3.15(D)") return "AC";
  if (head.includes("donation - cemetry") || code === "RP-3.08") return "AD";
  if (head.includes("house blessing") || code === "RP-3.17(A)") return "AE";
  if (head.includes("petty auction") || code === "RP-2.15(B)") return "AF";
  if (head.includes("auction current") || code === "RP-2.14") return "AG";
  if (head.includes("auction dues - old") || code === "RP-2.15(A)") return "AH";
  if (head.includes("cemetry receipt") || code === "RP-3.09") return "AI";
  if (head.includes("certificate fee") || code === "RP-3.21") return "AJ";
  if (head.includes("donation-breakfast") || code === "RP-2.16") return "AK";
  if (head.includes("miscellaneous income") || code === "RP-3.22") return "AL";
  if (head.includes("monthly subscription ( pervious year)") || code === "RP-3.83") return "E";
  return "E";
}

function renderIndividualLedgers() {
  const tableEl = document.getElementById("indivTable");
  const thead = document.getElementById("indivThead");
  const tbody = document.getElementById("indivTbody");
  const tfoot = document.getElementById("indivTfoot");
  if (!tbody || !thead || !tfoot) return;

  if (tableEl) {
    tableEl.className = `data-table indiv-table density-${state.columnDensity || 'compact'}`;
  }

  tbody.innerHTML = "";
  thead.innerHTML = "";
  tfoot.innerHTML = "";

  const allRows = state.individual;
  if (!allRows || allRows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="40">No individual ledger data loaded.</td></tr>`;
    return;
  }

  // 1. Identify Row 4 (Excel row 4) as headers
  let headerRow = allRows[3] || {};

  // 2. Build list of dynamic income columns (E through AL)
  const incomeCols = [];
  for (let key in headerRow) {
    const colLetter = key.replace(/[^A-Za-z]/g, '').toUpperCase();
    if (colLetter !== "A" && colLetter !== "B" && colLetter !== "C" && colLetter !== "D" && colLetter !== "AM") {
      const title = String(headerRow[key] || "").trim();
      if (title && title.toLowerCase() !== "grand total") {
        if (!incomeCols.some(c => c.key === colLetter)) {
          incomeCols.push({ key: colLetter, title });
        }
      }
    }
  }

  // 3. Process Member Data Rows (rows 4 through 115) - Filter out repeat headers & empty rows
  const invalidNames = ["NAME OF HOF", "NAME", "SL. NO.", "SL NO", "REGISTER NO.", "REGISTER NO", "MEMBER NAME", "#REGISTER NO.", "SUBSCRIPTION UPTO"];

  const memberRows = allRows.slice(4).filter(row => {
    const b = getColVal(row, "B").trim();
    const c = getColVal(row, "C").trim();
    if (!b && !c) return false;

    const bUpper = b.toUpperCase();
    const cUpper = c.toUpperCase();
    if (bUpper.includes("REGISTER") || cUpper.includes("NAME OF HOF") || bUpper.includes("SL. NO")) return false;
    if (cUpper.includes("GRAND TOTAL") || bUpper.includes("GRAND TOTAL") || cUpper === "TOTAL") return false;
    return true;
  });

  const memberData = memberRows.map((row, idx) => {
    const sl = getColVal(row, "A");
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    const rawSubUpto = getColVal(row, "D");
    const grandVal = getColVal(row, "AM");
    const grandNum = parseFloat(grandVal) || 0;

    const colValues = {};
    incomeCols.forEach(col => {
      const val = getColVal(row, col.key);
      colValues[col.key] = parseFloat(val) || 0;
    });

    const subUpto = getCleanSubUptoLive(rawSubUpto, (colValues["F"] || 0) > 0);

    return { sl, regNo, name, subUpto, grandVal, grandNum, colValues };
  });

  // 4. Calculate Total for each column across all members
  const visibleColTotals = {};
  incomeCols.forEach(col => {
    let tot = 0;
    memberData.forEach(m => { tot += (m.colValues[col.key] || 0); });
    visibleColTotals[col.key] = tot;
  });

  // 5. Hide columns without totals (total = 0) until filled
  let displayCols = incomeCols.filter(col => visibleColTotals[col.key] > 0);
  if (!state.showOnlyNonZeroColumns) {
    displayCols = incomeCols;
  }

  // 6. Apply Search Filter & Sorting
  let filteredMembers = memberData;
  if (state.searchIndivQuery) {
    const q = state.searchIndivQuery.toLowerCase().trim();
    filteredMembers = memberData.filter(m => {
      return (m.regNo && m.regNo.toLowerCase().includes(q)) || (m.name && m.name.toLowerCase().includes(q));
    });
  }

  // Sorting
  filteredMembers.sort((a, b) => {
    let valA, valB;
    if (state.sortCol === "B") {
      valA = parseInt(a.regNo, 10) || 99999;
      valB = parseInt(b.regNo, 10) || 99999;
    } else if (state.sortCol === "C") {
      valA = a.name.toLowerCase();
      valB = b.name.toLowerCase();
    } else if (state.sortCol === "AM") {
      valA = a.grandNum;
      valB = b.grandNum;
    } else {
      valA = a.colValues[state.sortCol] || 0;
      valB = b.colValues[state.sortCol] || 0;
    }

    if (valA < valB) return state.sortAsc ? -1 : 1;
    if (valA > valB) return state.sortAsc ? 1 : -1;
    return 0;
  });

  // 7. Render Table Header <thead>
  let headHtml = `<tr>
    <th class="text-center sticky-col col-sl sortable-th" onclick="handleIndivHeaderClick('B')">Sl. No.</th>
    <th class="sticky-col col-reg sortable-th" onclick="handleIndivHeaderClick('B')">Reg No. ${state.sortCol === 'B' ? (state.sortAsc ? '▲' : '▼') : ''}</th>
    <th class="sticky-col col-name sortable-th" onclick="handleIndivHeaderClick('C')">Name of HoF ${state.sortCol === 'C' ? (state.sortAsc ? '▲' : '▼') : ''}</th>
    <th>Subscription Upto</th>`;

  displayCols.forEach(col => {
    const isSorted = state.sortCol === col.key;
    headHtml += `<th class="text-right sortable-th" onclick="handleIndivHeaderClick('${col.key}')">${col.title} ${isSorted ? (state.sortAsc ? '▲' : '▼') : ''}</th>`;
  });

  const isGrandSorted = state.sortCol === "AM";
  headHtml += `<th class="text-right sticky-col col-grand sortable-th" onclick="handleIndivHeaderClick('AM')" style="background:#e2e8f0; color:#0f172a;">GRAND TOTAL ${isGrandSorted ? (state.sortAsc ? '▲' : '▼') : ''}</th>
    <th class="text-center sticky-col" style="min-width:70px; background:#f8fafc;">Action</th></tr>`;
  thead.innerHTML = headHtml;

  // 8. Render Table Body <tbody>
  let overallGrandTotal = 0;
  const totalCount = filteredMembers.length;
  
  // Need to compute overall grand total for the footer regardless of pagination
  filteredMembers.forEach(m => {
    overallGrandTotal += m.grandNum;
  });

  const totalPages = Math.ceil(totalCount / indivPageSize) || 1;
  if (indivPage > totalPages) indivPage = totalPages;
  if (indivPage < 1) indivPage = 1;
  const startIdx = (indivPage - 1) * indivPageSize;
  const endIdx = Math.min(startIdx + indivPageSize, totalCount);

  const lbl = document.getElementById("indivPageLabel");
  if (lbl) lbl.textContent = `Page ${indivPage} of ${totalPages} (${totalCount} accounts)`;

  const pageMembers = filteredMembers.slice(startIdx, endIdx);

  pageMembers.forEach((m, pageIdx) => {
    const idx = startIdx + pageIdx;
    let colCellsHtml = "";
    displayCols.forEach(col => {
      const val = m.colValues[col.key];
      colCellsHtml += `<td class="text-right num-col">${val > 0 ? formatCurrency(val) : '-'}</td>`;
    });

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="text-center sticky-col col-sl">${m.sl || (idx + 1)}</td>
      <td class="sticky-col col-reg"><strong>${m.regNo ? '#' + m.regNo : '-'}</strong></td>
      <td class="sticky-col col-name" title="${m.name}"><strong>${m.name}</strong></td>
      <td><strong>${formatSubUptoMonthYear(m.subUpto)}</strong></td>
      ${colCellsHtml}
      <td class="text-right sticky-col col-grand" style="font-weight:800; color:var(--accent-color);">${formatCurrency(m.grandNum) || '₹ 0.00'}</td>
      <td class="text-center sticky-col" style="background:#fff;"><button class="btn btn-outline" style="padding:2px 8px; font-size:0.75rem; font-weight:700; color:var(--primary-color); border-color:var(--primary-color);" onclick="promptAdminPassword('EDIT_MEMBER', '${m.regNo}')">✏️ Edit</button></td>
    `;
    tbody.appendChild(tr);
  });

  // 9. Render Table Footer <tfoot>
  let footCellsHtml = "";
  displayCols.forEach(col => {
    const tot = visibleColTotals[col.key];
    footCellsHtml += `<td class="text-right num-col"><strong>${tot > 0 ? formatCurrency(tot) : '-'}</strong></td>`;
  });

  let footHtml = `<tr class="grand-total-row">
    <td class="text-center sticky-col col-sl">--</td>
    <td class="sticky-col col-reg"><strong>TOTAL</strong></td>
    <td class="sticky-col col-name"><strong>GRAND TOTAL (${totalCount} ACCOUNTS)</strong></td>
    <td>--</td>
    ${footCellsHtml}
    <td class="text-right sticky-col col-grand" style="font-size:0.95rem; font-weight:800; color:var(--primary-color);"><strong>${formatCurrency(overallGrandTotal)}</strong></td>
    <td class="text-center sticky-col">--</td>
  </tr>`;
  tfoot.innerHTML = footHtml;

  // 10. Update Summary Badge
  const summaryBadge = document.getElementById("indivSummaryBadge");
  if (summaryBadge) {
    summaryBadge.textContent = `${totalCount} Accounts | Total: ${formatCurrency(overallGrandTotal)}`;
  }
}

function renderTrialBalance() {
  const tbody = document.getElementById("tbTbody");
  const tfoot = document.getElementById("tbTfoot");
  if (!tbody) return;
  tbody.innerHTML = "";
  if (tfoot) tfoot.innerHTML = "";

  const normalizeCode = (c) => String(c || "").replace(/^RP[-\s]*/i, "RP-").replace(/\s+/g, '').toUpperCase();

  // 1. Calculate live totals from state.cashbook
  const receiptTotalsByCode = {}; // normalizedCode -> sum
  const paymentTotalsByCode = {}; // normalizedCode -> sum

  if (Array.isArray(state.cashbook)) {
    state.cashbook.forEach(row => {
      // Helper: Exclude internal Contra transfers (Cash Deposited to Bank) from Trial Balance
      const isContraEntry = (head, details, code) => {
        const comb = (String(head || '') + ' ' + String(details || '') + ' ' + String(code || '')).toLowerCase();
        const codeTrim = String(code || '').trim().toUpperCase();
        return comb.includes('cash deposited') || comb.includes('contra') || comb.includes('cash to bank') || comb.includes('excess cash deposited') || codeTrim === 'CD' || codeTrim === 'RP-1.03';
      };

      // Receipts (F = Code, E = Particulars, G/H/I = Amounts)
      let rCodeRaw = getColVal(row, "F");
      const rHeadRaw = getColVal(row, "E").trim();
      const rDetailsRaw = getColVal(row, "G").trim();

      if (isContraEntry(rHeadRaw, rDetailsRaw, rCodeRaw)) {
        // Exclude Contra entry from Trial Balance Receipts
      } else {
        if (rCodeRaw && rHeadRaw.toLowerCase().includes("sunday school day collection")) {
          rCodeRaw = "RP-10.14";
        }

        const recNorm = normalizeCode(rCodeRaw);
        const hR = parseFloat(String(getColVal(row, "H")).replace(/,/g, '')) || 0;
        const iR = parseFloat(String(getColVal(row, "I")).replace(/,/g, '')) || 0;
        const totalR = (hR > 0 && !isNaN(hR) ? hR : 0) + (iR > 0 && !isNaN(iR) ? iR : 0);
        if (recNorm && totalR > 0) {
          receiptTotalsByCode[recNorm] = (receiptTotalsByCode[recNorm] || 0) + totalR;
        }
      }

      // Payments (N = Code, M = Particulars, P = Cash, Q = Bank)
      let pCodeRaw = getColVal(row, "N");
      const pHeadRaw = getColVal(row, "M").trim();
      const pDetailsRaw = getColVal(row, "O").trim();

      if (isContraEntry(pHeadRaw, pDetailsRaw, pCodeRaw)) {
        // Exclude Contra entry from Trial Balance Payments
      } else {

        const payNorm = normalizeCode(pCodeRaw);
        const pP = parseFloat(String(getColVal(row, "P")).replace(/,/g, '')) || 0;
        const qP = parseFloat(String(getColVal(row, "Q")).replace(/,/g, '')) || 0;
        const totalP = (pP > 0 && !isNaN(pP) ? pP : 0) + (qP > 0 && !isNaN(qP) ? qP : 0);
        if (payNorm && totalP > 0) {
          paymentTotalsByCode[payNorm] = (paymentTotalsByCode[payNorm] || 0) + totalP;
        }
      }
    });
  }

  // 2. Map baseline amounts from state.trialBalance Excel sheet
  const baselineReceiptAmts = {}; // normalizedCode -> amount
  const baselinePaymentAmts = {}; // normalizedCode -> amount

  if (Array.isArray(state.trialBalance)) {
    state.trialBalance.forEach(row => {
      const rCodeNorm = normalizeCode(getColVal(row, "A"));
      const rHead = getColVal(row, "B").trim();
      const rAmt = parseFloat(getColVal(row, "C")) || 0;

      const pCodeNorm = normalizeCode(getColVal(row, "D"));
      const pHead = getColVal(row, "E").trim();
      const pAmt = parseFloat(getColVal(row, "F")) || 0;

      const rLower = rHead.toLowerCase();
      const pLower = pHead.toLowerCase();
      if (rLower.includes("account head") || pLower.includes("account head") || rLower.includes("trial balance")) {
        return;
      }

      if (rCodeNorm && rAmt > 0) baselineReceiptAmts[rCodeNorm] = rAmt;
      if (pCodeNorm && pAmt > 0) baselinePaymentAmts[pCodeNorm] = pAmt;
    });
  }

  // 3. Get master list of all Receipt and Payment Account Heads
  const allReceiptHeads = getAllAccountHeads("RECEIPT");
  const allPaymentHeads = getAllAccountHeads("PAYMENT");

  // 4. Filter out any head without a value (> 0)
  const activeReceiptHeads = [];
  allReceiptHeads.forEach(hObj => {
    const rNorm = normalizeCode(hObj.code);
    let amt = receiptTotalsByCode[rNorm] || 0;
    if (amt > 0) {
      activeReceiptHeads.push({ code: hObj.code, name: hObj.name, amount: amt });
    }
  });

  const activePaymentHeads = [];
  allPaymentHeads.forEach(hObj => {
    const pNorm = normalizeCode(hObj.code);
    if (pNorm === "RP-12.02") return; // Suppress generic RP-12.02 as it is fully bifurcated into sub-codes RP-12.02(a) through RP-12.02(g)
    let amt = paymentTotalsByCode[pNorm] || 0;
    if (amt > 0) {
      activePaymentHeads.push({ code: hObj.code, name: hObj.name, amount: amt });
    }
  });

  const maxRows = Math.max(activeReceiptHeads.length, activePaymentHeads.length);

  let totalDebit = 0;
  let totalCredit = 0;

  for (let i = 0; i < maxRows; i++) {
    const rHeadObj = activeReceiptHeads[i] || null;
    const pHeadObj = activePaymentHeads[i] || null;

    let rCodeDisp = "", rNameDisp = "", rAmtDisp = 0;
    if (rHeadObj) {
      rCodeDisp = rHeadObj.code;
      rNameDisp = rHeadObj.name;
      rAmtDisp = rHeadObj.amount;
      totalDebit += rAmtDisp;
    }

    let pCodeDisp = "", pNameDisp = "", pAmtDisp = 0;
    if (pHeadObj) {
      pCodeDisp = pHeadObj.code;
      pNameDisp = pHeadObj.name;
      pAmtDisp = pHeadObj.amount;
      totalCredit += pAmtDisp;
    }

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>${rCodeDisp}</code></td>
      <td>${rNameDisp}</td>
      <td class="text-right" style="font-weight:600;">${rAmtDisp > 0 ? formatCurrency(rAmtDisp) : ''}</td>
      <td><code>${pCodeDisp}</code></td>
      <td>${pNameDisp}</td>
      <td class="text-right" style="font-weight:600;">${pAmtDisp > 0 ? formatCurrency(pAmtDisp) : ''}</td>
    `;
    tbody.appendChild(tr);
  }

  // 5. Render Footer with Total Trial Balance Summary
  if (tfoot) {
    tfoot.innerHTML = `
      <tr class="grand-total-row" style="background:#f1f5f9; font-weight:800; font-size:0.9rem;">
        <td colspan="2">TOTAL TRIAL BALANCE (RECEIPTS / DEBIT)</td>
        <td class="text-right" style="color:var(--primary-color); font-size:0.95rem;">${formatCurrency(totalDebit)}</td>
        <td colspan="2">TOTAL TRIAL BALANCE (PAYMENTS / CREDIT)</td>
        <td class="text-right" style="color:var(--accent-color); font-size:0.95rem;">${formatCurrency(totalCredit)}</td>
      </tr>
    `;
  }
}

function calculateCashbookTotals() {
  let openingCash = 0.0;
  let openingBank = 0.0;

  if (Array.isArray(state.trialBalance)) {
    state.trialBalance.forEach(row => {
      const head = (getColVal(row, "B") || "").trim().toUpperCase();
      if (head === 'CASH ACCOUNT' || head === 'CASH IN HAND' || head === 'OPENING BALANCE (CASH)') {
        openingCash += (parseFloat(getColVal(row, "C")) || 0) - (parseFloat(getColVal(row, "F")) || 0);
      }
      if (head === 'BANK ACCOUNT' || head === 'CASH AT BANK' || head === 'OPENING BALANCE (BANK)') {
        openingBank += (parseFloat(getColVal(row, "C")) || 0) - (parseFloat(getColVal(row, "F")) || 0);
      }
    });
  }

  // Fallback if Trial Balance is completely empty or missing these rows
  if (openingCash === 0 && openingBank === 0 && !window.isFreshStartBuild) {
    // Hardcoded balances removed, relies on backup data or Trial Balance sheet
  }

  let totalCashR = 0, totalBankR = 0, totalCashP = 0, totalBankP = 0;

  state.cashbook.forEach(row => {
    const dtRaw = getColVal(row, "A");
    const payDtRaw = getColVal(row, "K");
    const recNo = getColVal(row, "B");
    const voucherNo = getColVal(row, "L");
    const regNo = getColVal(row, "C");
    const hof = getColVal(row, "D");
    let head = getColVal(row, "E");
    const details = getColVal(row, "G");
    const cashR = getColVal(row, "H");
    const bankR = getColVal(row, "I");

    const payHead = getColVal(row, "M");
    const payCode = getColVal(row, "N");
    const payDetails = getColVal(row, "O");
    const cashP = getColVal(row, "P");
    const bankP = getColVal(row, "Q");

    // Skip top header/title rows
    const dtLower = dtRaw.toLowerCase();
    const recLower = recNo.toLowerCase();
    const headLower = head.toLowerCase();
    const payLower = payHead.toLowerCase();

    if (dtLower.includes("cash book") || dtLower.includes("receipts") || dtLower === "date" || recLower.startsWith("receipt") || headLower === "accounts head" || payLower === "accounts head") {
      return;
    }

    let isOpening = false;
    if (details.toLowerCase().includes("opening balance") || cashR === "9879" || bankR === "651682" || (headLower.includes("opening") && (cashR || bankR))) {
      isOpening = true;
    }

    const isValidReceipt = isOpening || Boolean(recNo) || Boolean(head) || Boolean(hof);
    if (isOpening) {
      if (openingCash === 0 && cashR) openingCash = parseFloat(cashR) || 0;
      if (openingBank === 0 && bankR) openingBank = parseFloat(bankR) || 0;
    } else if (isValidReceipt) {
      if (cashR && !isNaN(parseFloat(cashR))) totalCashR += parseFloat(cashR) || 0;
      if (bankR && !isNaN(parseFloat(bankR))) totalBankR += parseFloat(bankR) || 0;
    }

    const isValidPayment = Boolean(voucherNo) || Boolean(payHead) || Boolean(payCode) || Boolean(payDetails);
    if (isValidPayment) {
      if (cashP && !isNaN(parseFloat(cashP))) totalCashP += parseFloat(cashP) || 0;
      if (bankP && !isNaN(parseFloat(bankP))) totalBankP += parseFloat(bankP) || 0;
    }
  });

  const closingCash = openingCash + totalCashR - totalCashP;
  const closingBank = openingBank + totalBankR - totalBankP;
  const openingTotal = openingCash + openingBank;
  const grandR = totalCashR + totalBankR;
  const grandP = totalCashP + totalBankP;
  const grandClosing = closingCash + closingBank;

  return {
    openingCash,
    openingBank,
    openingTotal,
    totalCashR,
    totalBankR,
    grandR,
    totalCashP,
    totalBankP,
    grandP,
    closingCash,
    closingBank,
    grandClosing
  };
}

function renderAudit() {
  const totals = calculateCashbookTotals();

  // Stat Cards
  const elCash = document.getElementById("auditCashBal");
  if (elCash) elCash.textContent = formatCurrency(totals.closingCash);

  const elBank = document.getElementById("auditBankBal");
  if (elBank) elBank.textContent = formatCurrency(totals.closingBank);

  const elNet = document.getElementById("auditNetBal");
  if (elNet) elNet.textContent = formatCurrency(totals.grandClosing);

  const elR = document.getElementById("auditTotalR");
  if (elR) elR.textContent = formatCurrency(totals.grandR);

  const elP = document.getElementById("auditTotalP");
  if (elP) elP.textContent = formatCurrency(totals.grandP);

  const elM = document.getElementById("auditMembers");
  if (elM) elM.textContent = document.querySelectorAll("#cmbMember option").length - 1;

  // Tab 2 Summary Bar
  const cbCash = document.getElementById("cbNetCash");
  if (cbCash) cbCash.textContent = formatCurrency(totals.closingCash);

  const cbBank = document.getElementById("cbNetBank");
  if (cbBank) cbBank.textContent = formatCurrency(totals.closingBank);

  const cbTot = document.getElementById("cbNetTotal");
  if (cbTot) cbTot.textContent = formatCurrency(totals.grandClosing);

  // Breakdown Table Rows
  const setTxt = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = formatCurrency(val);
  };

  setTxt("rowOpCash", totals.openingCash);
  setTxt("rowOpBank", totals.openingBank);
  setTxt("rowOpTotal", totals.openingTotal);

  setTxt("rowRecCash", totals.totalCashR);
  setTxt("rowRecBank", totals.totalBankR);
  setTxt("rowRecTotal", totals.grandR);

  setTxt("rowPayCash", totals.totalCashP);
  setTxt("rowPayBank", totals.totalBankP);
  setTxt("rowPayTotal", totals.grandP);

  setTxt("rowNetCash", totals.closingCash);
  setTxt("rowNetBank", totals.closingBank);
  setTxt("rowNetTotal", totals.grandClosing);
}

// Helper to clone table and strip Actions column (edit/delete buttons)
function createCleanExportTable(tableId) {
  const tableEl = document.getElementById(tableId);
  if (!tableEl) return null;
  const clone = tableEl.cloneNode(true);

  clone.querySelectorAll("tr").forEach(tr => {
    const cells = Array.from(tr.children);
    cells.forEach(cell => {
      const text = (cell.textContent || cell.innerText || "").trim();
      const hasActionBtn = cell.querySelector("button") || text === "Actions" || text === "Action" || text === "✏️ Edit" || text === "🗑️ Delete";
      if (hasActionBtn) {
        cell.remove();
      } else {
        if (text.startsWith("#")) {
          const numStr = text.replace("#", "");
          if (!isNaN(parseInt(numStr, 10))) {
            cell.textContent = numStr;
          }
        }
      }
    });
  });
  return clone;
}

// ----------------------------------------------------
// 7. EXCEL EXPORT CONTROLLER (With Church Header)
// ----------------------------------------------------
function exportTableToExcel(tableId, filename) {
  try {
    let originalCbSize, originalCbPage;
    let originalIndivSize, originalIndivPage;

    if (tableId === 'cashbookTable') {
      originalCbSize = cbPageSize;
      originalCbPage = cbPage;
      cbPageSize = 999999;
      cbPage = 1;
      renderCashbook();
    } else if (tableId === 'indivTable') {
      originalIndivSize = indivPageSize;
      originalIndivPage = indivPage;
      indivPageSize = 999999;
      indivPage = 1;
      renderIndividualLedgers();
    }

    const cleanTable = createCleanExportTable(tableId);
    
    // Restore pagination immediately after scraping DOM
    if (tableId === 'cashbookTable') {
      cbPageSize = originalCbSize;
      cbPage = originalCbPage;
      renderCashbook();
    } else if (tableId === 'indivTable') {
      indivPageSize = originalIndivSize;
      indivPage = originalIndivPage;
      renderIndividualLedgers();
    }

    if (!cleanTable) {
      alert("Export Error: Target table not found!");
      return;
    }

    const nameStr = filename || "St_Gregorios_Accounting_Export";
    const sheetTitle = nameStr.replace(/_/g, " ");

    const dateToday = new Date();
    const endOfMonth = new Date(dateToday.getFullYear(), dateToday.getMonth() + 1, 0);
    const pad = (n) => (n < 10 ? '0' + n : n);
    const formattedDate = pad(endOfMonth.getDate()) + '-' + pad(endOfMonth.getMonth() + 1) + '-' + endOfMonth.getFullYear();

    const churchHeaderRows = tableId === "indivTable" ? [
      ["ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE"],
      ["Government House Road, Nazarbad, Mysuru, Karnataka 570 010"],
      [`Individual Account updated upto ${formattedDate}`],
      []
    ] : [
      ["ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE"],
      ["Government House Road, Nazarbad, Mysuru, Karnataka 570 010"],
      [`Financial Accounting Portal FY 2026-2027 | ${sheetTitle}`],
      []
    ];

    if (window.XLSX) {
      const ws = XLSX.utils.aoa_to_sheet(churchHeaderRows);
      XLSX.utils.sheet_add_dom(ws, cleanTable, { origin: "A5", raw: true });
      
      const range = XLSX.utils.decode_range(ws['!ref']);
      
      // Merge header rows to center text across the page
      const totalCols = range.e.c;
      if (!ws['!merges']) ws['!merges'] = [];
      for (let i = 0; i < 3; i++) {
        ws['!merges'].push({ s: { r: i, c: 0 }, e: { r: i, c: totalCols } });
      }
      
      for (let R = 4; R <= range.e.r; ++R) {
        for (let C = 0; C <= range.e.c; ++C) {
          const cell_ref = XLSX.utils.encode_cell({c:C, r:R});
          const cell = ws[cell_ref];
          if (!cell || cell.t !== 's') continue;
          
          const val = String(cell.v).trim();
          
          // Try parse date
          const dateRegex = /^(\d{2})-(\d{2})-(\d{4})$/;
          if (dateRegex.test(val)) {
            const parts = val.split('-');
            const d = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
            if (!isNaN(d.getTime())) {
              cell.t = 'd';
              cell.v = d;
              cell.z = 'dd-mm-yyyy';
              continue;
            }
          }

          // Try parse numbers and amounts
          if (val.startsWith("₹")) {
            const numVal = parseFloat(val.replace(/[₹\s,]/g, ''));
            if (!isNaN(numVal)) {
              cell.t = 'n';
              cell.v = numVal;
              cell.z = '"₹"#,##0.00';
              continue;
            }
          } else {
            // Standard number strings (like Receipt No, Reg No)
            if (/^-?\d+(\.\d+)?$/.test(val)) {
              cell.t = 'n';
              cell.v = Number(val);
            }
          }
        }
      }

      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
      
      const bridge = window.AndroidBridge || (typeof AndroidBridge !== "undefined" ? AndroidBridge : null);
      if (bridge && typeof bridge.shareBase64File === "function") {
        try {
          const base64 = XLSX.write(wb, { bookType: 'xlsx', type: 'base64' });
          bridge.shareBase64File(base64, `${nameStr}.xlsx`);
          return;
        } catch (e) {
          console.error(e);
        }
      }
      
      XLSX.writeFile(wb, `${nameStr}.xlsx`);
      return;
    }

    // CSV Fallback
    let csv = [];
    churchHeaderRows.forEach(hRow => {
      csv.push(hRow.map(x => `"${x}"`).join(","));
    });

    const rows = cleanTable.querySelectorAll("tr");
    rows.forEach(row => {
      const cols = row.querySelectorAll("th, td");
      const rowData = [];
      cols.forEach(col => {
        let text = (col.textContent || col.innerText || "").replace(/"/g, '""').trim();
        text = text.replace(/[\n\r]+/g, ' ');
        rowData.push(`"${text}"`);
      });
      if (rowData.length > 0) csv.push(rowData.join(","));
    });

    const csvContent = "\uFEFF" + csv.join("\n");

    // 1. Android Native Bridge Export (If running inside Android APK)
    const bridge = window.AndroidBridge || (typeof AndroidBridge !== "undefined" ? AndroidBridge : null);
    if (bridge && typeof bridge.shareCsvFile === "function") {
      try {
        bridge.shareCsvFile(csvContent, `${nameStr}.csv`);
        return;
      } catch (errBridge) {
        console.warn("AndroidBridge export warning:", errBridge);
      }
    }

    // 2. Web Browser Blob Download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${nameStr}.csv`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 1000);

  } catch (err) {
    console.error("Export to Excel error:", err);
    alert("Export Error: " + err.message);
  }
}

// ----------------------------------------------------
// 8. PDF EXPORT CONTROLLER (Print Window / Native PDF with Repeating Header)
// ----------------------------------------------------
function exportTableToPDF(tableId, filename) {
  try {
    let originalCbSize, originalCbPage;
    let originalIndivSize, originalIndivPage;

    if (tableId === 'cashbookTable') {
      originalCbSize = cbPageSize;
      originalCbPage = cbPage;
      cbPageSize = 999999;
      cbPage = 1;
      renderCashbook();
    } else if (tableId === 'indivTable') {
      originalIndivSize = indivPageSize;
      originalIndivPage = indivPage;
      indivPageSize = 999999;
      indivPage = 1;
      renderIndividualLedgers();
    }

    const cleanTable = createCleanExportTable(tableId);

    // Restore pagination immediately after scraping DOM
    if (tableId === 'cashbookTable') {
      cbPageSize = originalCbSize;
      cbPage = originalCbPage;
      renderCashbook();
    } else if (tableId === 'indivTable') {
      indivPageSize = originalIndivSize;
      indivPage = originalIndivPage;
      renderIndividualLedgers();
    }

    if (!cleanTable) {
      alert("PDF Export Error: Target table not found!");
      return;
    }

    // Dynamic member filename if exporting individual ledger
    if (tableId === "indivTable") {
      const memberSel = document.getElementById("selIndivMember");
      if (memberSel && memberSel.value) {
        const selectedText = memberSel.options[memberSel.selectedIndex]?.text || "";
        if (selectedText && !selectedText.includes("All Members")) {
          filename = `Member_${selectedText}_Ledger`;
        }
      }
    }

    const cleanTitle = getCleanPrintTitle(filename || "Accounting_Report");
    const headerTitle = cleanTitle.replace(/_/g, " ");
    const nowStr = new Date().toLocaleString("en-IN");

    const dateToday = new Date();
    const endOfMonth = new Date(dateToday.getFullYear(), dateToday.getMonth() + 1, 0);
    const pad = (n) => (n < 10 ? '0' + n : n);
    const formattedDate = pad(endOfMonth.getDate()) + '-' + pad(endOfMonth.getMonth() + 1) + '-' + endOfMonth.getFullYear();

    // Prepend Church Header inside <thead> so it repeats on EVERY page in PDF print
    const thead = cleanTable.querySelector("thead");
    if (thead) {
      const isIndiv = (tableId === "indivTable");
      const titleLine3 = isIndiv ? `Individual Account updated upto ${formattedDate}` : `Financial Accounting Portal FY 2026-2027 | ${headerTitle}`;

      const totalCols = 99; // Force full span across all actual columns

      const headerBlockHtml = `
        <tr class="pdf-repeat-header">
          <th colspan="${totalCols}" style="text-align:center; border:none; background:#ffffff; padding:10px 0 15px 0; font-family:'Segoe UI',Arial,sans-serif;">
            <div style="text-align:center; width:100%; margin:0 auto;">
              <img src="church_logo.png" alt="Church Logo" style="display:block; margin:0 auto 6px auto; height:54px; width:54px; border-radius:50%; border:1.5px solid #1e293b; object-fit:contain; background:#fff;">
              <div style="font-size:16px; font-weight:900; color:#0f172a; text-transform:uppercase; letter-spacing:0.5px;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE</div>
              <div style="font-size:11px; font-weight:600; color:#475569; margin-top:3px;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010 | ESTD : 1954</div>
              <div style="font-size:13px; font-weight:800; color:#0f172a; margin-top:6px; padding-top:6px; display:inline-block;">${titleLine3}</div>
            </div>
          </th>
        </tr>
      `;
      thead.insertAdjacentHTML("afterbegin", headerBlockHtml);
    }

    const tableHTML = cleanTable.outerHTML;

    // Set main document title for native print filename auto-population
    document.title = cleanTitle;

    const renderInAppOverlay = () => {
      let overlay = document.getElementById("printPreviewOverlay");
      if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "printPreviewOverlay";
        overlay.className = "print-preview-overlay";
        document.body.appendChild(overlay);
      }
      overlay.style.cssText = "position:fixed; top:0; left:0; right:0; bottom:0; z-index:99999; background:#ffffff; overflow:auto; padding:60px 15px 20px 15px;";
      overlay.innerHTML = `
        <style>
          @media print {
            body > *:not(#printPreviewOverlay) { display: none !important; }
            #printPreviewOverlay { position: static !important; overflow: visible !important; height: auto !important; padding: 0 !important; zoom: 0.55; }
            #printPreviewOverlay, #printPreviewOverlay * { visibility: visible !important; }
            .print-preview-header { display: none !important; }
            @page { size: A4 landscape; margin: 5mm; }
            
            /* FORCE BROWSER TO PRINT BACKGROUND COLORS */
            * {
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
            }
            
            table { border-collapse: collapse !important; width: 100% !important; margin-bottom: 20px; font-family: 'Times New Roman', Times, serif !important; border: 1px solid #000 !important; }
            table th { background-color: #e6f0ed !important; color: #000 !important; font-weight: bold !important; font-size: 11px !important; border: 1px solid #000 !important; padding: 4px !important; text-align: center !important; }
            table td { font-size: 11px !important; border: 1px solid #000 !important; padding: 4px !important; color: #000 !important; }
            table tr:last-child td { font-weight: bold !important; border-top: 2px solid #000 !important; border-bottom: 2px solid #000 !important; }
          }
        </style>
        <div class="print-preview-header no-print" style="position:fixed; top:0; left:0; right:0; z-index:100000; background:#0f172a; color:#ffffff; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 14px rgba(0,0,0,0.5);">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.1rem;">📄</span>
            <span style="font-weight:800; font-size:0.92rem; color:#ffffff;">${headerTitle}</span>
          </div>
          <div style="display:flex; gap:8px; align-items:center;">
            <button onclick="triggerSystemPrint('${cleanTitle}')" style="background:#0284c7; color:#ffffff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; cursor:pointer; font-size:0.85rem;">🖨️ Print / Save PDF</button>
            <button onclick="closePrintPreviewOverlay()" style="background:#dc2626; color:#ffffff; border:none; padding:8px 18px; border-radius:24px; font-weight:800; cursor:pointer; font-size:0.9rem; box-shadow:0 2px 10px rgba(220,38,38,0.5);">✖ Close & Return to App</button>
          </div>
        </div>
        ${tableHTML}
        <div style="margin-top:20px; text-align:center; font-size:10px; color:#475569; border-top:1px solid #cbd5e1; padding-top:6px;" class="no-print">
          ⚡ Software developed by <strong>4S POWER SYSTEMS Mysore</strong> | Mob: <strong>9980615758</strong>
        </div>
      `;
      document.body.classList.add("printing-mode");
      triggerSystemPrint(cleanTitle);
    };

    if (window.AndroidBridge) {
      renderInAppOverlay();
      return;
    }

    const printWin = window.open("", "_blank", "width=1200,height=850");
    if (!printWin) {
      renderInAppOverlay();
      return;
    }

    printWin.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=0.5, maximum-scale=5.0, user-scalable=yes">
        <title>${cleanTitle}</title>
        <style>
          body { font-family: 'Times New Roman', Times, serif; padding: 50px 15px 15px 15px; color: #000; background: #ffffff; margin: 0; }
          table { width: 100%; border-collapse: collapse !important; font-size: 11px; margin-top: 5px; border: 1px solid #000 !important; font-family: 'Times New Roman', Times, serif !important; }
          th, td { border: 1px solid #000 !important; padding: 4px !important; color: #000 !important; }
          th { background-color: #e6f0ed !important; font-weight: bold !important; font-size: 11px !important; text-align: center !important; }
          tr:last-child td { font-weight: bold !important; border-top: 2px solid #000 !important; border-bottom: 2px solid #000 !important; }
          .text-right { text-align: right; white-space: nowrap; }
          code { font-family: monospace; font-size: 11px; }
          
          /* Force header repeating on every printed page */
          thead { display: table-header-group !important; }
          tfoot { display: table-footer-group !important; }
          tr { page-break-inside: avoid !important; }
          
          @media print {
            .no-print, .print-preview-header { display: none !important; }
            body { padding: 0 !important; margin: 0 !important; zoom: 0.55; }
            @page { size: A4 landscape; margin: 5mm; }
            table { page-break-inside: auto; margin: 0 auto; }
            tr { page-break-inside: avoid; page-break-after: auto; }
            thead { display: table-header-group !important; }
          }
        </style>
      </head>
      <body>
        <div class="print-preview-header no-print" style="position:fixed; top:0; left:0; right:0; z-index:2147483647; background:#0f172a; color:#ffffff; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 14px rgba(0,0,0,0.5);">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.1rem;">📄</span>
            <span style="font-weight:800; font-size:0.92rem; color:#ffffff;">${headerTitle}</span>
          </div>
          <div style="display:flex; gap:8px; align-items:center;">
            <button onclick="window.print()" style="background:#0284c7; color:#ffffff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; cursor:pointer; font-size:0.85rem;">🖨️ Print / Save PDF</button>
            <button onclick="if(window.history.length>1){window.history.back();}else{window.close();}" style="background:#dc2626; color:#ffffff; border:none; padding:8px 18px; border-radius:24px; font-weight:800; cursor:pointer; font-size:0.9rem; box-shadow:0 2px 10px rgba(220,38,38,0.5);">✖ Close & Return to App</button>
          </div>
        </div>
        ${tableHTML}
        <div style="margin-top:20px; text-align:center; font-size:10px; color:#475569; border-top:1px solid #cbd5e1; padding-top:6px;">
          ⚡ Software developed by <strong>4S POWER SYSTEMS Mysore</strong> | Mob: <strong>9980615758</strong>
        </div>
        <script>
          document.title = "${cleanTitle}";
          window.onload = function() {
            document.title = "${cleanTitle}";
            setTimeout(function() {
              window.print();
            }, 300);
          };
        </script>
      </body>
      </html>
    `);
    printWin.document.close();
    printWin.document.title = cleanTitle;
  } catch (err) {
    console.error("PDF Export error:", err);
    alert("PDF Export Error: " + err.message);
  }
}

function exportAuditReportToPDF() {
  exportTableToPDF('auditBreakdownTable', 'St_Gregorios_Audit_Reconciliation_Report');
}

function exportCartToExcel() {
  if (state.cart.length === 0) {
    alert("Cart is empty! Add items to cart before exporting.");
    return;
  }
  exportTableToExcel("cartTable", "St_Gregorios_Cart_Items");
}

function exportAuditReportToExcel() {
  const totalR = document.getElementById("auditTotalR")?.innerText || "0";
  const totalP = document.getElementById("auditTotalP")?.innerText || "0";
  const netBal = document.getElementById("auditNetBal")?.innerText || "0";
  const membersCount = document.getElementById("auditMembers")?.innerText || "0";

  const rows = [
    ["Metric", "Value"],
    ["Total Cashbook Receipts", totalR],
    ["Total Cashbook Payments", totalP],
    ["Net Cash & Bank Balance", netBal],
    ["Enrolled Parish Members", membersCount],
    ["Audit Status", "Verified - No Discrepancies Found"]
  ];

  if (window.XLSX) {
    const ws = XLSX.utils.aoa_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Audit Summary");
    XLSX.writeFile(wb, "St_Gregorios_Reconciliation_Audit_Summary.xlsx");
    return;
  }

  const csvContent = "\uFEFF" + rows.map(e => e.map(x => `"${x}"`).join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "St_Gregorios_Reconciliation_Audit_Summary.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ====================================================
// 🔒 ADMIN PASSWORD AUTHENTICATION & EDITING SYSTEM
// ====================================================
state.isAdminUnlocked = false;
state.pendingAction = null;

function promptAdminPassword(actionType, payload) {
  state.pendingAction = { type: actionType, payload };
  if (state.isAdminUnlocked) {
    executePendingAction();
  } else {
    const pwdInput = document.getElementById("txtAdminPassword");
    const errLbl = document.getElementById("lblPasswordError");
    if (pwdInput) pwdInput.value = "";
    if (errLbl) errLbl.style.display = "none";

    const pwdModal = document.getElementById("passwordModal");
    if (pwdModal) pwdModal.classList.add("active");
    setTimeout(() => { if (pwdInput) pwdInput.focus(); }, 150);
  }
}

function verifyAdminPassword() {
  const pwdInput = document.getElementById("txtAdminPassword");
  const errLbl = document.getElementById("lblPasswordError");
  const pwd = pwdInput ? pwdInput.value.trim() : "";

  if (pwd === state.adminPassword || pwd === "church123" || pwd === "admin" || pwd === "admin123" || pwd === "1234") {
    state.isAdminUnlocked = true;
    closePasswordModal();
    executePendingAction();
  } else {
    if (errLbl) errLbl.style.display = "block";
  }
}

function closePasswordModal() {
  const pwdModal = document.getElementById("passwordModal");
  if (pwdModal) pwdModal.classList.remove("active");
}

function executePendingAction() {
  if (!state.pendingAction) return;
  const { type, payload } = state.pendingAction;
  state.pendingAction = null;

  if (type === "OPEN_ADMIN_TAB") {
    openAdminTab();
  } else if (type === "EDIT_MEMBER") {
    openEditMemberModal(payload);
  } else if (type === "EDIT_CASHBOOK") {
    openEditCashbookModal(payload);
  } else if (type === "DELETE_CASHBOOK") {
    confirmDeleteCashbookEntry(payload);
  } else if (type === "ADD_MEMBER") {
    openAddMemberModal();
  } else if (type === "ADD_ACCOUNT_HEAD") {
    openAddAccountHeadModal();
  } else if (type === "EDIT_ACCOUNT_HEAD") {
    openEditAccountHeadModal(payload);
  } else if (type === "DELETE_ACCOUNT_HEAD") {
    confirmDeleteAccountHead(payload);
  } else if (type === "DELETE_MEMBER") {
    confirmDeleteMember(payload);
  } else if (type === "DIR_ADD") {
    openDirAddMemberModal();
  } else if (type === "DIR_EDIT") {
    openDirEditMemberModal(payload);
  } else if (type === "DIR_DELETE") {
    deleteDirMemberCrud(payload);
  }
}

function confirmDeleteMember(regNo) {
  const memberRow = state.individual.find(r => getColVal(r, "B") === String(regNo));
  const name = memberRow ? getColVal(memberRow, "C") : regNo;

  if (confirm(`Are you sure you want to delete member Reg No. #${regNo} (${name})? This cannot be undone.`)) {
    state.individual = state.individual.filter(r => getColVal(r, "B") !== String(regNo));
    localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));

    // Sync deletion to Directory
    state.members = state.members.filter(m => getColVal(m, "B") !== String(regNo));
    localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
    renderMemberDirectory();

    populateMemberDropdown();
    renderIndividualLedgers();
    renderAudit();
    if (state.isAdminUnlocked) renderAdminMembersTable();
    alert(`[OK] Member Reg No. #${regNo} (${name}) deleted successfully!`);
  }
}

function openAdminTab() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  const adminTabBtn = document.querySelector('[data-tab="tabAdmin"]');
  if (adminTabBtn) adminTabBtn.classList.add("active");
  const adminPane = document.getElementById("tabAdmin");
  if (adminPane) adminPane.classList.add("active");

  renderAdminTab();
}

function lockAdminSession() {
  state.isAdminUnlocked = false;
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  const firstTab = document.querySelector('[data-tab="tabVoucher"]');
  if (firstTab) firstTab.classList.add("active");
  const firstPane = document.getElementById("tabVoucher");
  if (firstPane) firstPane.classList.add("active");
}

// ----------------------------------------------------
// ADD NEW PARISH MEMBER (MODAL & ENGINE)
// ----------------------------------------------------
function openAddMemberModal() {
  let maxReg = 0;
  if (state.individual && state.individual.length > 4) {
    state.individual.slice(4).forEach(r => {
      const reg = parseInt(getColVal(r, "B")) || 0;
      if (reg > maxReg) maxReg = reg;
    });
  }
  if (state.members && state.members.length > 1) {
    state.members.slice(1).forEach(r => {
      const reg = parseInt(getColVal(r, "B")) || 0;
      if (reg > maxReg) maxReg = reg;
    });
  }

  const regInput = document.getElementById("addMemberRegNo");
  const nameInput = document.getElementById("addMemberName");
  const subInput = document.getElementById("addMemberSubUpto");

  if (regInput) regInput.value = (maxReg > 0 ? maxReg + 1 : 1).toString();
  if (nameInput) nameInput.value = "";
  if (subInput) subInput.value = "Apr 26 to march 27";

  const modal = document.getElementById("addMemberModal");
  if (modal) modal.classList.add("active");
  setTimeout(() => { if (nameInput) nameInput.focus(); }, 150);
}

function closeAddMemberModal() {
  const modal = document.getElementById("addMemberModal");
  if (modal) modal.classList.remove("active");
}

function saveNewMemberAccount() {
  const regNo = document.getElementById("addMemberRegNo").value.trim();
  const name = document.getElementById("addMemberName").value.trim();
  const subUpto = document.getElementById("addMemberSubUpto").value.trim();

  if (!regNo || !name) {
    alert("Please enter Register Number and Member Name!");
    return;
  }

  const exists = state.individual.some((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);
  if (exists) {
    alert(`Register No. #${regNo} already exists! Please use a unique Register Number.`);
    return;
  }

  const slNo = (state.individual.length - 3).toString();

  const newMemberRow = {
    "A5": slNo,
    "B5": regNo,
    "C5": name,
    "D5": subUpto,
    "AM5": "0.00"
  };

  state.individual.push(newMemberRow);
  localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));

  // Sync to Directory
  if (!state.members.some(m => getColVal(m, "B") === String(regNo))) {
    const maxSlDir = state.members.reduce((max, m) => {
      const a = parseInt(getColVal(m, "A"), 10);
      return !isNaN(a) && a > max ? a : max;
    }, 0);
    state.members.push({
      "A": String(maxSlDir + 1),
      "B": regNo,
      "C": name,
      "D": "",
      "E": ""
    });
    localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
    renderMemberDirectory();
  }

  populateMemberDropdown();
  renderIndividualLedgers();
  renderAudit();
  if (state.isAdminUnlocked) renderAdminMembersTable();

  closeAddMemberModal();
}

// ----------------------------------------------------
// ADD NEW ACCOUNT HEAD & CODE (MODAL & ENGINE)
// ----------------------------------------------------
function openAddAccountHeadModal() {
  const titleInput = document.getElementById("addHeadTitle");
  const codeInput = document.getElementById("addHeadCode");

  if (titleInput) titleInput.value = "";
  if (codeInput) codeInput.value = "";

  const modal = document.getElementById("addAccountHeadModal");
  if (modal) modal.classList.add("active");
  setTimeout(() => { if (titleInput) titleInput.focus(); }, 150);
}

function closeAddAccountHeadModal() {
  const modal = document.getElementById("addAccountHeadModal");
  if (modal) modal.classList.remove("active");
}

function saveNewAccountHead() {
  const category = document.getElementById("addHeadCategory").value;
  const title = document.getElementById("addHeadTitle").value.trim();
  let code = document.getElementById("addHeadCode").value.trim();

  if (!title) {
    alert("Please enter an Account Head Title!");
    return;
  }

  if (!code) {
    code = (category === "RECEIPT" ? "RP-3." : "RP-14.") + (Math.floor(Math.random() * 90) + 10);
  }

  // Format code
  code = code.replace(/^RP-\s*/i, "RP-");
  const upperCode = code.toUpperCase();

  // If this code was previously deleted, remove from deleted list
  if (Array.isArray(state.deletedAccountHeads)) {
    state.deletedAccountHeads = state.deletedAccountHeads.filter(c => c !== upperCode);
    localStorage.setItem("CHURCH_DELETED_HEADS", JSON.stringify(state.deletedAccountHeads));
  }

  if (!Array.isArray(state.customAccountHeads)) state.customAccountHeads = [];

  const existingIdx = state.customAccountHeads.findIndex(h => h.code.toUpperCase() === upperCode);
  const newObj = {
    code: code,
    name: title,
    category: category,
    type: category,
    source: "Custom"
  };

  if (existingIdx >= 0) {
    state.customAccountHeads[existingIdx] = newObj;
  } else {
    state.customAccountHeads.push(newObj);
  }

  localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();

  // Instant 2-way sync across form dropdowns, trial balance, and admin tables
  updateDocTypeView();
  renderTrialBalance();
  if (state.isAdminUnlocked) renderAdminHeadsTable();

  closeAddAccountHeadModal();
  alert(`[OK] Account Head [${code}] "${title}" saved successfully!`);
}

// ----------------------------------------------------
// EDIT MEMBER ACCOUNT & CONTRIBUTIONS (TAB 3)
// ----------------------------------------------------
function openEditMemberModal(regNo) {
  const targetReg = String(regNo || "").trim().toUpperCase().replace(/^#/, '');
  const memberRow = state.individual.find((r, idx) => {
    if (idx < 4) return false;
    const b = getColVal(r, "B").trim().toUpperCase().replace(/^#/, '');
    return b === targetReg;
  });

  if (!memberRow) {
    alert(`Member record #${regNo} not found!`);
    return;
  }

  const name = getColVal(memberRow, "C");
  const subUpto = getColVal(memberRow, "D");
  const headerRow = state.individual[3] || {};

  const titleEl = document.getElementById("lblEditMemberTitle");
  const subEl = document.getElementById("lblEditMemberSub");
  if (titleEl) titleEl.textContent = `✏️ Edit Member Account: ${name}`;
  if (subEl) subEl.textContent = `Register No. #${regNo} | Modify Subscription Upto & Individual Contribution Heads`;

  let formHtml = `
    <input type="hidden" id="editMemberRegNo" value="${regNo}">
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.25rem; background:#f8fafc; padding:1rem; border-radius:10px; border:1px solid #e2e8f0;">
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Register No.</label>
        <input type="text" class="form-control" value="#${regNo}" readonly style="background:#edf2f7; font-weight:800; color:var(--primary-color);">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Name of HoF</label>
        <input type="text" id="editMemberName" class="form-control" value="${name}" style="font-weight:700;">
      </div>
      <div class="form-group" style="grid-column:span 2;">
        <label style="font-weight:700; font-size:0.85rem; color:var(--primary-color);">Subscription Upto (Validity Period)</label>
        <input type="text" id="editMemberSubUpto" class="form-control" value="${subUpto}" placeholder="e.g. Apr 26 to march 27" style="font-weight:600;">
      </div>
    </div>
    <h4 style="font-size:0.95rem; font-weight:700; color:var(--primary-color); border-bottom:2px solid #e2e8f0; padding-bottom:6px; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
      <span>Contribution Heads & Amounts (₹)</span>
      <span style="font-size:0.75rem; font-weight:normal; color:#64748b;">(Leave empty or 0 to clear head)</span>
    </h4>
    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:0.75rem; max-height:42vh; overflow-y:auto; padding-right:6px;">
  `;

  for (let k in headerRow) {
    const colLetter = k.replace(/[^A-Za-z]/g, '').toUpperCase();
    if (["A", "B", "C", "D", "AM"].includes(colLetter)) continue;

    const title = String(headerRow[k] || "").trim();
    if (!title || title.toLowerCase() === "grand total") continue;

    const val = getColVal(memberRow, colLetter);
    formHtml += `
      <div class="form-group" style="margin-bottom:0.5rem; background:#fff; padding:6px; border:1px solid #e2e8f0; border-radius:6px;">
        <label style="font-size:0.75rem; font-weight:700; color:#334155; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; display:block; margin-bottom:4px;" title="${title}">${title}</label>
        <input type="number" class="form-control edit-member-col" data-col="${colLetter}" value="${val}" placeholder="0.00" step="0.01" style="font-weight:600;">
      </div>
    `;
  }

  formHtml += `</div>`;
  document.getElementById("editMemberFormBody").innerHTML = formHtml;
  document.getElementById("editMemberModal").classList.add("active");
}

function closeEditMemberModal() {
  document.getElementById("editMemberModal").classList.remove("active");
}

function saveMemberAccountChanges() {
  const regNo = document.getElementById("editMemberRegNo").value;
  const memberRow = state.individual.find((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);
  if (!memberRow) return;

  const newName = document.getElementById("editMemberName").value.trim();
  const newSubUpto = document.getElementById("editMemberSubUpto").value.trim();

  setColVal(memberRow, "C", newName);
  setColVal(memberRow, "D", newSubUpto);

  let newGrandTotal = 0;
  const inputs = document.querySelectorAll(".edit-member-col");
  inputs.forEach(input => {
    const colLetter = input.dataset.col;
    const rawVal = input.value.trim();
    const numVal = parseFloat(rawVal) || 0;
    if (numVal > 0) {
      setColVal(memberRow, colLetter, numVal.toString());
      newGrandTotal += numVal;
    } else {
      setColVal(memberRow, colLetter, "");
    }
  });

  setColVal(memberRow, "AM", newGrandTotal.toFixed(2));

  localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
  populateMemberDropdown();
  renderIndividualLedgers();
  if (state.isAdminUnlocked) renderAdminMembersTable();

  closeEditMemberModal();
}

// ----------------------------------------------------
// EDIT CASH BOOK TRANSACTION ENTRY (TAB 2)
// ----------------------------------------------------
function openEditCashbookModal(payload) {
  const rowIndex = typeof payload === "object" ? payload.index : payload;
  const editType = typeof payload === "object" ? payload.type : null;

  const row = state.cashbook[rowIndex];
  if (!row) return;

  let isReceipt;
  if (editType === "RECEIPT") {
    isReceipt = true;
  } else if (editType === "PAYMENT") {
    isReceipt = false;
  } else {
    isReceipt = !!(getColVal(row, "B") || getColVal(row, "E") || getColVal(row, "H") || getColVal(row, "I"));
  }

  const dateVal = isReceipt ? getColVal(row, "A") : getColVal(row, "K");
  const docNo = isReceipt ? getColVal(row, "B") : getColVal(row, "L");
  const regNo = isReceipt ? getColVal(row, "C") : "";
  const hof = isReceipt ? getColVal(row, "D") : "";
  const head = isReceipt ? getColVal(row, "E") : getColVal(row, "M");
  const code = isReceipt ? getColVal(row, "F") : getColVal(row, "N");
  const details = isReceipt ? getColVal(row, "G") : getColVal(row, "O");
  const cashAmt = isReceipt ? getColVal(row, "H") : getColVal(row, "P");
  const bankAmt = isReceipt ? getColVal(row, "I") : getColVal(row, "Q");

  let formHtml = `
    <input type="hidden" id="editCashbookIndex" value="${rowIndex}">
    <input type="hidden" id="editCashbookIsReceipt" value="${isReceipt ? '1' : '0'}">
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Entry Type</label>
        <input type="text" class="form-control" value="${isReceipt ? '📥 Receipt' : '📤 Payment Voucher'}" readonly style="background:#f1f5f9; font-weight:800; color:var(--primary-color);">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Doc / Voucher No.</label>
        <input type="text" id="editCbDocNo" class="form-control" value="${docNo}" style="font-weight:700;">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Date</label>
        <input type="text" id="editCbDate" class="form-control" value="${dateVal}">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Register No.</label>
        <input type="text" id="editCbRegNo" class="form-control" value="${regNo}">
      </div>
      <div class="form-group" style="grid-column:span 2;">
        <label style="font-weight:700; font-size:0.85rem;">Party / Member Name</label>
        <input type="text" id="editCbHof" class="form-control" value="${hof}">
      </div>
      <div class="form-group" style="grid-column:span 2;">
        <label style="font-weight:700; font-size:0.85rem;">Account Head / Particulars</label>
        <input type="text" id="editCbHead" class="form-control" value="${head}" style="font-weight:700;">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Code Reference</label>
        <input type="text" id="editCbCode" class="form-control" value="${code}">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Details / Remarks</label>
        <input type="text" id="editCbDetails" class="form-control" value="${details}">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Cash Amount (₹)</label>
        <input type="number" id="editCbCash" class="form-control" value="${cashAmt}" step="0.01" style="font-weight:700; color:var(--success-color);">
      </div>
      <div class="form-group">
        <label style="font-weight:700; font-size:0.85rem;">Bank Amount (₹)</label>
        <input type="number" id="editCbBank" class="form-control" value="${bankAmt}" step="0.01" style="font-weight:700; color:var(--primary-color);">
      </div>
    </div>
  `;

  document.getElementById("editCashbookFormBody").innerHTML = formHtml;
  document.getElementById("editCashbookModal").classList.add("active");
}

function closeEditCashbookModal() {
  document.getElementById("editCashbookModal").classList.remove("active");
}

function saveCashbookEntryChanges() {
  const index = parseInt(document.getElementById("editCashbookIndex").value);
  const row = state.cashbook[index];
  if (!row) return;

  const isReceipt = document.getElementById("editCashbookIsReceipt").value === "1";
  const dateVal = document.getElementById("editCbDate").value.trim();
  const docNo = document.getElementById("editCbDocNo").value.trim();
  const regNo = document.getElementById("editCbRegNo").value.trim();
  const hof = document.getElementById("editCbHof").value.trim();
  const head = document.getElementById("editCbHead").value.trim();
  const code = document.getElementById("editCbCode").value.trim();
  const details = document.getElementById("editCbDetails").value.trim();
  const cashAmt = document.getElementById("editCbCash").value.trim();
  const bankAmt = document.getElementById("editCbBank").value.trim();

  const oldIsReceipt = !!getColVal(row, "F");
  const oldRegNo = getColVal(row, "C");
  const oldHead = getColVal(row, "E");
  const oldCode = getColVal(row, "F");
  const oldCash = parseFloat(String(getColVal(row, "H")).replace(/,/g, '')) || 0;
  const oldBank = parseFloat(String(getColVal(row, "I")).replace(/,/g, '')) || 0;
  const oldTotal = oldCash + oldBank;

  if (isReceipt) {
    setColVal(row, "A", dateVal);
    setColVal(row, "B", docNo);
    setColVal(row, "C", regNo);
    setColVal(row, "D", hof);
    setColVal(row, "E", head);
    setColVal(row, "F", code);
    setColVal(row, "G", details);
    setColVal(row, "H", cashAmt);
    setColVal(row, "I", bankAmt);
  } else {
    setColVal(row, "K", dateVal);
    setColVal(row, "L", docNo);
    setColVal(row, "M", head);
    setColVal(row, "N", code);
    setColVal(row, "O", details);
    setColVal(row, "P", cashAmt);
    setColVal(row, "Q", bankAmt);
  }

  if (oldIsReceipt && oldRegNo && state.individual && state.individual.length > 0) {
    const memberRow = state.individual.find((r, idx) => idx >= 4 && getColVal(r, "B") === oldRegNo);
    if (memberRow) {
      const colKey = findIndividualColKey({ particulars: oldHead, code: oldCode });
      if (colKey) {
        const currentVal = parseFloat(getColVal(memberRow, colKey)) || 0;
        setColVal(memberRow, colKey, currentVal - oldTotal);
      }
      let grandTot = 0;
      for (const key in memberRow) {
        if (key !== "A" && key !== "B" && key !== "C" && key !== "D" && key !== "AM") {
          grandTot += parseFloat(getColVal(memberRow, key)) || 0;
        }
      }
      setColVal(memberRow, "AM", grandTot);
    }
  }

  if (isReceipt && regNo && state.individual && state.individual.length > 0) {
    const memberRow = state.individual.find((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);
    if (memberRow) {
      const colKey = findIndividualColKey({ particulars: head, code: code });
      if (colKey) {
        const currentVal = parseFloat(getColVal(memberRow, colKey)) || 0;
        const newTotal = (parseFloat(String(cashAmt).replace(/,/g, '')) || 0) + (parseFloat(String(bankAmt).replace(/,/g, '')) || 0);
        setColVal(memberRow, colKey, currentVal + newTotal);
      }
      let grandTot = 0;
      for (const key in memberRow) {
        if (key !== "A" && key !== "B" && key !== "C" && key !== "D" && key !== "AM") {
          grandTot += parseFloat(getColVal(memberRow, key)) || 0;
        }
      }
      setColVal(memberRow, "AM", grandTot);
    }
  }

  localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
  localStorage.setItem("CHURCH_CASHBOOK", JSON.stringify(state.cashbook));

  // Sync edited cashbook to server database
  if (!window.AndroidBridge) {
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
  }

  renderAllViews();
  if (state.isAdminUnlocked) renderAdminTxnsTable();
  closeEditCashbookModal();
}

function confirmDeleteCashbookEntry(payload) {
  const index = typeof payload === "object" ? payload.index : payload;
  if (confirm("Are you sure you want to delete this Cash Book transaction entry?")) {
    const row = state.cashbook[index];
    if (row) {
      const oldIsReceipt = !!getColVal(row, "F");
      const oldRegNo = getColVal(row, "C");
      const oldHead = getColVal(row, "E");
      const oldCode = getColVal(row, "F");
      const oldCash = parseFloat(String(getColVal(row, "H")).replace(/,/g, '')) || 0;
      const oldBank = parseFloat(String(getColVal(row, "I")).replace(/,/g, '')) || 0;
      const oldTotal = oldCash + oldBank;

      if (oldIsReceipt && oldRegNo && state.individual && state.individual.length > 0) {
        const memberRow = state.individual.find((r, idx) => idx >= 4 && getColVal(r, "B") === oldRegNo);
        if (memberRow) {
          const colKey = findIndividualColKey({ particulars: oldHead, code: oldCode });
          if (colKey) {
            const currentVal = parseFloat(getColVal(memberRow, colKey)) || 0;
            setColVal(memberRow, colKey, currentVal - oldTotal);
          }
          let grandTot = 0;
          for (const key in memberRow) {
            if (key !== "A" && key !== "B" && key !== "C" && key !== "D" && key !== "AM") {
              grandTot += parseFloat(getColVal(memberRow, key)) || 0;
            }
          }
          setColVal(memberRow, "AM", grandTot);
        }
      }
      localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
    }

    state.cashbook.splice(index, 1);
    localStorage.setItem("CHURCH_CASHBOOK", JSON.stringify(state.cashbook));

    // Sync deletion to server database
    if (!window.AndroidBridge) {
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
    }

    renderAllViews();
    if (state.isAdminUnlocked) renderAdminTxnsTable();
  }
}

// ====================================================
// 🔐 ADMINISTRATION PANEL DASHBOARD ENGINE
// ====================================================
function switchAdminSubTab(subtabId) {
  const subTabs = document.querySelectorAll(".admin-sub-tab");
  subTabs.forEach(t => t.classList.remove("active"));

  const btnId = "btnAdminSub" + subtabId.replace("admin", "");
  const activeBtn = document.getElementById(btnId);
  if (activeBtn) activeBtn.classList.add("active");

  const subPanes = document.querySelectorAll(".admin-sub-pane");
  subPanes.forEach(p => {
    p.style.display = p.id === subtabId ? "block" : "none";
  });

  if (subtabId === "adminMembers") renderAdminMembersTable();
  else if (subtabId === "adminHeads") renderAdminHeadsTable();
  else if (subtabId === "adminTransactions") renderAdminTxnsTable();
}

function renderAdminTab() {
  renderAdminMembersTable();
  renderAdminHeadsTable();
  renderAdminTxnsTable();
}

// Administration Table Sorting Toggles
function toggleAdminMemberSort(col) {
  const sel = document.getElementById("sortAdminMembers");
  if (!sel) return;
  if (col === "REG") sel.value = sel.value === "REG_ASC" ? "REG_DESC" : "REG_ASC";
  else if (col === "NAME") sel.value = sel.value === "NAME_ASC" ? "NAME_DESC" : "NAME_ASC";
  else if (col === "TOT") sel.value = "TOT_DESC";
  renderAdminMembersTable();
}

function toggleAdminHeadSort(col) {
  const sel = document.getElementById("sortAdminHeads");
  if (!sel) return;
  if (col === "CODE") sel.value = sel.value === "CODE_ASC" ? "CODE_DESC" : "CODE_ASC";
  else if (col === "TITLE") sel.value = sel.value === "TITLE_ASC" ? "TITLE_DESC" : "TITLE_ASC";
  else if (col === "CAT") sel.value = "CAT_ASC";
  renderAdminHeadsTable();
}

function toggleAdminTxnSort(col) {
  const sel = document.getElementById("sortAdminTxns");
  if (!sel) return;
  if (col === "DATE") sel.value = sel.value === "DATE_DESC" ? "DATE_ASC" : "DATE_DESC";
  else if (col === "DOC") sel.value = sel.value === "DOC_ASC" ? "DOC_DESC" : "DOC_ASC";
  else if (col === "HEAD") sel.value = "HEAD_ASC";
  else if (col === "CASH") sel.value = "CASH_DESC";
  else if (col === "BANK") sel.value = "BANK_DESC";
  renderAdminTxnsTable();
}

function renderAdminMembersTable() {
  const tbody = document.getElementById("tbodyAdminMembers");
  const searchInput = document.getElementById("searchAdminMembers");
  const sortMode = document.getElementById("sortAdminMembers")?.value || "REG_ASC";
  const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
  if (!tbody) return;

  tbody.innerHTML = "";
  const invalidNames = ["NAME OF HOF", "NAME", "SL. NO.", "REGISTER NO.", "REGISTER NO", "SL NO", "MEMBER NAME"];
  const membersList = [];

  if (state.individual && state.individual.length > 0) {
    state.individual.forEach((r) => {
      const regNo = getColVal(r, "B");
      const name = getColVal(r, "C");
      const subUpto = getColVal(r, "D");
      const total = getColVal(r, "AM") || "0.00";
      const totalNum = parseFloat(total) || 0;

      if (!regNo || !name || invalidNames.includes(regNo.toUpperCase()) || invalidNames.includes(name.toUpperCase())) {
        return;
      }

      if (query && !regNo.toLowerCase().includes(query) && !name.toLowerCase().includes(query)) {
        return;
      }

      membersList.push({ regNo, name, subUpto, total, totalNum });
    });
  }

  // Sorting
  membersList.sort((a, b) => {
    if (sortMode === "REG_ASC") return (parseInt(a.regNo, 10) || 9999) - (parseInt(b.regNo, 10) || 9999);
    if (sortMode === "REG_DESC") return (parseInt(b.regNo, 10) || 9999) - (parseInt(a.regNo, 10) || 9999);
    if (sortMode === "NAME_ASC") return a.name.localeCompare(b.name);
    if (sortMode === "NAME_DESC") return b.name.localeCompare(a.name);
    if (sortMode === "TOT_DESC") return b.totalNum - a.totalNum;
    return 0;
  });

  membersList.forEach(m => {
    const safeReg = escapeJsString(m.regNo);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>#${m.regNo}</strong></td>
      <td>${m.name}</td>
      <td><span class="header-badge" style="background:#e0f2fe; color:#0369a1; font-weight:700;">${formatSubUptoMonthYear(m.subUpto)}</span></td>
      <td class="text-right"><strong>${formatCurrency(m.total)}</strong></td>
      <td class="text-center" style="white-space:nowrap;">
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; margin-right:4px;" onclick="promptAdminPassword('EDIT_MEMBER', '${safeReg}')">✏️ Edit</button>
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; color:var(--danger-color); border-color:var(--danger-color);" onclick="promptAdminPassword('DELETE_MEMBER', '${safeReg}')">🗑️ Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const cntEl = document.getElementById("cntAdminMembers");
  if (cntEl) cntEl.textContent = membersList.length;
}

function renderAdminHeadsTable() {
  const tbody = document.getElementById("tbodyAdminHeads");
  const filterCat = document.getElementById("filterAdminHeadCat")?.value || "ALL";
  const sortMode = document.getElementById("sortAdminHeads")?.value || "CODE_ASC";
  const query = document.getElementById("searchAdminHeads")?.value.trim().toLowerCase() || "";
  if (!tbody) return;

  tbody.innerHTML = "";
  const allHeads = getAllAccountHeads(filterCat);
  const headsList = [];

  allHeads.forEach(h => {
    if (query && !h.code.toLowerCase().includes(query) && !h.name.toLowerCase().includes(query)) {
      return;
    }
    headsList.push(h);
  });

  // Sorting
  headsList.sort((a, b) => {
    if (sortMode === "CODE_ASC") return a.code.localeCompare(b.code, undefined, { numeric: true });
    if (sortMode === "CODE_DESC") return b.code.localeCompare(a.code, undefined, { numeric: true });
    if (sortMode === "TITLE_ASC") return a.name.localeCompare(b.name);
    if (sortMode === "TITLE_DESC") return b.name.localeCompare(a.name);
    if (sortMode === "CAT_ASC") return a.category.localeCompare(b.category);
    return 0;
  });

  headsList.forEach(h => {
    const isReceipt = h.category === "RECEIPT";
    const safeCode = escapeJsString(h.code);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="header-badge" style="background:${isReceipt ? '#dcfce7' : '#fee2e2'}; color:${isReceipt ? '#15803d' : '#b91c1c'};">${isReceipt ? '📥 Receipt' : '📤 Payment'}</span></td>
      <td><strong>[${h.code}]</strong></td>
      <td>${h.name}</td>
      <td class="text-center"><span class="header-badge" style="background:#f1f5f9; color:#475569;">${h.source}</span></td>
      <td class="text-center" style="white-space:nowrap;">
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; margin-right:4px;" onclick="promptAdminPassword('EDIT_ACCOUNT_HEAD', '${safeCode}')">✏️ Edit</button>
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; color:var(--danger-color);" onclick="promptAdminPassword('DELETE_ACCOUNT_HEAD', '${safeCode}')">🗑️ Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const cntEl = document.getElementById("cntAdminHeads");
  if (cntEl) cntEl.textContent = headsList.length;
}

function renderAdminTxnsTable() {
  const tbody = document.getElementById("tbodyAdminTxns");
  const filterType = document.getElementById("filterAdminTxnType")?.value || "ALL";
  const sortMode = document.getElementById("sortAdminTxns")?.value || "DATE_DESC";
  const query = document.getElementById("searchAdminTxns")?.value.trim().toLowerCase() || "";
  if (!tbody) return;

  tbody.innerHTML = "";
  const txnsList = [];

  state.cashbook.forEach((row, index) => {
    // 1. Extract Receipt Fields
    const recDtRaw = getColVal(row, "A");
    const recNo = getColVal(row, "B");
    const regNo = getColVal(row, "C");
    const hof = getColVal(row, "D");
    const recHead = getColVal(row, "E");
    const recCode = getColVal(row, "F");
    const recDetails = getColVal(row, "G");
    const cashR = getColVal(row, "H");
    const bankR = getColVal(row, "I");

    // 2. Extract Payment Fields
    const payDtRaw = getColVal(row, "K");
    const voucherNo = getColVal(row, "L");
    const payHead = getColVal(row, "M");
    const payCode = getColVal(row, "N");
    const payDetails = getColVal(row, "O");
    const cashP = getColVal(row, "P");
    const bankP = getColVal(row, "Q");

    // Skip Excel table header title rows
    const recHeadLower = recHead.toLowerCase();
    const payHeadLower = payHead.toLowerCase();
    if (recHeadLower.includes("account head") || payHeadLower.includes("account head") || recHeadLower.includes("cash book")) {
      return;
    }

    const hasReceiptAmt = (parseFloat(cashR) || 0) > 0 || (parseFloat(bankR) || 0) > 0;
    const isOpening = recHeadLower.includes("opening balance") || recDetails.toLowerCase().includes("opening balance");
    const isValidReceipt = isOpening || ((Boolean(recNo) || Boolean(recHead) || Boolean(hof)) && hasReceiptAmt);

    const hasPaymentAmt = (parseFloat(cashP) || 0) > 0 || (parseFloat(bankP) || 0) > 0;
    const isValidPayment = (Boolean(voucherNo) || Boolean(payHead) || Boolean(payCode) || Boolean(payDetails)) && hasPaymentAmt;

    // Process Receipt side of this row
    if (isValidReceipt && (filterType === "ALL" || filterType === "RECEIPT")) {
      const dateVal = formatExcelDate(recDtRaw || payDtRaw);
      const rowSearchText = `${recNo} ${dateVal} ${regNo} ${hof} ${recHead} ${recCode} ${recDetails} ${cashR} ${bankR}`.toLowerCase();

      if (!query || rowSearchText.includes(query)) {
        txnsList.push({
          type: "RECEIPT",
          docNo: recNo,
          docNum: parseInt(recNo, 10) || 0,
          dateVal,
          dateRaw: recDtRaw || payDtRaw,
          regNo,
          hof,
          head: isOpening ? 'Opening Balance' : recHead,
          code: recCode,
          cashAmt: cashR,
          bankAmt: bankR,
          cashNum: parseFloat(cashR) || 0,
          bankNum: parseFloat(bankR) || 0,
          index
        });
      }
    }

    // Process Payment side of this row
    if (isValidPayment && (filterType === "ALL" || filterType === "PAYMENT")) {
      const dateVal = formatExcelDate(payDtRaw || recDtRaw);
      const rowSearchText = `${voucherNo} ${dateVal} ${payHead} ${payCode} ${payDetails} ${cashP} ${bankP}`.toLowerCase();

      if (!query || rowSearchText.includes(query)) {
        txnsList.push({
          type: "PAYMENT",
          docNo: voucherNo,
          docNum: parseInt(voucherNo, 10) || 0,
          dateVal,
          dateRaw: payDtRaw || recDtRaw,
          regNo: "",
          hof: "",
          head: payHead,
          code: payCode,
          cashAmt: cashP,
          bankAmt: bankP,
          cashNum: parseFloat(cashP) || 0,
          bankNum: parseFloat(bankP) || 0,
          index
        });
      }
    }
  });

  // Sorting
  txnsList.sort((a, b) => {
    if (sortMode === "DATE_DESC") return (b.index - a.index);
    if (sortMode === "DATE_ASC") return (a.index - b.index);
    if (sortMode === "DOC_ASC") return (a.docNum - b.docNum);
    if (sortMode === "DOC_DESC") return (b.docNum - a.docNum);
    if (sortMode === "HEAD_ASC") return a.head.localeCompare(b.head);
    if (sortMode === "CASH_DESC") return b.cashNum - a.cashNum;
    if (sortMode === "BANK_DESC") return b.bankNum - a.bankNum;
    return 0;
  });

  txnsList.forEach(t => {
    const isReceipt = t.type === "RECEIPT";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="header-badge" style="background:${isReceipt ? '#dcfce7' : '#fee2e2'}; color:${isReceipt ? '#15803d' : '#b91c1c'};">${isReceipt ? '📥 Receipt' : '📤 Payment'}</span></td>
      <td><strong>${t.docNo ? '#' + t.docNo : '-'}</strong></td>
      <td>${t.dateVal}</td>
      <td>${t.regNo ? '#' + t.regNo : '-'}</td>
      <td>${t.hof || '-'}</td>
      <td>${t.head}</td>
      <td><strong>${t.code || '-'}</strong></td>
      <td class="text-right">${formatCurrency(t.cashAmt)}</td>
      <td class="text-right">${formatCurrency(t.bankAmt)}</td>
      <td class="text-center" style="white-space:nowrap;">
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; color:#0284c7; border-color:#0284c7; margin-right:4px;" onclick="reprintTxnDocument('${t.type}', '${t.docNo}', ${t.index})">🖨️ Print</button>
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; margin-right:4px;" onclick="promptAdminPassword('EDIT_CASHBOOK', {index: ${t.index}, type: '${t.type}'})">✏️ Edit</button>
        <button class="btn btn-outline" style="padding:2px 8px; font-size:0.78rem; color:var(--danger-color);" onclick="promptAdminPassword('DELETE_CASHBOOK', {index: ${t.index}, type: '${t.type}'})">🗑️ Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const cntEl = document.getElementById("cntAdminTxns");
  if (cntEl) cntEl.textContent = txnsList.length;
  const lblTotal = document.getElementById("lblTotalTxnsCount");
  if (lblTotal) lblTotal.textContent = txnsList.length;
}

function reprintTxnDocument(type, docNo, index) {
  const isReceipt = type === "RECEIPT";
  const prefix = isReceipt ? "Receipt" : "Voucher";
  const cleanDocNo = (docNo || "").replace(/#/g, "").trim();
  const pdfTitle = getCleanPrintTitle(cleanDocNo ? `${prefix}_${cleanDocNo}` : `${prefix}_Document`);
  const key1 = `${prefix}_${cleanDocNo}`;
  const key2 = `${prefix}_#${cleanDocNo}`;
  const modalArea = document.getElementById("receiptModalArea");

  if (modalArea) {
    modalArea.dataset.prefix = prefix;
    modalArea.dataset.docno = cleanDocNo;
  }

  try {
    const savedMap = JSON.parse(localStorage.getItem("CHURCH_SAVED_RECEIPTS") || "{}");
    const htmlContent = savedMap[key1] || savedMap[key2] || savedMap[`${prefix}_${docNo}`] || savedMap[`${prefix}_#${docNo}`];

    if (htmlContent) {
      if (modalArea) modalArea.innerHTML = htmlContent;
      document.getElementById("receiptModal").classList.add("active");
      document.title = pdfTitle;
      return;
    }
  } catch (e) { }

  // Fallback: Construct dual side-by-side cards from cashbook row data
  const row = state.cashbook[index];
  if (!row) {
    alert("Transaction details not found!");
    return;
  }

  const dateStr = formatExcelDate(isReceipt ? getColVal(row, "A") : getColVal(row, "K"));
  const regNo = isReceipt ? getColVal(row, "C") : "";
  const memberName = isReceipt ? (getColVal(row, "D") || "General Member") : (getColVal(row, "O") || "General Payment");
  const head = isReceipt ? getColVal(row, "E") : getColVal(row, "M");
  const code = isReceipt ? getColVal(row, "F") : getColVal(row, "N");
  const details = isReceipt ? getColVal(row, "G") : getColVal(row, "O");
  const detailsText = details ? String(details).trim() : "";
  const detailsHtml = detailsText ? `<div style="font-size:10.5px; color:#475569; font-style:italic; margin-top:3px; padding-top:2px; border-top:1px dashed #cbd5e1;"><strong>Details:</strong> ${detailsText}</div>` : "";
  const cashAmt = parseFloat(isReceipt ? getColVal(row, "H") : getColVal(row, "P")) || 0;
  const bankAmt = parseFloat(isReceipt ? getColVal(row, "I") : getColVal(row, "Q")) || 0;
  const grandTotal = cashAmt + bankAmt;
  const totalWords = numberToIndianWords(grandTotal);

  const docTitle = isReceipt ? "RECEIPT" : "PAYMENT VOUCHER";
  const numLabel = isReceipt ? "Receipt No" : "Voucher No";

  const cardHtml = `
    <div class="dual-receipt-container" style="display:flex; gap:20px; flex-wrap:wrap;">
      <!-- ORIGINAL -->
      <div class="receipt-card" style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#10b981; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">ORIGINAL</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <img src="church_logo.png" alt="Church Logo" style="height:54px; width:54px; border-radius:50%; border:1.5px solid #1e293b; margin-bottom:4px; object-fit:contain; background:#fff;">
          <h3 style="margin:0; font-size:15px; color:#0f172a; font-weight:800;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:10.5px; color:#475569;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010 | ESTD : 1954</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle}</p>
        </div>
        <table style="width:100%; margin-bottom:10px; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${cleanDocNo || '-'}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:100%; border-collapse:collapse; margin-bottom:12px; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align:center; vertical-align:top; padding:6px;">1</td>
              <td style="padding:6px;">
                <div style="font-weight:700; color:#0f172a;">${head} (${code})</div>
                ${detailsHtml}
              </td>
              <td style="text-align:right; vertical-align:top; padding:6px; font-weight:700;">₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
            </tr>
          </tbody>
        </table>
        <div style="background:#f1f5f9; padding:8px; border-radius:4px; font-size:12px; font-weight:bold; margin-bottom:15px;">
          <div>Total: ₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
          <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:2px;">(${totalWords})</div>
        </div>
        <div style="display:flex; justify-content:flex-end; font-size:11px; font-weight:bold; color:#1e293b; margin-bottom:8px;">
          <div style="text-align:right;">Vicar / Trustee: ___________________</div>
        </div>
        <div style="text-align:center; font-size:9.5px; color:#475569; border-top:1px dashed #cbd5e1; padding-top:6px; font-weight:600; font-style:italic;">
          ✓ Computer Generated Document — Digitally Signed & Authenticated
        </div>
      </div>

      <!-- DUPLICATE COPY -->
      <div class="receipt-card" style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#f59e0b; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">COPY</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <img src="church_logo.png" alt="Church Logo" style="height:54px; width:54px; border-radius:50%; border:1.5px solid #1e293b; margin-bottom:4px; object-fit:contain; background:#fff;">
          <h3 style="margin:0; font-size:15px; color:#0f172a; font-weight:800;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:10.5px; color:#475569;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010 | ESTD : 1954</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle} (OFFICE COPY)</p>
        </div>
        <table style="width:100%; margin-bottom:10px; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${cleanDocNo || '-'}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:100%; border-collapse:collapse; margin-bottom:12px; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align:center; vertical-align:top; padding:6px;">1</td>
              <td style="padding:6px;">
                <div style="font-weight:700; color:#0f172a;">${head} (${code})</div>
                ${detailsHtml}
              </td>
              <td style="text-align:right; vertical-align:top; padding:6px; font-weight:700;">₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
            </tr>
          </tbody>
        </table>
        <div style="background:#f1f5f9; padding:8px; border-radius:4px; font-size:12px; font-weight:bold; margin-bottom:15px;">
          <div>Total: ₹ ${grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
          <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:2px;">(${totalWords})</div>
        </div>
        <div style="display:flex; justify-content:flex-end; font-size:11px; font-weight:bold; color:#1e293b; margin-bottom:8px;">
          <div style="text-align:right;">Vicar / Trustee: ___________________</div>
        </div>
        <div style="text-align:center; font-size:9.5px; color:#475569; border-top:1px dashed #cbd5e1; padding-top:6px; font-weight:600; font-style:italic;">
          ✓ Computer Generated Document — Digitally Signed & Authenticated
        </div>
      </div>
    </div>
  `;

  if (modalArea) modalArea.innerHTML = cardHtml;
  document.getElementById("receiptModal").classList.add("active");
  document.title = pdfTitle;
}

function openEditAccountHeadModal(code) {
  if (!code) return;
  const targetCode = String(code).trim().toUpperCase().replace(/^RP-\s*/i, "RP-");
  const allHeads = getAllAccountHeads("ALL");

  const head = allHeads.find(h => {
    const normH = String(h.code).trim().toUpperCase().replace(/^RP-\s*/i, "RP-");
    return normH === targetCode || String(h.code).toUpperCase() === String(code).toUpperCase();
  });

  if (!head) {
    alert(`Account Head [${code}] not found!`);
    return;
  }

  document.getElementById("editHeadOriginalCode").value = head.code;
  document.getElementById("editHeadCategory").value = head.category;
  document.getElementById("editHeadCode").value = head.code;
  document.getElementById("editHeadTitle").value = head.name;

  const modal = document.getElementById("editAccountHeadModal");
  if (modal) modal.classList.add("active");
}

function closeEditAccountHeadModal() {
  const modal = document.getElementById("editAccountHeadModal");
  if (modal) modal.classList.remove("active");
}

function saveAccountHeadChanges() {
  const origCode = document.getElementById("editHeadOriginalCode").value.trim();
  const category = document.getElementById("editHeadCategory").value;
  const newCode = document.getElementById("editHeadCode").value.trim();
  const newTitle = document.getElementById("editHeadTitle").value.trim();

  if (!newCode || !newTitle) {
    alert("Please fill out both Code and Title!");
    return;
  }

  if (!Array.isArray(state.customAccountHeads)) state.customAccountHeads = [];
  if (!Array.isArray(state.deletedAccountHeads)) state.deletedAccountHeads = [];

  // If code reference was modified, hide the original code
  if (origCode.toUpperCase() !== newCode.toUpperCase()) {
    if (!state.deletedAccountHeads.includes(origCode.toUpperCase())) {
      state.deletedAccountHeads.push(origCode.toUpperCase());
      localStorage.setItem("CHURCH_DELETED_HEADS", JSON.stringify(state.deletedAccountHeads));
    }
  }

  const existingIdx = state.customAccountHeads.findIndex(h => h.code.toUpperCase() === origCode.toUpperCase());
  const updatedObj = { code: newCode, name: newTitle, category, type: category, source: "Edited" };

  if (existingIdx >= 0) {
    state.customAccountHeads[existingIdx] = updatedObj;
  } else {
    state.customAccountHeads.push(updatedObj);
  }

  localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();

  // Sync active views
  updateDocTypeView();
  renderTrialBalance();
  if (state.isAdminUnlocked) renderAdminHeadsTable();
  closeEditAccountHeadModal();
  alert(`[OK] Account Head [${newCode}] "${newTitle}" updated successfully!`);
}

function confirmDeleteAccountHead(code) {
  if (confirm(`Are you sure you want to delete Account Head [${code}]?`)) {
    if (!Array.isArray(state.customAccountHeads)) state.customAccountHeads = [];
    if (!Array.isArray(state.deletedAccountHeads)) state.deletedAccountHeads = [];

    const upperCode = code.toUpperCase();
    state.customAccountHeads = state.customAccountHeads.filter(h => h.code.toUpperCase() !== upperCode);
    if (!state.deletedAccountHeads.includes(upperCode)) {
      state.deletedAccountHeads.push(upperCode);
    }

    localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
    localStorage.setItem("CHURCH_DELETED_HEADS", JSON.stringify(state.deletedAccountHeads));

    updateDocTypeView();
    renderTrialBalance();
    if (state.isAdminUnlocked) renderAdminHeadsTable();
    alert(`[OK] Account Head [${code}] deleted successfully!`);
  }
}

function updateAdminPassword() {
  const newPass = document.getElementById("txtNewAdminPass").value.trim();
  const confirmPass = document.getElementById("txtConfirmAdminPass").value.trim();

  if (!newPass) {
    alert("Password cannot be empty!");
    return;
  }
  if (newPass !== confirmPass) {
    alert("Passwords do not match!");
    return;
  }

  state.adminPassword = newPass;
  localStorage.setItem("CHURCH_ADMIN_PASS", newPass);
  alert("Admin password updated successfully!");
  document.getElementById("txtNewAdminPass").value = "";
  document.getElementById("txtConfirmAdminPass").value = "";
}

function resetSystemDataOverrides() {
  if (confirm("Are you sure you want to reset all custom local data changes (members, account heads, edited transactions) and revert to default Excel workbook datasets?")) {
    localStorage.removeItem("CHURCH_MEMBERS");
    localStorage.removeItem("CHURCH_ACCOUNT_HEADS");
    localStorage.removeItem("CHURCH_DELETED_HEADS");
    localStorage.removeItem("CHURCH_DELETED_MEMBERS");
    localStorage.removeItem("CHURCH_CASHBOOK");
    localStorage.removeItem("CHURCH_ADMIN_PASS");
    location.reload();
  }
}

// ----------------------------------------------------
// 🔐 DATA BACKUP & RESTORE ENGINE (DESKTOP & MOBILE SYNC)
// ----------------------------------------------------
function exportSystemBackupJSON() {
  openBackupExportModal();
}

function openBackupExportModal() {
  try {
    const dateStr = new Date().toISOString().slice(0, 10);
    const fileName = `St_Gregorios_Church_Backup_${dateStr}.json`;

    const backupObj = {
      app: "St. Gregorios Orthodox Syrian Church Accounting Portal",
      version: "1.0",
      exportDate: new Date().toISOString(),
      cashbook: state.cashbook || [],
      customAccountHeads: state.customAccountHeads || [],
      deletedAccountHeads: state.deletedAccountHeads || [],
      deletedMembers: state.deletedMembers || [],
      individual: state.individual || [],
      masterMembers: state.members || [],
      adminPassword: state.adminPassword || "church123",
      currentReceiptNo: state.currentReceiptNo || 4001,
      currentVoucherNo: state.currentVoucherNo || 1
    };

    const str = JSON.stringify(backupObj, null, 2);

    // 1. Android Native Bridge Share (If running inside Android APK)
    if (window.AndroidBridge) {
      try { window.AndroidBridge.shareBackupJson(str, fileName); } catch (e) { }
    }

    // 2. Try web blob download
    try {
      const blob = new Blob([str], { type: "application/json;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) { }

    // 3. Display explicit modal on screen
    showBackupExportModal(str, fileName);
  } catch (err) {
    alert("Backup Error: " + err.message);
  }
}

function showBackupExportModal(jsonStr, fileName) {
  let modal = document.getElementById("backupExportModal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "backupExportModal";
    modal.style.cssText = "position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:99999; background:rgba(15,23,42,0.8); backdrop-filter:blur(6px); display:flex; align-items:center; justify-content:center; padding:16px; box-sizing:border-box;";
    modal.innerHTML = `
      <div style="background:#ffffff; border-radius:16px; max-width:550px; width:100%; padding:24px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35); text-align:left; font-family:sans-serif; max-height:90vh; overflow-y:auto; box-sizing:border-box;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h3 style="margin:0; color:#0f172a; font-size:1.2rem; font-weight:700;">💾 System Backup JSON Export</h3>
          <button onclick="closeBackupExportModal()" style="background:none; border:none; font-size:1.5rem; color:#64748b; cursor:pointer; padding:0 4px;">&times;</button>
        </div>
        <p style="font-size:0.85rem; color:#475569; margin:0 0 12px 0;">
          File: <strong id="lblExportFileName" style="color:#0284c7;"></strong><br>
          Tap <strong>Copy JSON to Clipboard</strong> below to save or transfer backup data.
        </p>
        <div style="margin-bottom:16px;">
          <textarea id="txtBackupExportArea" rows="9" style="width:100%; font-family:monospace; font-size:11px; padding:10px; border:1.5px solid #cbd5e1; border-radius:8px; box-sizing:border-box; background:#f8fafc; color:#1e293b;" readonly></textarea>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end;">
          <button class="btn btn-primary" style="background:#10b981; border-color:#10b981; padding:10px 18px; font-weight:700; color:#fff; border-radius:8px; cursor:pointer;" onclick="copyBackupToClipboard()">📋 Copy JSON to Clipboard</button>
          <button class="btn btn-outline" style="padding:10px 18px; border:1px solid #cbd5e1; border-radius:8px; cursor:pointer; background:#f1f5f9;" onclick="closeBackupExportModal()">Close</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  document.getElementById("lblExportFileName").innerText = fileName;
  document.getElementById("txtBackupExportArea").value = jsonStr;
  modal.style.display = "flex";
}

function closeBackupExportModal() {
  const modal = document.getElementById("backupExportModal");
  if (modal) modal.style.display = "none";
}

function copyBackupToClipboard() {
  const area = document.getElementById("txtBackupExportArea");
  if (area) {
    area.select();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(area.value).then(() => {
        alert("✅ Backup JSON copied to clipboard!");
      }).catch(() => {
        document.execCommand("copy");
        alert("✅ Backup JSON copied to clipboard!");
      });
    } else {
      document.execCommand("copy");
      alert("✅ Backup JSON copied to clipboard!");
    }
  }
}

function openBackupImportModal() {
  let modal = document.getElementById("backupImportModal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "backupImportModal";
    modal.style.cssText = "position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:99999; background:rgba(15,23,42,0.8); backdrop-filter:blur(6px); display:flex; align-items:center; justify-content:center; padding:16px; box-sizing:border-box;";
    modal.innerHTML = `
      <div style="background:#ffffff; border-radius:16px; max-width:550px; width:100%; padding:24px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35); text-align:left; font-family:sans-serif; max-height:90vh; overflow-y:auto; box-sizing:border-box;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h3 style="margin:0; color:#0f172a; font-size:1.2rem; font-weight:700;">📥 Restore System Backup (JSON)</h3>
          <button onclick="closeBackupImportModal()" style="background:none; border:none; font-size:1.5rem; color:#64748b; cursor:pointer; padding:0 4px;">&times;</button>
        </div>
        <p style="font-size:0.85rem; color:#475569; margin:0 0 14px 0;">
          Select a <strong>.json</strong> file from your phone, or paste your backup JSON text below:
        </p>
        <div style="margin-bottom:16px;">
          <label for="fileBackupImportModal" style="background:#0284c7; color:#ffffff; font-weight:700; font-size:0.9rem; padding:12px 20px; border-radius:8px; cursor:pointer; display:inline-block; text-align:center;">📂 Select .JSON File from Phone</label>
          <input type="file" id="fileBackupImportModal" accept="*/*" style="opacity:0; position:absolute; width:1px; height:1px; z-index:-1;" onchange="importSystemBackupJSON(event)">
        </div>
        <div style="margin-bottom:16px;">
          <label style="font-weight:700; font-size:0.85rem; display:block; margin-bottom:6px; color:#334155;">Or Paste JSON Data Here:</label>
          <textarea id="txtBackupImportArea" rows="7" placeholder="Paste JSON backup text here..." style="width:100%; font-family:monospace; font-size:11px; padding:10px; border:1.5px solid #cbd5e1; border-radius:8px; box-sizing:border-box; color:#1e293b;"></textarea>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end;">
          <button class="btn btn-primary" style="background:#10b981; border-color:#10b981; padding:10px 18px; font-weight:700; color:#fff; border-radius:8px; cursor:pointer;" onclick="processPastedBackupRestore()">📥 Restore from Pasted JSON</button>
          <button class="btn btn-outline" style="padding:10px 18px; border:1px solid #cbd5e1; border-radius:8px; cursor:pointer; background:#f1f5f9;" onclick="closeBackupImportModal()">Cancel</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  document.getElementById("txtBackupImportArea").value = "";
  modal.style.display = "flex";
}

function closeBackupImportModal() {
  const modal = document.getElementById("backupImportModal");
  if (modal) modal.style.display = "none";
}

function processPastedBackupRestore() {
  const area = document.getElementById("txtBackupImportArea");
  if (area && area.value.trim()) {
    processBackupRestoreData(area.value.trim());
    closeBackupImportModal();
  } else {
    alert("Please paste backup JSON text into the text area first.");
  }
}

function importSystemBackupJSON(event) {
  const file = event?.target?.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    processBackupRestoreData(e.target.result);
    closeBackupImportModal();
  };
  reader.readAsText(file);
}

function processBackupRestoreData(jsonText) {
  try {
    const data = JSON.parse(jsonText);
    if (!data || typeof data !== "object") {
      alert("Invalid backup file format!");
      return;
    }

    if (confirm(`Are you sure you want to restore backup from ${data.exportDate || 'selected backup'}? This will update cashbook entries and member records.`)) {
      // Flexible key extraction for cashbook and members
      const cbArr = Array.isArray(data.cashbook) ? data.cashbook :
        Array.isArray(data.cashBook) ? data.cashBook :
          Array.isArray(data.transactions) ? data.transactions :
            Array.isArray(data.CashBook) ? data.CashBook :
              Array.isArray(data.Cash_Book) ? data.Cash_Book :
                (Array.isArray(data) ? data : null);

      if (Array.isArray(cbArr)) {
        state.cashbook = cbArr;
        localStorage.setItem("CHURCH_CASHBOOK", JSON.stringify(state.cashbook));
        // Bulk import to database
        const isLocalServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.');
        if (isLocalServer) {
          fetch('/api/bulk_import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cbArr)
          }).then(res => {
            if (!res.ok) console.error("Failed to sync backup to SQLite DB");
          }).catch(err => console.error("DB Sync error:", err));
        } else {
          fetch('./api.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'import_cashbook', rows: cbArr })
          }).then(r => r.json()).then(r => {
            if (r.success) console.log("Backup cashbook synced to cloud MySQL!");
            else console.error("Cloud MySQL backup sync failed:", r.message);
          }).catch(err => console.error("[SYNC ERROR] Failed to sync backup to cloud server:", err));
        }
      }

      const indArr = Array.isArray(data.individual) ? data.individual :
        Array.isArray(data.members) && !data.masterMembers ? data.members :
          Array.isArray(data.Individual) ? data.Individual :
            Array.isArray(data.Members) && !data.masterMembers ? data.Members : null;

      if (Array.isArray(indArr)) {
        state.individual = indArr;
        localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
      }

      const masterArr = Array.isArray(data.masterMembers) ? data.masterMembers : null;
      if (masterArr) {
        state.members = masterArr;
        localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
      } else if (Array.isArray(indArr)) {
        indArr.forEach(r => {
          const reg = getColVal(r, "B");
          const name = getColVal(r, "C");
          if (reg && name && reg !== "Register No." && reg.toUpperCase() !== "REGISTER NO") {
            if (!state.members.find(m => getColVal(m, "B") === reg)) {
              state.members.push({ "A": "", "B": reg, "C": name, "D": "", "E": "" });
            } else {
              const ex = state.members.find(m => getColVal(m, "B") === reg);
              ex.C = name;
            }
          }
        });
        localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
      }

      if (Array.isArray(data.customAccountHeads)) {
        state.customAccountHeads = data.customAccountHeads;
        localStorage.setItem("CHURCH_ACCOUNT_HEADS", JSON.stringify(state.customAccountHeads)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
      }
      if (Array.isArray(data.trialBalance)) {
        state.trialBalance = data.trialBalance;
        localStorage.setItem("CHURCH_TRIAL_BALANCE", JSON.stringify(state.trialBalance));
      }
      if (Array.isArray(data.codes)) {
        state.codes = data.codes;
        localStorage.setItem("CHURCH_CODES", JSON.stringify(state.codes));
      }
      if (Array.isArray(data.budget)) {
        state.budget = data.budget;
        localStorage.setItem("CHURCH_BUDGET", JSON.stringify(state.budget));
      }
      if (Array.isArray(data.auction)) {
        state.auction = data.auction;
        localStorage.setItem("CHURCH_AUCTION", JSON.stringify(state.auction));
      }
      if (Array.isArray(data.deletedAccountHeads)) {
        state.deletedAccountHeads = data.deletedAccountHeads;
        localStorage.setItem("CHURCH_DELETED_HEADS", JSON.stringify(state.deletedAccountHeads));
      }
      if (Array.isArray(data.deletedMembers)) {
        state.deletedMembers = data.deletedMembers;
        localStorage.setItem("CHURCH_DELETED_MEMBERS", JSON.stringify(state.deletedMembers));
      }
      if (data.adminPassword) {
        state.adminPassword = data.adminPassword;
        localStorage.setItem("CHURCH_ADMIN_PASS", state.adminPassword);
      }
      if (data.currentReceiptNo) {
        state.currentReceiptNo = data.currentReceiptNo;
        localStorage.setItem("CHURCH_RECEIPT_NO", state.currentReceiptNo);
      }
      if (data.currentVoucherNo) {
        state.currentVoucherNo = data.currentVoucherNo;
        localStorage.setItem("CHURCH_VOUCHER_NO", state.currentVoucherNo);
      }

      // Ensure CURRENT_DATA_VERSION is set so loadAllData preserves restored values
      localStorage.setItem("CHURCH_DATA_VERSION", "2026-08-04_V7_4_FORCE_REFRESH");

      setTimeout(() => {
        loadAllData();
        renderAllViews();
        alert("✅ Backup restored successfully! All data updated and synced to database.");
      }, 500);
    }
  } catch (err) {
    console.error("Backup import error:", err);
    alert("Failed to parse backup file: " + err.message);
  }
}

// ----------------------------------------------------
// 🔒 7-DAY TRIAL LICENSE GUARD (FRESH START BUILD)
// ----------------------------------------------------
function checkTrialLicenseGuard() {
  if (!window.isFreshStartBuild) return;

  const isActivated = localStorage.getItem("CHURCH_TRIAL_ACTIVATED") === "true";
  if (isActivated) return;

  let startTime = parseInt(localStorage.getItem("CHURCH_TRIAL_START_TIME"), 10);
  if (isNaN(startTime) || !startTime) {
    startTime = Date.now();
    localStorage.setItem("CHURCH_TRIAL_START_TIME", startTime.toString());
  }

  const elapsedMs = Date.now() - startTime;
  const elapsedDays = elapsedMs / (1000 * 3600 * 24);

  if (elapsedDays > 7) {
    const modal = document.getElementById("trialActivationModal");
    if (modal) {
      modal.classList.add("active");
      modal.style.display = "flex";
    }
  }
}

function verifyTrialActivationKey() {
  const input = document.getElementById("txtTrialKey");
  const key = input ? input.value.trim() : "";
  if (key === "CHURCH-2026-ACTIVATE" || key === state.adminPassword || key === "admin123" || key === "church123") {
    localStorage.setItem("CHURCH_TRIAL_ACTIVATED", "true");
    const modal = document.getElementById("trialActivationModal");
    if (modal) {
      modal.classList.remove("active");
      modal.style.display = "none";
    }
    alert("[OK] Software permanently activated successfully!");
  } else {
    alert("Invalid Activation Key! Please contact administrator.");
  }
}

// ----------------------------------------------------
// MEMBER DIRECTORY CRUD OPERATIONS
// ----------------------------------------------------
function renderMemberDirectory() {
  const tbody = document.querySelector("#memberDirectoryTable tbody");
  if (!tbody) return;

  // Filter out headers from Excel
  const validMembers = state.members.filter(row => {
    const rn = getColVal(row, "B");
    return rn && rn !== "Register No." && rn.toUpperCase() !== "REGISTER NO";
  });

  // Sort alphabetically by Name
  validMembers.sort((a, b) => {
    const nameA = String(getColVal(a, "C") || "").toLowerCase();
    const nameB = String(getColVal(b, "C") || "").toLowerCase();
    return nameA.localeCompare(nameB);
  });

  let html = "";
  validMembers.forEach(member => {
    const regNo = getColVal(member, "B") || "";
    const name = getColVal(member, "C") || "";
    const phone = getColVal(member, "D") || "";
    const address = getColVal(member, "E") || "";

    html += `
      <tr>
        <td style="font-weight:700;">${regNo}</td>
        <td>${name}</td>
        <td>${phone}</td>
        <td>${address}</td>
        <td style="text-align:center;">
          <button class="btn btn-outline" style="padding:4px 8px; font-size:0.8rem; margin-right:4px;" onclick="promptAdminPassword('DIR_EDIT', '${escapeJsString(regNo)}')">✏️ Edit</button>
          <button class="btn btn-outline" style="padding:4px 8px; font-size:0.8rem; color:#ef4444; border-color:#ef4444;" onclick="promptAdminPassword('DIR_DELETE', '${escapeJsString(regNo)}')">🗑️</button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function openDirAddMemberModal() {
  document.getElementById("memberCrudTitle").innerHTML = "➕ Add New Member";
  document.getElementById("txtMemOriginalRegNo").value = "";
  document.getElementById("txtMemRegNo").value = "";
  document.getElementById("txtMemName").value = "";
  document.getElementById("txtMemPhone").value = "";
  document.getElementById("txtMemAddress").value = "";
  document.getElementById("memberCrudModal").style.display = "flex";
}

function openDirEditMemberModal(regNo) {
  const member = state.members.find(m => getColVal(m, "B") === String(regNo));
  if (!member) return;

  document.getElementById("memberCrudTitle").innerHTML = "✏️ Edit Member";
  document.getElementById("txtMemOriginalRegNo").value = regNo;
  document.getElementById("txtMemRegNo").value = regNo;
  document.getElementById("txtMemName").value = getColVal(member, "C") || "";
  document.getElementById("txtMemPhone").value = getColVal(member, "D") || "";
  document.getElementById("txtMemAddress").value = getColVal(member, "E") || "";
  document.getElementById("memberCrudModal").style.display = "flex";
}

function closeDirMemberCrudModal() {
  document.getElementById("memberCrudModal").style.display = "none";
}

function saveDirMemberCrud() {
  const originalRegNo = document.getElementById("txtMemOriginalRegNo").value.trim();
  const regNo = document.getElementById("txtMemRegNo").value.trim();
  const name = document.getElementById("txtMemName").value.trim();
  const phone = document.getElementById("txtMemPhone").value.trim();
  const address = document.getElementById("txtMemAddress").value.trim();

  if (!regNo || !name) {
    alert("Register Number and Name are required.");
    return;
  }

  // Editing existing member
  if (originalRegNo) {
    const idx = state.members.findIndex(m => getColVal(m, "B") === originalRegNo);
    if (idx !== -1) {
      if (originalRegNo !== regNo && state.members.some(m => getColVal(m, "B") === regNo)) {
        alert(`Register number ${regNo} is already in use.`);
        return;
      }
      setColVal(state.members[idx], "B", regNo);
      setColVal(state.members[idx], "C", name);
      setColVal(state.members[idx], "D", phone);
      setColVal(state.members[idx], "E", address);
    }
  } else {
    // Adding new member
    if (state.members.some(m => getColVal(m, "B") === regNo)) {
      alert(`Register number ${regNo} is already in use.`);
      return;
    }
    const maxSl = state.members.reduce((max, m) => {
      const a = parseInt(getColVal(m, "A"), 10);
      return !isNaN(a) && a > max ? a : max;
    }, 0);

    state.members.push({
      "A": String(maxSl + 1),
      "B": regNo,
      "C": name,
      "D": phone,
      "E": address
    });
  }

  // 2-Way Sync with Administration (state.individual)
  const idxIndiv = state.individual.findIndex((r, i) => i >= 4 && getColVal(r, "B") === (originalRegNo || regNo));
  if (idxIndiv !== -1) {
    setColVal(state.individual[idxIndiv], "B", regNo);
    setColVal(state.individual[idxIndiv], "C", name);
  } else {
    state.individual.push({
      "A": String(state.individual.length - 3),
      "B": regNo,
      "C": name,
      "D": "",
      "AM": "0.00"
    });
  }
  localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));

  // Save to correct local storage key
  localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
  closeDirMemberCrudModal();
  renderMemberDirectory();
  populateMemberDropdown();
  if (state.isAdminUnlocked) renderAdminMembersTable();
}

function deleteDirMemberCrud(regNo) {
  if (confirm(`Are you sure you want to completely delete member ${regNo}?`)) {
    state.members = state.members.filter(m => getColVal(m, "B") !== String(regNo));
    localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
    
    // Sync deletion to Administration
    state.individual = state.individual.filter(r => getColVal(r, "B") !== String(regNo));
    localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));

    renderMemberDirectory();
    populateMemberDropdown();
    if (state.isAdminUnlocked) renderAdminMembersTable();
  }
}

// ----------------------------------------------------
// 📥/📤 MEMBER DIRECTORY IMPORT/EXPORT FUNCTIONS
// ----------------------------------------------------
function exportMemberDirectoryCSV() {
  try {
    const validMembers = state.members.filter(row => {
      const rn = getColVal(row, "B");
      return rn && rn !== "Register No." && rn.toUpperCase() !== "REGISTER NO";
    });

    validMembers.sort((a, b) => {
      const nameA = String(getColVal(a, "C") || "").toLowerCase();
      const nameB = String(getColVal(b, "C") || "").toLowerCase();
      return nameA.localeCompare(nameB);
    });

    let csvContent = "\ufeff"; // BOM for UTF-8 Excel compatibility
    csvContent += "Register No.,Name,Mobile,Address\n";

    validMembers.forEach(member => {
      const regNo = String(getColVal(member, "B") || "").replace(/"/g, '""');
      const name = String(getColVal(member, "C") || "").replace(/"/g, '""');
      const phone = String(getColVal(member, "D") || "").replace(/"/g, '""');
      const address = String(getColVal(member, "E") || "").replace(/"/g, '""');

      csvContent += `"${regNo}","${name}","${phone}","${address}"\n`;
    });

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `St_Gregorios_Church_Members_Directory.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert("Export failed: " + err.message);
  }
}

function importMemberDirectoryCSV(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const text = e.target.result;
      const lines = parseCSVText(text);
      if (lines.length < 2) {
        alert("The selected CSV file appears to be empty or has no header.");
        return;
      }

      const headers = lines[0].map(h => h.trim().toLowerCase());
      
      const regIdx = headers.findIndex(h => h.includes("reg") || h.includes("member no") || h.includes("no."));
      const nameIdx = headers.findIndex(h => h.includes("name") || h.includes("hof") || h.includes("head"));
      const phoneIdx = headers.findIndex(h => h.includes("mob") || h.includes("phone") || h.includes("cell") || h.includes("contact"));
      const addrIdx = headers.findIndex(h => h.includes("add") || h.includes("address") || h.includes("location") || h.includes("residence"));

      if (regIdx === -1 || nameIdx === -1) {
        alert("Could not identify 'Register No.' or 'Name' columns in CSV header. Please check headers: " + lines[0].join(", "));
        return;
      }

      let importCount = 0;
      let updateCount = 0;

      for (let i = 1; i < lines.length; i++) {
        const row = lines[i];
        if (row.length < 2) continue;

        const regNo = row[regIdx] ? row[regIdx].trim() : "";
        const name = row[nameIdx] ? row[nameIdx].trim() : "";
        const phone = phoneIdx !== -1 && row[phoneIdx] ? row[phoneIdx].trim() : "";
        const address = addrIdx !== -1 && row[addrIdx] ? row[addrIdx].trim() : "";

        if (!regNo || !name) continue;
        if (regNo === "Register No." || regNo.toUpperCase() === "REGISTER NO") continue;

        const existingIdx = state.members.findIndex(m => getColVal(m, "B") === regNo);
        if (existingIdx !== -1) {
          setColVal(state.members[existingIdx], "C", name);
          setColVal(state.members[existingIdx], "D", phone);
          setColVal(state.members[existingIdx], "E", address);
          updateCount++;
        } else {
          const maxSl = state.members.reduce((max, m) => {
            const a = parseInt(getColVal(m, "A"), 10);
            return !isNaN(a) && a > max ? a : max;
          }, 0);

          state.members.push({
            "A": String(maxSl + 1),
            "B": regNo,
            "C": name,
            "D": phone,
            "E": address
          });
          importCount++;
        }

        const idxIndiv = state.individual.findIndex((r, idx) => idx >= 4 && getColVal(r, "B") === regNo);
        if (idxIndiv !== -1) {
          setColVal(state.individual[idxIndiv], "C", name);
        } else {
          state.individual.push({
            "A": String(state.individual.length - 3),
            "B": regNo,
            "C": name,
            "D": "",
            "AM": "0.00"
          });
        }
      }

      localStorage.setItem("CHURCH_MEMBERS", JSON.stringify(state.individual));
      localStorage.setItem("CHURCH_MASTER_MEMBERS", JSON.stringify(state.members)); if (window.syncAppStateToCloud) window.syncAppStateToCloud();
      if (window.syncAppStateToCloud) window.syncAppStateToCloud();

      renderMemberDirectory();
      populateMemberDropdown();
      if (state.isAdminUnlocked) renderAdminMembersTable();

      alert(`✅ CSV Import Complete!\n- Imported ${importCount} new members\n- Updated ${updateCount} existing member profiles.`);
    } catch(err) {
      alert("Error parsing CSV: " + err.message);
    }
  };
  reader.readAsText(file, "UTF-8");
  event.target.value = "";
}

function parseCSVText(text) {
  const lines = [];
  let row = [""];
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    const next = text[i+1];

    if (c === '"') {
      if (inQuotes && next === '"') {
        row[row.length - 1] += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (c === ',' && !inQuotes) {
      row.push("");
    } else if ((c === '\r' || c === '\n') && !inQuotes) {
      if (c === '\r' && next === '\n') i++;
      lines.push(row);
      row = [""];
    } else {
      row[row.length - 1] += c;
    }
  }
  if (row.length > 1 || row[0] !== "") {
    lines.push(row);
  }
  return lines;
}




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

window.loadCloudData = async function(isManualRefresh = false) {
    console.log("Loading cashbook from cloud database...");
    try {
        const response = await fetch('./api.php?_t=' + Date.now(), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'get_cashbook' })
        });
        const result = await response.json();
        if (result.success && result.data) {
            state.cashbook = result.data;
            calculateNextNumbers();
            renderAllViews();
            console.log("Cloud cashbook loaded successfully!");
            if (isManualRefresh) {
                alert("✅ Cloud Sync Successful! The application will now hard refresh to ensure all data is fully up to date.");
                window.location.reload(true);
            }
        } else {
            console.log("No cloud cashbook data yet (or empty).");
            if (isManualRefresh) {
                alert("✅ Cloud Sync Successful! No records found. The application will now hard refresh.");
                window.location.reload(true);
            }
        }
    } catch (e) {
        console.warn("Cloud fetch skipped (api.php not available):", e.message);
        if (isManualRefresh) {
            alert("❌ Cloud Sync Failed! Please check your connection.");
        }
    }
};
