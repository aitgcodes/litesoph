from tkinter import filedialog
import subprocess 
from litesoph.io.IO import UserInput as ui
from litesoph.simulations.esmd import GroundState
from litesoph.simulations import engine

def show_message(label_name,message):
        """
        Shows a update
        """
        label_name['text'] = message
        label_name['foreground'] = 'black'    
 


# def open_file(outpath):
#      text_file = filedialog.askopenfilename(initialdir="./", title="Open Text File", filetypes=((" Text Files", "*.xyz"),))
#      text_file = open(text_file,'r')
#      stuff = text_file.read()
#      out_file = open(outpath+"/coordinate.xyz",'w')
#      out_file.write(stuff)
#      text_file.close()
#      out_file.close()
   
     
# def open_existing_project():
#      oldProject = filedialog.askdirectory()

# def run_job(fpath:str):
#     subprocess.run(["python", fpath])


# def inpdict(job:str, gui_dict):
#     ui.user_param.update(gui_dict) # update the user parameters
#     user_input = ui.user_param
#     print(user_input)
#     engn = engine.choose_engine(user_input)
#     if job == 'gs':
#         GroundState(user_input,engn)    

#def esmd_gui(self,job,var_dict):
    #    ui.user_param.update(var_dict) # update the user parameters
    #    user_input = ui.user_param
    #    print(user_input)
    #    engn = engine.choose_engine(user_input)
    #    if job == 'gs':
    #        GroundState(user_input, engn)
    #    elif job == 'td':
     #       pass             

  
# def submitjob(job:str):
        #     if job == 'gs':
        #         run_job(user_path+'/gs.py')
        #     elif job == 'td':
        #         run_job(user_path+'/td.py')
        #     elif job == 'spec':
        #         run_job(user_path+'/spec.py')        
      