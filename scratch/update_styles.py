import os
import glob

# Paths to all styles.css files
base_dir = r"c:\saju_old pc\Church_App\anti_gravity_v9.2"
paths = [
    os.path.join(base_dir, "styles.css"),
    os.path.join(base_dir, "deployment_files", "mobile apk", "styles.css"),
    os.path.join(base_dir, "deployment_files", "cpanel", "styles.css"),
    os.path.join(base_dir, "deployment_files", "github-supabase", "styles.css"),
    os.path.join(base_dir, "android-app", "app", "src", "main", "assets", "styles.css")
]

target_name_old = """  .indiv-table .sticky-col.col-name {
    position: sticky !important;
    left: 45px !important;
    min-width: 70px !important;
    max-width: 90px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    padding: 2px !important;
    font-size: 0.65rem !important;
    border-right: 1px solid #e2e8f0 !important;
  }"""

target_name_new = """  .indiv-table .sticky-col.col-name {
    position: static !important;
    min-width: 70px !important;
    max-width: 90px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    padding: 2px !important;
    font-size: 0.65rem !important;
    border-right: 1px solid #e2e8f0 !important;
  }"""

target_grand_old = """  .indiv-table .sticky-col.col-grand {
    min-width: 55px !important;
    max-width: 65px !important;
    font-size: 0.68rem !important;
    padding: 2px !important;
  }"""

target_grand_new = """  .indiv-table .sticky-col.col-grand {
    min-width: 42px !important;
    max-width: 50px !important;
    font-size: 0.60rem !important;
    padding: 2px !important;
  }"""

for path in paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace content
        content = content.replace(target_name_old, target_name_new)
        content = content.replace(target_grand_old, target_grand_new)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {path}")
    else:
        print(f"File not found: {path}")
