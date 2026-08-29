import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
deploy_dir = os.path.join(base_dir, "deployment_files")

print("====================================================")
print(" PREPARING SEPARATE DEPLOYMENT FOLDERS")
print("====================================================")

# Remove old deploy dir if exists
if os.path.exists(deploy_dir):
    shutil.rmtree(deploy_dir)

# Create 3 distinct deployment folders
github_dir = os.path.join(deploy_dir, "github-supabase")
cpanel_dir = os.path.join(deploy_dir, "cpanel")
local_dir = os.path.join(deploy_dir, "mobile apk v1.0")

os.makedirs(github_dir)
os.makedirs(cpanel_dir)
os.makedirs(local_dir)

# Helper function to copy files
def copy_files(file_list, dest_folder):
    for f in file_list:
        src = os.path.join(base_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest_folder, f))

# Common files across all
common_files = ["styles.css", "church_logo.png", "church_logo.jpg", "logo.jpg", "data.js", "html2pdf.bundle.min.js"]

# 1. GitHub (Cloud Sync)
# Uses index_supabase.html as index.html, app_supabase.js, and supabase.js
print("Packaging GitHub Cloud Sync version...")
copy_files(common_files + ["app_supabase.js", "supabase.js"], github_dir)
shutil.copy2(os.path.join(base_dir, "index_supabase.html"), os.path.join(github_dir, "index.html"))

# 2. cPanel (Cloud Sync)
# Same as GitHub, but maybe includes API or htaccess if they are present
print("Packaging cPanel Cloud Sync version...")
copy_files(common_files + ["app_supabase.js", "supabase.js", ".htaccess", "api.php"], cpanel_dir)
shutil.copy2(os.path.join(base_dir, "index_supabase.html"), os.path.join(cpanel_dir, "index.html"))

# 3. Mobile APK / Local (No Cloud Sync)
# Uses standard index.html (which points to app.js) and app.js
print("Packaging Mobile APK / Local version...")
copy_files(common_files + ["app.js", "index.html"], local_dir)

print("\n[OK] Deployment folders created successfully in 'deployment_files/'!")
