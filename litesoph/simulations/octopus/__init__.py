def pre_condition_ground_state(status):

    return (True, 'yes')

def pre_condition_rt_tddft_delta(status):

    try:
        if status.get_status('octopus.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with delta pulse.')


def pre_condition_rt_tddft_laser(status):

    try:
        if status.get_status('octopus.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with laser pulse.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics with laser pulse.')

def pre_condition_spectrum(status):

    try:
        if status.get_status('octopus.rt_tddft_delta.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform Electron Dynamics with delta pulse calculation before proceeding to spectrum.')
    except KeyError:
        return (False, 'Please perform Electron Dynamics with delta pulse calculation before proceeding to spectrum.')

def pre_condition_tcm(status):

    try:
        if status.get_status('octopus.ground_state.done') and ['td_occup'] in status.get_status('octopus.rt_tddft_delta.param.TDOutput'):
            return(True, 'yes')
        else:
            return (False, 'Please perform RT-TDDFT delta pulse calculation with Kohn-Sham decomposition option before proceeding to KSD.')
    except KeyError:
        return (False, 'Please perform RT-TDDFT delta pulse calculation with Kohn-Sham decomposition option before proceeding to KSD .')
   