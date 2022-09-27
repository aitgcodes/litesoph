def pre_condition_ground_state(status):

    return (True, 'yes')

def pre_condition_rt_tddft_delta(status):

    try:
        if status.get('gpaw.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with delta pulse.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with delta pulse.')

def pre_condition_rt_tddft_laser(status):

    try:
        if status.get('gpaw.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with Laser.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with Laser.')

def pre_condition_spectrum(status):

    try:
        if status.get('gpaw.rt_tddft_delta.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform RT-TDDFT delta pulse calculation before proceeding to Spectrum.')
    except KeyError:
        return (False, 'Please perform RT-TDDFT delta pulse calculation before proceeding to Spectrum.')

def pre_condition_tcm(status):

    try:
        if status.get('gpaw.ground_state.done') and 'wavefunction' in status.get('gpaw.rt_tddft_delta.param.analysis_tools'):
            return(True, 'yes')
        else:
            return (False, 'Please perform RT-TDDFT delta pulse calculation with Kohn-Sham decomposition option before proceeding to KSD.')
    except KeyError:
        return (False, 'Please perform RT-TDDFT delta pulse calculation with Kohn-Sham decomposition option before proceeding to KSD .')