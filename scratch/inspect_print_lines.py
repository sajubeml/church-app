import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("=== SEARCHING FOR ALL PRINT / TITLE / PDF MENTIONS IN APP.JS ===")
lines = js.splitlines()
for idx, line in enumerate(lines, 1):
    if any(k in line.lower() for k in ['print', 'pdf', 'document.title']):
        print(f"Line {idx}: {line.strip()}")
