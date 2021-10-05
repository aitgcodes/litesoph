from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
#from ttkthemes import ThemedTk
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk


class Aitg(Tk):
 
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        MainMenu(self)
        window = Frame(self)
        window.pack(side="top", fill = "both", expand = True)
        window.grid_rowconfigure(700,weight=700)
        window.grid_columnconfigure(600,weight=400)

  

        self.frames = {}

        for F in (StartPage, Octopus, Gpaw, GroundState, GroundState_2, GroundState_3, GroundState_4 ,GroundState_gpaw,TimeDependent,\
                TimeDependent_2,TimeDependent_3,TimeDependent_4,TimeDependent_gpaw,Choose_expert_octopus,Choose_expert_gpaw):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky ="nsew")

        self.show_frame(StartPage)

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
        text_file = open(text_file,'r')
        stuff = text_file.read()
        out_file = open("coordinate.xyz",'w')
        out_file.write(stuff)
        text_file.close()
        out_file.close()

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        myFont = font.Font(family='Courier', size=30, weight ='bold')
   #     tyle = ttk.Style()
   #     gui_style.configure('My.TButton', foreground='#334353')=font.Font(family ='Courier', size=60,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=60,weight='bold')
        m=font.Font(family ='Courier', size=20,weight='bold')
#

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 40))

        self.configure(bg="grey60")
        
        # Setting Theme
    #    s = ThemedStyle(theme="scidgrey")
   


        label1 = Label(self, text="WELCOME!!!",font=l,bg="grey60",fg="gainsboro")
        label1.place(x=650,y=20)
   #     label2 = Label(self, text="AITG",font=myFont,bg= "turquoise1",fg="aquamarine4")
   #     label2.place(x=775,y=130)
        label3 = Label(self, text="Graphical User Interface for Laser Simulations",font=k,bg= "grey60",fg="gainsboro")
        label3.place(x=65,y=200)
        label4 = Label(self, text="Select your engine",font=m,bg= "grey60",fg="gainsboro")
        label4.place(x=1200,y=500)
#        label5 = Label(self, text="Graphic User Interface for Laser Simulations",font=k,bg= "grey16",fg="gainsboro")
#        label5.place(x=65,y=180)
#        label6 = Label(self, text="Graphic User Interface for Laser Simulations",font=k,bg= "grey16",fg="gainsboro")
#        label6.place(x=65,y=180)
 
        octopus =ttk.Button(self, text="OCTOPUS",style="TButton",command=lambda:controller.show_frame(Choose_expert_octopus))
    #    octopus['font'] = myFont
        octopus.place(x=100,y=500)
        gpaw = ttk.Button(self, text="GPAW",style="TButton",command=lambda:controller.show_frame(Choose_expert_gpaw))
    #    gpaw['font']= myFont
        gpaw.place(x=500, y=500)
        NWchem = ttk.Button(self, text="NWCHEM",style="TButton",command=lambda:controller.show_frame(Choose_expert_GS))
    #    gpaw['font']= myFont
        NWchem.place(x=900, y=500)


class Octopus(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        self.configure(bg="grey64")

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 20))




        label = Label(self, text="Octopus")
        start_page = ttk.Button(self, text="Start Page",style="TButton", command=lambda:controller.show_frame(StartPage))
 #       start_page['font'] = myFont
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        groundState = ttk.Button(self, text="Ground State",style="TButton", command=lambda:controller.show_frame(GroundState))
     #   groundState['font'] = myFont
        groundState.grid(row=0, column =1, padx=40, pady=40)
        timeDependent = ttk.Button(self, text="Time Dependent",style="TButton", command=lambda:controller.show_frame(TimeDependent))
   #     timeDependent['font'] = myFont
        timeDependent.grid(row=0, column =2, padx=40, pady=40)
       
           
class Gpaw(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        self.configure(bg="grey16")
        label = Label(self, text="Gpaw")
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage),bg="aquamarine4",fg="black")
        start_page.grid(row=0,column=0,padx=40,pady=40)
        groundState = ttk.Button(self, text="Ground State",style="TButton", command=lambda:controller.show_frame(GroundState_gpaw))
        groundState.grid(row=0, column =1, padx=40, pady=40)
        timeDependent = ttk.Button(self, text="Time Dependent",style="TButton", command=lambda:controller.show_frame(TimeDependent_gpaw))
        timeDependent.grid(row=0, column =2, padx=40, pady=40)
  
class GroundState(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 
         
 #       label_photo = Image.open("label_size.png")
 #       label_photo = label_photo.resize((250, 250), Image.ANTIALIAS)
 #       label_image = ImageTk.PhotoImage(label_photo)

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='grey60',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='aquamarine4',background='grey60',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='grey60',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Octopus))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
#       label1 = Canvas.create_text(self,(400, 190), text="Label text")
        label1 = Label(self,text = "From Scratch", font =j,bg="grey60",fg="gainsboro")
 #       label1.image = label_image
        label1.place(x=5,y=140)
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
        entry1.insert(0,"0.16")
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

class Choose_expert_octopus(Frame):

     
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

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Octopus))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
     #   button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
     #   button_3.place(x=690,y=470) 
  
        start_page = ttk.Button(self, text="Start Page",style="TButton", command=lambda:controller.show_frame(StartPage))
 #       start_page['font'] = myFont
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        groundState = ttk.Button(self, text="Basic",style="TButton", command=lambda:[messagebox.showinfo("Basics","You have chosen Basics. It takes minimum instruction from the user and uses default for\
                                   rest of the inputs. If you want to fine tune the parameters choose advanced"),controller.show_frame(Octopus)])
     #   groundState['font'] = myFont
        groundState.grid(row=0, column =1, padx=40, pady=40)
        timeDependent = ttk.Button(self, text="Advanced",style="TButton", command=lambda:controller.show_frame(TimeDependent))
   #     timeDependent['font'] = myFont
        timeDependent.grid(row=0, column =2, padx=40, pady=40)
 
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
  
        start_page = ttk.Button(self, text="Start Page",style="TButton", command=lambda:controller.show_frame(StartPage))
 #       start_page['font'] = myFont
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        groundState = ttk.Button(self, text="Basic",style="TButton", command=lambda:[messagebox.showinfo("Basics","You have chosen Basics. It takes minimum instruction from the user and uses default for\
                                   rest of the inputs. If you want to fine tune the parameters choose advanced"),controller.show_frame(Gpaw)])
     #   groundState['font'] = myFont
        groundState.grid(row=0, column =1, padx=40, pady=40)
        timeDependent = ttk.Button(self, text="Advanced",style="TButton", command=lambda:controller.show_frame(TimeDependent_gpaw))
   #     timeDependent['font'] = myFont
        timeDependent.grid(row=0, column =2, padx=40, pady=40)
 



