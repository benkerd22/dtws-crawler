import json

def show_items(items):
    for x in items:
        if x['score'] < 40000:
            continue
        print('￥', int(x['price']), '  \t', x['score'], '\t', ' ' if x['pets_legend_count'] == 0 else x['pets_legend_count'],
         '\t', x['collect'], '\t', x['name'], '\t', x['type'])

def main():
    items = {}
    with open('data.txt', 'r') as f:
        items = json.load(f)
    items.sort(key=lambda x:x['score']/x['price'])
    #items.sort(key=lambda x:x['collect'])
    show_items(items)

if __name__ == '__main__':
    main()