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

    time.sleep(0.3)
    return data

def page_crawler():
    lastpage = False
    page = 1
    while not lastpage:
        data = get_url('/query.py', params={'kindid':2, 'page':page})

        for x in data['equip_list']:
            t = {}
            t['sn'] = x['game_ordersn']
            t['serverid'] = x['equip_serverid']
            t['price'] = int(re.match(r'￥(\d+)', x['price_desc']).group(1))
            t['score'] = int(re.match(r'性别:.  装备评分:(\d+)', x['subtitle']).group(1))
            yield t

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
    item['lastest'] = time.asctime(time.localtime(time.time()))
    
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
    item['pets_legend_count'] = 0
    for x in pets:
        t = {}
        t['name'] = x['Type']
        t['type'] = x['Attr']['DangCi']
        t['progress'] = x['Attr']['ZhuanSheng']
        item['pets'].append(t)

        if (t['type'], t['progress']) == ('钻石卡', '0/0'):
            item['pets_legend_count'] += 1

    item['equip_info'] = []
    for s in equip:
        d = list(filter(None, map(lambda x:x.strip(), re.split(r'#[0-9a-zA-Z\_]{1,9}', s))))
        try:
            item['equip_info'].append(d[1])
        except:
            item['equip_info'].append('')
        
    return item

def work(src, only_lastest=True):
    with open(src, 'r') as f:
        data = json.load(f)
    
    i = 0
    for x in page_crawler():
        sn = x['sn']
        if sn in data:
            if x['price'] != data[sn]['price']:
                try:
                    data[sn]['minprice'] = min(x['price'], data[sn]['minprice'])
                except:
                    data[sn]['minprice'] = x['price']
                data[sn]['price'] = x['price']
                print('Change:', i, data[sn]['name'], '￥', data[sn]['price'], data[sn]['score'], sep=' ')
                i += 1
                continue
            
            if x['score'] == data[sn]['score']:
                if only_lastest:
                    print('Stopped at:', i)
                    break
                i += 1
                continue
        
        item = role_crawler(sn, x['serverid'])
        if item:
            data[sn] = item
            print('New:', i, item['name'], '￥', item['price'], item['score'], sep=' ')
        else:
            print('Bad at ', x['price'], ' ', x['score'])

        i += 1

    print('Crawler success')
    with open(src, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print('Refresh success')