class GroundState_2(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Radius    = StringVar()
        mixing    = StringVar()
        ConRelDens = StringVar()
        ConRelEner = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(GroundState))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "Theory Level",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font'] = l
        entry1.delete(0,END)
        entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Sphere")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="Select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470) 
        label5 = Label(self, text= "Radius",font=j,bg= "grey60",fg="gainsboro")
        label5.place(x=5,y=550)
        entry2 = ttk.Entry(self,textvariable="radius")
        entry2['font'] = l
        entry2.delete(0,END)
        entry2.insert(0,"6.0")
        entry2.place(x= 400, y =550)
        label6 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label6.place(x=5,y=630)
        button5 = ttk.Button(self, text="Select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=630)
        label7 = Label(self, text= "EigenSolver",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=710)
        drop5=ttk.Combobox(self,values=["rmmdiis","plan","arpack","feast","psd","cg","cg_new","lobpcg","evolution"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=710)
        label7 = Label(self, text= "Mixing",font=j,bg= "grey60",fg="gainsboro" )
        label7.place(x=5,y=790)
        entry3 = ttk.Entry(self,textvariable="mixing")
        entry3['font'] = l
        entry3.delete(0,"end")
        entry3.insert(0,"0.02")
        entry3.place(x= 400, y =790)
        label8 = Label(self, text= "Convergence(Rel Density)",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=900,y=140)
        entry4 = ttk.Entry(self,textvariable="ConRelDens")
        entry4['font'] = l
        entry4.insert(0,"1e-5")
        entry4.place(x= 1400, y =140)
        label9 = Label(self, text= "Convergence(Rel Energy)",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=900,y=230)
        entry5 = ttk.Entry(self,textvariable="ConRelEner")
        entry5.delete(0,"end")
        entry5.insert(0,"0.00")
        entry5['font']=l
        entry5.place(x= 1400, y =230)
        label10 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=310)
        drop6 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop6['font']= l
        drop6.current(0)
        drop6.place(x=1400,y=310)
        label11 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=390)
        entry6 = ttk.Entry(self,textvariable="Smearing")
        entry6.delete(0,END)
        entry6.insert(0,"0.01")
        entry6['font']=l
        entry6.place(x= 1400, y =390)

        label12 = Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=470)
        entry7 = ttk.Entry(self,textvariable="Cores")
        entry7.delete(0,END)
        entry7.insert(0,"2")
        entry7['font'] = l
        entry7.place(x= 1400, y =470)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),drop5.get(),entry3.get(),entry4.get(),entry5.get(),drop6.get(),entry6.get(),entry7.get()),self.run(),messagebox.showinfo("Job Submitted","Your Job to compute the ground state is submitted to the cluster")])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,Radius,drop5,mixing,ConRelDens,ConRelEner,drop6,smearing,cores):
        first_line = " CalculationMode  =  gs "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]

        rad = str(Radius)
        fourth_line = [" Dimensions   =   ", drop2]
        spa = str(spacing)
        fifth_line = [" TheoryLevel  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" Radius = ", rad,"*angstrom"]
        ninth_line = [' XYZCoordinates   = "coordinate.xyz" ']
        tenth_line = [" EigenSolver   =  ", drop5 ]
        eleventh_line = [" Mixing = ", mixing ]
        twelth_line = [" ConvRelDens = ", ConRelDens]
        thirteenth_line = [" ConvRelEv = ", ConRelEner]
        fourteenth_line = [" SmearingFunction = ", drop6]
        fifteenth_line = [" Smearing = ", smearing]






        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()
       
        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_ru "
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
      

    def run(self):
           subprocess.run(["qsub","run.sh"])





   
class GroundState_3(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Radius    = StringVar()
        mixing    = StringVar()
        ConRelDens = StringVar()
        ConRelEner = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(GroundState))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
     #   entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Parallelepiped")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470) 
   #     label5 = ttk.Label(self, text= "Radius",style="BW.TLabel")
   #     label5.place(x=5,y=550)
   #     entry2 = ttk.Entry(self,textvariable="Radius")
   #     entry2.place(x= 400, y =550)
        label5 = Label(self, text= "Box sides[ Ang Units]",font=j,bg= "grey60",fg="gainsboro")
        label5.place(x=5,y=550)
        entry2 = ttk.Entry(self,textvariable="X",width=7)
        entry2['font']=l
    #    entry2.insert(0,"0.00")
        entry2.place(x= 400, y =550)
        entry3 = ttk.Entry(self,textvariable="Y",width=7)
        entry3['font']=l
   #     entry3.insert(0,"0.00")
        entry3.place(x= 500, y =550)
        entry4 = ttk.Entry(self,textvariable="Z",width=7)
        entry4['font']=l
    #    entry4.insert(0,"0.00")
        entry4.place(x= 600, y =550)


        label6 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label6.place(x=5,y=630)
        button5 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=630)
        label7 = Label(self, text= "EigenSolver",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=710)
        drop5=ttk.Combobox(self,values=["rmmdiis","plan","arpack","feast","psd","cg","cg_new","lobpcg","evolution"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=710)
        label7 = Label(self, text= "Mixing",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=790)
        entry5 = ttk.Entry(self,textvariable="mixing")
        entry5['font']=l
 #       entry5.insert(0,"0.00")
        entry5.place(x= 400, y =790)
        label8 = Label(self, text= "Convergence(Rel Density)",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=900,y=140)
        entry6 = ttk.Entry(self,textvariable="ConRelDens")
        entry6['font']=l
 #       entry6.insert(0,"1e-5")
        entry6.place(x= 1400, y =140)
        label9 = Label(self, text= "Convergence(Rel Energy)",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=900,y=230)
        entry7 = ttk.Entry(self,textvariable="ConRelEner")
        entry7['font']=l
  #      entry7.insert(0,"0.00")
        entry7.place(x= 1400, y =230)
        label10 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=310)
        drop6 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop6['font']=l
        drop6.current(0)
        drop6.place(x=1400,y=310)
        label11 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=390)
        entry8 = ttk.Entry(self,textvariable="smearing")
        entry8['font']=l
 #       entry8.insert(0,"0.1")
        entry8.place(x= 1400, y =390)

        label12 = Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=470)
        entry9 = ttk.Entry(self,textvariable="cores")
        entry9['font'] = l
    #    entry9.insert(0,"2")
        entry9.place(x= 1400, y =470)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),entry3.get(),entry4.get(),drop5.get(),entry5.get(),entry6.get(),entry7.get(),drop6.get(),entry8.get(),entry9.get()),self.run(),messagebox.showinfo("Job Submitted","Your Job to compute\
                    the ground state is submitted to the cluster")])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,x,y,z,drop5,mixing,ConRelDens,ConRelEner,drop6,smearing,cores):
        first_line = " CalculationMode  =  gs "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]
        line = " | "
   #     rad = str(Radius)
        fourth_line = [" Dimensions  =   ", drop2]
        spa = str(spacing)
        fifth_line = [" TheoryLevel  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" %Lsize  ","\n"," ",x,"*angstrom",line, y,"*angstrom",line,z,"*angstrom","\n"," %"]
        ninth_line = [' XYZCoordinates   = "coordinate.xyz"  ']
        tenth_line = [" EigenSolver   =  ", drop5 ]
        eleventh_line = [" Mixing = ", mixing ]
        twelth_line = [" ConvRelDens = ", ConRelDens]
        thirteenth_line = [" ConvRelEv = ", ConRelEner]
        fourteenth_line = [" SmearingFunction = ", drop6]
        fifteenth_line = [" Smearing = ", smearing]






        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

  #      line = "  |  "
  #      fifth_line="%Coordinates"
  #      self.inp_file.write("\n")
  #      sixth_line=["\"",species1,"\"",line,coor11,line,coor12,line,coor13]
  #      seventh_line=["\"",species2,"\"",line,coor21,line,coor22,line,coor23]
  #      eigth_line=["\"",species3,"\"",line,coor31,line,coor32,line,coor33]
  #      ninth_line=["\"",species4,"\"",line,coor41,line,coor42,line,coor43]
  #      tenth_line=["\"",species5,"\"",line,coor51,line,coor52,line,coor53]
  #      eleventh_line="%"


        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()
        
        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_run"
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
        
    def run(self):
           subprocess.run(["qsub", "run.sh"])


   
class GroundState_4(Frame):

     
    def __init__(self, parent, controller):
        
        spacing    = StringVar()
        Radius     = StringVar()
        mixing     = StringVar()
        ConRelDens = StringVar()
        ConRelEner = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()
        Xlength    = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(GroundState))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3" ,"2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
     #   entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Cylinder")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470) 
        label5 = Label(self, text= "Radius",font=j,bg= "grey60",fg="gainsboro")
        label5.place(x=5,y=550)
        label6 = Label(self, text= "Xlength",font=j,bg= "grey60",fg="gainsboro")
        label6.place(x=5,y=630) 
        entry2 = ttk.Entry(self,textvariable="Radius")
        entry2.delete(0,END)
    #    entry2.insert(0,"0.00")
        entry2['font']=l
        entry2.place(x= 400, y =550)
        entry3 = ttk.Entry(self,textvariable="Xlength")
        entry3.delete(0,END)
    #    entry3.insert(0,"0.00")
        entry3['font']=l
        entry3.place(x= 400, y =630)

        label7 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label7.place(x=5,y=710)
        button5 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=710)
        label8 = Label(self, text= "EigenSolver",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=5,y=790)
        drop5=ttk.Combobox(self,values=["rmmdiis","plan","arpack","feast","psd","cg","cg_new","lobpcg","evolution"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=790)
        label9 = Label(self, text= "Mixing",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=5,y=870)
        entry4 = ttk.Entry(self,textvariable="mixing")
  #      entry4.insert(0,"0.00")
        entry4.place(x= 400, y =870)
        entry4['font']=l
        label10 = Label(self, text= "Convergence(Rel Density)",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=140)
        entry5 = ttk.Entry(self,textvariable="ConRelDens")
 #       entry5.insert(0,"1e-5")
        entry5.place(x= 1400, y =140)
        entry5['font']=l
        label9 = Label(self, text= "Convergence(Rel Energy)",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=900,y=230)
        entry6 = ttk.Entry(self,textvariable="ConRelEner")
        entry6['font']=l
 #       entry6.insert(0,"0.00")
        entry6.place(x= 1400, y =230)
        label11 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=310)
        drop6 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop6['font']=l
        drop6.current(0)
        drop6.place(x=1400,y=310)
        label12 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=390)
        entry7 = ttk.Entry(self,textvariable="smearing")
   #     entry7.insert(0,"0.1")
        entry7.place(x= 1400, y =390)
        entry7['font']=l

        label13 =Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro")
        label13.place(x=900,y=470)
        entry8 = ttk.Entry(self,textvariable="cores")
        entry8['font']=l
   #     entry8.insert(0,"2")
        entry8.place(x= 1400, y =470)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),entry3.get(),drop5.get(),entry4.get(),entry5.get(),entry6.get(),drop6.get(),entry7.get(),entry8.get()),self.run(),messagebox.showinfo("Job Submitted","Your Job to compute the ground state is submitted to the cluster")])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,Radius,Xlength,drop5,mixing,ConRelDens,ConRelEner,drop6,smearing,cores):
        first_line = " CalculationMode  =  gs "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]

        rad = str(Radius)
        fourth_line = [" Dimensions   =   ", drop2]
        spa = str(spacing)
        fifth_line = [" TheoryLevel  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" Radius = ", rad,"*angstrom"]
        after_eight_line = [" Xlength = ", Xlength,"*angstrom"]
        ninth_line = ['XYZCoordinates   =  "coordinate.xyz"  ']
        tenth_line = [" EigenSolver   =  ", drop5 ]
        eleventh_line = [" Mixing = ", mixing ]
        twelth_line = [" ConvRelDens = ", ConRelDens]
        thirteenth_line = [" ConvRelEv = ", ConRelEner]
        fourteenth_line = [" SmearingFunction = ", drop6]
        fifteenth_line = [" Smearing = ", smearing]


            



        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")
 
        self.inp_file.writelines(after_eight_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")



        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()

        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_ru "
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
      
    def run(self):
           subprocess.run(["qsub", "run.sh"])

class TimeDependent(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="TimeDependent - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Octopus))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3=Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 =  Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2","1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
  #      entry1.insert(0,"0.16")
        entry1.place(x= 400, y =390 )
        drop_3=ttk.Combobox(self,values=["Sphere", "Parallelepiped","Cylinder"])
        drop_3.current(0)
        drop_3['font']=l
        drop_3.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd_td(drop_3.get()))
        button_3.place(x=690,y=470) 
 


class TimeDependent_2(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Radius    = StringVar()
        TDTimeStep    = StringVar()
        TDMaxSteps = StringVar()
        TDDeltaStrength = StringVar()
        TDPolarizationDirection = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="TimeDependent - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(TimeDependent))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 =  Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
     #   entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Sphere")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470) 
        label5 = Label(self, text= "Radius",font=j,bg= "grey60",fg="gainsboro")
        label5.place(x=5,y=550)
        entry2 = ttk.Entry(self,textvariable="radiuS")
        entry2['font']=l

        entry2.insert(0,"6.00")
        entry2.place(x= 400, y =550)
        label6 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label6.place(x=5,y=630)
        button5 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=630)
        label7 = Label(self, text= "TDPropagator",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=710)
        drop5=ttk.Combobox(self,values=["crank_nicolsan","magnus","aetrs","etrs","runge_kutta4","runge_kutta2","caetrs","exp_mid","cfmagnus4"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=710)
        label7 = Label(self, text= "TDTimeStep",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=790)
        entry3 = ttk.Entry(self,textvariable="TDTimeStep")
        entry3['font']=l
        entry3.insert(0,"0.00")
        entry3.place(x= 400, y =790)
        label_7 = Label(self, text= "TDMaxSteps",font=j,bg= "grey60",fg="gainsboro")
        label_7.place(x=900,y=140)
        entry_3 = ttk.Entry(self,textvariable="TDMaxSteps")
        entry_3['font']=l
        entry_3.insert(0,"0.00")
        entry_3.place(x= 1400, y =140)

        label8 = Label(self, text= "TDDeltaStrength",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=900,y=230)
        entry4 = ttk.Entry(self,textvariable="TDDeltastrength")
        entry4['font']=l
        entry4.insert(0,"0.001")
        entry4.place(x= 1400, y =230)
        label9 = Label(self, text= "TDPolarizationDirection",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=900,y=310)
        drop6 = ttk.Combobox(self,values=["1","2","3"])
        drop6.current(0)
        drop6['font']=l
 #       entry5.insert(0,"0.00")
        drop6.place(x= 1400, y =310)
        label10 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=390)
        drop7 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop7['font']=l
        drop7.current(0)
        drop7.place(x=1400,y=390)
        label11 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=470)
        entry5 = ttk.Entry(self,textvariable="SmearinG")
        entry5['font']=l
        entry5.insert(0,"0.1")
        entry5.place(x= 1400, y =470)

        label12 = Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=550)
        entry6 = ttk.Entry(self,textvariable="cores")
        entry6.insert(0,"2")
        entry6['font']=l
        entry6.place(x= 1400, y =550)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),drop5.get(),entry3.get(),entry_3.get(),entry4.get(),drop6.get(),drop7.get(),entry5.get(),entry6.get()),self.run(),messagebox.showinfo("Job Submitted","Your Job to compute the TimeDependent propagation is submitted to the cluster")])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,Radius,drop5,TDTimeStep,TDMaxSteps,TDDeltaStrength,drop6,drop7,smearing,cores):
        first_line = " CalculationMode  =  td "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]

        rad = str(Radius)
        fourth_line = [" Dimensions  =   ", drop2]
        spa = str(spacing)
        fifth_line = [" TheoryLevel  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" Radius = ", rad,"*angstrom"]
        ninth_line = [' XYZCoordinates   = "coordinate.xyz" ']
        tenth_line = [" TDPropagator   =  ", drop5 ]
        eleventh_line = [" TDTimeStep = ", TDTimeStep ]
        eleventh_post_line =[" TDMaxSteps = ", TDMaxSteps ]
        twelth_line = [" TDDeltaStrength = ", TDDeltaStrength]
        thirteenth_line = [" TDPolarizationDirection = ", drop6]
        fourteenth_line = [" SmearingFunction = ", drop7]
        fifteenth_line = [" Smearing = ", smearing]






        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_post_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")


        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()
       
        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_ru "
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
      

    def run(self):
           subprocess.run(["qsub","run.sh"])

class TimeDependent_3(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Radius    = StringVar()
        TDTimeStep    = StringVar()
        TDMaxSteps = StringVar()
        TDDeltaStrength = StringVar()
        TDPolarizationDirection = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="TimeDependent - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(TimeDependent))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro")
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3= Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
     #   entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Parallelepiped")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd_td(drop_3.get()))
        button_3.place(x=690,y=470) 
   #     label5 = ttk.Label(self, text= "Radius",style="BW.TLabel")
   #     label5.place(x=5,y=550)
   #     entry2 = ttk.Entry(self,textvariable="Radius")
   #     entry2.insert(0,"0.00")
   #     entry2.place(x= 400, y =550)
        label5 = Label(self, text= "Box Sides[ Ang Units]",font=j,bg= "grey60",fg="gainsboro" )
        label5.place(x=5,y=550)
        entry2 = ttk.Entry(self,textvariable="X",width=7)
        entry2['font']=l
        entry2.insert(0,"0.00")
        entry2.place(x= 400, y =550)
        entry3 = ttk.Entry(self,textvariable="Y",width=7)
        entry3['font']=l
        entry3.insert(0,"0.00")
        entry3.place(x= 500, y =550)
        entry4 = ttk.Entry(self,textvariable="Z",width=7)
        entry4['font']=l
        entry4.insert(0,"0.00")
        entry4.place(x= 600, y =550)


        label6 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label6.place(x=5,y=630)
        button5 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=630)
        label7 = Label(self, text= "TDPropagator",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=710)
        drop5=ttk.Combobox(self,values=["crank_nicolsan","magnus","aetrs","etrs","runge_kutta4","runge_kutta2","caetrs","exp_mid","cfmagnus4"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=710)
        label7 = Label(self, text= "TDTimeStep",font=j,bg= "grey60",fg="gainsboro")
        label7.place(x=5,y=790)
        entry5 = ttk.Entry(self,textvariable="TDTimeStep")
        entry5['font']=l
#       entry5.insert(0,"0.00")
        entry5.place(x= 400, y =790)
        label_7 = Label(self, text= "TDMaxSteps",font=j,bg= "grey60",fg="gainsboro")
        label_7.place(x=900,y=140)
        entry_5 = ttk.Entry(self,textvariable="TDMaxSteps")
        entry_5['font']=l
#       entry5.insert(0,"0.00")
        entry_5.place(x= 1400, y =140)

        label8 = Label(self, text= "TDDeltaStrength",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=900,y=230)
        entry6 = ttk.Entry(self,textvariable="TDDeltaStrength")
        entry6['font']=l
#       entry6.insert(0,"1e-5")
        entry6.place(x= 1400, y =230)
        label9 = Label(self, text= "TDPolarizationDirection",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=900,y=310)
        drop6 = ttk.Combobox(self,values=["1","2","3"])
        drop6['font']=l
  #      entry7.insert(0,"0.00")
        drop6.place(x= 1400, y =310)
        label10 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=390)
        drop7 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop7['font']=l
        drop7.current(0)
        drop7.place(x=1400,y=390)
        label11 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=470)
        entry7 = ttk.Entry(self,textvariable="smearing")
 #       entry8.insert(0,"0.1")
        entry7['font']=l
        entry7.place(x= 1400, y =470)

        label12 = Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=550)
        entry8 = ttk.Entry(self,textvariable="cores")
    #    entry9.insert(0,"2")
        entry8['font']=l
        entry8.place(x= 1400, y =550)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),entry3.get(),entry4.get(),drop5.get(),entry5.get(),entry_5.get(),entry6.get(),drop6.get(),drop7,entry7.get(),entry8.get()),self.run()])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,x,y,z,drop5,TDTimeStep,TDMaxSteps,TDDeltaStrength,drop7,smearing,cores):
        first_line = " CalculationMode  =  td "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]
        line = " | "
   #     rad = str(Radius)
        fourth_line = [" Dimension   =   ", drop2]
        spa = str(spacing)
        fifth_line = [" Theory  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" %Lsize = ","\n"," ",x,"*angstrom",line, y,"*angstrom",line,z,"*angstrom","\n"," %"]
        ninth_line = [" XYZCoordinates   =  coordinate.xyz  "]
        tenth_line = [" TDPropagator   =  ", drop5 ]
        eleventh_line = [" TDTimeStep = ", TDTimeStep ]
        eleventh_post_line = [" TDMaxSteps = ", TDMaxSteps ]
        twelth_line = [" TDDeltaStrength = ", TDDeltaStrength]
        thirteenth_line = [" TDPolarizationDirection = ", drop6]
        fourteenth_line = [" SmearingFunstion = ", drop7]
        fifteenth_line = [" Smearing = ", smearing]






        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

  #      line = "  |  "
  #      fifth_line="%Coordinates"
  #      self.inp_file.write("\n")
  #      sixth_line=["\"",species1,"\"",line,coor11,line,coor12,line,coor13]
  #      seventh_line=["\"",species2,"\"",line,coor21,line,coor22,line,coor23]
  #      eigth_line=["\"",species3,"\"",line,coor31,line,coor32,line,coor33]
  #      ninth_line=["\"",species4,"\"",line,coor41,line,coor42,line,coor43]
  #      tenth_line=["\"",species5,"\"",line,coor51,line,coor52,line,coor53]
  #      eleventh_line="%"


        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")
        
        self.inp_file.writelines(eleventh_post_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

   

        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()
        
        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_run"
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
        
    def run(self):
           subprocess.run(["qsub", "run.sh"])

   
class TimeDependent_4(Frame):

     
    def __init__(self, parent, controller):
        
        spacing    = StringVar()
        Radius     = StringVar()
        TDTimeStep     = StringVar()
        TDMaxSteps = StringVar()
        TDDeltaStrength = StringVar()
        TDPolarizationDirection = StringVar()
        cores      = StringVar() 
        smearing   = StringVar()
        Xlength    = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="TimeDependent - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(GroundState))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = Label(self, text= "From Scratch",font=j,bg= "grey60",fg="gainsboro"  )
        label1.place(x=5,y=140)
        label2 = Label(self, text= "Dimension",font=j,bg= "grey60",fg="gainsboro")
        label2.place(x=5,y=230)
        label3 = Label(self, text= "TheoryLevel",font=j,bg= "grey60",fg="gainsboro")
        label3.place(x=5,y=310)

        label_3=Label(self, text= "Spacing(in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_3.place(x=5,y=390)

        label4 = Label(self, text= "Box Shape",font=j,bg= "grey60",fg="gainsboro")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = l
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "3", "2", "1"])
        drop2.current(0)
        drop2['font'] = l
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"])
        drop3.current(0)
        drop3['font'] = l
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
        entry1['font']=l
     #   entry1.insert(0,"0.160")
        entry1.place(x= 400, y =390 )
        drop4=ttk.Combobox(self,values="Cylinder")
        drop4.current(0)
        drop4['font']=l
        drop4.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd_td(drop_3.get()))
        button_3.place(x=690,y=470) 
        label5 = Label(self, text= "Radius",font=j,bg= "grey60",fg="gainsboro")
        label5.place(x=5,y=550)
        label6 = Label(self, text= "Xlength",font=j,bg= "grey60",fg="gainsboro")
        label6.place(x=5,y=630) 
        entry2 = ttk.Entry(self,textvariable="Radius")
        entry2['font']=l
        entry2.insert(0,"0.00")
        entry2.place(x= 400, y =550)
        entry3 = ttk.Entry(self,textvariable="Xlength")
        entry3['font']=l
        entry3.insert(0,"0.00")
        entry3.place(x= 400, y =630)

        label7 = Label(self,text="XYZCoordinates",font=j,bg= "grey60",fg="gainsboro") 
        label7.place(x=5,y=710)
        button5 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.open_file())
        button5.place(x=400,y=710)
        label8 = Label(self, text= "TDPropagator",font=j,bg= "grey60",fg="gainsboro")
        label8.place(x=5,y=790)
        drop5=ttk.Combobox(self,values=["crank_nicolsan","magnus","aetrs","etrs","runge_kutta4","runge_kutta2","caetrs","exp_mid","cfmagnus4"])
        drop5.current(0)
        drop5['font']=l
        drop5.place(x=400,y=790)
        label9 = Label(self, text= "TDTimeStep",font=j,bg= "grey60",fg="gainsboro")
        label9.place(x=5,y=870)
        entry4 = ttk.Entry(self,textvariable="TDTimeStep")
        entry4['font']=l
  #      entry4.insert(0,"0.00")
        entry4.place(x= 400, y =870)
        label_9 = Label(self, text= "TDMaxSteps",font=j,bg= "grey60",fg="gainsboro")
        label_9.place(x=900,y=140)
        entry_4 = ttk.Entry(self,textvariable="TDMaxSteps")
        entry_4['font']=l
  #      entry4.insert(0,"0.00")
        entry_4.place(x= 1400, y =140)
    
        label10 = Label(self, text= "TDDeltaStrength",font=j,bg= "grey60",fg="gainsboro")
        label10.place(x=900,y=230)
        entry5 = ttk.Entry(self,textvariable="TDDeltaStrength")
        entry5['font']=l
 #       entry5.insert(0,"1e-5")
        entry5.place(x= 1400, y =230)
        label11 = Label(self, text= "TDPolarizationDirection",font=j,bg= "grey60",fg="gainsboro")
        label11.place(x=900,y=310)
        drop6 = ttk.Combobox(self,value=["1","2","3"])
        drop6['font']=l
 #       entry6.insert(0,"0.00")
        drop6.place(x= 1400, y =310)
        label12 = Label(self, text= "SmearingFunction",font=j,bg= "grey60",fg="gainsboro")
        label12.place(x=900,y=390)
        drop7 =  ttk.Combobox(self, values=["Semiconducting", "fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"])
        drop7['font']=l
        drop7.current(0)
        drop7.place(x=1400,y=390)
        label13 = Label(self, text= "Smearing",font=j,bg= "grey60",fg="gainsboro")
        label13.place(x=900,y=470)
        entry6 = ttk.Entry(self,textvariable="smearing")
        entry6['font']=l
   #     entry7.insert(0,"0.1")
        entry6.place(x= 1400, y =470)
        entry6['font']=l
        label14 = Label(self, text= "No of Processors",font=j,bg= "grey60",fg="gainsboro" )
        label14.place(x=900,y=550)
        entry7 = ttk.Entry(self,textvariable="cores")
        entry7['font']=l
   #     entry8.insert(0,"2")
        entry7.place(x= 1400, y =550)
      
        
        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(drop1.get(),drop2.get(),drop3.get(),entry1.get(),drop4.get(),\
                entry2.get(),entry3.get(),drop5.get(),entry4.get(),entry_4.get(),entry5.get(),drop6.get(),drop7.get(),entry6.get(),entry7.get()),self.run()])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,drop1,drop2,drop3,spacing,drop4,Radius,Xlength,drop5,TDTimeStep,TDMaxSteps,TDDeltaStrength,drop6,drop7,smearing,cores):
        first_line = " CalculationMode  =  td "
        scra = " FromScratch     =  "
        second_line =" UnitsOutput    =  eV_Angstrom"
        third_line = [scra,drop1]

        rad = str(Radius)
        fourth_line = [" Dimension   =   ", drop2]
        spa = str(spacing)
        fifth_line = [" Theory  =    ", drop3]
        sixth_line = [" Spacing   =  ",spa,"*angstrom"]
        seventh_line = [" BoxShape = ", drop4 ]
        eigth_line = [" Radius = ", rad,"*angstrom"]
        after_eight_line = [" Xlength = ", Xlength  ]
        ninth_line = [' XYZCoordinates   =  "coordinate.xyz"  ']
        tenth_line = [" TDPropagator   =  ", drop5 ]
        eleventh_line = [" TDTimeStep = ", TDTimeStep ]
        eleventh_post_line = [" TDMaxSteps = ", TDMaxSteps ]
        twelth_line = [" TDDeltaStrength = ", TDDeltaStrength]
        thirteenth_line = [" TDPolarizationDirection = ", drop6]
        fourteenth_line = [" SmearingFunstion = ", drop7]
        fifteenth_line = [" Smearing = ", smearing]

     
            



        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")

        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")
 
        self.inp_file.writelines(after_eight_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")



        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(eleventh_post_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")


        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(thirteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fourteenth_line)
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.writelines(fifteenth_line) 
        self.inp_file.write("\n")
        self.inp_file.write("\n")

        self.inp_file.close()

        self.run_file=open("run.sh","w")
        run_first_line   = "#!/bin/sh "
        run_second_line  = "#PBS -N gui-gs-test "
        run_third_line   = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_fourth_line  = "#PBS -l walltime=00:30:00 "
        run_fifth_line   = "#PBS -q debug "
        run_sixth_line   = "#PBS -m abe "
        run_seventh_line = "#PBS -V "
        run_eighth_line   = "module load octopus/9.2 "
        run_post_eighth_line  = "cd $PBS_O_WORKDIR "
        run_ninth_line   = "NPROCS=`wc -l < $PBS_NODEFILE`"
        run_tenth_line  = "cat $PBS_NODEFILE > node_ru "
        run_eleventh_line   = "SCRDIR=/lscratch/users/vardha/Vignesh/gs-gui-test "
        run_twelth_line   = "mkdir -p $SCRDIR "
        run_thirteenth_line = "cp {inp,coordinate.xyz} $SCRDIR/ "
        run_fourteenth_line   = "cd $SCRDIR "
        run_fifteenth_line  = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE octopus >> octopus.output "
        run_sixteenth_line = " cp -r * $PBS_O_WORKDIR "
        run_seventeenth_line = " cd $PBS_O_WORKDIR "
        run_eighteenth_line = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_first_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_second_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_third_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fourth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_fifth_line)
        self.run_file.write("\n")

        self.run_file.writelines(run_sixth_line)
        self.run_file.write("\n")

     
        self.run_file.writelines(run_seventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_post_eighth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_ninth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_tenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eleventh_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_twelth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_thirteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fourteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_fifteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_sixteenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_seventeenth_line)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_eighteenth_line) 
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
      
    def run(self):
           subprocess.run(["qsub", "run.sh"])

