import os
import re

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Make sure all scripts have crossorigin
html = re.sub(r'<script src="app_supabase\.js\?v=\d+"></script>', '<script src="app_supabase.js?v=9999" crossorigin="anonymous"></script>', html)
html = html.replace('<script src="supabase.js"></script>', '<script src="supabase.js" crossorigin="anonymous"></script>')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Added crossorigin to local scripts.')
