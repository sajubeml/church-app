import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

for name in ['Codes.json', 'Resources.json', 'Master_Ledgers.json']:
    path = os.path.join('data_export', name)
    if os.path.exists(path):
        print(f"=== {name} ===")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for row in data[:20]:
            print(row)
