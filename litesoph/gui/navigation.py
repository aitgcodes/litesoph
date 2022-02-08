import os
import pathlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile
from tkinter import filedialog

class ProjectList(tk.Frame):

    def __init__(self, parent, *args, **Kwargs):
        super().__init__( parent, *args, **Kwargs)
        
        self.nodes = dict()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
       
        self.tree = ttk.Treeview(self, columns=['ProjectList'], selectmode='browse')

        self.tree.grid(row=0, column=0, sticky='NSEW')

        self.tree.bind('<Double-1>', self._on_open_record)
        self.tree.bind('<Retrun>', self._on_open_record)
        
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        # xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky='NSW')

        # self.tree.heading('#0',anchor='w')
       

        
        # ysb.grid(row=0, column=1, sticky='ns')
        # xsb.grid(row=1, column=0, sticky='ew')
        
       

        abspath = os.path.abspath(self.path)
        self.insert_node('', abspath, abspath)
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        
    def populate(self, project_list):

        for row in self.tree.get_children():
            self.tree.delete(row)
        
        abspath = os.path.abspath(self.path)
        self.insert_node('', abspath, abspath)
    

    def _on_open_record(self, *args):
        self.event_generate('<<OpenProject>>')

    @property
    def selection_id(self):
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

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

