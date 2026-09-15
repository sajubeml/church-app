import os

with open("index_cloud.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("app_cloud_final.js", "app_supabase.js")
html = html.replace("</head>", '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n</head>')

with open("index_supabase.html", "w", encoding="utf-8") as f:
    f.write(html)
print("index_supabase.html generated!")
