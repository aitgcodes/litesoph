import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile
from tkinter import filedialog
class Nav():
    def __init__(self, master,path):
        self.nodes = dict()
        #frame = tk.Frame(master)
        self.tree = ttk.Treeview(master)
        ysb = ttk.Scrollbar(master, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(master, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0',anchor='w')
       # filename = filedialog.askopenfilename(title="Open a File", filetypes=(("xlxs files", ".*xlsx"),
#("All Files", "*.")))

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        #frame.grid()
 
        abspath = os.path.abspath(path)
        self.insert_node('', abspath, abspath)
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        
#    def openfile():
#        self.tree = filedialog.askopenfilename(initialdir="str(Path.home())",filetypes=(("python files", "*.py")))
#        text = open(self.tree,'r')
#        stuff = self.tree.read()
#        #print(message)
#        self.tree.readlines()
        #my_text_insert(END, stuff)
#        self.tree.close()

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

    #def readfile(self, parent, text):
        #file = filedialog.askopenfilename(
            #filetypes=[("CSV files", ".csv", "text files", ".txt", "python files", ".py")])
        #if file:        
            #fob=open(file,'r')    
            #i=0
            #for data in fob:
                #trv.insert("",'end',iid=i,text=data)
                #i=i+1
        #else:
            #print("No file chosen")
    
#if __name__ == '__main__':
    #root = tk.Tk()
    #Nav = Nav(root, path='.')
   # root.mainloop()
