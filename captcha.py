from PIL import Image, ImageTk
from io import BytesIO
import requests
import tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.master.title('captcha')
        self.master.geometry("300x600")
        self.pack()

        #self.panel = tk.Label(self, image = img)
        #self.panel.image = img
        #self.panel.pack()#side = "bottom", fill = "both", expand = "yes")
        self.refresh()
        
        self.input = tk.Entry(self)
        self.input.pack()

        self.button = tk.Button(self, text='send', command=self.send)
        self.button.pack()

        self.button2 = tk.Button(self, text='refresh', command=self.refresh)
        self.button2.pack()
    
    def refresh(self):
        data = requests.get('http://dtws-android2.cbg.163.com/cbg-center//captcha_auth.py', params={'act':'query_captcha'})
        rawimg = Image.open(BytesIO(data.content))
        img = ImageTk.PhotoImage(rawimg)
        self.panel = tk.Label(self, image = img)
        self.panel.image = img
        self.panel.pack()
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