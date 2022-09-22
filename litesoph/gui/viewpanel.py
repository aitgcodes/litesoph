import tkinter as tk

class ViewPanelManager:
    def __init__(self, app):
        self.app = app
        builder = self.app.builder
        self.view_txt = builder.get_object('view_text')

    def clear_text(self):
        self.view_txt.delete("1.0", tk.END)

    def insert_text(self, text, state='normal'):
        self.view_txt.configure(state='normal')
        self.clear_text()
        
        self.view_txt.insert(tk.END, text)
        self.view_txt.configure(state=state)

    def get_text(self):
        txt = self.view_txt.get(1.0, tk.END)
        return txt
       
