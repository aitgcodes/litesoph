import tkinter as tk
from tkinter import ttk
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from  PIL import Image,ImageTk

import pathlib

from litesoph.gui.filehandler import show_message


class StartPage(tk.Frame):

    def __init__(self, parent, lsroot, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.lsroot = lsroot
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        mainframe = ttk.Frame(self,padding="12 12 24 24")
        #mainframe = ttk.Frame(self)
        mainframe.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        frame =ttk.Frame(self, relief=tk.SUNKEN, padding="6 6 0 24")
        #frame =ttk.Frame(self)
        frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        j=tk.font.Font(family ='Courier', size=20,weight='bold')
        k=tk.font.Font(family ='Courier', size=40,weight='bold')
        l=tk.font.Font(family ='Courier', size=10,weight='bold')
        myFont = tk.font.Font(family='Helvetica', size=15, weight='bold')

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 20))

        parent.configure(bg="grey60")

        # create a canvas to show project list icon
        canvas_for_project_list_icon=tk.Canvas(frame, bg='gray', height=400, width=400, borderwidth=0, highlightthickness=0)
        canvas_for_project_list_icon.grid(column=1, row=1, sticky=(tk.W, tk.E) ,columnspan=8,rowspan=8)
        #canvas_for_project_list_icon.place(x=5,y=5)

        #image_project_list = Image.open('images/project_list.png')
        #canvas_for_project_list_icon.image = ImageTk.PhotoImage(image_project_list.resize((100,100), Image.ANTIALIAS))
        #canvas_for_project_list_icon.create_image(0,0, image=canvas_for_project_list_icon.image, anchor='nw')
        
        #frame_1_label_1 = Label(frame,text="Manage Job(s)", fg="blue")
        #frame_1_label_1['font'] = myFont
        #frame_1_label_1.grid(row=10, column=2, sticky=(W, E) ,columnspan=3,rowspan=2)

        #label_1 = Label(mainframe,text="Welcome to LITESOPH", bg='#0052cc',fg='#ffffff')
        label_1 = tk.Label(mainframe,text="Welcome to LITESOPH",fg='blue')
        label_1['font'] = myFont
        #label_1.grid(row=0,column=1,sticky=(E,S))
        label_1.place(x=200,y=50)
        
        label_2 = tk.Label(mainframe,text="Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena",fg='blue')
        label_2['font'] = l
        label_2.grid(row=1,column=1)
        #label_2.place(x=200,y=100)

        # create a canvas to show image on
        canvas_for_image = tk.Canvas(mainframe, bg='gray', height=125, width=125, borderwidth=0, highlightthickness=0)
        #canvas_for_image.grid(row=30,column=0, sticky='nesw', padx=0, pady=0)
        canvas_for_image.place(x=30,y=5)

        # create image from image location resize it to 100X100 and put in on canvas
        path1 = pathlib.PurePath(self.lsroot) / "litesoph" / "gui" / "images"

        image = Image.open(str(pathlib.Path(path1) / "logo_ls.jpg"))
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((125, 125), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=tk.Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open(str(pathlib.Path(path1) / "project_create.png"))
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = tk.Button(mainframe,text="Start LITESOPH Project", activebackground="#78d6ff",command=lambda: self.event_generate('<<ShowWorkManagerPage>>'))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        #button_open_project = Button(mainframe,text="About LITESOPH",fg="white")
        button_open_project = tk.Button(mainframe,text="About LITESOPH")
        button_open_project['font'] = myFont
        button_open_project.place(x=80,y=300)
                       


class WorkManagerPage(tk.Frame):


    MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]
    Pre_task = ["Ground State","Geometry Optimisation"]
    Sim_task = ["Delta Kick","Gaussian Pulse"]
    Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]

    def __init__(self, parent, lsroot, directory, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        
        self.lsroot = lsroot
        self.directory = directory
        self.proj_path = tk.StringVar()
        self.proj_name = tk.StringVar()
        myFont = tk.font.Font(family='Helvetica', size=10, weight='bold')

        j=tk.font.Font(family ='Courier', size=20,weight='bold')
        k=tk.font.Font(family ='Courier', size=40,weight='bold')
        l=tk.font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1 = tk.Frame(self)
        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        self.Frame1_label_path = tk.Label(self.Frame1,text="Project Path",bg="gray",fg="black")
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=10,y=10)

        self.entry_path = tk.Entry(self.Frame1,textvariable=self.proj_path)
        self.entry_path['font'] = myFont
        self.entry_path.delete(0, tk.END)
        #self.proj_path.set(self.directory)
        self.entry_path.place(x=200,y=10)     

        self.label_proj = tk.Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)
        
        self.entry_proj = tk.Entry(self.Frame1,textvariable=self.proj_name)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=70)
        self.entry_proj.delete(0, tk.END)
                
        self.button_project = tk.Button(self.Frame1,text="Create New Project",activebackground="#78d6ff",command=self._create_project)
        self.button_project['font'] = myFont
        self.button_project.place(x=125,y=380)
      
        self.Frame1_Button_MainPage = tk.Button(self.Frame1, text="Start Page",activebackground="#78d6ff", command=lambda:self.event_generate('<<ShowStartPage>>'))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=10,y=380)
        
        self.button_project = tk.Button(self.Frame1,text="Open Existing Project",activebackground="#78d6ff",command=self._open_project)
        self.button_project['font'] = myFont
        self.button_project.place(x=290,y=380)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = tk.Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",activebackground="#78d6ff",command=self._get_geometry_file)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = tk.Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        
        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=350,y=10)

        self.label_proj = tk.Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

            
        self.task = ttk.Combobox(self.Frame2,width= 30, values= self.MainTask)
        self.task.set("--choose job task--")
        self.task['font'] = myFont
        self.task.place(x=200,y=70)
        self.task.bind("<<ComboboxSelected>>", self.pick_task)
        self.task['state'] = 'readonly'

        self.Frame2_label_3 = tk.Label(self.Frame2, text="Sub Task",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=130)
          
        self.sub_task = ttk.Combobox(self.Frame2, width= 30, value = [" "])
        self.sub_task['font'] = myFont
        self.sub_task.current(0)
        self.sub_task.place(x=200,y=130)
        self.sub_task['state'] = 'readonly'   
           
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",activebackground="#78d6ff",command=lambda:self.event_generate('<<SelectTask>>'))
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

    def pick_task(self, *_):
            if self.task.get() == "Preprocessing Jobs":
                self.sub_task.config(value = self.Pre_task)
                self.sub_task.current(0)
            if self.task.get() == "Simulations":
                self.sub_task.config(value = self.Sim_task)
                self.sub_task.current(0)
            if self.task.get() == "Postprocessing Jobs":
                self.sub_task.config(value = self.Post_task)
                self.sub_task.current(0)

    def update_project_entry(self, proj_path):
        proj_path = pathlib.Path(proj_path)
        self.proj_path.set(proj_path.parent)
        self.entry_path.config(textvariable=self.proj_path)
        self.proj_name.set(proj_path.name)
        self.entry_proj.config(textvariable=self.proj_name)

    def _open_project(self):
        self.event_generate('<<OpenExistingProject>>')

    def get_project_path(self):
        project_path = pathlib.Path(self.entry_path.get()) / self.entry_proj.get()
        return project_path

    def _create_project(self):
        self.event_generate('<<CreateNewProject>>')

    def _get_geometry_file(self):
        self.event_generate('<<GetMolecule>>')
        show_message(self.message_label,"Uploaded")
    
    def _geom_visual(self):
        self.event_generate('<<VisualizeMolecule>>')
    

