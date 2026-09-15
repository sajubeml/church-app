import os
import shutil

shutil.copy("app_cloud_final.js", "app_supabase.js")

SUPABASE_INJECT = """
const SUPABASE_URL = 'https://djpuxmrjxsrhgfrtppky.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_QjkuMrFMwtc2imGfy0XCdw_37h05VtE';

const originalFetch = window.fetch;
window.fetch = async function(url, options) {
  if (url && typeof url === 'string' && url.includes('api.php')) {
    try {
      const body = JSON.parse(options.body);
      
      if (body.action === 'get_app_state') {
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/app_state?select=*`, {
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
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
                'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
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
        return new Response(JSON.stringify({ success: true }));
      }
      if (body.action === 'import_cashbook') {
        return new Response(JSON.stringify({ success: true }));
      }
    } catch(err) {
      alert("Supabase API Mock Failed!\\n" + err.message);
      return new Response(JSON.stringify({ success: false, message: err.message }));
    }
  }
  
  if (url && typeof url === 'string' && url.includes('/api/bulk_import')) {
      return new Response('', {status: 200}); 
  }
  
  return originalFetch(url, options);
};
"""

with open("app_supabase.js", "r", encoding="utf-8") as f:
    original = f.read()

new_content = SUPABASE_INJECT + "\n" + original
with open("app_supabase.js", "w", encoding="utf-8") as f:
    f.write(new_content)
print("Injected raw REST fetch logic.")

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
html = re.sub(r'<script src="supabase\.js".*?></script>', '<!-- pure REST mode -->', html)
html = re.sub(r'app_supabase\.js\?v=\d+', 'app_supabase.js?v=5555', html)

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Removed supabase.js completely.")
