import requests
import json
import time
import re
import os
import captcha

def get_url(url, **kw):
    qurl = 'http://dtws-android2.cbg.163.com/cbg-center/'
    succ = -1
    while succ != 1:
        if succ != -1:
            captcha.auth()
        data = requests.get(qurl + url, **kw).json()
        succ = data['status']

    time.sleep(0.4)
    return data

def get_time():
    return time.strftime('%Y-%m-%d %H', time.localtime())

def get_plus_num(s):
    ret = re.match(r'.+?\((.+?)\)', s).group(1)
    if ret[0] == '+':
        return int(ret[1:])
    return ret

def page_crawler():
    lastpage = False
    page = 1
    i = 0
    while not lastpage:
        data = get_url('/query.py', params={'kindid':2, 'page':page})

        for x in data['equip_list']:
            t = {}
            t['sn'] = x['game_ordersn']
            t['serverid'] = x['equip_serverid']
            t['price'] = int(re.match(r'￥(\d+)', x['price_desc']).group(1))
            t['score'] = int(re.match(r'性别:.  装备评分:(\d+)', x['subtitle']).group(1))
            i += 1
            yield t, i

        lastpage = data['is_last_page']
        print('Finish Page:', page)
        page += 1

def role_crawler(sn, serverid):
    data = get_url('/query.py', params={'act':'get_equip_detail', 'game_ordersn':sn, 'serverid':serverid})

    data = data['equip']
    if data['appointed_roleid'] != '':
        return None

    detail = json.loads(data['equip_desc'])
    base = detail['BaseInfo']
    pets = detail['PetInfo']
    equip = detail['RoleStatus']["EquipInfo"]
    item = {}

    item['serverid'] = serverid
    item['lastest'] = get_time()
    
    item['name'] = data['equip_name']
    item['price'] = data['price'] // 100
    item['minprice'] = item['price']
    item['allow_bargain'] = data['allow_bargain']
    item['area'] = data['area_name']
    item['server'] = data['server_name']
    item['icon'] = data['icon']
    item['status'] = data['status_desc'] + '，' + data['fair_show_end_time_desc']
    item['collect'] = data['collect_num']
    
    item['score'] = int(base['PingFen'])
    item['rank_world'] = base['ShiJiePaiMing']
    item['rank_local'] = base['MenPaiPaiMing']
    item['type'] = base['Faction'] + '（' + base['Sex'] + '）'
    try:
        item['vicetype'] = detail['ViceFactionStatus'][0]['ViceFaction']
    except:
        item['vicetype'] = ""
    item['level'] = base['Level']

    item['pets'] = []
    for x in pets:
        t = {}
        t['name'] = x['Type']
        t['type'] = x['Attr']['DangCi']
        t['progress'] = x['Attr']['ZhuanSheng']
        item['pets'].append(t)

    item['equip_info'] = []
    for s in equip:
        d = list(filter(None, map(lambda x:x.strip(), re.split(r'#[0-9a-zA-Z\_]{1,9}', s))))
        try:
            item['equip_info'].append(d[1])
        except:
            item['equip_info'].append('')
        
    return item

def gen_dataTable(data):
    '状态 性价比 价格 战力 收藏人数 武将（3） 武器（6） 饰品（4） 护心镜 披风 昵称 职业'
    ' 0     1     2    3    4      567      8-13      14-17    18    19   20  21 '

    lastest = max([x[1]['lastest'] for x in data.items()])
    
    table = []
    for sn, x in data.items():
        row = []
        for i in range(22):
            row.append('')

        if not x['exist']:
            status = '下架'
        elif x['lastest'] == lastest:
            status = '新！'
        else:
            status = '正常'
        row[0] = status

        row[1] = x['score'] // x['price']
        row[2] = '¥' + str(x['price'])
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
                row[col] = 0
        
        try:
            row[19] = equip[15]
        except:
            row[19] = '空'
        row[20] = x['name']
        row[21] = x['type'].replace('（', '(').replace('）', ')')

        table.append(row)
    
    real_data = {}
    real_data['data'] = table
    return real_data

def work(src='data.txt'):
    if not os.path.exists(src):
        with open(src, 'w') as f:
            f.write('{}')
        data = {}
    else:
        with open(src, 'r') as f:
            data = json.load(f)

    for y, x in data.items():
        x['exist'] = False
    
    for x, i in page_crawler():
        sn = x['sn']
        if sn in data:
            d = data[sn]
            d['exist'] = True

            if x['price'] != d['price']:
                d['price'] = x['price']
                d['minprice'] = min(d['price'], d['minprice'])
                d['lastest'] = get_time()
                
                print('Change:', i, d['name'], '￥' + str(d['price']), d['score'], sep=' ')
                continue
            
            if x['score'] == d['score']:
                continue
        
        item = role_crawler(sn, x['serverid'])
        if item:
            data[sn] = item
            data[sn]['exist'] = True
            print('New:', i, item['name'], '￥' + str(item['price']), item['score'], sep=' ')
        else:
            pass
            #print('Bad at:', i, '￥' + str(x['price']), x['score'], sep=' ')

    print('Network success')

    with open(src, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    with open('dataTable.json', 'w') as f:
        json.dump(gen_dataTable(data), f)

    print('Refresh success')