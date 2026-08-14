import os
import shutil
import sys
import json

mode = sys.argv[1].lower() if len(sys.argv) > 1 else "full"
src_dir = os.path.dirname(os.path.abspath(__file__))
dest_assets = os.path.join(src_dir, "android-app", "app", "src", "main", "assets")

os.makedirs(dest_assets, exist_ok=True)

files_to_copy = [
    "index.html",
    "styles.css",
    "app.js",
    "church_logo.png",
    "church_logo.jpg",
    "html2pdf.bundle.min.js"
]

for fname in files_to_copy:
    src_path = os.path.join(src_dir, fname)
    if os.path.exists(src_path):
        dest_name = fname
        shutil.copy2(src_path, os.path.join(dest_assets, dest_name))
        print(f"Copied: {fname} -> {dest_name}")

if mode == "fresh":
    # Copy data_fresh.js as data.js
    fresh_js = os.path.join(src_dir, "data_fresh.js")
    if os.path.exists(fresh_js):
        shutil.copy2(fresh_js, os.path.join(dest_assets, "data.js"))
        print("Copied dataset: data_fresh.js -> data.js (FRESH START)")
    else:
        print("[WARNING] data_fresh.js not found, using data.js")
        shutil.copy2(os.path.join(src_dir, "data.js"), os.path.join(dest_assets, "data.js"))
else:
    # Copy standard data.js
    full_js = os.path.join(src_dir, "data.js")
    shutil.copy2(full_js, os.path.join(dest_assets, "data.js"))
    print("Copied dataset: data.js (FULL DATA)")

# Copy directory data_export
data_export_src = os.path.join(src_dir, "data_export")
data_export_dest = os.path.join(dest_assets, "data_export")
if os.path.exists(data_export_dest):
    shutil.rmtree(data_export_dest)

if os.path.exists(data_export_src):
    shutil.copytree(data_export_src, data_export_dest)
    if mode == "fresh":
        # Overwrite Cash_Book.json and Trial_Balance.json with empty [] in fresh mode
        with open(os.path.join(data_export_dest, "Cash_Book.json"), "w", encoding="utf-8") as f:
            json.dump([], f)
        with open(os.path.join(data_export_dest, "Trial_Balance.json"), "w", encoding="utf-8") as f:
            json.dump([], f)
        print("Emptied Cash_Book.json and Trial_Balance.json in android assets for Fresh Start build.")

print(f"[OK] Android assets populated for {mode.upper()} mode successfully!")
