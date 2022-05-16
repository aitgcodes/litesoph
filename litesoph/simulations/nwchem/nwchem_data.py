import pathlib

ground_state = {'inp':'nwchem/GS/gs.nwi',
            'out_log' : 'nwchem/GS/gs.nwo',
            'req' : ['coordinate.xyz', 'nwchem/restart'],
            'check_list':['Converged', 'Fermi level:','Total:']}

rt_tddft_delta = {'inp':'nwchem/TD_Delta/td.nwi',
        'out_log' : 'nwchem/TD_Delta/td.nwo',
        'req' : ['coordinate.xyz', 'nwchem/restart'],
        'check_list':['Converged', 'Fermi level:','Total:']}

rt_tddft_laser = {'inp':'nwchem/TD_Laser/tdlaser.nwi',
        'out_log' : 'nwchem/TD_Laser/tdlaser.nwo',
        'req' : ['coordinate.xyz', 'nwchem/restart'],
        'check_list':['Converged', 'Fermi level:','Total:']}

spectrum = {'inp':'nwchem/TD_Laser/tdlaser.nwi',
        'out_log' : 'nwchem/TD_Delta/td.nwo',
        'req' : ['nwchem/TD_Delta/td.nwo'],
        'spectra_file': ['nwchem/Spectrum/spec_x.dat','nwchem/Spectrum/spec_y.dat', 'nwchem/Spectrum/spec_z.dat' ],
        'spec_dir_path' : 'nwchem/Spectrum',
        'check_list':['Converged', 'Fermi level:','Total:']}

restart = 'nwchem/restart'

task_dirs =[('NwchemOptimisation', 'Opt'),
        ('NwchemGroundState', 'GS'),
        ('NwchemDeltaKick', 'TD_Delta'),
        ('NwchemGaussianPulse', 'TD_Laser')]
