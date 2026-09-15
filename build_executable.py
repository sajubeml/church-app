"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Build Desktop Executable (Python Native)
Replaces build_executable.ps1
"""

import os
import subprocess
import sys

CSC_PATH = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
OUTPUT_EXE = "St_Gregorios_Church_Accounting.exe"
SOURCE_CS = "AppLauncher.cs"

def build_executable():
    if not os.path.exists(CSC_PATH):
        print(f"[ERROR] C# Compiler (csc.exe) not found at: {CSC_PATH}")
        sys.exit(1)

    if not os.path.exists(SOURCE_CS):
        print(f"[ERROR] Source file {SOURCE_CS} not found!")
        sys.exit(1)

    print("Building St. Gregorios Church Accounting Standalone Application...")
    if os.path.exists(OUTPUT_EXE):
        try:
            os.remove(OUTPUT_EXE)
        except Exception:
            pass
    
    cmd = [
        CSC_PATH,
        "/target:winexe",
        "/optimize+",
        "/win32manifest:app.manifest",
        "/r:System.Windows.Forms.dll",
        "/r:System.Drawing.dll",
        f"/out:{OUTPUT_EXE}",
        SOURCE_CS
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0 and os.path.exists(OUTPUT_EXE):
        exe_size_kb = os.path.getsize(OUTPUT_EXE) / 1024.0
        print(f"[OK] Compilation Successful!")
        print(f"     Executable Created: {OUTPUT_EXE} ({exe_size_kb:.2f} KB)")
    else:
        print("[ERROR] Compilation Failed!")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
