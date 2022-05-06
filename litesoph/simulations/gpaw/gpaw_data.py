
import pathlib

ground_state = {'inp':'gpaw/GS/gs.py',
            'req' : ['coordinate.xyz'],
            'out_log': 'gpaw/GS/gs.out',
            'restart': 'gpaw/GS/gs.gpw',
            'check_list':['Converged', 'Fermi level:','Total:']}

rt_tddft_delta = {'inp':'gpaw/TD_Delta/td.py',
        'req' : ['gpaw/GS/gs.gpw'],
        'out_log': 'gpaw/TD_Delta/tdx.out',
        'restart': 'gpaw/TD_Delta/td.gpw',
        'check_list':['Writing','Total:']}

rt_tddft_laser = {'inp':'gpaw/TD_Laser/tdlaser.py',
        'req' : ['gpaw/GS/gs.gpw'],
        'out_log': 'gpaw/TD_Laser/tdlaser.out',
        'restart': 'gpaw/TD_Laser/tdlaser.gpw',
        'check_list':['Writing','Total:']}

spectrum = {'inp':'gpaw/Spectrum/spec.py',
        'req' : ['gpaw/TD_Delta/dm.dat'],
        'out_log': 'gpaw/Spectrum/spec.dat',
        'restart': 'gpaw/TD_Delta/dm.dat',
        'check_list':['FWHM'],
        'spectra_file': ['gpaw/Spectrum/spec_x.dat','gpaw/Spectrum/spec_y.dat', 'gpaw/Spectrum/spec_z.dat' ]}

tcm = {'inp':'gpaw/TCM/tcm.py',
        'req' : ['gpaw/GS/gs.gpw','gpaw/TD_Delta/wf.ulm'],
        'out_log': 'gpaw/TCM/unocc.out',
        'restart': '',
        'check_list':['Writing','Total:']}

task_dirs =[('GpawGroundState', 'GS'),
            ('GpawRTLCAOTddftDelta', 'TD_Delta'),
            ('GpawRTLCAOTddftLaser', 'TD_Laser'),
            ('GpawSpectrum', 'Spectrum'),
            ('GpawCalTCM', 'TCM')]


def get_task_class(task: str, user_param, project_name,status, *_):

    from litesoph.simulations.gpaw import gpaw_template as gp

    if task == "ground_state":
        user_param['geometry']= str(pathlib.Path(project_name) / ground_state['req'][0])
        return gp.GpawGroundState(user_param) 
    if task == "rt_tddft_delta":
        user_param['gfilename']= str(pathlib.Path(project_name)  / rt_tddft_delta['req'][0])
        return gp.GpawRTLCAOTddftDelta(user_param)
    if task == "rt_tddft_laser":
        user_param['gfilename']= str(pathlib.Path(project_name)  / rt_tddft_laser['req'][0])
        return gp.GpawRTLCAOTddftLaser(user_param)
    if task == "spectrum":
        pol =  status.get_status('rt_tddft_delta.param.pol_dir')
        user_param['spectrum_file'] = f'spec_{str(pol[1])}.dat'
        user_param['moment_file']= str(pathlib.Path(project_name) / spectrum['req'][0])
        return gp.GpawSpectrum(user_param) 
    if task == "tcm":
        user_param['gfilename']= str(pathlib.Path(project_name)  / tcm['req'][0])
        user_param['wfilename']= str(pathlib.Path(project_name)  / tcm['req'][1])
        return gp.GpawCalTCM(user_param)   