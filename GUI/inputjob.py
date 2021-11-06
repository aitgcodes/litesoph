from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from tkinter import scrolledtext
#from ttkthemes import ThemedTk
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
import os
#import esmd
from tkinter.messagebox import showinfo

import numpy as np

# LITESOPH modules

#from litesoph_modules import *
import esmd




class InputJob(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Excited state simulations")
        #self.geometry("1200x800")
        MainMenu(self)
        window = Frame(self)
        window.pack(side="top", fill = "both", expand = True)
        # window.grid_rowconfigure(700,weight=700)
        # window.grid_columnconfigure(600,weight=400)


        self.frames = {}

        for F in (Gpaw, GroundState, Choose_expert_gpaw, GroundState_gpaw, TimeDependent_gpaw):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky ="nsew")

            self.show_frame(Gpaw)

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()


    def cmd(self,drop_3):
        if drop_3  == "Sphere":
          self.show_frame(GroundState_2)
        elif drop_3 == "Parallelepiped":
          self.show_frame(GroundState_3)
        elif drop_3 == "Cylinder":
          self.show_frame(GroundState_4)

    def cmd_td(self,drop_3):
        if drop_3  == "Sphere":
          self.show_frame(TimeDependent_2)
        elif drop_3 == "Parallelepiped":
          self.show_frame(TimeDependent_3)
        elif drop_3 == "Cylinder":
          self.show_frame(TimeDependent_4)

    def open_file(self):
        text_file = filedialog.askopenfilename(initialdir="./", title="Open Text File", filetypes=((" Text Files", "*.xyz"),))
        with open(text_file,'r') as tf:
            stuff = tf.read()
        with open("coordinate.xyz",'w') as out_file:
            out_file.write(stuff)

class Gpaw(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.configure(bg="gray")

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        myFont = font.Font(family='Helvetica', size=100, weight='bold')

        groundState = Button(self, text="Ground State",bg='#0052cc',fg='#ffffff', command=lambda:controller.show_frame(GroundState_gpaw))
        groundState['font'] = myFont
        groundState.grid(row=0, column =1,columnspan=5, padx=60, pady=60)
        timeDependent = Button(self, text="Time Dependent",bg='#0052cc',fg='#ffffff', command=lambda:controller.show_frame(TimeDependent_gpaw))
        timeDependent['font'] = myFont 
        timeDependent.grid(row=0, column =10,columnspan=5, padx=60, pady=60)

        #button_1 = Button(self, text="Exit", bg='#0052cc',fg='#ffffff')
        #button_1['font'] = myFont
        #button_1.place(x=200,y=200)




class GroundState(Frame):


    def __init__(self, parent, controller):

        spacing   = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60")

                #Frame.columnconfigure(0,weight=1)
                #Frame.rowconfigure(1, weight=1)
                #F.rowconfigure(0, weight=1)
                #group1.columnconfigure(0, weight=1)

 #       label_photo = Image.open("label_size.png")
 #       label_photo = label_photo.resize((250, 250), Image.ANTIALIAS)
 #       label_image = ImageTk.PhotoImage(label_photo)

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='grey60',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='aquamarine4',background='grey60',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='grey60',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=20)

        #octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Octopus))
        #octopus.grid(row=10,column=20,padx=1500,pady=900)
