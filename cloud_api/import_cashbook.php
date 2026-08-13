<!DOCTYPE html>
<html>
<head>
<title>Import Cashbook to MySQL</title>
<style>
body { font-family: Arial; padding: 20px; background: #1a1a2e; color: #e0e0e0; }
#log { background: #16213e; padding: 15px; border-radius: 8px; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
button { padding: 12px 24px; font-size: 16px; cursor: pointer; background: #0f3460; color: white; border: none; border-radius: 8px; margin: 10px 5px; }
button:hover { background: #1a5276; }
.done { color: #2ecc71; font-weight: bold; }
.err { color: #e74c3c; }
</style>
</head>
<body>
<h1>Cashbook → MySQL Import</h1>
<p>This imports your Cash_Book.json data into the MySQL database, 10 rows at a time.</p>
<button onclick="startImport()">Start Import</button>
<button onclick="testAPI()">Test API First</button>
<div id="log"></div>

<script>
const log = document.getElementById('log');
function addLog(msg, cls) {
  log.innerHTML += `<span class="${cls||''}">${msg}</span>\n`;
  log.scrollTop = log.scrollHeight;
}

async function testAPI() {
  addLog("Testing API...");
  try {
    const r = await fetch('./api.php', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({action:'test'})
    });
    const d = await r.json();
    addLog("API Response: " + JSON.stringify(d), d.success ? 'done' : 'err');
  } catch(e) {
    addLog("API Error: " + e.message, 'err');
  }
}

async function startImport() {
  addLog("Loading Cash_Book.json...");
  
  let rows;
  try {
    const res = await fetch('./data_export/Cash_Book.json');
    rows = await res.json();
    addLog("Loaded " + rows.length + " rows from JSON.");
  } catch(e) {
    addLog("Failed to load JSON: " + e.message, 'err');
    return;
  }

  // Setup tables first
  addLog("Setting up tables...");
  try {
    const r = await fetch('./api.php', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({action:'setup_tables'})
    });
    const d = await r.json();
    addLog("Tables: " + d.message, d.success ? 'done' : 'err');
  } catch(e) {
    addLog("Setup error: " + e.message, 'err');
  }

  // Import in batches of 10
  const batchSize = 10;
  let imported = 0;
  
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    try {
      const r = await fetch('./api.php', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({action:'import_cashbook', rows: batch})
      });
      const d = await r.json();
      if (d.success) {
        imported += d.count || batch.length;
        addLog(`Batch ${Math.floor(i/batchSize)+1}: imported ${imported}/${rows.length}`);
      } else {
        addLog(`Batch error: ${d.message}`, 'err');
      }
    } catch(e) {
      addLog(`Network error at batch ${Math.floor(i/batchSize)+1}: ${e.message}`, 'err');
    }
    
    // Small delay to not overwhelm server
    await new Promise(r => setTimeout(r, 200));
  }

  addLog("");
  addLog("========================================", 'done');
  addLog("IMPORT COMPLETE! " + imported + " rows in MySQL!", 'done');
  addLog("========================================", 'done');
  addLog("");
  addLog("You can now delete this file from cPanel.");
}
</script>
</body>
</html>
