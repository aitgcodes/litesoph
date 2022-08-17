from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
import collections
from tkinter import *
import os
import ctypes
import pathlib

class ProjectList:

    def __init__(self, app):
        
        self.treedata = dict()
        self.current_path_list = []
        self.treeview = app.treeview
        
        self.treeview.bind('<<TreeviewOpen>>', self.open_node)


    def pathChange(self, project_path: Path):
        # Get all Files and Folders from the given Directory

        currentPath = StringVar(self, name='currentPath',value=pathlib.Path.cwd())

        directory = os.listdir(currentPath.get())
        # Clearing the list
        list.delete(0, END)
        # Inserting the files and directories into the list
        for file in directory:
            list.insert(0, file)
        
    def populate(self, project_path: Path):
        
        paths = [path for path in project_path.glob('**/*')]
        if not compare_list(paths, self.current_path_list):    
            rot = self.treeview.get_children()
            if rot:
                self.treeview.delete(rot)

            self.current_path_list = paths
            self.insert_node('', project_path.name, project_path)
        else:
            return

    def insert_node(self, parent, text, abspath):
        node = self.treeview.insert(parent, 'end', text=text, open=False)
        if Path.is_dir(abspath):
            self.treedata[node] = abspath
            self.treeview.insert(node, 'end')

    def open_node(self, event):
        node = self.treeview.focus()
        abspath = self.treedata.pop(node, None)
        if abspath:
            self.treeview.delete(self.treeview.get_children(node))
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


# class navsidebar:

#     def __init__(self, app):
        
#         self.newFileName = StringVar(self, "File.dot", 'new_name')
#         self.currentPath = StringVar(self, name='currentPath', value=pathlib.Path.cwd())
        

#     def create_new_job(self,*_):
#         print("new job working") 

#         global top
#         top = Toplevel(self)
#         top.geometry("250x150")
#         top.resizable(False, False)
#         top.title("Child Window")
#         top.columnconfigure(0, weight=1)
#         Label(top, text='Enter File or Folder name').grid()
#         Entry(top, textvariable=self.newFileName).grid(column=0, pady=10, sticky='NSEW')
#         Button(top, text="Create", command=self.newFileOrFolder).grid(pady=10, sticky='NSEW')

#     def newFileOrFolder(self,*_):
#     # check if it is a file name or a folder
#         # self.project_window = v.StartPage(self.main_window) 
#         # newFileName = StringVar(self.project_window, "File.dot", 'new_name')
#         self.currentPath = StringVar(self.project_window, name='currentPath', value=pathlib.Path.cwd())


#         if len(self.newFileName.get().split('.')) != 1:
#             open(os.path.join(self.currentPath.get(), self.newFileName.get()), 'w').close()
#         else:
#             os.mkdir(os.path.join(self.currentPath.get(), self.newFileName.get()))
#         # destroy the top
#         top.destroy()
#         # pathChange()