###############################################################################
#                     Inputs Starting for GPAW
##############################################################################
class GroundState_gpaw(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        bands = StringVar()
        vacuum = StringVar()
        cores = StringVar()
        #maxiter = StringVar()
        #width = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 
         
 #       label_photo = Image.open("label_size.png")
 #       label_photo = label_photo.resize((250, 250), Image.ANTIALIAS)
 #       label_image = ImageTk.PhotoImage(label_photo)

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='grey60',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='aquamarine4',background='grey60',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='grey60',font=('Helvetica', 8))

        label_m = Label(self, text="Ground State - GPAW",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        back_gpaw = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Gpaw))
        back_gpaw.grid(row=10,column=20,padx=1500,pady=900)
#       label1 = Canvas.create_text(self,(400, 190), text="Label text")
        
        label_mode = Label(self,text = "Mode", font =j,bg="grey60",fg="gainsboro")
        label_mode.place(x=5,y=140)

        drop_mode =  ttk.Combobox(self, values=[ "LCAO", "FD","PW"])
        drop_mode.current(0)
        drop_mode['font'] = l
        drop_mode.place(x=400,y=140)

        label_ftype = Label(self, text= "Functional Type", font =j,bg="grey60",fg="gainsboro")
        label_ftype.place(x=5,y=230)

        drop_ftype =  ttk.Combobox(self, values=["PBE", "LDA"])
        drop_ftype.current(0)
        drop_ftype['font'] = l
        drop_ftype.place(x=400, y=230)

        label_basis = Label(self, text= "Basis", font =j,bg="grey60",fg="gainsboro" )
        label_basis.place(x=5,y=310)

        drop_basis =  ttk.Combobox(self, values=["dzp","scp","pvalence.dz"])
        drop_basis.current(0)
        drop_basis['font'] = l
        drop_basis.place(x=400,y=310)

        label_spacing= Label(self, text= "Spacing (in a.u)", font =j,bg="grey60",fg="gainsboro"  )
        label_spacing.place(x=5,y=390)

        entry_spacing = ttk.Entry(self,textvariable="spacing")
        entry_spacing['font'] = l
        entry_spacing.insert(0,"0.16")
        entry_spacing.place(x= 400, y =390 )


        label_bands = Label(self, text= "Number of bands",  font =j,bg="grey60",fg="gainsboro"  )
        label_bands.place(x=5,y=470)

        entry_bands=ttk.Entry(self,textvariable="bands")
        entry_bands['font']=l
        entry_bands.place(x=400,y=470)


        label_coordinates = Label(self, text="XYZ Coordinates", font =j, bg="grey60", fg="gainsboro")
        label_coordinates.place(x=5,y=560)

        button_coordinates = ttk.Button(self, text="Select", style="K.TButton", command=lambda:controller.open_file())
        button_coordinates.place(x=400, y=560)

        label_vacuum = Label(self,text="Vacuum size (in Angstrom)", font =j,bg="grey60",fg="gainsboro")
        label_vacuum.place(x=5,y=620)

        entry_vacuum=ttk.Entry(self,textvariable="vacuum")
        entry_vacuum['font'] = l
        entry_vacuum.insert(0,"6")
        entry_vacuum.place(x=400,y=620)

        label_processors = Label(self, text="No of Processors", font=j, bg = "grey60", fg="gainsboro")
        label_processors.place(x=5,y=690)

        entry_processors=ttk.Entry(self,textvariable="cores")
        entry_processors.delete(0,END)
        entry_processors.insert(0,"4")
        entry_processors['font'] = l
        entry_processors.place(x=400, y=690)


        enter = ttk.Button(self, text="SUBMIT", style="TButton", command=lambda:[self.input_file(drop_mode.get(), drop_ftype.get(), drop_basis.get(), entry_spacing.get(), entry_bands.get(), entry_vacuum.get(), entry_processors.get()), self.run(), messagebox.showinfo("Job Submitted", "Your Job to compute the ground state is submitted to the cluster")]) 
         

        enter.place(x=900,y=900)

