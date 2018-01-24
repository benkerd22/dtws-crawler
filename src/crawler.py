import requests
import json
import time
import re
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

def work(src):
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
    print('Refresh success')