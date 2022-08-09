from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.     
from tkinter import messagebox
from tkinter import scrolledtext
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
import os

import pathlib 
from tkinter import filedialog 
from litesoph.gui.viewpanel import ViewPanelManager
from litesoph.gui import views as v
from litesoph.simulations import check_task_pre_conditon, get_engine_task, models as m

from tkinter.filedialog import askdirectory
import tkinter.messagebox
import tkinter as tk
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15


# class MainMenu(tk.Menu):
#     """The Application's main menu"""

#     def _event(self, sequence):
#         def callback(*_):
#             root = self.master.winfo_toplevel()
#             root.event_generate(sequence)
#         return callback

#     def __init__(self, parent, **kwargs):
#         super().__init__(parent, **kwargs)


#         file_menu = Menu(self, tearoff=0)
#         file_menu.add_command(label="New")
#         file_menu.add_command(label="Open")
#         file_menu.add_command(label="Save")
#         file_menu.add_command(label="Save as...")
#         file_menu.add_command(label="Exit", command=parent.quit)
#         self.add_cascade(label="file")


#         edit = Menu(self, tearoff=0)
#         edit.add_command(label="Undo")
#         edit.add_command(label="Cut")
#         edit.add_command(label="Copy")
#         edit.add_command(label="Paste")
#         edit.add_command(label="Delete")
#         edit.add_command(label="Select All")
#         edit.add_cascade(label="Edit")

#         view = Menu(self, tearoff=0)
#         view.add_command(label="file")
#         view.add_command(label="Graphs")
#         view.add_command(label="Images")
#         view.add_command(label="Movies")
#         view.add_command(label="VMD")
#         view.add_command(label="Vesta")
#         self.add_cascade(label="View", menu=view)
        
#         help = Menu(self, tearoff=0)
#         help.add_command(label="About")
#         help.add_command(label="Webpage")
#         self.add_cascade(label="Help", menu=help)


#         myFont = font.Font(family='Helvetica', size=10, weight='bold')

#         self['font'] = myFont

#         parent.config(menu=self)
#         self.configure(bg="gainsboro")

    


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import OrderedDict                        # importing subprocess to run command line jobs as in terminal.





