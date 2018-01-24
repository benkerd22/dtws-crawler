from flask import Flask, render_template, send_from_directory
import os
import re
import json

template_dir = os.path.abspath('../web')
app = Flask(__name__, static_url_path='', template_folder='f:\\dtws-crawler\\web')

def get_plus_num(s):
    ret = re.match(r'.+?\((.+?)\)', s).group(1)
    if ret[0] == '+':
        return ret[1:]
    return ret

def gen():
    with open('data.txt', 'r') as f:
        data = json.load(f)
    
    lastest = max([x[1]['lastest'] for x in data.items()])
    header = ['状态', '性价比', '价格', '评分', '武将', '收藏人数', '昵称', '职业']
    '状态 性价比 价格 战力 收藏人数 武将（3） 武器（6） 饰品（4） 护心镜 披风 昵称 职业'
    ' 0     1     2    3    4      567      8-13      14-17    18    19   20  21 '
    table = []
    for sn, x in data.items():
        row = []
        for i in range(22):
            row.append('')

        if not x['exist']:
            row[0] = '下架'
        elif x['lastest'] == lastest:
            row[0] = '新！'
        else:
            row[0] = '  '
        
        row[1] = x['score'] // x['price']
        row[2] = x['price']
        row[3] = x['score']
        row[4] = x['collect']

        row[5], row[6], row[7] = 0, 0, 0
        for pet in x['pets']:
            if pet['type'] == '钻石卡':
                if re.match(r'0/0', pet['progress']):
                    row[5] += 1
                elif re.match(r'\d+/10440', pet['progress']):
                    row[6] += 1
                elif re.match(r'\d+/1510', pet['progress']):
                    row[7] += 1

        equip = x['equip_info']
        edict = {8:0, 9:6, 10:7, 11:8, 12:9, 13:10, 14:4, 15:5, 16:11, 17:12, 18:16}
        for col, index in edict.items():
            try:
                row[col] = get_plus_num(equip[index])
            except:
                row[col] = ' '
        
        try:
            row[19] = equip[15]
        except:
            row[19] = ' '
        row[20] = x['name']
        row[21] = x['type'].replace('（', '(').replace('）', ')')

        table.append(row)
    
    return header, table

@app.route('/')
def index():
    with open('web\\index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    return html

@app.route('/data.json')
def home():
    header, table = gen()
    data = {}
    data['data'] = table
    return json.dumps(data)

@app.route('/<string:folder>/<path:path>')
def send_file(folder, path):
    print('PATH=', path)
    return send_from_directory('f:\\dtws-crawler\\web\\' + folder, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)