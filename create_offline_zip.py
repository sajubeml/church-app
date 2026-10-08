import os
import shutil
import zipfile

base_dir = r"c:\CASHBOOK_APP"
target_folder_name = "St_Gregorios_Church_Accounting_Offline"
staging_dir = os.path.join(base_dir, "temp_offline_staging", target_folder_name)
zip_name_v11 = os.path.join(base_dir, "St_Gregorios_Church_Accounting_Offline_PC_v11.13.zip")
zip_name_latest = os.path.join(base_dir, "St_Gregorios_Church_Accounting_Offline_PC.zip")

# Recreate staging directory
if os.path.exists(os.path.dirname(staging_dir)):
    shutil.rmtree(os.path.dirname(staging_dir))
os.makedirs(staging_dir, exist_ok=True)

# 1. Single core files
files_map = [
    ("St_Gregorios_Church_Accounting.exe", "St_Gregorios_Church_Accounting.exe"),
    ("index_offline.html", "index.html"),          # Server opens index.html by default
    ("index_offline.html", "index_offline.html"),  # User can also directly double-click this
    ("app.js", "app.js"),
    ("data.js", "data.js"),
    ("styles.css", "styles.css"),
    ("logo_data.js", "logo_data.js"),
    ("church_logo.png", "church_logo.png"),
    ("church_logo.jpg", "church_logo.jpg"),
    ("html2pdf.bundle.min.js", "html2pdf.bundle.min.js"),
    ("jszip.min.js", "jszip.min.js"),
    ("bulk_pdf.js", "bulk_pdf.js"),
]

for src, dst in files_map:
    src_path = os.path.join(base_dir, src)
    if os.path.exists(src_path):
        shutil.copy2(src_path, os.path.join(staging_dir, dst))
        print(f"Copied: {src} -> {dst}")
    else:
        print(f"[WARNING] Missing: {src}")

# 2. Copy data_export directory
data_export_src = os.path.join(base_dir, "data_export")
if os.path.exists(data_export_src):
    shutil.copytree(data_export_src, os.path.join(staging_dir, "data_export"))
    print("Copied: data_export directory")

# 3. Create empty Receipts directory
os.makedirs(os.path.join(staging_dir, "Receipts"), exist_ok=True)
print("Created: Receipts directory")

# 4. Add clear README
readme_text = """============================================================
 ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE
 Offline Accounting Portal (Windows Standalone)
 Version 11.13
============================================================

HOW TO USE ON THIS PC (100% OFFLINE - NO INTERNET NEEDED):

Method 1 (Recommended):
  Double-click 'St_Gregorios_Church_Accounting.exe'
  -> This launches the internal offline application server
     and automatically opens your browser at http://localhost:8088/

Method 2 (Direct Browser):
  Double-click 'index.html' or 'index_offline.html'
  -> Opens directly in Microsoft Edge, Google Chrome, or Brave.

FILES INCLUDED IN THIS PACKAGE:
- St_Gregorios_Church_Accounting.exe : Native Windows Application Launcher
- index.html & index_offline.html    : Main user interface
- app.js                             : Core application engine
- data.js                            : Offline cashbook & ledger database
- styles.css                         : UI styles
- logo_data.js & church_logo.*       : Church branding & print assets
- html2pdf.bundle.min.js & jszip     : Offline PDF & ZIP generators
- data_export/                       : JSON accounting datasets
- Receipts/                          : Auto-saved printed receipts
============================================================
"""
with open(os.path.join(staging_dir, "README_HOW_TO_RUN.txt"), "w", encoding="utf-8") as f:
    f.write(readme_text)

# 5. Build ZIP
root_staging = os.path.dirname(staging_dir)
for zip_path in [zip_name_v11, zip_name_latest]:
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_file = os.path.relpath(abs_file, start=root_staging)
                z.write(abs_file, arcname=rel_file)
    size_mb = os.path.getsize(zip_path) / (1024.0 * 1024.0)
    print(f"[OK] Created: {zip_path} ({size_mb:.2f} MB)")

# Clean up staging directory
shutil.rmtree(root_staging)
print("[OK] Done!")
