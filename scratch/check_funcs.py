import sys, re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

onclicks = set(re.findall(r'onclick=[\"\']([a-zA-Z0-9_]+)\(', html))
print('Onclick functions in index.html:')
for fn in sorted(onclicks):
    in_js = fn in js
    print(f'  {fn}: {"EXISTS" if in_js else "MISSING!"}')
