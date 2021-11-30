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


# def submitjob(job:str):
        #     if job == 'gs':
        #         run_job(user_path+'/gs.py')
        #     elif job == 'td':
        #         run_job(user_path+'/td.py')
        #     elif job == 'spec':
        #         run_job(user_path+'/spec.py')        
      