def pre_condition_ground_state(status):

    return (True, 'yes')

def pre_condition_rt_tddft_delta(status):

    try:
        if status.get('nwchem.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics.')

def pre_condition_rt_tddft_laser(status):

    try:
        if status.get('nwchem.ground_state.done'):
            return (True, 'yes')
        else:
            return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics.')
    except KeyError:
        return (False, 'Please perform ground state calculation before proceeding to Electron Dynamics.')

def pre_condition_spectrum(status):

    try:
        if status.get('nwchem.rt_tddft_delta.done'):
            return (True, 'yes')
        else:
           return (False, 'Please perform Electron Dynamics delta pulse calculation before proceeding to Spectrum.')
    except KeyError:
        return (False, 'Please perform Electron Dynamics delta pulse calculation before proceeding to Spectrum.')


def pre_condition_tcm(status):

   return (False, 'Kohn-Sham is not implemented for NWChem')