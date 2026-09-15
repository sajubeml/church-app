import os
import re

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>', '<!-- <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script> -->')

# Change cache buster
html = re.sub(r'app_supabase\.js\?v=\d+', 'app_supabase.js?v=1010', html)

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Disabled Excel script and busted cache.')
