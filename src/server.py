from flask import Flask, render_template, send_from_directory
import os
import json

template_dir = os.path.abspath('../web')
app = Flask(__name__, static_url_path='', template_folder='f:\\dtws-crawler\\web')

def gen():
    with open('data.txt', 'r') as f:
        data = json.load(f)
    
    lastest = max([x[1]['lastest'] for x in data.items()])
    header = ['状态', '性价比', '价格', '评分', '武将', '收藏人数', '昵称', '职业']
    table = []
    for sn, x in data.items():
        row = []
        for i in range(len(header)):
            row.append('')

        if not x['exist']:
            row[0] = 'x'
        elif x['lastest'] == lastest:
            row[0] = 'N'
        else:
            row[0] = ' '
        
        row[1] = x['score'] // x['price']
        row[2] = x['price']
        row[3] = x['score']
        try:
            row[4] = x['pets'][0]['name']
        except:
            row[4] = ''
        row[5] = x['collect']
        row[6] = x['name']
        row[7] = x['type']

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