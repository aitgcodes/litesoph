
import pathlib

engine_dir = 'octopus'

engine_log_dir = f'{engine_dir}/log'

general_input_file = f'{engine_dir}/inp'

unoccupied_task = {'out_log':f'{engine_log_dir}/unocc.log'}
ground_state = {'inp':general_input_file,
        'out_log': f'{engine_log_dir}/gs.log',
        'req' : ['coordinate.xyz'],
        'check_list':['SCF converged']}

rt_tddft_delta = {'inp':general_input_file,
        'out_log': f'{engine_log_dir}/delta.log',
            'req' : ['coordinate.xyz'],
            'check_list':['Finished writing information', 'Calculation ended']}    

rt_tddft_laser = {'inp':general_input_file,
            'out_log': f'{engine_log_dir}/laser.log',
            'req' : ['coordinate.xyz']}

spectrum = {'inp':general_input_file,
        'out_log': f'{engine_log_dir}/spec.log',
            'req' : ['coordinate.xyz'],
            'spectra_file': [f'{engine_dir}/cross_section_vector']}

ksd = {'inp': f'{engine_dir}/ksd/oct.inp',
        'req':[f'{engine_dir}/static/info',
        f'{engine_dir}/td.general/projections'],
        'ksd_file': f'{engine_dir}/ksd/transwt.dat'}            

