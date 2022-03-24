from tkinter import font
import tkinter as tk

def myfont1():
    myFont15= font.Font(family='Helvetica', size=15, weight='bold')
    l= font.Font(family ='Courier', size=10,weight='bold') 
    return myFont15  

def myfont():
    myFont = font.Font(family='Helvetica', size=10, weight='bold')
    l= font.Font(family ='Courier', size=15,weight='bold') 
    font5 = font.Font(family='Times New Roman',size=15)
    return font5

def myfont2():
    myfont2= font.Font(family='Helvetica', size=10)
    font3 = font.Font(family='Comic Sans MS', size=10)
    font4 = font.Font(family='Times New Roman',size=15, weight='bold' )
    font5 = font.Font(family='Times New Roman',size=15)
    return myfont2

f1=('Noto sans', 15, 'italic')    
       