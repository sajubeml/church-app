"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Project Handover Status Checker (Python Native)
Replaces handover_status.ps1
"""

import os

FILES_TO_CHECK = [
    "working Church_Accounting_ok ind updte 21-7-(26-27).xlsm",
    "St_Gregorios_Church_Accounting.exe",
    "index.html",
    "styles.css",
    "app.js",
    "data.js",
    "AppLauncher.cs",
    "church_automation.py",
    "convert_xlsm_data.py",
    "build_data_js.py",
    "build_executable.py",
    "package_distributable.py",
    "handover_status.py",
    "start_server.py",
    os.path.join("dist", "St_Gregorios_Church_Accounting_App_v1.0.zip")
]

def check_status():
    print("==================================================")
    print("  ST. GREGORIOS CHURCH ACCOUNTING HANDOVER STATUS ")
    print("==================================================")

    for f in FILES_TO_CHECK:
        if os.path.exists(f):
            size_kb = os.path.getsize(f) / 1024.0
            print(f"  [OK] {f:<55} ({size_kb:.2f} KB)")
        else:
            print(f"  [MISSING] {f}")

    print("\n=== PORTABLE RELEASE PACKAGE ===")
    zip_path = os.path.join("dist", "St_Gregorios_Church_Accounting_App_v1.0.zip")
    if os.path.exists(zip_path):
        zip_size_mb = os.path.getsize(zip_path) / (1024.0 * 1024.0)
        print(f"  Distributable ZIP: {zip_path} ({zip_size_mb:.2f} MB)")
    else:
        print("  Distributable ZIP: Not found")

    print("\n=== PROJECT CONTEXT SUMMARY ===")
    print("  * Web Portal: index.html (Data loaded from data.js & data_export/)")
    print("  * Desktop Executable: St_Gregorios_Church_Accounting.exe (Port 8080)")
    print("  * Python Engine: church_automation.py & build scripts (Python 3.11)")
    print("  * All documentation saved in HANDOVER.md")
    print("==================================================\n")

if __name__ == "__main__":
    check_status()
