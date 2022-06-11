from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
import collections

class ProjectList(tk.Frame):

    def __init__(self, parent, *args, **Kwargs):
        super().__init__( parent, *args, **Kwargs)
        
        self.nodes = dict()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.current_path_list = []
        self.tree = ttk.Treeview(self, selectmode='none')

        self.tree.heading('#0',text='ProjectList', anchor='w')

        self.tree.grid(row=0, column=0, sticky='NSEW')

        self.scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
       
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.grid(row=0, column=1,rowspan=2, sticky='NSW')
        self.scrollbar_x.grid(row=1, column=0, sticky='NSEW')
        
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        
    def populate(self, project_path: Path):
        
        paths = [path for path in project_path.glob('**/*')]
        if not compare_list(paths, self.current_path_list):    
            rot = self.tree.get_children()
            if rot:
                self.tree.delete(rot)

            self.current_path_list = paths
            self.insert_node('', project_path.name, project_path)
        else:
            return

    def insert_node(self, parent, text, abspath):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if Path.is_dir(abspath):
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(self.tree.get_children(node))
            for p in Path.iterdir(abspath):
                self.insert_node(node, p.name, Path.joinpath(abspath, p))

def compare_list(list1,list2):
        if(collections.Counter(list1)==collections.Counter(list2)):
            return True
        else:
            return False

def summary_of_current_project(status):

    state = ["Summary of all the tasks performed."]

    s_dict = status.status_dict

    engine_list = s_dict.keys()
    if engine_list:
        state.append(" ")
        for engine in engine_list:
            state.append(f"Engine: {engine}")

            task_list = s_dict[engine].keys()

            if task_list:
                for i, task in  enumerate(task_list):
                    if s_dict[engine][task]['done'] == True:
                        state.append(f"     {task}")
                    
                
                state.append(" ")
    else:
        state.append("No tasks have been performed yet.")

    state = "\n".join(state)

    return state
