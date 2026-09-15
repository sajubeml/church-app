import urllib.request
import json
import os

url = "https://orthodoxchurchmysore.in/accounting/api.php"
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data_export")

def fetch_action(action):
    req = urllib.request.Request(
        url,
        data=json.dumps({"action": action}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

try:
    print("Fetching cashbook from cloud MySQL...")
    cb_res = fetch_action("get_cashbook")
    if cb_res.get("success") and "data" in cb_res:
        cb_file = os.path.join(data_dir, "Cash_Book.json")
        with open(cb_file, "w", encoding="utf-8") as f:
            json.dump(cb_res["data"], f, indent=2)
        print(f"SUCCESS: Saved {len(cb_res['data'])} cashbook rows to Cash_Book.json")
    else:
        print("Failed to fetch cashbook:", cb_res)

    print("Fetching app state (Members / Codes / Ledgers) from cloud MySQL...")
    state_res = fetch_action("get_app_state")
    if state_res.get("success") and "data" in state_res:
        data = state_res["data"]
        
        # Map cloud keys to local json filenames
        mappings = {
            "CHURCH_MASTER_MEMBERS": "Members.json",
            "CHURCH_ACCOUNT_HEADS": "Codes.json",
            "CHURCH_INDIVIDUAL_LEDGERS": "Individual.json",
            "CHURCH_TRIAL_BALANCE": "Trial_Balance.json",
            "CHURCH_BUDGET": "Budget.json"
        }
        
        for key, filename in mappings.items():
            if key in data and data[key]:
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data[key], f, indent=2)
                print(f"SUCCESS: Updated {filename} from cloud state key {key}")
    else:
        print("Failed to fetch app state:", state_res)
except Exception as e:
    print("ERROR syncing data from cloud:", str(e))
