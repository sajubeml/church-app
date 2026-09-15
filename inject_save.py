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
        const updates = [];
        for (let key in body.state_data) {
           updates.push({ key_name: key, json_data: body.state_data[key] }); 
        }
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/app_state?on_conflict=key_name`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
                'Content-Type': 'application/json',
                'Prefer': 'resolution=merge-duplicates'
            },
            body: JSON.stringify(updates)
        });
        if (!res.ok) throw new Error("Failed to save app state: " + res.status);
        return new Response(JSON.stringify({ success: true }));
      }
      
      if (body.action === 'import_cashbook') {
        const rows = body.rows;
        
        // 1. Delete all existing rows
        await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook?id=gt.0`, {
            method: 'DELETE',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
            }
        });
        
        // 2. Prepare new rows for bulk insert
        const insertArr = rows.map((row, idx) => {
            const insertObj = { id: (idx + 1) }; 
            const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            cols.forEach(c => {
                if (row[c] !== undefined && row[c] !== null) insertObj['col_' + c] = String(row[c]);
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
                    'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(batch)
            });
            if (!res.ok) throw new Error("Batch insert failed: " + res.status);
        }
        
        return new Response(JSON.stringify({ success: true }));
      }
      
    } catch(err) {
      console.error('Supabase Mock Fetch Error:', err);
      return new Response(JSON.stringify({ success: false, message: err.message }));
    }
  }
  
  // Also handle the alternative /api/bulk_import URL just in case
  if (url && typeof url === 'string' && url.includes('/api/bulk_import')) {
     try {
        const rows = JSON.parse(options.body);
        
        await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook?id=gt.0`, {
            method: 'DELETE',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
            }
        });
        
        const insertArr = rows.map((row, idx) => {
            const insertObj = { id: (idx + 1) };
            const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            cols.forEach(c => {
                if (row[c] !== undefined && row[c] !== null) insertObj['col_' + c] = String(row[c]);
            });
            return insertObj;
        });
        
        for (let i=0; i<insertArr.length; i+=500) {
            const batch = insertArr.slice(i, i+500);
            const res = await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(batch)
            });
            if (!res.ok) throw new Error("Batch insert failed: " + res.status);
        }
        
        return new Response('', {status: 200}); 
     } catch(e) {
         console.error('Supabase Bulk Import Mock Error:', e);
         return new Response('', {status: 500});
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
print("Injected fully working save queries.")

# Update the HTML file to bust the cache
import re
with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'app_supabase\.js\?v=\d+', 'app_supabase.js?v=7890', html)
with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index_supabase.html to bust cache.")
