
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

ksd = {'inp': 'octopus/Post_Processing/inp',
        'req':['octopus/static/info',
        'octopus/td.general/projections']}            

