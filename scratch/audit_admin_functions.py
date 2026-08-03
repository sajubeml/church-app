import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

index_path = r"c:\saju_old pc\Church_App\anti_gravity\index.html"
app_path = r"c:\saju_old pc\Church_App\anti_gravity\app.js"

with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

with open(app_path, "r", encoding="utf-8") as f:
    js = f.read()

# Find all onclick function calls in HTML
onclicks = re.findall(r'onclick="([^"]+)"', html)
funcs_in_html = set()
for c in onclicks:
    m = re.match(r'([a-zA-Z0-9_]+)\s*\(', c)
    if m:
        funcs_in_html.add(m.group(1))

print(f"Total unique onclick functions in index.html: {len(funcs_in_html)}")

missing = []
found = []
for func in sorted(funcs_in_html):
    # Check if function exists in JS
    if re.search(r'function\s+' + func + r'\b', js) or f"window.{func}" in js:
        found.append(func)
    else:
        missing.append(func)

print("\n--- ADMIN & APPLICATION ONCLICK AUDIT ---")
print(f"✅ Found functions in app.js ({len(found)}):")
for f in found:
    print(f"  [OK] {f}")

if missing:
    print(f"\n❌ Missing functions in app.js ({len(missing)}):")
    for f in missing:
        print(f"  [MISSING] {f}")
else:
    print("\n🎉 ALL HTML ONCLICK FUNCTIONS ARE DEFINED IN APP.JS!")