class TextViewerPage(tk.Frame):

    def __init__(self, parent, controller, file=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        self.file = file
        self.template = template

        #self.axis = StringVar()

        myFont = tk.font.Font(family='Helvetica', size=10, weight='bold')

        j=tk.font.Font(family ='Courier', size=20,weight='bold')
        k=tk.font.Font(family ='Courier', size=40,weight='bold')
        l=tk.font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)

        self.Frame.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.98)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
  
        self.FrameTcm1_label_path = tk.Label(self, text="LITESOPH Text Viewer",fg="blue")
        self.FrameTcm1_label_path['font'] = myFont
        self.FrameTcm1_label_path.place(x=400,y=10)

        
        text_scroll =tk.Scrollbar(self)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_view = tk.Text(self, width = 130, height = 20, yscrollcommand= text_scroll.set)
        self.text_view['font'] = myFont
        self.text_view.place(x=15,y=60)

        # if self.file:
        #     self.inserttextfromfile(self.file, my_Text)
        #     self.current_file = self.file
        # if self.task:
        #     self.inserttextfromstring(self.task.template, my_Text)
        #     self.current_file = self.file

        text_scroll.config(command= self.text_view.yview)
    
         
        #view = tk.Button(self, text="View",activebackground="#78d6ff",command=lambda:[self.open_txt(my_Text)])
        #view['font'] = myFont
        #view.place(x=150,y=380)

        save = tk.Button(self, text="Save",activebackground="#78d6ff",command=lambda:[self.save_txt(my_Text)])
        save['font'] = myFont
        save.place(x=320, y=380)

        back = tk.Button(self, text="Back",activebackground="#78d6ff",command=lambda:[self.back_button()])
        back['font'] = myFont
        back.place(x=30,y=380)

    #def open_txt(self,my_Text):
        #text_file_name = filedialog.askopenfilename(initialdir= user_path, title="Select File", filetypes=(("All Files", "*"),))
        #self.current_file = text_file_name
        #self.inserttextfromfile(text_file_name, my_Text)
    
   
    def inserttext(self, text):
        self.text_view.insert(tk.END, text)
 
    def save_txt(self, my_Text):
        if self.file:
            text_file = self.current_file
            text_file = open(text_file,'w')
            text_file.write(my_Text.get(1.0, tk.END))
        else:
            self.task.write_input(template=my_Text.get(1.0, tk.END))

    def inserttextfromstring(self, string, my_Text):
        my_Text.insert(tk.END,string)
    
    def back_button(self):
        self.event_generate('<<ShowWorkManagerPage>>')