#       label1 = Canvas.create_text(self,(400, 190), text="Label text")
        label1 = Label(self,text = "From Scratch", font =j,bg="grey60",fg="gainsboro")
 #       label1.image = label_image
        label1.place(x=5,y=200)
        label2 = Label(self, text= "Dimension", font =j,bg="grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "Theory Level", font =j,bg="grey60",fg="gainsboro" )
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing (in a.u)", font =j,bg="grey60",fg="gainsboro"  )
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",  font =j,bg="grey60",fg="gainsboro"  )
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=["3", "2","1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font'] = l
        entry1.insert(0," ")
        entry1.place(x= 400, y =390 )
        drop_3=ttk.Combobox(self,values=["Sphere", "Parallelepiped","Cylinder"])
        drop_3.current(0)
        drop_3['font']=l
        drop_3.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470)
   #     enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(from_scra.get(),dimension.get(),theory.get(),radius.get(),spacing.get(),\
   #             species1.get(),species2.get(),species3.get(),species4.get(),species5.get(),\
   #             coor11.get(),coor21.get(),coor31.get(),coor41.get(),coor51.get(),\
   #             coor12.get(),coor22.get(),coor33.get(),coor42.get(),coor52.get(),\
   #             coor13.get(),coor23.get(),coor33.get(),coor43.get(),coor53.get()),self.run()])

 #       enter['font'] = myFont
  #      enter.place(x=900,y=900)

class Choose_expert_gpaw(Frame):


    def __init__(self, parent, controller):

        spacing   = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=10,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')

        self.configure(bg="grey60")

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

   #     label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey16",fg="gainsboro")
   #     label_m.place(x=450,y=5)

        gpaw = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Gpaw))
        gpaw.grid(row=10,column=20,padx=1500,pady=900)
     #   button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
     #   button_3.place(x=690,y=470)

        Gpaw_page = ttk.Button(self, text="LITESOPH",style="TButton", command=lambda:controller.show_frame(Gpaw))
 #       start_page['font'] = myFont
        Gpaw_page.grid(row=0, column = 0,padx=40,pady=40)
        groundState = ttk.Button(self, text="Basic",style="TButton", command=lambda:controller.show_frame(Gpaw))
     #   groundState['font'] = myFont
        groundState.grid(row=0, column =1, padx=40, pady=40)
        timeDependent = ttk.Button(self, text="Advanced",style="TButton", command=lambda:controller.show_frame(TimeDependent_gpaw))
   #     timeDependent['font'] = myFont
        timeDependent.grid(row=0, column =2, padx=40, pady=40)


class GroundState_gpaw(Frame):


    def __init__(self, parent, controller):

        spacing   = StringVar()
        bands = StringVar()
        vacuum = StringVar()
        cores = StringVar()
        maxiter = StringVar()
        width = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=30, weight ='bold')
        #j=font.Font(family ='Courier', size=40,weight='bold')
        #k=font.Font(family ='Courier', size=40,weight='bold')
        #l=font.Font(family ='Courier', size=15,weight='bold')
        j=('Courier',20,'bold')
        k=('Courier',60,'bold')
        l=('Courier',20,'bold')
        n=font.Font(size=900)
#       label1 = Canvas.create_text(self,(400, 190), text="Label text")
        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))


        self.configure(bg="grey60")
        label_mode = Label(self,text = "Mode", font =j,bg="grey60",fg="gainsboro")
        label_mode.place(x=5,y=90)

        drop_mode =  ttk.Combobox(self, values=[ "lcao", "fd","pw","gaussian"])
        drop_mode.current(0)
        drop_mode['font'] = l
        drop_mode.place(x=400,y=90)

        label_ftype = Label(self, text= "Exchange Correlation", font =j,bg="grey60",fg="gainsboro")
        label_ftype.place(x=5,y=130)

        drop_ftype =  ttk.Combobox(self, values=["PBE", "LDA","B3LYP"])
        drop_ftype.current(0)
        drop_ftype['font'] = l
        drop_ftype.place(x=400, y=130)

        label_basis = Label(self, text= "Basis", font =j,bg="grey60",fg="gainsboro" )
        label_basis.place(x=5,y=170)

        drop_basis =  ttk.Combobox(self, values=["dzp","pvalence.dz","6-31+G*","6-31+G","6-31G*","6-31G","3-21G","cc-pvdz"])
        drop_basis.current(0)
        drop_basis['font'] = l
        drop_basis.place(x=400,y=170)

        label_spacing= Label(self, text= "Spacing (in a.u)", font =j,bg="grey60",fg="gainsboro"  )
        label_spacing.place(x=5,y=210)

        entry_spacing = ttk.Entry(self,textvariable="spacing")
        entry_spacing['font'] = l
        entry_spacing.insert(0,"0.3")
        entry_spacing.place(x= 400, y =210 )


        label_bands = Label(self, text= "Number of bands",  font =j,bg="grey60",fg="gainsboro"  )
        label_bands.place(x=5,y=250)

        entry_bands=ttk.Entry(self,textvariable="bands")
        entry_bands['font']=l
        entry_bands.place(x=400,y=250)


        label_vacuum = Label(self,text="Vacuum size (in Angstrom)", font =j,bg="grey60",fg="gainsboro")
        label_vacuum.place(x=5,y=290)

        entry_vacuum=ttk.Entry(self,textvariable="vacuum")
        entry_vacuum['font'] = l
        entry_vacuum.insert(0,"6")
        entry_vacuum.place(x=400,y=290)


        #enter = ttk.Button(self, text="Create Input", style="TButton", command=lambda:[messagebox.showinfo("Message", "Input Created")])


        #enter.place(x=900,y=900)
        enter = ttk.Button(self, text="Create Input for Ground state calculation", style="TButton", command=lambda:[messagebox.showinfo("Message", "Input for ground state calculation is Created"), esmd.dft_input_file(drop_mode.get(), drop_ftype.get(), drop_basis.get(), entry_spacing.get(), entry_bands.get(), entry_vacuum.get())])


        enter.place(x=200,y=350)
        #enter = ttk.Button(self, text="Create Input", style="TButton", command=lambda:[messagebox.showinfo("Message", "Input Created"), esmd.dft_input_file(drop_mode.get(), drop_ftype.get(), drop_basis.get())
        back_gpaw = ttk.Button(self, text="Back",style="TButton",command=lambda:controller.show_frame(Gpaw))
        back_gpaw.place(x=500,y=350)


        #enter.place(x=900,y=900)

