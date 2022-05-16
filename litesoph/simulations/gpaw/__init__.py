def pre_condition_ground_state(status):

    return (True, 'yes')
    
def pre_condition_rt_tddft_delta(status):

    if status.get_status('gpaw.ground_state.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform ground state calculation.')

def pre_condition_rt_tddft_laser(status):

    if status.get_status('gpaw.ground_state.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform ground state calculation.')

def pre_condition_spectrum(status):

    if status.get_status('gpaw.rt_tddft_delta.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform RT-TDDFT delta pulse calculation.')

def pre_condition_tcm(status):

    if status.get_status('gpaw.ground_state.done') and 'wavefunction' in status.get_status('gpaw.rt_tddft_delta.param.analysis_tools'):
        return(True, 'yes')
    else:
        return (False, 'Please perform RT-TDDFT delta pulse calculation with Kohn-Sham decomposition option.')