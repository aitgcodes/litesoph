from tkinter import filedialog
import subprocess 


def open_file(outpath):
        text_file = filedialog.askopenfilename(initialdir="./", title="Open Text File", filetypes=((" Text Files", "*.xyz"),))
        text_file = open(text_file,'r')
        stuff = text_file.read()
        out_file = open(outpath+"/coordinate.xyz",'w')
        out_file.write(stuff)
        text_file.close()
        out_file.close()
        
def open_existing_project():
        oldProject = filedialog.askdirectory()

def runpython(fpath:str):
        subprocess.run(["python", fpath])

def show_message(label_name,message):
        """
        Shows a update
        """
        label_name['text'] = message
        label_name['foreground'] = 'black'    

