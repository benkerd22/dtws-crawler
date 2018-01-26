from flask import Flask, send_from_directory
import os
import json
import crawler
import threading
import time
import comm

app = Flask(__name__, static_url_path='')
th = threading.Thread()

def myfunc():
    time.sleep(3);
    print('wake up')
    crawler.work()
    time.sleep(5);

@app.route('/')
def index():
    with open('web\\index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    return html

@app.route('/dataTable.json')
def rawdata():
    with open('dataTable.json') as f:
        return f.read()

@app.route('/crawler_refresh')
def crawler_refresh():
    global th

    if not th.isAlive():
        th = threading.Thread(target=myfunc)
        th.start()
    
    response = {}
    response['status'] = comm.progress == 50
    response['progress'] = comm.progress * 2

    if comm.progress == 50:
        comm.progress = 0
    return json.dumps(response)

@app.route('/<string:folder>/<path:path>')
def send_file(folder, path):
    print('PATH=', path)
    return send_from_directory('f:\\dtws-crawler\\web\\' + folder, path)

if __name__ == '__main__':
    comm.init()
    app.run(host='0.0.0.0', port=5000)