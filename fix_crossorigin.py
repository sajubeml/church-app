import os

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>', '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2" crossorigin="anonymous"></script>')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Added crossorigin attribute.')