class GenericMainMenu(tk.Menu, v.WorkManagerPage):
  """The Application's main menu"""



  accelerators = {
    'file_open': 'Ctrl+O',
    'quit': 'Ctrl+Q',
    
  }

  keybinds = {
    '<Control-o>': '<<FileSelect>>',
    '<Control-q>': '<<FileQuit>>',
   
  }

  styles = {}

  def _event(self, sequence):
    """Return a callback function that generates the sequence"""
    def callback(*_):
      root = self.master.winfo_toplevel()
      root.event_generate(sequence)

    return callback


  def _add_file_open(self, menu):

    menu.add_command(
      label='Select file…', command=self._event('<<FileSelect>>'),
      #image=self.icons.get('file'), compound=tk.LEFT
  )

  
 
  
  
  def _add_new_project(self, menu):
    
    
    # path = tk.StringVar()   # Receiving user's file_path selection
    # folder = tk.StringVar() # Receiving user's folder_name selection
    
    # # Dir select
    # def selectPath():   
    #   path_ = askdirectory()
    #   path.set(path_)

    # def create_file():  

    #   print("folder_name: ", folder.get())
    #   print("path_name: ", path.get())
    #   dirs = os.path.join(path.get(), folder.get())
    #   if not os.path.exists(dirs):
    #       os.makedirs(dirs)
    #       tkinter.messagebox.showinfo('Tips:','Folder name created successfully!')
    #   else:
    #       tkinter.messagebox.showerror('Tips','The folder name exists, please change it')

      



    # def donothing():
    #   print('Do Nothing ....')

    def create_project():

      
      # Create widget
      # root = tk.Menu()
      # root.title("Root Window")
      # root.geometry("450x300")
    
    # Create widget
      top1 = Toplevel(self)
      
      # Define title for window
      top1.title("Create New Project")
      
      # specify size
      top1.geometry("550x200")

      
      self.label_proj = Label(top1,text="Project Name",bg=label_design['bg'],fg=label_design['fg'])
      self.label_proj['font'] = label_design['font']
      self.label_proj.grid(column=0, row= 3, sticky=tk.W,  pady=10, padx=10)        
      
      self.entry_proj = Entry(top1,textvariable=  self._var['proj_name'])
      self.entry_proj['font'] = myfont()
      self.entry_proj.grid(column=1, row= 3, sticky=tk.W)
      self.entry_proj.delete(0, tk.END)
              
      self.button_project = Button(top1,text="Create New Project",width=18, activebackground="#78d6ff",command=self._create_project)
      self.button_project['font'] = myfont()
      self.button_project.grid(column=2, row= 3, sticky=tk.W, padx= 10, pady=10)        
        
      
      # Create label
      # label = Label(top1, text="Project Name")
      # name_entry = Entry(top1,textvariable = 'x', font=('calibre',10,'normal'))
      # submit_button = Button(top1, text = "Create New Project", command = donothing)

      # label_path = Label(top1,text = "Target path:")
      # name_entry_path = Entry(top1, textvariable = path, font=('calibre',10,'normal'))
      # submit_button_path = Button(top1, text = "Path select: ", command = selectPath)

      # label_fname=Label(top1,text = "Folder name:")
      # name_entry_fname=Entry(top1,textvariable = folder)
      # submit_button_fname=Button(top1, text = "Submit: ", command = self._create_project)


      # label.pack()
      # name_entry.pack()
      # submit_button.pack()

      
      # label_path.grid(row=0,column=0)
      # name_entry_path.grid(row=0,column=1)
      # submit_button_path.grid(row=0,column=2)


      # label_fname.grid(row=1,column=0)
      # name_entry_fname.grid(row=1,column=1)
      # submit_button_fname.grid(row=1,column=2)




     

      
      

    def open_project():
	
      # Create widget
      root = Tk()
      root.title("Root Window")
      root.geometry("450x300")
      top1 = Toplevel(root)
      
      # Define title for window
      top1.title("Toplevel1")
      
      # specify size
      top1.geometry("200x200")
      
      # Create label
      label = Label(top1,
            text = "This is a Toplevel1 window")
        
        
        # entry widget
        
        
        
      name_entry = Entry(top1,textvariable = 'x', font=('calibre',10,'normal'))
      # Create Exit button
      button1 = Button(top1, text = "Exit", command = top1.destroy)
      
      # create button to open toplevel2
      # button2 = Button(top1, text = "open toplevel2",
      # 				command = open_Toplevel2)
      label.pack()
      name_entry.pack()
      button1.pack()
        
      name_entry.place(x = 100, y = 50)

      # Display until closed manually
      top1.mainloop()


    menu.add_command(
      label='New Project…', command= create_project,
      #image=self.icons.get('file'), compound=tk.LEFT
      )


  
  def _add_open_project(self, menu):

    menu.add_command(
      label='Open Project…', command=self._event('<<OpenExistingProject>>'),
      #image=self.icons.get('file'), compound=tk.LEFT
  )

  def _add_quit(self, menu):
    menu.add_command(
      label='Exit', command=self._event('<<ProjectQuit>>'),
      #image=self.icons.get('quit'), compound=tk.LEFT
    )

  def _add_refresh_config(self, menu):
    menu.add_command(
      label='Refresh Config', command=self._event('<<RefreshConfig>>'),
      #image=self.icons.get('quit'), compound=tk.LEFT
    )


  def _add_about(self, menu):
    menu.add_command(
      label='About…', command=self.show_about,
      #image=self.icons.get('about'), compound=tk.LEFT
    )

  def _add_webpage(self, menu):
    menu.add_command(
      label='Webpage', command=self.show_about,
      #image=self.icons.get('about'), compound=tk.LEFT
    )

  def _build_menu(self):
    # The file menu
    self._menus['File'] = tk.Menu(self, tearoff=False, **self.styles)
    #self._add_file_open(self._menus['File'])
    self._add_new_project(self._menus['File'])
    self._add_open_project(self._menus['File'])
    self._menus['File'].add_separator()
    self._add_quit(self._menus['File'])

    #Tools menu
    self._menus['Tools'] = tk.Menu(self, tearoff=False, **self.styles)

    # The options menu
    self._menus['Options'] = tk.Menu(self, tearoff=False, **self.styles)
    
    

    # switch from recordlist to recordform
    self._menus['Go'] = tk.Menu(self, tearoff=False, **self.styles)
    self._add_refresh_config(self._menus['Go'])

    # The help menu
    self._menus['Help'] = tk.Menu(self, tearoff=False, **self.styles)
    self.add_cascade(label='Help', menu=self._menus['Help'])
    self._add_about(self._menus['Help'])

    for label, menu in self._menus.items():
      self.add_cascade(label=label, menu=menu)
    self.configure(**self.styles)

  def __init__(self, parent, **kwargs):
    super().__init__(parent, **kwargs)
    self._menus = dict()
    self._build_menu()
    self._bind_accelerators()
    self.configure(**self.styles)

  def show_about(self):
    """Show the about dialog"""

    about_message = ''
    about_detail = ()
    
    messagebox.showinfo(
      title='About', message=about_message, detail=about_detail
    )

  @staticmethod
  def _on_theme_change(*_):
    """Popup a message about theme changes"""
    message = "Change requires restart"
    detail = (
      "Theme changes do not take effect"
      " until application restart"
    )
    messagebox.showwarning(
      title='Warning',
      message=message,
      detail=detail
    )

  def _bind_accelerators(self):

    for key, sequence in self.keybinds.items():
      self.bind_all(key, self._event(sequence))

