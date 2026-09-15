import json
import os
import shutil

backup_path = r"C:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-13 (3).json"
script_dir = os.path.dirname(os.path.abspath(__file__))

# Target directories to update
targets = [
    os.path.join(script_dir, "data_export"),
    r"C:\saju_old pc\Church_App\final working version-9\data_export"
]

try:
    print(f"Reading backup from: {backup_path}...")
    with open(backup_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cb_data = data.get("cashbook", [])
    members_data = data.get("masterMembers", [])
    heads_data = data.get("customAccountHeads", [])
    individual_data = data.get("individual", [])
    
    print(f"Loaded: {len(cb_data)} cashbook rows, {len(members_data)} members, {len(heads_data)} account heads, {len(individual_data)} individual ledger rows.")
    
    for t_dir in targets:
        if not os.path.exists(t_dir):
            os.makedirs(t_dir)
            
        # Write Cash Book
        with open(os.path.join(t_dir, "Cash_Book.json"), "w", encoding="utf-8") as f:
            json.dump(cb_data, f, indent=2)
            
        # Write Members
        with open(os.path.join(t_dir, "Members.json"), "w", encoding="utf-8") as f:
            json.dump(members_data, f, indent=2)
            
        # Write Codes (Account Heads)
        with open(os.path.join(t_dir, "Codes.json"), "w", encoding="utf-8") as f:
            json.dump(heads_data, f, indent=2)
            
        # Write Individual Ledgers
        with open(os.path.join(t_dir, "Individual.json"), "w", encoding="utf-8") as f:
            json.dump(individual_data, f, indent=2)
            
        print(f"Successfully updated database folder: {t_dir}")
        
    print("SUCCESS: Local JSON database files updated with latest backup data!")
except Exception as e:
    print("ERROR importing backup:", str(e))
