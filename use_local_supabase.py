import os

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2" crossorigin="anonymous"></script>', '<script src="supabase.js"></script>')
html = html.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>', '<script src="supabase.js"></script>')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated index_supabase.html to use local supabase.js')
