import os
import re

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Strip any comments around supabase.js
html = re.sub(r'<!--\s*<script src="supabase\.js".*?></script>\s*-->', '<script src="supabase.js"></script>', html)

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Properly un-commented supabase.js!')
