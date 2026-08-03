import os
import shutil
import subprocess

base_dir = r"c:\saju_old pc\Church_App\anti_gravity"

print("====================================================")
print(" BUILDING ST. GREGORIOS CHURCH ACCOUNTING BUILDS")
print("====================================================")

# Step 1: Rebuild data.js & data_fresh.js
print("\n--- STEP 1: Building Data Bundles ---")
subprocess.run(["py", "build_data_js.py"], cwd=base_dir, check=True)
subprocess.run(["py", "build_fresh_start_data.py"], cwd=base_dir, check=True)

# Step 2: Build Desktop Launcher .exe
print("\n--- STEP 2: Building Desktop Launcher .exe ---")
subprocess.run(["py", "build_executable.py"], cwd=base_dir, check=True)

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Users\sajub\AppData\Local\JDK17\jdk-17.0.10+7"
env["ANDROID_HOME"] = r"C:\Users\sajub\AppData\Local\Android\Sdk"
env["PATH"] = f"{env['JAVA_HOME']}\\bin;{env.get('PATH', '')}"

# Step 3: Build Full Android APK
print("\n--- STEP 3: Compiling FULL Android APK ---")
subprocess.run(["py", r"C:\Users\sajub\.gemini\antigravity-ide\brain\5f917e5b-5caf-4d4c-9628-e225edcce409\scratch\copy_assets_to_android.py", "full"], cwd=base_dir, check=True)
subprocess.run(["cmd.exe", "/c", ".\\gradlew.bat assembleFullDebug"], cwd=os.path.join(base_dir, "android-app"), env=env, check=True)

src_full_apk = os.path.join(base_dir, "android-app", "app", "build", "outputs", "apk", "full", "debug", "app-full-debug.apk")
full_apk_dest = os.path.join(base_dir, "St_Gregorios_Church_Accounting.apk")
full_apk_v73 = os.path.join(base_dir, "St_Gregorios_Church_Accounting_v7.3.apk")
shutil.copy2(src_full_apk, full_apk_dest)
shutil.copy2(src_full_apk, full_apk_v73)
print(f"[OK] Full APK Compiled: {full_apk_dest} & {full_apk_v73} ({os.path.getsize(full_apk_dest)/(1024*1024):.2f} MB)")

# Step 4: Build Fresh Start Android APK
print("\n--- STEP 4: Compiling FRESH START Android APK ---")
subprocess.run(["py", r"C:\Users\sajub\.gemini\antigravity-ide\brain\5f917e5b-5caf-4d4c-9628-e225edcce409\scratch\copy_assets_to_android.py", "fresh"], cwd=base_dir, check=True)
subprocess.run(["cmd.exe", "/c", ".\\gradlew.bat assembleFreshDebug"], cwd=os.path.join(base_dir, "android-app"), env=env, check=True)

src_fresh_apk = os.path.join(base_dir, "android-app", "app", "build", "outputs", "apk", "fresh", "debug", "app-fresh-debug.apk")
fresh_apk_dest = os.path.join(base_dir, "St_Gregorios_Church_Accounting_Fresh_Start.apk")
fresh_apk_v73 = os.path.join(base_dir, "St_Gregorios_Church_Accounting_v7.3_Fresh.apk")
shutil.copy2(src_fresh_apk, fresh_apk_dest)
shutil.copy2(src_fresh_apk, fresh_apk_v73)
print(f"[OK] Fresh Start APK Compiled: {fresh_apk_dest} & {fresh_apk_v73} ({os.path.getsize(fresh_apk_dest)/(1024*1024):.2f} MB)")

# Step 5: Package Distributables
print("\n--- STEP 5: Packaging Distribution ZIP Files ---")
dist_dir = os.path.join(base_dir, "dist")
os.makedirs(dist_dir, exist_ok=True)
shutil.copy2(full_apk_dest, os.path.join(dist_dir, "St_Gregorios_Church_Accounting.apk"))
shutil.copy2(full_apk_v73, os.path.join(dist_dir, "St_Gregorios_Church_Accounting_v7.3.apk"))
shutil.copy2(fresh_apk_dest, os.path.join(dist_dir, "St_Gregorios_Church_Accounting_Fresh_Start.apk"))
shutil.copy2(fresh_apk_v73, os.path.join(dist_dir, "St_Gregorios_Church_Accounting_v7.3_Fresh.apk"))

subprocess.run(["py", "package_distributable.py"], cwd=base_dir, check=True)

print("\n====================================================")
print(" ALL TWIN RELEASES (FULL & FRESH START) BUILT SUCCESSFULLY!")
print("====================================================")