#---------------------------------------------------------------------------------
#           Prepare the input file for the ground state calculation in GPAW
#---------------------------------------------------------------------------------

    def input_file(self,drop_mode,drop_ftype,drop_basis,spacing,bands,vacuum,cores):
        line_1 = "from ase.io import read, write"
        line_2 = "from ase import Atoms" 
        line_3 = "from ase.parallel import paropen"
        line_4 = "from gpaw.poisson import PoissonSolver"
        line_5 = "from gpaw.eigensolvers import CG"
        line_6 = "from gpaw import GPAW, FermiDirac"
        line_7 = "from gpaw import Mixer, MixerSum, MixerDif"
        line_8 = "from gpaw.lcao.eigensolver import DirectLCAO"

        line_9 = "# Molecule or nanostructure"
        line_10 = "layer = read('coordinate.xyz')"
        vac = str(vacuum)
        line_11 = [ "layer.center(vacuum=", vac,")"]

        line_12 = "#Ground-state calculation"
        mode = str(drop_mode)
        line_13 = ["calc = GPAW(mode='",mode, "',"]
        spa = str(spacing)
        line_14 = ["            h=", spa, ","]
        line_15 = ["            basis='",str(drop_basis),"',"]
        line_16 = ["            xc='",str(drop_ftype),"',"]
        line_17 = ["            nbands=",str(bands),","]
        line_18 =  "            setups={'default': 'paw'}, "
        line_19 =  "            occupations=FermiDirac(width=0.07),"
        line_20 =  "            mixer=Mixer(0.02, 5, 1.0),"
        line_21 =  "            maxiter=2500,"
        line_22 =  "            convergence={'density': 1e-12, 'bands': -20},"
        line_23 =  "            txt='gs.out')"
        line_24 =  "layer.calc = calc"
        line_25 =  "energy = layer.get_potential_energy()"
        line_26 =  "calc.write('gs.gpw', mode='all')"



        self.gs_file=open("gs.py", "w")

        self.gs_file.truncate()

        self.gs_file.write(line_1)
        self.gs_file.write("\n")

        self.gs_file.write(line_2)
        self.gs_file.write("\n")
            
        self.gs_file.write(line_3)
        self.gs_file.write("\n")

        self.gs_file.write(line_4)
        self.gs_file.write("\n")

        self.gs_file.write(line_5)
        self.gs_file.write("\n")

        self.gs_file.write(line_6)
        self.gs_file.write("\n")

        self.gs_file.write(line_7)
        self.gs_file.write("\n")

        self.gs_file.write(line_8)
        self.gs_file.write("\n")
        self.gs_file.write("\n")

        self.gs_file.write(line_9)
        self.gs_file.write("\n")

        self.gs_file.write(line_10)
        self.gs_file.write("\n")

        self.gs_file.writelines(line_11)
        self.gs_file.write("\n")
        self.gs_file.write("\n")

        self.gs_file.writelines(line_12)
        self.gs_file.write("\n")

        self.gs_file.writelines(line_13)
        self.gs_file.write("\n")

        self.gs_file.writelines(line_14)
        self.gs_file.write("\n")

        self.gs_file.writelines(line_15)
        self.gs_file.write("\n")

        self.gs_file.writelines(line_16)
        self.gs_file.write("\n")
        
        self.gs_file.writelines(line_17)
        self.gs_file.write("\n")

        self.gs_file.write(line_18)
        self.gs_file.write("\n")

        self.gs_file.write(line_19)
        self.gs_file.write("\n")

        self.gs_file.write(line_20)
        self.gs_file.write("\n")

        self.gs_file.write(line_21)
        self.gs_file.write("\n")

        self.gs_file.write(line_22)
        self.gs_file.write("\n")

        self.gs_file.write(line_23)
        self.gs_file.write("\n")
        
        self.gs_file.write(line_24)
        self.gs_file.write("\n")

        self.gs_file.write(line_25)
        self.gs_file.write("\n")

        self.gs_file.write(line_26)
        self.gs_file.write("\n")


        self.gs_file.close()

