import os
import shutil

shutil.copy("app_cloud_final.js", "app_supabase.js")

SUPABASE_INJECT = """
const SUPABASE_URL = 'https://djpuxmrjxsrhgfrtppky.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_QjkuMrFMwtc2imGfy0XCdw_37h05VtE';
let supabase = null;

try {
    if (!window.supabase) {
        alert("Supabase CDN script failed to load! Please check your internet connection.");
    } else {
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
          auth: {
            persistSession: false,
            autoRefreshToken: false,
            detectSessionInUrl: false
          }
        });
    }
} catch (e) {
    alert("Supabase Init Error: " + e.message + "\\nLine: " + e.lineNumber);
}

const originalFetch = window.fetch;
window.fetch = async function(url, options) {
  if (url && typeof url === 'string' && url.includes('api.php')) {
    try {
      const body = JSON.parse(options.body);
      
      if (body.action === 'get_app_state') {
        const { data, error } = await supabase.from('app_state').select('*');
        if (error) throw error;
        const stateMap = {};
        data.forEach(row => { 
            try { 
                stateMap[row.key_name] = typeof row.json_data === 'string' ? JSON.parse(row.json_data || '[]') : row.json_data; 
            } catch(e){}
        });
        // DEBUG ALERT
        alert("Supabase Mock: get_app_state fetched " + Object.keys(stateMap).length + " keys.");
        return new Response(JSON.stringify({ success: true, data: stateMap }));
      }
      
      if (body.action === 'get_cashbook') {
        const { data, error } = await supabase.from('cashbook').select('*').order('id', { ascending: true });
        if (error) throw error;
        const mappedRows = data.map(row => {
            const mapped = {};
            if(row.id) mapped.id = row.id;
            const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            cols.forEach(c => {
                if (row['col_'+c] !== undefined && row['col_'+c] !== null && row['col_'+c] !== 'NULL') mapped[c] = row['col_'+c];
            });
            return mapped;
        });
        // DEBUG ALERT
        alert("Supabase Mock: get_cashbook fetched " + mappedRows.length + " rows.");
        return new Response(JSON.stringify({ success: true, data: mappedRows }));
      }
      
      if (body.action === 'save_app_state') {
        // ... (not needed for startup)
        return new Response(JSON.stringify({ success: true }));
      }
      if (body.action === 'import_cashbook') {
        // ... (not needed for startup)
        return new Response(JSON.stringify({ success: true }));
      }
    } catch(err) {
      alert("Supabase Mock Fetch CRASHED! Action: " + (options && options.body ? options.body : "unknown") + "\\nError: " + err.message);
      console.error('Supabase Mock Fetch Error:', err);
      return new Response(JSON.stringify({ success: false, message: err.message }));
    }
  }
  
  return originalFetch(url, options);
};
"""

with open("app_supabase.js", "r", encoding="utf-8") as f:
    original = f.read()

new_content = SUPABASE_INJECT + "\n" + original
with open("app_supabase.js", "w", encoding="utf-8") as f:
    f.write(new_content)
print("Injected Supabase safely with debug alerts.")
