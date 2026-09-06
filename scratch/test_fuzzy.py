import json

d = json.load(open('c:/Users/sajub/Downloads/St_Gregorios_Church_Backup_2026-08-31.json', encoding='utf-8'))
cb = d['cashbook']
headers = d['individual'][3]
for r in cb:
    if r.get('A') == 'Date' or not r.get('B'): continue
    partStr = str(r.get('E', r.get('M', ''))).lower()
    
    targetCol = 'E'
    for col in 'E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL'.split():
        title = str(headers.get(col, '')).lower()
        if not title: continue
        
        if (
            ('holy qurbana' in partStr and 'qurbana' in title) or
            ('donat' in partStr and 'donat' in title and 'breakfast' not in partStr and 'marriage' not in partStr and 'cemetry' not in partStr) or
            ('perunnal' in partStr and 'perunnal' in title) or
            ('passion' in partStr and 'passion' in title) or
            ('george' in partStr and 'george' in title) or
            ('thomas' in partStr and 'thomas' in title) or
            ('mary' in partStr and 'mary' in title) or
            ('blessing' in partStr and 'blessing' in title) or
            ('auction' in partStr and 'auction' in title) or
            ('cemetry' in partStr and 'cemetry' in title) or
            ('breakfast' in partStr and 'breakfast' in title) or
            ('birthday' in partStr and 'birthday' in title) or
            ('anniversary' in partStr and 'anniversary' in title) or
            ('baptism' in partStr and 'baptism' in title) or
            ('bann' in partStr and 'bann' in title) or
            ('catholicate' in partStr and 'catholicate' in title) or
            ('metropolitan' in partStr and 'metropolitan' in title) or
            ('mission' in partStr and 'mission' in title) or
            ('seminary' in partStr and 'seminary' in title) or
            ('priest' in partStr and 'priest' in title) or
            ('sunday school' in partStr and 'sunday school' in title) or
            ('harvest' in partStr and 'harvest' in title) or
            ('christmas' in partStr and 'christmas' in title) or
            ('new year' in partStr and 'new year' in title) or
            ('miscellaneous' in partStr and 'miscellaneous' in title)
        ):
            targetCol = col
            break
            
    # Now check if it mapped to something unexpected
    if 'mary' in partStr and targetCol == 'Y':
        pass # Expected
    if 'seminary' in partStr and targetCol == 'Y':
        print(f"BUG! {r['B']}: {partStr} mapped to Y (St. Mary's)")
        
    print(f"{r['B']}: {partStr} -> {targetCol}")