#-----------------------------------------------------------------------------
#          Prepare the job script for the ground state calculation in GPAW
#-----------------------------------------------------------------------------

        self.run_file=open("run.sh","w")

        run_line_1    = "#!/bin/sh "
        run_line_2    = "#PBS -N gui-gs-test "
        run_line_3    = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_line_4    = "#PBS -l walltime=00:30:00 "
        run_line_5    = "#PBS -q debug "
        run_line_6    = "#PBS -m abe "
        run_line_7    = "#PBS -V "
        
        run_line_8    = "export OMP_NUM_THREADS=1" 
        run_line_9    = "module load gpaw/21.6.0_VS "
  
        run_line_10   = "NPROCS=`wc -l < $PBS_NODEFILE`"

        run_line_11   = "cd $PBS_O_WORKDIR "

        run_line_12   = "cat $PBS_NODEFILE > node_ru "

        run_line_13   = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE python3 gs.py >& gs.log "
        
        run_line_14   = " echo $NPROCS "
        
        self.run_file.truncate()
        self.run_file.write(run_line_1)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_2)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_3)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_4)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_5)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_6)
        self.run_file.write("\n")
     
        self.run_file.writelines(run_line_7)
        self.run_file.write("\n")
        self.run_file.write("\n")
  

        self.run_file.writelines(run_line_8)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_9)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_line_10)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_11)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_12)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_13)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_14)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()
      
    def run(self):
           subprocess.run(["qsub", "run.sh"])
        
#---------------------------------------------------------------
#            TDDFT calculations in GPAW
#--------------------------------------------------------------

