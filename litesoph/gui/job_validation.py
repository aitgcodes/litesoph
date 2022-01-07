import tkinter as tk
from litesoph.gui.filehandler import show_message, file_check


def select_job(job_frame, job, status ):
    if job == 'gs':
        job_frame.job_d = job_frame.controller.task.engine.gs
        job_frame.job_d['cal_check'] = status.check_status('gs_cal', 1)                       
        gs_check= status.check_status('gs_inp', 1)           
        if gs_check is True :
            job_frame.run_job('gs_cal', 1, 0)
        else:
            show_message(job_frame.msg_label1, job_frame.job_d["GS inputs not found"])

    if job == 'delta':
        job_frame.job_d = job_frame.controller.task.engine.td_delta 
        job_frame.job_d['cal_check'] = status.check_status('td_cal', 1)
        td_check = status.check_status('td_inp', 1) 
        gs_cal_check = status.check_status('gs_cal', 1)
        if td_check is True and gs_cal_check is True :
            job_frame.run_job('td_cal', 1, 0)                 
        else:
            if td_check is False:
                show_message(job_frame.msg_label1,"Inputs not found. Please create inputs for delta kick." ) 
            elif gs_cal_check is False:
                show_message(job_frame.msg_label1, "Inputs not found. Please run GS calculation.")   
                    
    if job == 'laser':
        job_frame.job_d = job_frame.controller.task.engine.laser
        print('laser start') 
        print(job_frame.job_d) 
        job_frame.job_d['cal_check'] = status.check_status('td_cal', 2)
        td_check = status.check_status('td_inp', 2)
        gs_cal_check = status.check_status('gs_cal', 1)
        if td_check is True and gs_cal_check is True:
            print(job_frame.job_d)
            print("laser calc")
            job_frame.run_job('td_cal', 2, 1)                  
        else:
            show_message(job_frame.msg_label1, "Inputs not found.") 

    if job == 'spec':
        job_frame.job_d = job_frame.controller.task.engine.spectra
        td_check = status.check_status('td_inp', 1)
        job_frame.job_d['cal_check'] = status.check_status('spectra', 1)
        td_cal_check = status.check_status('td_cal', 1) 
        if td_check is True and td_cal_check is True:
            job_frame.run_job('spectra', 1, 0)
        else:
            pass