import os

base_dir = r"c:\saju_old pc\Church_App\anti_gravity_v9.2"

# 1. Update build.gradle.kts version
gradle_path = os.path.join(base_dir, "android-app", "app", "build.gradle.kts")
with open(gradle_path, "r", encoding="utf-8") as f:
    gradle_content = f.read()

gradle_content = gradle_content.replace('versionCode = 57', 'versionCode = 58')
gradle_content = gradle_content.replace('versionName = "9.8"', 'versionName = "9.9"')
gradle_content = gradle_content.replace('versionCode = 55', 'versionCode = 58')
gradle_content = gradle_content.replace('versionName = "9.6"', 'versionName = "9.9"')

with open(gradle_path, "w", encoding="utf-8") as f:
    f.write(gradle_content)
print("Updated build.gradle.kts version to 9.9")


# 2. Update MainActivity.kt for zoom mode
main_activity_path = os.path.join(base_dir, "android-app", "app", "src", "main", "java", "com", "stgregorios", "churchaccounting", "MainActivity.kt")
with open(main_activity_path, "r", encoding="utf-8") as f:
    ma_content = f.read()

ma_content = ma_content.replace('settings.displayZoomControls = false', 'settings.displayZoomControls = true')
with open(main_activity_path, "w", encoding="utf-8") as f:
    f.write(ma_content)
print("Enabled zoom controls in MainActivity.kt")


# 3. Update styles.css in all locations to remove sticky headers for mobile scrolling
css_paths = [
    os.path.join(base_dir, "styles.css"),
    os.path.join(base_dir, "deployment_files", "mobile apk", "styles.css"),
    os.path.join(base_dir, "deployment_files", "cpanel", "styles.css"),
    os.path.join(base_dir, "deployment_files", "github-supabase", "styles.css"),
    os.path.join(base_dir, "android-app", "app", "src", "main", "assets", "styles.css")
]

target_col_reg_old = """  .indiv-table .sticky-col.col-reg {
    position: sticky !important;
    left: 0 !important;"""
target_col_reg_new = """  .indiv-table .sticky-col.col-reg {
    position: static !important;"""

target_thead_col_reg_old = """  .indiv-table thead th.sticky-col.col-reg {
    position: sticky !important;
    left: 0 !important;"""
target_thead_col_reg_new = """  .indiv-table thead th.sticky-col.col-reg {
    position: static !important;"""

target_tfoot_col_reg_old = """  .indiv-table tfoot td.sticky-col.col-reg {
    position: sticky !important;
    left: 0 !important;"""
target_tfoot_col_reg_new = """  .indiv-table tfoot td.sticky-col.col-reg {
    position: static !important;"""

target_col_grand_old = """  .indiv-table .sticky-col.col-grand {
    min-width: 42px !important;"""
target_col_grand_new = """  .indiv-table .sticky-col.col-grand {
    position: static !important;
    min-width: 42px !important;"""


for path in css_paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace(target_col_reg_old, target_col_reg_new)
        content = content.replace(target_thead_col_reg_old, target_thead_col_reg_new)
        content = content.replace(target_tfoot_col_reg_old, target_tfoot_col_reg_new)
        content = content.replace(target_col_grand_old, target_col_grand_new)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated CSS: {path}")

