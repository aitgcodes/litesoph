from litesoph.io.IO import write2file as write
from gpaw import GPAW

class ground_state:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    Engine_list = ['gpaw', 'nwchem', 'octupus']

    def __init__(self, user_input) -> None:
        self.user_input = user_input
        
        engine = self.decide_engine(self.user_input)
        print(engine)
        if engine == 'gpaw':
            from litesoph.simulations.GPAW.gpaw_template import ground_state_template as gt
            parameters = self.user2gpaw(self.user_input)
            print(parameters)
            directory = parameters['work_dir'] + '/gs.py'
            print(directory)
            write(directory,gt.gs_template, parameters)

            
    def decide_engine(self, user_input):
        """This function decides the engine from the user input dictionary."""
        
        if user_input['engine'] == 'gpaw':
            if user_input['mode'] not in ['fd', 'lcao', 'paw']:
                return 'This mode is not compatable with gpaw use fd, lcao or paw'
            engine = 'gpaw'
            return  engine
        elif user_input['engine'] == 'octopus':
            engine = 'octupus'
            return  engine
        elif user_input['engine'] == 'nwchem':
            engine = 'nwchem '
            return  engine
        elif user_input['engine'] is None:
            if user_input['basis'] == 'guassian':
                engine = 'nwchem'
                return engine
            engine = ''
            return engine
        else:
            return ValueError
            
    def user_para2engine_para(self, user_input, engine):
        """It converts user input parameter to engine specific parameters."""

        if engine == 'gpaw':
            pass
        elif engine == 'octupus':
            pass
        elif engine == 'nwchem':
            pass


    def user2gpaw(self, user_input):
        import os
        parameters = GPAW.default_parameters
        
        for key in user_input:
            if key not in ['tolerance','convergance','box'] and user_input[key] is not None:
                parameters[key] = user_input[key]
                         
            if key == 'work_dir' and user_input[key] is None:
                print('The project directory is not specified so the current directory will be taken as working directory')
                parameters.update(key = user_input['work_dir'][os.getcwd()])

            if key == 'geometry' and user_input[key] is None:
                return ValueError('The structure file is not found')
        return parameters