class TimeDependent_gpaw(Frame):

     
    def __init__(self, parent, controller):
        
        dt   = StringVar()
        Nt   = StringVar()
        cores = StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_m = Label(self, text="Time Dependent - GPAW",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        gpaw = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Gpaw))
        gpaw.grid(row=10,column=20,padx=1500,pady=900)

        label_strength = Label(self, text= "Laser strength (in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_strength.place(x=5,y=140)

        label_polarization = Label(self, text= "Electric polarization:",font=j,bg= "grey60",fg="gainsboro")
        label_polarization.place(x=5,y=230)

        label_pol_x = Label(self, text="Select the value of x", font=j,bg= "grey60",fg="gainsboro")
        label_pol_x.place(x=50,y=280)

        label_pol_y = Label(self, text="Select the value of y", font=j,bg= "grey60",fg="gainsboro")
        label_pol_y.place(x=50,y=330)


        label_pol_z = Label(self, text="Select the value of z", font=j,bg= "grey60",fg="gainsboro")
        label_pol_z.place(x=50,y=380)

        label_timestep = Label(self, text= "Propagation time step (in attosecond)",font=j,bg= "grey60",fg="gainsboro")
        label_timestep.place(x=5,y=430)

        label_steps=Label(self, text= "Total time steps",font=j,bg= "grey60",fg="gainsboro")
        label_steps.place(x=5,y=480)

        drop_strength =  ttk.Combobox(self, values=[ "1e-5", "1e-3"])
        drop_strength.current(0)
        drop_strength['font'] = l
        drop_strength.place(x=700,y=140)

        drop_pol_x =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_x.current(0)
        drop_pol_x['font'] = l
        drop_pol_x.place(x=700, y=280)

        drop_pol_y =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_y.current(0)
        drop_pol_y['font'] = l
        drop_pol_y.place(x=700, y=330)

        drop_pol_z =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_z.current(0)
        drop_pol_z['font'] = l
        drop_pol_z.place(x=700, y=380)

        entry_dt = ttk.Entry(self,textvariable="dt")
        entry_dt['font']=l
        entry_dt.insert(0,"10")
        entry_dt.place(x=700, y=430 )

        entry_Nt = ttk.Entry(self,textvariable="Nt")
        entry_Nt['font']=l
        entry_Nt.insert(0,"2000")
        entry_Nt.place(x=700, y=480 )

        label_processors = Label(self, text="No of Processors", font=j, bg = "grey60", fg="gainsboro")
        label_processors.place(x=5,y=550)

        entry_processors=ttk.Entry(self,textvariable="cores")
        entry_processors.delete(0,END)
        entry_processors.insert(0,"4")
        entry_processors['font'] = l
        entry_processors.place(x=700, y=550)


        enter = ttk.Button(self, text="SUBMIT", style="TButton", command=lambda:[self.input_file(drop_strength.get(), drop_pol_x.get(), drop_pol_y.get(), drop_pol_z.get(), entry_dt.get(), entry_Nt.get(), entry_processors.get()), self.run(), messagebox.showinfo("Job Submitted", "Your Job to compute the Absorption spectrum is submitted to the cluster")])


        enter.place(x=900,y=900)

#---------------------------------------------------------------------------------
#           Prepare the input file for the TDDFT calculation in GPAW
#---------------------------------------------------------------------------------


    def input_file(self,drop_strength,drop_pol_x,drop_pol_y,drop_pol_z,dt,Nt,cores):
        line_1 = "# Time-propagation calculation"
        line_2 = "from gpaw.lcaotddft import LCAOTDDFT"
        line_3 = "from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter"
        line_4 = "# Read converged ground-state file"
        line_5 = "td_calc = LCAOTDDFT('gs.gpw', txt='tdx.out')"
        line_6 = "# Attach any data recording or analysis tools"
        line_7 = "DipoleMomentWriter(td_calc, 'dm.dat')"
        line_8 = "# Kick"

        Ex = float(drop_strength)*int(drop_pol_x)
        Ey = float(drop_strength)*int(drop_pol_y)
        Ez = float(drop_strength)*int(drop_pol_z)
        #Ey = drop_strength*drop_pol_y
        #Ez = drop_strength*drop_pol_z

        line_9 = ["td_calc.absorption_kick([", str(Ex), ", ", str(Ey), ", ",  str(Ez),"])"]
        line_10 = "# Propagate"
        line_11 = ["td_calc.propagate(", str(dt), ", ", str(Nt),")"]
        line_12 = "# Save the state for restarting later"
        line_13 = "td_calc.write('td.gpw', mode='all')"


        self.td_file=open("td.py", "w")

        self.td_file.truncate()

        self.td_file.write(line_1)
        self.td_file.write("\n")

        self.td_file.write(line_2)
        self.td_file.write("\n")

        self.td_file.write(line_3)
        self.td_file.write("\n")
        self.td_file.write("\n")

        self.td_file.write(line_4)
        self.td_file.write("\n")

        self.td_file.write(line_5)
        self.td_file.write("\n")
        self.td_file.write("\n")

        self.td_file.write(line_6)
        self.td_file.write("\n")

        self.td_file.write(line_7)
        self.td_file.write("\n")
        self.td_file.write("\n")

        self.td_file.write(line_8)
        self.td_file.write("\n")

        self.td_file.writelines(line_9)
        self.td_file.write("\n")
        self.td_file.write("\n")

        self.td_file.writelines(line_10)
        self.td_file.write("\n")

        self.td_file.writelines(line_11)
        self.td_file.write("\n")
        self.td_file.write("\n")

        self.td_file.writelines(line_12)
        self.td_file.write("\n")

        self.td_file.writelines(line_13)
        self.td_file.write("\n")

        self.td_file.close()


        #-------------------------------------------------------------
        #       Preparing the input file for the spectrum calculation
        #-------------------------------------------------------------

        spec_line_1 = "# Analyze the results"
        spec_line_2 = "from gpaw.tddft.spectrum import photoabsorption_spectrum"
        spec_line_3 = "photoabsorption_spectrum('dm.dat', 'spec_x.dat', width=0.09, e_min=0.0, e_max=15.0, delta_e=0.05)"

        self.spec_file=open("spec.py", "w")

        self.spec_file.truncate()

        self.spec_file.write(spec_line_1)
        self.spec_file.write("\n")

        self.spec_file.write(spec_line_2)
        self.spec_file.write("\n")

        self.spec_file.write(spec_line_3)
        self.spec_file.write("\n")


        self.spec_file.close()



#-----------------------------------------------------------------------------
#          Prepare the job script for the spectrum calculation in GPAW
#-----------------------------------------------------------------------------

        self.run_file=open("run_td.sh","w")

        run_line_1    = "#!/bin/sh "
        run_line_2    = "#PBS -N spec "
        run_line_3    = ["#PBS -l select=1:ncpus=",cores,":mpiprocs=",cores]
        run_line_4    = "#PBS -l walltime=00:30:00 "
        run_line_5    = "#PBS -q debug "
        run_line_6    = "#PBS -m abe "
        run_line_7    = "#PBS -V "

        run_line_8    = "export OMP_NUM_THREADS=1"
        run_line_9    = "module load gpaw/21.6.0_VS "

        run_line_10   = "NPROCS=`wc -l < $PBS_NODEFILE`"

        run_line_11   = "cd $PBS_O_WORKDIR "

        run_line_12   = "cat $PBS_NODEFILE > node_ru "

        run_line_13   = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE python3 td.py >& td.log "
        run_line_14   = " mpirun -np $NPROCS -machinefile $PBS_NODEFILE python3 spec.py >& spec.log "

        run_line_15   = " echo $NPROCS "

        self.run_file.truncate()
        self.run_file.write(run_line_1)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_2)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_3)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_4)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_5)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_6)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_7)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_line_8)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_9)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.writelines(run_line_10)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_11)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_12)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_13)
        self.run_file.write("\n")

        self.run_file.writelines(run_line_14)
        self.run_file.write("\n")
        self.run_file.write("\n")

        self.run_file.writelines(run_line_15)
        self.run_file.write("\n")
        self.run_file.write("\n")


        self.run_file.close()

    def run(self):
           subprocess.run(["qsub", "run_td.sh"])


        
class GroundState_5(Frame):

     
    def __init__(self, parent, controller):
        
        spacing   = StringVar()
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=10,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')

        self.configure(bg="grey16") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("A.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))
        gui_style.configure("B.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 14))

        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey60",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(GroundState))
        octopus.grid(row=10,column=20,padx=1500,pady=900)
        label1 = ttk.Label(self, text= "From Scratch",style="A.TLabel")
        label1.place(x=5,y=140)
        label2 = ttk.Label(self, text= "Dimension",style="A.TLabel")
        label2.place(x=5,y=230)
        label3 = ttk.Label(self, text= "TheoryLevel",style="A.TLabel")
        label3.place(x=5,y=310)

        label_3=ttk.Label(self, text= "Spacing(in a.u)",style="A.TLabel")
        label_3.place(x=5,y=390)

        label4 = ttk.Label(self, text= "Box Shape",style="A.TLabel")
        label4.place(x=5,y=470)
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = j
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "ONE", "TWO", "THREE"])
        drop2.current(0)
        drop2['font'] = j
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["HARTREE", "INDEPENDENT_PARTICLES","HARTREE_FOCK","DFT","RDMFT"])
        drop3.current(0)
        drop3['font'] = j
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self,textvariable="spacing")
   #    entry1.insert(0,"0.16")
        entry1.place(x= 400, y =390 )
        drop_3=ttk.Combobox(self,values="parallelepiped")
        drop_3.current(0)
        drop_3['font']=j
        drop_3.place(x=400,y=470)
        button_3 = ttk.Button(self, text="select",style="K.TButton",command=lambda:controller.cmd(drop_3.get()))
        button_3.place(x=690,y=470) 
        label5 = ttk.Label(self, text= "Box Length[x/2 y/2 z/2 in Ang Units]",style="B.TLabel")
        label5.place(x=5,y=550)
        entry2 = ttk.Entry(self,textvariable="X",width=7)
   #     entry2.insert(0,"0.00")
        entry2.place(x= 400, y =550)
        entry3 = ttk.Entry(self,textvariable="Y",width=7)
   #     entry3.insert(0,"0.00")
        entry3.place(x= 500, y =550)
        entry4 = ttk.Entry(self,textvariable="Z",width=7)
   #     entry4.insert(0,"0.00")
        entry4.place(x= 600, y =550)

 

