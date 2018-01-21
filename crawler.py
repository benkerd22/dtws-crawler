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

    return data

def page_crawler():
    brief = []
    lastpage = False
    i = 1
    while not lastpage:
        data = get_url('/query.py', params={'kindid':2, 'page':i})

        for x in data['equip_list']:
            t = {}
            t['sn'] = x['game_ordersn']
            t['serverid'] = x['equip_serverid']
            t['price'] = int(re.match(r'￥(\d+)', x['price_desc']).group(1))
            t['score'] = int(re.match(r'性别:.  装备评分:(\d+)', x['subtitle']).group(1))
            brief.append(t)

        lastpage = data['is_last_page']
        print(i)
        i += 1
        time.sleep(0.3)
    
    return brief

def role_crawler(sn, serverid):
    data = get_url('/query.py', params={'act':'get_equip_detail', 'game_ordersn':sn, 'serverid':serverid})

    data = data['equip']
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

def crawler():
    with open('data.txt', 'r') as f:
        data = json.load(f)
    
    brief = page_crawler()
    i = 0
    for x in brief:
        sn = x['sn']
        if sn in data:
            if x['price'] != data[sn]['price']:
                data[sn]['minprice'] = min(x['price'], data[sn]['minprice'])
                data[sn]['price'] = x['price']
                print(i, data[sn]['name'], sep=' ')
            
            if x['score'] == data[sn]['score']:
                i += 1
                continue
        
        item = role_crawler(sn, x['serverid'])
        data[sn] = item
        i += 1
        print(i, ' ', item['name'], ' ￥', item['price'], ' ', item['score'])
        time.sleep(0.3)

    with open('data.txt', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    crawler()
    
if __name__ == '__main__':
    main()