with open('app_supabase.js', 'r', encoding='utf-8') as f:
    js = f.read()

insert_code = '''
      if (body.action === 'save_transaction') {
        const row = body.row;
        const insertObj = {};
        const cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
        cols.forEach(c => {
            insertObj['col_' + c] = (row[c] !== undefined && row[c] !== null) ? String(row[c]) : null;
        });
        
        const res = await originalFetch(`${SUPABASE_URL}/rest/v1/cashbook`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(insertObj)
        });
        
        if (!res.ok) {
            const errText = await res.text();
            throw new Error("Failed to save transaction: " + res.status + " " + errText);
        }
        return new Response(JSON.stringify({ success: true }));
      }
'''

if 'save_transaction' not in js:
    js = js.replace('if (body.action === \'get_app_state\')', insert_code.strip() + '\n\n      if (body.action === \'get_app_state\')')
    with open('app_supabase.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print('save_transaction interceptor added!')
else:
    print('already exists')
