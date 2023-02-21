from tkinter import ttk
import tkinter as tk
from litesoph.gui.visual_parameter import myfont


class TreeView(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args) 
        self.frame1= ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame2= ttk.Frame(self, borderwidth=2, relief='groove')

        self.frame1.pack(fill=tk.BOTH, anchor='n', expand=True)
        self.frame2.pack(fill=tk.BOTH, anchor='n', expand=True)
               
        self.tree = create_tree_and_scroll(parent= self.frame1)

    def add_button_widgets(self):
        self.button_add = tk.Button(self.frame2, text="Add", activebackground="#78d6ff", command=lambda: self.add_button())
        self.button_add['font'] = myfont()
        self.button_add.grid(row=1, column=1, padx=3, pady=3,sticky='nsew')

        self.button_del = tk.Button(self.frame2, text="Remove", activebackground="#78d6ff", command=lambda: self.remove_button())
        self.button_del['font'] = myfont()
        self.button_del.grid(row=1, column=2, padx=3, pady=3,sticky='nsew')

    
    def add_button(self):
        # adds data and updates tree
        pass

    def remove_button(self):
        # removes data and updates tree
        pass

def create_tree_and_scroll(parent):
    tree = ttk.Treeview(parent)
    tree.grid(row=0, column=1,columnspan=3, sticky=tk.NSEW)

    # add a scrollbar
    scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=4, sticky='ns')
    return tree

def add_columns(tree:ttk.Treeview, tree_data:list, column_map:dict= {}):

    # Get the columns
    data_sample = tree_data[0]
    assert isinstance(data_sample, dict)
    columns = tuple(data_sample.keys())
    tree['columns'] = columns

    # Defining columns
    tree.column("#0", width=0, stretch=0)
    for c in columns:
        tree.column(column=c, anchor=tk.W, width=140)

    # Adding headings
    tree.heading("#0", text="", anchor=tk.W)
    for c in columns:
        column_name = column_map.get(c, c)
        tree.heading(column= c, text=column_name, anchor=tk.W)
        
def update_tree_data(tree:ttk.Treeview, tree_data:list):
    """ Updates tree from tree_data"""

    # Adding data
    for i, set in enumerate(tree_data):        
        assert isinstance(set, dict)      
        _entries = tuple(set.values()) 
        tree.insert(parent='', index='end', iid=i, values=_entries) 

def get_pol_list(pol_var:str):
    assert pol_var in ["X", "Y", "Z"] 
    if pol_var == "X":
        pol_list = [1,0,0]         
    elif pol_var == "Y":
        pol_list = [0,1,0] 
    elif pol_var == "Z":
        pol_list = [0,0,1]                
    return pol_list

def get_pol_var(pol_list:list):
    if pol_list == [1,0,0]:
        pol_var = "X"          
    elif pol_list == [0,1,0]:
        pol_var = "Y" 
    elif pol_list == [0,0,1]:
        pol_var = "Z"                
    return pol_var
