#!/usr/bin/python3
# -*- coding: utf-8 -*-
'A tiny web server for showing data from the crawler'

import os
import json
import time
import threading
import requests
from flask import Flask, request#, send_from_directory

import crawler
import comm


app = Flask(__name__, static_url_path='')
th = threading.Thread()
cookies = 0

def do_crawler():
    'A new thread for crawler'

    time.sleep(1)
    print('wake up')
    crawler.work()
    time.sleep(10)

@app.route('/')
def index():
    'Home html'

    with open(os.path.join('web', 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()

    return html

@app.route('/dataTable.json')
def raw_data():
    'Crawler results for showing'

    with open('dataTable.json') as f:
        return f.read()

@app.route('/crawler_refresh')
def crawler_refresh():
    'Web client requests for a new crawler thread'

    global th

    response = {}
    response['status'] = (comm.nowpage == comm.maxpage)
    response['progress'] = comm.nowpage / comm.maxpage * 100

    if comm.nowpage == comm.maxpage:
        comm.nowpage = 0

    if not th.isAlive():
        th = threading.Thread(target=do_crawler)
        th.start()

    if comm.needcaptcha:
        response['status'] = 2

    return json.dumps(response)

@app.route('/captcha.jpg')
def raw_captcha_img():
    'Web client needs a new captcha image'

    global cookies

    res = requests.get('http://dtws-android2.cbg.163.com/cbg-center//captcha_auth.py',
                       params={'act':'query_captcha'})
    cookies = res.cookies
    return res.content

@app.route('/check_captcha')
def check_captcha():
    'Web client provide an answer'

    global cookies

    captcha = request.args.get('ans')
    res = requests.get('http://dtws-android2.cbg.163.com/cbg-center//query.py',
                       params={'act':'check_query_captcha', 'captcha':captcha},
                       cookies=cookies)
    comm.needcaptcha = (res.json()['status'] == 1)

    return res.json()['msg']

'''
@app.route('/<string:folder>/<path:path>')
def send_file(folder, path):
    print('PATH=', path)
    return send_from_directory('f:\\dtws-crawler\\web\\' + folder, path)
'''

if __name__ == '__main__':
    comm.init()
    app.run(host='0.0.0.0', port=5000)