class TimeDependent_gpaw(Frame):


    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        myFont = font.Font(family='Courier', size=30, weight ='bold')
    #    dt   = StringVar()
    #    Nt   = StringVar()
    #    cores = StringVar()
        j=('Courier',20,'bold')
        k=('Courier',60,'bold')
        l=('Courier',20,'bold')
        n=font.Font(size=900)

    #    Frame.__init__(self, parent)
    #    myFont = font.Font(family='Courier', size=20, weight ='bold')
    #    j=font.Font(family ='Courier', size=20,weight='bold')
    #    k=font.Font(family ='Courier', size=40,weight='bold')
    #    l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60")

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

    #    label_m = Label(self, text="Time Dependent - GPAW",font=k,bg= "grey60",fg="gainsboro")
    #    label_m.place(x=450,y=5)


        label_strength = Label(self, text= "Laser strength (in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_strength.place(x=5,y=90)

        label_polarization = Label(self, text= "Electric polarization:",font=j,bg= "grey60",fg="gainsboro")
        label_polarization.place(x=5,y=130)

        label_pol_x = Label(self, text="Select the value of x", font=j,bg= "grey60",fg="gainsboro")
        label_pol_x.place(x=50,y=170)

        label_pol_y = Label(self, text="Select the value of y", font=j,bg= "grey60",fg="gainsboro")
        label_pol_y.place(x=50,y=210)


        label_pol_z = Label(self, text="Select the value of z", font=j,bg= "grey60",fg="gainsboro")
        label_pol_z.place(x=50,y=250)

        label_timestep = Label(self, text= "Propagation time step (in attosecond)",font=j,bg= "grey60",fg="gainsboro")
        label_timestep.place(x=5,y=290)

        label_steps=Label(self, text= "Total time steps",font=j,bg= "grey60",fg="gainsboro")
        label_steps.place(x=5,y=330)

        drop_strength =  ttk.Combobox(self, values=[ "1e-5", "1e-3"])
        drop_strength.current(0)
        drop_strength['font'] = l
        drop_strength.place(x=600,y=90)

        drop_pol_x =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_x.current(0)
        drop_pol_x['font'] = l
        drop_pol_x.place(x=600, y=170)

        drop_pol_y =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_y.current(0)
        drop_pol_y['font'] = l
        drop_pol_y.place(x=600, y=210)

        drop_pol_z =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_z.current(0)
        drop_pol_z['font'] = l
        drop_pol_z.place(x=600, y=250)

        entry_dt = ttk.Entry(self,textvariable="dt")
        entry_dt['font']=l
        entry_dt.insert(0,"10")
        entry_dt.place(x=600, y=290 )

        entry_Nt = ttk.Entry(self,textvariable="Nt")
        entry_Nt['font']=l
        entry_Nt.insert(0,"2000")
        entry_Nt.place(x=600, y=330 )


        enter = ttk.Button(self, text="Create TD Input", style="TButton", command=lambda:[messagebox.showinfo("Message", "Input for Time dependent calculation is Created"), esmd.tddft_input_file(drop_strength.get(), drop_pol_x.get(), drop_pol_y.get(), drop_pol_z.get(), entry_dt.get(), entry_Nt.get())])
        enter.place(x=200,y=400)

        gpaw = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Gpaw))
        gpaw.grid(row=10,column=20,padx=350,pady=400)


class MainMenu():
    def __init__(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Help", menu=filemenu)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        menubar['font'] = myFont

        master.config(menu=menubar)
        menubar.configure(bg="gainsboro")



#app = InputJob()
#app.title("AITG -LITESOPH")
#app.mainloop
