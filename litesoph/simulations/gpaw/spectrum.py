class spectrum:
    """This class contains the gpaw template for getting spectrum
    from dipole moment."""
    
    user_input = {
        'moment_file':None,
        'spectrum_file':None,
        'folding':'Gauss',
        'width':0.2123,
        'e_min':0.0,
        'e_max':30.0,
        'delta_e':0.05 
        }

    def cal_photoabs_spectrum(self, user_input):

        from gpaw.tddft.spectrum import photoabsorption_spectrum
        photoabsorption_spectrum(user_input['moment_file'], user_input['spectrum_file'],
                        folding=user_input['folding'], width=user_input['width'],
                        e_min=user_input['e_min'], e_max=user_input['e_max'], delta_e=user_input['delta_e'])

    def cal_polarizability_spectrum(self, user_input):

        from gpaw.tddft.spectrum import polarizability_spectrum
        polarizability_spectrum(user_input['moment_file'], user_input['spectrum_file'],
                        folding=user_input['folding'], width=user_input['width'],
                        e_min=user_input['e_min'], e_max=user_input['e_max'], delta_e=user_input['delta_e'])

    def cal_rotatory_strength_spectrum(self, user_input):

        from gpaw.tddft.spectrum import rotatory_strength_spectrum
        rotatory_strength_spectrum(user_input['moment_file'], user_input['spectrum_file'],
                        folding=user_input['folding'], width=user_input['width'],
                        e_min=user_input['e_min'], e_max=user_input['e_max'], delta_e=user_input['delta_e'])