class GroundState_(Frame):

     
    def __init__(self, parent, controller):
        
        radius= StringVar()
        spacing   = StringVar()
        species1  = StringVar()
        species2  = StringVar()
        species3  = StringVar()
        species4  = StringVar()
        species5  = StringVar()

        coor11= StringVar()
        coor21= StringVar()
        coor31= StringVar()
        coor41= StringVar()
        coor51= StringVar()

        coor12 = StringVar()
        coor22 = StringVar()
        coor32 = StringVar()
        coor42= StringVar()
        coor52= StringVar()

        coor13 = StringVar()
        coor23 = StringVar()
        coor33 = StringVar()
        coor43= StringVar()
        coor53= StringVar()
            
        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=10,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')

        self.configure(bg="grey16") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))


        label_m = Label(self, text="Ground State - OCTOPUS",font=k,bg= "grey16",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(Octopus))
   #     octopus['font'] = myFont
        octopus.grid(row=10,column=20,padx=1500,pady=900)
  #      enter = Button(self, text="ENTER", command=lambda:controller.write_File(self),bg="aquamarine4",fg="black")
  #      enter['font'] = myFont
  #      enter.grid(row=7, column = 7,padx=40,pady=40)
      #  enter = Button(self, text="ENTER", command=inp_file.write(radius.get()),bg="aquamarine4",fg="black")
      #  enter['font'] = myFont
      #  enter.grid(row=7, column = 7,padx=40,pady=40)
        label1 = ttk.Label(self, text= "From Scratch",style="BW.TLabel")
   #     label1['font'] = myFont
        label1.place(x=5,y=140)
        label2 = ttk.Label(self, text= "Dimension",style="BW.TLabel")
   #     label2['font'] = myFont
        label2.place(x=5,y=230)
        label3 = ttk.Label(self, text= "TheoryLevel",style="BW.TLabel")
 #       label3['font'] = myFont
        label3.place(x=5,y=310)

        label_3=ttk.Label(self, text= "Box_Shape",style="BW.TLabel")
        label_3.place(x=5,y=340)

        label4 = ttk.Label(self, text= "Radius(in a.u)",style="BW.TLabel")
  #      label4['font'] = myFont
        label4.place(x=5,y=390)
        label5 = ttk.Label(self, text= "Spacing(in a.u)",style="BW.TLabel")
 #       label5['font'] = myFont
        label5.place(x=5,y=470)
        label6 = ttk.Label(self,text= "Coordinates", style="BW.TLabel")
 #        label6['font'] = myFont
        label6.place(x=650,y=140)
        label7 = ttk.Label(self, text= "Species(in CAPS)",style="BW.TLabel")
 #       label7['font'] = myFont
        label7.place(x=5, y=550)
        from_scra = StringVar()
        from_scra.set("No")
        dimension = StringVar()
        dimension.set("ONE")
        theory=StringVar()
        theory.set("DFT")
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
   #     drop1.current(0)
        if drop1 == "YES":
           # entry_try = ttk.Entry(self, textvariable = radius)
           # entry_try.insert(0," 007") 
           # entry_try.place(x=900,y=790)
           command=lambda:controller.show_frame(TimeDependent)                  
        drop1['font'] = j
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=[ "ONE", "TWO", "THREE"])
        drop2.current(0)
        drop2['font'] = j
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=["HARTREE", "INDEPENDENT_PARTICLES","HARTREE_FOCK","DFT","RDMFT"])
        drop3.current(0)
        drop3['font'] = j
   #     drop3.config(bg='light blue')
        drop3.place(x=400,y=310)
        drop_3=ttk.Combobox(self,values="Sphere")
        drop_3.current(0)
        drop_3['font']=j
        drop_3.place(x=400,y=350)
        ch = StringVar()
#        print(drop_3.get())
#        if drop_3.get() == "Sphere":
#            ch = "Octopus"
#            button_3 = ttk.Button(self, text="select",style="TButton",command=lambda:controller.cmd(drop_3.get()))
#        if drop_3.get() == "Cylinder":
#            ch = "Gpaw"
#            button_3 = ttk.Button(self, text="select",style="TButton",command=lambda:controller.cmd(drop_3.get()))
#        print(ch)
   #     button_3 = ttk.Button(self, text="select",style="TButton",command=lambda:controller.show_frame(str(ch)))  
