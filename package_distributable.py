"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Package Release Distribution (Python Native)
Generates Twin Packages: Full Data vs Fresh Start (7-Day Trial)
"""

import os
import shutil
import zipfile

FILES_TO_COPY = [
    "St_Gregorios_Church_Accounting.exe",
    "St_Gregorios_Church_Accounting.vbs",
    "St_Gregorios_Church_Accounting.apk",
    "St_Gregorios_Church_Accounting_v2.0.apk",
    "Quick_Start.cmd",
    "Start_Portal.cmd",
    "index.html",
    "styles.css",
    "app.js",
    "church_logo.png",
    "church_logo.jpg",
    "church_automation.py",
    "convert_xlsm_data.py",
    "build_data_js.py",
    "build_executable.py",
    "package_distributable.py",
    "handover_status.py",
    "start_server.py",
    "html2pdf.bundle.min.js",
]

README_FULL_TEXT = """============================================================
 ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE
 Financial Accounting Portal - Full Release Version 1.0
============================================================
Includes all historical parish accounting records, member ledgers,
and trial balance data up to FY 2026-2027.
"""

README_FRESH_TEXT = """============================================================
 ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE
 Financial Accounting Portal - Fresh Start (7-Day Trial)
============================================================
Initialized with empty cashbook transactions and default account heads
for starting a brand new financial year or clean parish installation.
* Includes 7-Day Trial License Guard.
"""

def create_dist_package(target_dir_name, zip_name, data_file_source, readme_content):
    dist_dir = os.path.join("dist", target_dir_name)
    zip_output = os.path.join("dist", zip_name)

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
        
    os.makedirs(dist_dir, exist_ok=True)
    print(f"\nAssembling Package in {dist_dir}...")

    # Copy standard files
    for f in FILES_TO_COPY:
        if os.path.exists(f):
            dest_name = f
            shutil.copy(f, os.path.join(dist_dir, dest_name))

    # Copy data file as data.js
    if os.path.exists(data_file_source):
        shutil.copy(data_file_source, os.path.join(dist_dir, "data.js"))
        print(f"  Copied dataset: {data_file_source} -> data.js")

    # Copy directory data_export
    if os.path.exists("data_export"):
        shutil.copytree("data_export", os.path.join(dist_dir, "data_export"))

    # Create Receipts directory
    os.makedirs(os.path.join(dist_dir, "Receipts"), exist_ok=True)

    # Write README.txt
    with open(os.path.join(dist_dir, "README.txt"), "w", encoding="utf-8") as rf:
        rf.write(readme_content)

    # Compress into ZIP
    print(f"Compressing into {zip_output}...")
    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, start=dist_dir)
                z.write(abs_path, arcname=rel_path)

    zip_size_mb = os.path.getsize(zip_output) / (1024.0 * 1024.0)
    print(f"[OK] Package Created: {zip_output} ({zip_size_mb:.2f} MB)")

def package_distributable():
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # 1. Full Release Package
    create_dist_package(
        target_dir_name="St_Gregorios_Church_Accounting_v9.1",
        zip_name="St_Gregorios_Church_Accounting_App_v9.1.zip",
        data_file_source="data.js",
        readme_content=README_FULL_TEXT
    )

    # 2. Fresh Start 7-Day Trial Package
    create_dist_package(
        target_dir_name="St_Gregorios_Church_Accounting_Fresh_Start_v9.1",
        zip_name="St_Gregorios_Church_Accounting_Fresh_Start_Trial_v9.1.zip",
        data_file_source="data_fresh.js" if os.path.exists("data_fresh.js") else "data.js",
        readme_content=README_FRESH_TEXT
    )

if __name__ == "__main__":
    package_distributable()
