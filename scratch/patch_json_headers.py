import json
import os

files_to_update = [
    r"c:\CASHBOOK_APP\data_export\Individual.json",
    r"c:\CASHBOOK_APP\Individual_fresh.json",
    r"C:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-10-23.json"
]

for fpath in files_to_update:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            d = json.load(f)
        
        if isinstance(d, dict) and "individual" in d:
            target = d["individual"]
        elif isinstance(d, list):
            target = d
        else:
            target = None
            
        if target and len(target) >= 4 and isinstance(target[3], dict):
            old_val = target[3].get("Q")
            target[3]["Q"] = "Sunday School / OVBS"
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
            print(f"Updated {fpath}:\n  Q was: '{old_val}' -> '{target[3]['Q']}'")
        else:
            print(f"Skipped or invalid format: {fpath}")
    else:
        print(f"File not found: {fpath}")
