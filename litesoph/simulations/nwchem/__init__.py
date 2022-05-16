def pre_condition_ground_state(status):

    return (True, 'yes')

def pre_condition_rt_tddft_delta(status):

    if status.get_status('nwchem.ground_state.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform ground state calculation.')

def pre_condition_rt_tddft_laser(status):

    if status.get_status('nwchem.ground_state.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform ground state calculation.')

def pre_condition_spectrum(status):

    if status.get_status('nwchem.rt_tddft_delta.done'):
        return (True, 'yes')
    else:
        return (False, 'Please perform RT-TDDFT delta pulse calculation.')

def pre_condition_tcm(status):

   return (False, 'Task not implemented')