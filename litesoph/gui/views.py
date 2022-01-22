import tkinter as tk
from tkinter import ttk
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox

import pathlib

from litesoph.gui.filehandler import show_message

class WorkManagerPage(tk.Frame):

    def __init__(self, parent, controller, *_):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        

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
        self.proj_path.set(self.controller.directory)
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
      
        self.Frame1_Button_MainPage = tk.Button(self.Frame1, text="Start Page",activebackground="#78d6ff", command=lambda:self.event_generate('<<StartPage'))
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

        MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]

        # Create a list of sub_task
       
        Pre_task = ["Ground State","Geometry Optimisation"]
        Sim_task = ["Delta Kick","Gaussian Pulse"]
        Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]
        
        
        def pick_task(e):
            if task.get() == "Preprocessing Jobs":
                sub_task.config(value = Pre_task)
                sub_task.current(0)
            if task.get() == "Simulations":
                sub_task.config(value = Sim_task)
                sub_task.current(0)
            if task.get() == "Postprocessing Jobs":
                sub_task.config(value = Post_task)
                sub_task.current(0)
            
        task = ttk.Combobox(self.Frame2,width= 30, values= MainTask)
        task.set("--choose job task--")
        task['font'] = myFont
        task.place(x=200,y=70)
        task.bind("<<ComboboxSelected>>", pick_task)
        task['state'] = 'readonly'

        self.Frame2_label_3 = tk.Label(self.Frame2, text="Sub Task",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=130)
          
        sub_task = ttk.Combobox(self.Frame2, width= 30, value = [" "])
        sub_task['font'] = myFont
        sub_task.current(0)
        sub_task.place(x=200,y=130)
        sub_task['state'] = 'readonly'   
           
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",activebackground="#78d6ff",command=lambda:[controller.task_input(sub_task,self.task_check(sub_task))])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)


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
    
    
    def task_check(self,sub_task):
        self.st_var = self.controller.status
        
        if sub_task.get()  == "Ground State":
            path = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            if path.exists() is True:
                return True
            else:
                messagebox.showerror(message= "Upload geometry file")
        elif sub_task.get() == "Delta Kick":
            if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
                return True
            else:
                messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")       
        elif sub_task.get() == "Gaussian Pulse":
            if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
                return True
            else:
                messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")
        elif sub_task.get() == "Spectrum":
            if self.st_var.check_status('gs_cal', 1) is True:
                if self.st_var.check_status('td_cal',1) is True or self.st_var.check_status('td_cal',2) is True:
                    return True
            else:
                messagebox.showerror(message=" Please complete Ground State and Delta kick calculation.")
        elif sub_task.get() == "Dipole Moment and Laser Pulse":
            if self.st_var.check_status('gs_cal', 1) is True and self.st_var.check_status('td_cal',2) is True:
                return True
            else:
                messagebox.showerror(message=" Please complete Ground State and Gaussian Pulse calculation.")
        else:
            return True