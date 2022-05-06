
import pathlib

ground_state = {'inp':'octopus/inp',
        'out_log': 'octopus/log',
        'req' : ['coordinate.xyz'],
        'check_list':['SCF converged']}

rt_tddft_delta = {'inp':'octopus/inp',
        'out_log': 'octopus/log',
            'req' : ['coordinate.xyz'],
            'check_list':['Finished writing information', 'Calculation ended']}    

rt_tddft_laser = {'inp':'octopus/inp',
        'out_log': 'octopus/log',
            'req' : ['coordinate.xyz']}

spectrum = {'inp':'octopus/inp',
        'out_log': 'octopus/log',
            'req' : ['coordinate.xyz'],
            'spectra_file': ['octopus/cross_section_vector']}


def get_task_class( task: str, user_param, project_name, status):

    from litesoph.simulations.octopus import octopus_template as ot
    
    if task == "ground_state":
        user_param['geometry']= str(pathlib.Path(project_name) / ground_state['req'][0])
        return ot.OctGroundState(user_param) 
    if task == "rt_tddft_delta":
        if status:
            gs_inp = status.get_status('ground_state.param')
            user_param.update(gs_inp)
        return ot.OctTimedependentState(user_param)
    if task == "rt_tddft_laser":
        if status:
            gs_inp = status.get_status('ground_state.param')
            user_param.update(gs_inp)
        return ot.OctTimedependentLaser(user_param)    
    if task == "spectrum":
        return ot.OctSpectrum(user_param)