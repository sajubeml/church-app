"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Package Release Distribution (Python Native)
Replaces package_distributable.ps1
"""

import os
import shutil
import zipfile

DIST_DIR = os.path.join("dist", "St_Gregorios_Church_Accounting_v1.0")
ZIP_OUTPUT = os.path.join("dist", "St_Gregorios_Church_Accounting_App_v1.0.zip")

FILES_TO_COPY = [
    "St_Gregorios_Church_Accounting.exe",
    "Quick_Start.cmd",
    "index.html",
    "styles.css",
    "app.js",
    "data.js",
    "church_automation.py",
    "convert_xlsm_data.py",
    "build_data_js.py",
    "build_executable.py",
    "package_distributable.py",
    "handover_status.py",
    "start_server.py",
]

README_TEXT = """============================================================
 ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE
 Financial Accounting Portal - Standalone Application v1.0
============================================================

HOW TO RUN:
------------------------------------------------------------
1. Simply double-click 'St_Gregorios_Church_Accounting.exe' 
   or 'Quick_Start.cmd'.

2. The application will start in the background and open 
   your accounting portal in your browser automatically:
   http://localhost:8080/

3. Look for the application icon in your Windows System Tray
   (bottom right near the clock) to manage or exit the app.

INCLUDED FEATURES:
------------------------------------------------------------
• New Voucher / Receipt (frmEntry) with Member Auto-Sync
• Payment Safety Lock (Cash XOR Bank validation)
• Live Receipt Cart & Indian Rupee Words Conversion
• Side-by-Side Dual Receipt (Original & Office Copy)
• Cash Book, Individual Ledgers, Trial Balance & Auction 2025
• Automated Reconciliation Audit Engine

REQUIREMENTS:
------------------------------------------------------------
• Any Windows 7, 8, 10, or 11 PC.
• Python-powered automation tools included!
• No installation required! Portable & ready to run.
"""

def package_distributable():
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    os.makedirs(DIST_DIR, exist_ok=True)
    print(f"Assembling Standalone Package in {DIST_DIR}...")

    # Copy files
    for f in FILES_TO_COPY:
        if os.path.exists(f):
            shutil.copy(f, DIST_DIR)
            print(f"  Copied: {f}")
        else:
            print(f"  [WARNING] File missing: {f}")

    # Copy directory
    if os.path.exists("data_export"):
        shutil.copytree("data_export", os.path.join(DIST_DIR, "data_export"))
        print("  Copied directory: data_export/")

    # Write README.txt
    readme_path = os.path.join(DIST_DIR, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as rf:
        rf.write(README_TEXT)
    print("  Created: README.txt")

    # Create ZIP archive
    print(f"\nCompressing into {ZIP_OUTPUT}...")
    with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, start=DIST_DIR)
                z.write(abs_path, arcname=rel_path)

    zip_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024.0 * 1024.0)
    print("\n[OK] DISTRIBUTION PACKAGE CREATED SUCCESSFULLY!")
    print(f"     ZIP File: {os.path.abspath(ZIP_OUTPUT)} ({zip_size_mb:.2f} MB)")
    print(f"     Uncompressed Folder: {os.path.abspath(DIST_DIR)}")

if __name__ == "__main__":
    package_distributable()
