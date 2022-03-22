from litesoph.simulations.esmd import Task
from litesoph.simulations.gpaw.gpaw_template import GpawRTLCAOTddftDelta



class RTSpecRecipe:

    def __init__(self, status, directory, input_dict:dict) -> None:
        self.status = status
        self.directory = directory
        self.input_dict = input_dict
        self.gs_data = None
        self.directions = self.input_dict.popitem['direction']
        if not self.directions:
            self.directions = [[1,0,0],[0,1,0],[0,0,1]]

    def create_templates(self):
        self.task = GpawRTLCAOTddftDelta(self.input_dict)
        self.template = self.task.format_template() 









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