#        button_3.place(x=690,y=350) 
        entry1 = ttk.Entry(self, textvariable = radius)
        entry1.insert(0," 6.6140") 
  #      Radius=radius.get()
        entry1.place(x=400,y=390)
     #   inp_file.write(radius.get())
        entry2 = ttk.Entry(self, textvariable = spacing)
        entry2.place(x=400,y=470)
        entry2.insert(0,"0.34") 
        entry3 = ttk.Entry(self,textvariable=coor11)
        entry3.place(x=885,y=140)
        entry3.insert(0,"0.00000") 
        entry4 = ttk.Entry(self,textvariable=coor21)
        entry4.place(x=885, y=180)
        entry4.insert(0,"0.63335") 
        entry5 = ttk.Entry(self,textvariable=coor31)
        entry5.place(x=885,y=220)
        entry5.insert(0,"-0.63335") 
        entry6 = ttk.Entry(self,textvariable=coor41)
        entry6.place(x=885,y=260)
        entry6.insert(0,"0.63335") 
        entry7 = ttk.Entry(self,textvariable=coor51)
        entry7.place(x=885,y=300)
        entry7.insert(0,"-0.63335") 

        entry8 = ttk.Entry(self,textvariable=coor12)
        entry8.place(x=1110,y=140)
        entry8.insert(0,"0.00000") 
        entry9 = ttk.Entry(self,textvariable=coor22)
        entry9.place(x=1110, y=180)
        entry9.insert(0,"0.63335") 
        entry10 = ttk.Entry(self, textvariable=coor32)
        entry10.place(x=1110,y=220)
        entry10.insert(0,"-0.63335") 
        entry11= ttk.Entry(self,textvariable=coor42)
        entry11.place(x=1110,y=260)
        entry11.insert(0,"-0.63335") 
        entry12= ttk.Entry(self,textvariable=coor52)
        entry12.place(x=1110,y=300)
        entry12.insert(0,"-0.63335") 
        entry13 = ttk.Entry(self, textvariable=coor13)
        entry13.place(x=1319,y=140)
        entry13.insert(0,"0.00000") 
        entry14 = ttk.Entry(self, textvariable=coor23)
        entry14.place(x=1319,y=180)
        entry14.insert(0,"0.63335") 
        entry15 = ttk.Entry(self, textvariable=coor33)
        entry15.place(x=1319, y=220)
        entry15.insert(0,"0.63335") 
        entry16 = ttk.Entry(self,textvariable=coor43)
        entry16.place(x=1319,y=260)
        entry16.insert(0,"-0.63335") 
        entry17 = ttk.Entry(self,textvariable=coor53)
        entry17.place(x=1319,y=300)
        entry17.insert(0,"-0.63335") 

        entry18 = ttk.Entry(self,textvariable=species1)
        entry18.place(x=400, y=550)
        entry18.insert(0,"C") 
        entry19 = ttk.Entry(self,textvariable=species2)
        entry19.place(x=400,y=590)
        entry19.insert(0,"H") 
        entry20 = ttk.Entry(self,textvariable=species3)
        entry20.place(x=400,y=630)
        entry20.insert(0,"H") 
        entry21 = ttk.Entry(self,textvariable=species4)
        entry21.place(x=400,y=670)
        entry21.insert(0,"H") 
        entry22 = ttk.Entry(self,textvariable=species5)
        entry22.place(x=400,y=710)
        entry22.insert(0,"H") 


        enter = ttk.Button(self, text="ENTER",style="TButton",command=lambda:[self.input_file(from_scra.get(),dimension.get(),theory.get(),radius.get(),spacing.get(),\
                species1.get(),species2.get(),species3.get(),species4.get(),species5.get(),\
                coor11.get(),coor21.get(),coor31.get(),coor41.get(),coor51.get(),\
                coor12.get(),coor22.get(),coor33.get(),coor42.get(),coor52.get(),\
                coor13.get(),coor23.get(),coor33.get(),coor43.get(),coor53.get()),self.run()])

 #       enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,from_scra,dimension,theory,radius,spacing,species1,species2,species3,species4,species5,\
            coor11,coor21,coor31,coor41,coor51,coor12,coor22,coor32,coor42,coor52,coor13,coor23,coor33,coor43,coor53):
        first_line = " CalculationMode  =  gs "
        scra = " FromScratch     =  "
        rad = str(radius)
        third_line = [" Radius   =   ", rad]
        spa = str(spacing)
        fourth_line = [" Spacing   =    ", spa]
        second_line = [scra,from_scra]
        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(fourth_line)
        
        line = "  |  "
        fifth_line="%Coordinates"
        self.inp_file.write("\n")
        sixth_line=["\"",species1,"\"",line,coor11,line,coor12,line,coor13]
        seventh_line=["\"",species2,"\"",line,coor21,line,coor22,line,coor23]
        eigth_line=["\"",species3,"\"",line,coor31,line,coor32,line,coor33]
        ninth_line=["\"",species4,"\"",line,coor41,line,coor42,line,coor43]
        tenth_line=["\"",species5,"\"",line,coor51,line,coor52,line,coor53]
        eleventh_line="%"


        self.inp_file.write(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(eleventh_line)
        self.inp_file.close()

    def run(self):
        subprocess.run(["qsub", "job.sh"])




class TimeDependent__(Frame):
    def __init__(self, parent, controller):
        
        radius    = StringVar()
        spacing   = StringVar()
        tdmax     = StringVar()
        tdstep    = StringVar()
        species1  = StringVar()
        species2  = StringVar()
        species3  = StringVar()
        species4  = StringVar()
        species5  = StringVar()


        coor11= StringVar()
        coor21= StringVar()
        coor31= StringVar()
        coor41= StringVar()
        coor51= StringVar()

        coor12 = StringVar()
        coor22 = StringVar()
        coor32 = StringVar()
        coor42= StringVar()
        coor52= StringVar()

        coor13 = StringVar()
        coor23 = StringVar()
        coor33 = StringVar()
        coor43= StringVar()
        coor53= StringVar()

        Frame.__init__(self, parent)
        myFont = font.Font(family='Courier', size=20, weight ='bold')
        j=font.Font(family ='Courier', size=10,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')

        self.configure(bg="grey16") 

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))


        label_m = Label(self, text="TimeDepedent - OCTOPUS",font=k,bg= "grey16",fg="gainsboro")
        label_m.place(x=450,y=5)

        octopus = ttk.Button(self, text="BACK",style="TButton", command=lambda:controller.show_frame(Octopus))
   #     octopus['font'] = myFont
        octopus.grid(row=10,column=20,padx=1500,pady=900)
  #      enter = Button(self, text="ENTER", command=lambda:controller.write_File(self),bg="aquamarine4",fg="black")
  #      enter['font'] = myFont
  #      enter.grid(row=7, column = 7,padx=40,pady=40)
      #  enter = Button(self, text="ENTER", command=inp_file.write(radius.get()),bg="aquamarine4",fg="black")
      #  enter['font'] = myFont
      #  enter.grid(row=7, column = 7,padx=40,pady=40)
        label1 = ttk.Label(self, text= "From Scratch",style="BW.TLabel")
   #     label1['font'] = myFont
        label1.place(x=5,y=140)
        label2 = ttk.Label(self, text= "Dimension",style="BW.TLabel")
   #     label2['font'] = myFont
        label2.place(x=5,y=230)
        label3 = ttk.Label(self, text= "TheoryLevel",style="BW.TLabel")
   #     label3['font'] = myFont
        label3.place(x=5,y=310)
        label4 = ttk.Label(self, text= "Radius(in a.u)",style="BW.TLabel")
   #     label4['font'] = myFont
        label4.place(x=5,y=390)
        label5 = ttk.Label(self, text= "Spacing(in a.u)",style="BW.TLabel")
  #      label5['font'] = myFont
        label5.place(x=5,y=470)
        label6 = ttk.Label(self, text= "TDMaxSteps",style="BW.TLabel")
   #     label6['font'] = myFont
        label6.place(x=5,y=550)
        label7 = ttk.Label(self, text= "TDTimeSteps(in a.u)",style="BW.TLabel")
  #      label7['font'] = myFont
        label7.place(x=5,y=630)

        label8 = ttk.Label(self,text="Coordinates",style="BW.TLabel")
   #     label8['font'] = myFont
        label8.place(x=600,y=140)
        label9 = ttk.Label(self, text= " Species(in CAPS)",style="BW.TLabel")
  #      label9['font'] = myFont
        label9.place(x=5, y=710)
        from_scra = StringVar()
        from_scra.set("No")
        dimension = StringVar()
        dimension.set("ONE")
        theory=StringVar()
        theory.set("DFT")
        drop1 =  ttk.Combobox(self, values=[ "YES", "No"])
        drop1.current(0)
        drop1['font'] = j
        drop1.place(x=400,y=140)
        drop2 =  ttk.Combobox(self, values=["ONE", "TWO", "THREE"])
        drop2.current(0)
        drop2['font'] = j
        drop2.place(x=400, y=230)
        drop3 =  ttk.Combobox(self, values=[ "HARTREE", "INDEPENDENT_PARTICLES","HARTREE_FOCK","DFT","RDMFT"])
        drop3.current(0)
        drop3['font'] = j
 #       drop3.config(bg='light blue')
        drop3.place(x=400,y=310)
        entry1 = ttk.Entry(self, textvariable = radius)
        entry1.insert(0," 6.6140") 
  #      Radius=radius.get()
        entry1.place(x=400,y=390)
     #   inp_file.write(radius.get())
        entry2 = ttk.Entry(self, textvariable = spacing)
        entry2.place(x=400,y=470)
        entry2.insert(0,"0.34")
        entry3 = ttk.Entry(self, textvariable = tdmax)
        entry3.place(x=400,y=550)
        entry3.insert(0,"3000") 
        entry4 = ttk.Entry(self, textvariable = tdstep)
        entry4.place(x=400,y=630)
        entry4.insert(0,"0.01") 

        entry5 = ttk.Entry(self,textvariable=coor11)
        entry5.place(x=885,y=140)
        entry5.insert(0,"0.00000") 
        entry6 = ttk.Entry(self,textvariable=coor21)
        entry6.place(x=885, y=180)
        entry6.insert(0,"0.63335") 
        entry7 = ttk.Entry(self,textvariable=coor31)
        entry7.place(x=885,y=220)
        entry7.insert(0,"-0.63335") 
        entry8 = ttk.Entry(self,textvariable=coor41)
        entry8.place(x=885,y=260)
        entry8.insert(0,"0.63335") 
        entry9 = ttk.Entry(self,textvariable=coor51)
        entry9.place(x=885,y=300)
        entry9.insert(0,"-0.63335") 

        entry10 = ttk.Entry(self,textvariable=coor12)
        entry10.place(x=1110,y=140)
        entry10.insert(0,"0.00000") 
        entry11 = ttk.Entry(self,textvariable=coor22)
        entry11.place(x=1110, y=180)
        entry11.insert(0,"0.63335") 
        entry12 = ttk.Entry(self, textvariable=coor32)
        entry12.place(x=1110,y=220)
        entry12.insert(0,"-0.63335") 
        entry13= ttk.Entry(self,textvariable=coor42)
        entry13.place(x=1110,y=260)
        entry13.insert(0,"-0.63335") 
        entry14= ttk.Entry(self,textvariable=coor52)
        entry14.place(x=1110,y=300)
        entry14.insert(0,"-0.63335") 
        entry15 = ttk.Entry(self, textvariable=coor13)
        entry15.place(x=1319,y=140)
        entry15.insert(0,"0.00000") 
        entry16 = ttk.Entry(self, textvariable=coor23)
        entry16.place(x=1319,y=180)
        entry16.insert(0,"0.63335") 
        entry17 = ttk.Entry(self, textvariable=coor33)
        entry17.place(x=1319, y=220)
        entry17.insert(0,"0.63335") 
        entry18 = ttk.Entry(self,textvariable=coor43)
        entry18.place(x=1319,y=260)
        entry18.insert(0,"-0.63335") 
        entry19 = ttk.Entry(self,textvariable=coor53)
        entry19.place(x=1319,y=300)
        entry19.insert(0,"-0.63335") 

        entry20 = ttk.Entry(self,textvariable=species1)
        entry20.place(x=400, y=710)
        entry20.insert(0,"C") 
        entry21 = ttk.Entry(self,textvariable=species2)
        entry21.place(x=400,y=750)
        entry21.insert(0,"H") 
        entry22 = ttk.Entry(self,textvariable=species3)
        entry22.place(x=400,y=790)
        entry22.insert(0,"H") 
        entry23 = ttk.Entry(self,textvariable=species4)
        entry23.place(x=400,y=830)
        entry23.insert(0,"H") 
        entry24 = ttk.Entry(self,textvariable=species5)
        entry24.place(x=400,y=880)
        entry24.insert(0,"H") 

       
        enter = ttk.Button(self, text="ENTER",style="TButton", command=lambda:[self.input_file(from_scra.get(),dimension.get(),theory.get(),radius.get(),spacing.get(),\
                tdmax.get(),tdstep.get(),species1.get(),species2.get(),species3.get(),species4.get(),species5.get(),\
                coor11.get(),coor21.get(),coor31.get(),coor41.get(),coor51.get(),\
                coor12.get(),coor22.get(),coor32.get(),coor42.get(),coor52.get(),\
                coor13.get(),coor23.get(),coor33.get(),coor43.get(),coor53.get()),self.run()])

  #      enter['font'] = myFont
        enter.place(x=900,y=900)


    def input_file(self,from_scra,dimension,theory,radius,spacing,tdmax,tdstep,species1,species2,species3,species4,species5,\
            coor11,coor21,coor31,coor41,coor51,coor12,coor22,coor32,coor42,coor52,coor13,coor23,coor33,coor43,coor53):
        first_line = " CalculationMode  =  td "
        scra = " FromScratch     =  "
        rad = str(radius)
        third_line = [" Radius   =   ", rad]
        spa = str(spacing)
        fourth_line = [" Spacing   =    ", spa]
        second_line = [scra,from_scra]
        self.inp_file=open("inp","w")
        self.inp_file.truncate()
        self.inp_file.write(first_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(second_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(third_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(fourth_line)
        
        line = "  |  "
        fifth_line="%Coordinates"
        self.inp_file.write("\n")
        sixth_line=["\"",species1,"\"",line,coor11,line,coor12,line,coor13]
        seventh_line=["\"",species2,"\"",line,coor21,line,coor22,line,coor23]
        eigth_line=["\"",species3,"\"",line,coor31,line,coor32,line,coor33]
        ninth_line=["\"",species4,"\"",line,coor41,line,coor42,line,coor43]
        tenth_line=["\"",species5,"\"",line,coor51,line,coor52,line,coor53]
        twelth_line=["TDMaxSteps  =  ",tdmax]
        thirteenth_line=["TDTimeSteps  =   ",tdstep]
        eleventh_line="%"


        self.inp_file.write(fifth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(sixth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(seventh_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(eigth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(ninth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(tenth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(eleventh_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(twelth_line)
        self.inp_file.write("\n")
        self.inp_file.writelines(thirteenth_line)
        self.inp_file.close()

    def run(self):
        subprocess.run(["qsub", "job1.sh"])


"""


class TimeDependent(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Octopus")
     #   label.pack(padx=10, pady=10)
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
#        start_page.pack()
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        gpaw = Button(self, text="GPAW", command=lambda:controller.show_frame(Gpaw))
#        gpaw.pack()
        gpaw.grid(row=0, column =1, padx=40, pady=40)

class Casida(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Octopus")
     #   label.pack(padx=10, pady=10)
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
#        start_page.pack()
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        gpaw = Button(self, text="GPAW", command=lambda:controller.show_frame(Gpaw))
#        gpaw.pack()
        gpaw.grid(row=0, column =1, padx=40, pady=40)

class VibrationalModes(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Octopus")
     #   label.pack(padx=10, pady=10)
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
#        start_page.pack()

#        start_page.grid(row=0, column = 0,padx=40,pady=40)
        gpaw = Button(self, text="GPAW", command=lambda:controller.show_frame(Gpaw))
#        gpaw.pack()
        gpaw.grid(row=0, column =1, padx=40, pady=40)

class Unoccupied(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Octopus")
     #   label.pack(padx=10, pady=10)
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
#        start_page.pack()
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        gpaw = Button(self, text="GPAW", command=lambda:controller.show_frame(Gpaw))
#        gpaw.pack()
        gpaw.grid(row=0, column =1, padx=40, pady=40)

class EM_RESPONSE(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Octopus")
        start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
        start_page.grid(row=0, column = 0,padx=40,pady=40)
        gpaw = Button(self, text="GPAW", command=lambda:controller.show_frame(Gpaw))
        gpaw.grid(row=0, column =1, padx=40, pady=40)

""" 


class MainMenu:
    def __init__(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)
        menubar.configure(bg="gainsboro")

app = Aitg()
#app = ThemedTk(theme="arc")
app.title("AITG Graphic User Interface for laser Simulation")
#app.geometry("1000x1000")
app.resizable(True,True)
app.mainloop()
