
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
