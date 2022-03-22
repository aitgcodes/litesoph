from litesoph.Pre_Processing.laser_design import laser_design

class pre_proc:

    default_dict = {
        'task' : 'design',
        'design' :{
                'inval': 5, 
                'fwhm': 2.0,
                'tin': 0.0,
                   },

        'mask' : { 'Type': 'Plane',
                  'Plane' : {'Type':'Plane','Axis': 0,'x0' : 0.5},
                  'Sphere' : {'Type':'Sphere','Radius' : 0.0,'Centre' : [0.0,0.0,0.0]},
                  'Boundary' :'Smooth',
                  'Rsig' : 0.1              # sigma of error function 
                   }
                  }

def unpack(dict):
    
    if  dict['task'] == 'design':
        calc_dict = dict['design']
        l_design = laser_design(**calc_dict)
        return l_design    
    elif dict['task'] == 'masking':
        return dict['mask']
        
# def calltask(task,**task_dict,):
#     from laser_method import laser_design
#     if task == 'design':
#         laser = laser_design(**task_dict)
#     return(laser)

