import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile
from tkinter import filedialog
class Nav():
    def __init__(self, master,path):
        self.nodes = dict()
        
        self.tree = ttk.Treeview(master)
        ysb = ttk.Scrollbar(master, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(master, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0',anchor='w')
       

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        
 
        abspath = os.path.abspath(path)
        self.insert_node('', abspath, abspath)
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        

    def insert_node(self, parent, text, abspath):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(abspath):
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(self.tree.get_children(node))
            for p in os.listdir(abspath):
                self.insert_node(node, p, os.path.join(abspath, p))

    
