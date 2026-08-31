"""
Patch the fixed individual ledger data from the recalculated JSON into data.js
for all deployment targets (android assets, deployment files, root).
"""
import json
import re
import os

# Load the fixed backup
with open(r"c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30_FIXED.json", "r", encoding="utf-8") as f:
    fixed_data = json.load(f)

fixed_individual = fixed_data["individual"]

# Convert individual array to JavaScript format
def individual_to_js(individual):
    lines = []
    for row in individual:
        parts = []
        for key in sorted(row.keys(), key=lambda k: (len(k), k)):
            val = row[key]
            # Format the value
            if isinstance(val, (int, float)):
                if val == 0:
                    parts.append(f'"{key}": 0')
                elif val == int(val):
                    parts.append(f'"{key}": {int(val)}')
                else:
                    parts.append(f'"{key}": {val}')
            else:
                # Escape quotes in string values
                val_str = str(val).replace('\\', '\\\\').replace('"', '\\"')
                parts.append(f'"{key}": "{val_str}"')
        lines.append("    {" + ", ".join(parts) + "}")
    return ",\n".join(lines)

js_individual = individual_to_js(fixed_individual)

# Patch data.js files
data_js_paths = [
    r"c:\saju_old pc\Church_App\anti_gravity_v9.2\android-app\app\src\main\assets\data.js",
    r"c:\saju_old pc\Church_App\anti_gravity_v9.2\data.js",
    r"c:\saju_old pc\Church_App\anti_gravity_v9.2\deployment_files\mobile apk\data.js",
    r"c:\saju_old pc\Church_App\anti_gravity_v9.2\deployment_files\cpanel\data.js",
    r"c:\saju_old pc\Church_App\anti_gravity_v9.2\deployment_files\github-supabase\data.js",
]

for path in data_js_paths:
    if not os.path.exists(path):
        print(f"SKIP (not found): {path}")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find and replace the individual array section
    # Pattern: individual: [\n...\n  ],\n  trialBalance:
    pattern = r'(individual:\s*\[)\n.*?\n(\s*\],\s*\n\s*trialBalance:)'
    
    replacement = f'individual: [\n{js_individual}\n  ],\n  trialBalance:'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"PATCHED: {path}")
    else:
        print(f"NO CHANGE (pattern not found): {path}")

print("\nDone patching data.js files!")
