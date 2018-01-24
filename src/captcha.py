from PIL import Image, ImageTk
from io import BytesIO
import requests
import tkinter as tk

class App(tk.Frame):
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

        self.button = tk.Button(self, text='confirm', command=self.send)
        self.button.pack(side='left', expand='yes')

        self.button2 = tk.Button(self, text='refresh', command=self.refresh)
        self.button2.pack(side='left', expand='yes')
    
    def refresh(self):
        data = requests.get('http://dtws-android2.cbg.163.com/cbg-center//captcha_auth.py', params={'act':'query_captcha'})
        rawimg = Image.open(BytesIO(data.content))
        img = ImageTk.PhotoImage(rawimg)
        self.panel.config(image=img)
        self.panel.image = img
        self.cookies = data.cookies
    
    def send(self):
        answer = self.input.get()
        data = requests.get('http://dtws-android2.cbg.163.com/cbg-center//query.py', 
            params={'act':'check_query_captcha', 'captcha':answer},
            cookies=self.cookies)
        data = data.json()
        print(data['msg'])
        if data['status'] == 1:
            self.master.destroy()

def auth():
    window = App()
    window.mainloop()