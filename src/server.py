from flask import Flask, send_from_directory
import os
import re
import json
import crawler
import threading

app = Flask(__name__, static_url_path='')
th = threading.Thread()

@app.route('/')
def index():
    with open('web\\index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    return html

@app.route('/dataTable.json')
def rawdata():
    with open('dataTable.json') as f:
        return f.read()

@app.route('/crawler-refresh')
def crawler_refresh():
    global th
    if not th.isAlive():
        th = threading.Thread(target=crawler.work())
        th.start()
        return "Now working"
    else:
        return "Still running"

@app.route('/<string:folder>/<path:path>')
def send_file(folder, path):
    print('PATH=', path)
    return send_from_directory('f:\\dtws-crawler\\web\\' + folder, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)