class LinuxMainMenu(GenericMainMenu):
  """Differences for Linux:

    - Edit menu for autofill options
    - View menu for font & theme options
    - Use color theme for menu
  """
  styles = {
    #'background': '#333',
    'foreground': 'black',
    'activebackground': '#777',
    'activeforeground': 'white',
    'relief': tk.GROOVE
  }


  def _build_menu(self):
    self._menus['File'] = tk.Menu(self, tearoff=False, **self.styles)
#    self._add_file_open(self._menus['File'])
    self._add_new_project(self._menus['File'])
    self._add_open_project(self._menus['File'])
    self._menus['File'].add_separator()
    self._add_quit(self._menus['File'])

    # The edit menu
    self._menus['Edit'] = tk.Menu(self, tearoff=False, **self.styles)
  

    #Tools menu
    self._menus['Tools'] = tk.Menu(self, tearoff=False, **self.styles)
    

    # The View menu
    self._menus['View'] = tk.Menu(self, tearoff=False, **self.styles)
   

    # switch from recordlist to recordform
    self._menus['Go'] = tk.Menu(self, tearoff=False, **self.styles)
    self._add_refresh_config(self._menus['Go'])

    # The help menu
    self._menus['Help'] = tk.Menu(self, tearoff=False, **self.styles)
    self._add_about(self._menus['Help'])
    self._add_webpage(self._menus['Help'])

    for label, menu in self._menus.items():
      self.add_cascade(label=label, menu=menu)


class MacOsMainMenu(GenericMainMenu):
  """
  Differences for MacOS:

    - Create App Menu
    - Move about to app menu, remove 'help'
    - Remove redundant quit command
    - Change accelerators to Command-[]
    - Add View menu for font & theme options
    - Add Edit menu for autofill options
    - Add Window menu for navigation commands
  """
  keybinds = {
      '<Command-o>': '<<FileSelect>>',
     
    }
  accelerators = {
    'file_open': 'Cmd-O',
   
    }

  def _add_about(self, menu):
    menu.add_command(
      label='About', command=self.show_about,
      #image=self.icons.get('about'), compound=tk.LEFT
    )

  def _build_menu(self):
    self._menus['LITESOPH'] = tk.Menu(
      self, tearoff=False,
      name='apple'
    )
    self._add_about(self._menus['LITESOPH'])
    self._menus['LITESOPH'].add_separator()

    self._menus['File'] = tk.Menu(self, tearoff=False)
#    self._add_file_open(self._menus['File'])

    self._menus['Edit'] = tk.Menu(self, tearoff=False)
    

    #Tools menu
    self._menus['Tools'] = tk.Menu(self, tearoff=False)
    

    # View menu
    self._menus['View'] = tk.Menu(self, tearoff=False)
   

    # Window Menu
    self._menus['Window'] = tk.Menu(self, name='window', tearoff=False)
    

    for label, menu in self._menus.items():
      self.add_cascade(label=label, menu=menu)


def get_main_menu_for_os(os_name):
  """Return the menu class appropriate to the given OS"""
  menus = {
    'Linux': LinuxMainMenu,
    'Darwin': MacOsMainMenu,
    'freebsd7': LinuxMainMenu
  }

  return menus.get(os_name, GenericMainMenu)
        

