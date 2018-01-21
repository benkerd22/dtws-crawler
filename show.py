import json
import re
import sys

def show_items(items):
    string = '￥{0: <6}  {1: >5}  {2}  {3: >3}'
    for y, x in items:
        if x['score'] < 30000:
            continue

        n = x['pets_legend_count']
        s = string.format(x['price'], x['score'], ' ' if n == 0 else n, x['collect'])
        print(s, end='')
        
        equip = x['equip_info']
        for i in set([0, 16]) | set(range(4, 13)):
            try:
                s = re.match(r'.+?\((.+?)\)', equip[i]).group(1)
                if s in ['+' + str(x) for x in range(11, 17)]:
                    s = ' '
            except:
                s = ' '
            print('   {0: <3}'.format(s), end='')

        try:
            print('  {0: <20}'.format(equip[15]), end='')
        except:
            print('  {:20}'.format(''), end='')
        print('  {0: <13}  {1}'.format(x['name'], x['type']))

def show(src, output):
    items = {}
    with open(src, 'r') as f:
        items = json.load(f)
    
    s = sorted(items.items(), key=lambda x:x[1]['score']/x[1]['price'], reverse=True)
    with open(output, 'w') as f:
        t = sys.stdout
        sys.stdout = f
        show_items(s)
        sys.stdout = t
    
    print('Show success')