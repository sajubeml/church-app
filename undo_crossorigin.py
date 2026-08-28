import os

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('crossorigin="anonymous"', '')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Removed crossorigin attribute.')
