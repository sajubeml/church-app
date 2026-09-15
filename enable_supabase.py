import os

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<!-- <script src="supabase.js"></script> -->', '<script src="supabase.js"></script>')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Re-enabled local supabase.js script.')
