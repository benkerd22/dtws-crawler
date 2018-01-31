#!/usr/bin/python3
# -*- coding: utf-8 -*-
'A GUI solution for captcha authentication'

import tkinter as tk
from io import BytesIO
import requests
from PIL import Image, ImageTk
import comm

class App(tk.Frame):
    'A GUI window for entering captcha'

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.master.title('captcha verify')
        self.master.geometry("300x150")
        self.pack()

        self.panel = tk.Label(self)
        self.panel.pack()
        self.refresh()

        self.input = tk.Entry(self)
        self.input.pack()

        self.button = tk.Button(self, text='confirm', command=self.confirm)
        self.button.pack(side='left', expand='yes')

        self.button2 = tk.Button(self, text='refresh', command=self.refresh)
        self.button2.pack(side='left', expand='yes')

    def refresh(self):
        'Refresh the captcha'

        data = requests.get('http://dtws-android2.cbg.163.com/cbg-center//captcha_auth.py',
                            params={'act':'query_captcha'})
        rawimg = Image.open(BytesIO(data.content))
        img = ImageTk.PhotoImage(rawimg)
        self.panel.config(image=img)
        self.panel.image = img
        self.cookies = data.cookies

    def confirm(self):
        'Confirm and send the captcha'

        answer = self.input.get()
        data = requests.get('http://dtws-android2.cbg.163.com/cbg-center//query.py',
                            params={'act':'check_query_captcha', 'captcha':answer},
                            cookies=self.cookies)
        data = data.json()
        print(data['msg'])
        if data['status'] == 1:
            comm.needcaptcha = False
            self.master.destroy()

def auth():
    'Main route'

    comm.needcaptcha = True

    window = App()
    window.mainloop()
