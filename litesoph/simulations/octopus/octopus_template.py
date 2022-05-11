from pathlib import Path
from typing import Any, Dict
from litesoph.utilities.units import ang_to_au, au_to_as, as_to_au

from litesoph.simulations.octopus import octopus_data
from litesoph.simulations.esmd import Task

class OctGroundState(Task):

    task_data = octopus_data.ground_state
    task_name = 'ground_state'
    NAME = 'inp'

    default_param = {
            'work_dir' : ".",         # default 
            'scratch' : 'yes',
            'exp' : "no",
            'calc_mode':'gs',         # default calc mode
            'out_unit':'ev_angstrom', # default output unit
            'name':'H',               # name of species
            'geometry' : "coordinate.xyz",       
            'dimension' : 3, 
            'theory':'dft' ,          # "DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"
            
            'pseudo': 'pseudodojo_pbe', # else 'file|pseudo potential filename'
            'mass' : 1.0,             # mass of species in atomic unit
            'box':{'shape':'minimum','radius':4.0,'xlength':0.0, 'sizex':0.0, 'sizey':0.0, 'sizez':0.0},
            'spacing': 0.23,           # spacing between points in the mesh
            'spin_pol': 'unpolarized',
            'charge': 0.0,
            'e_conv' : 0.0,
            'max_iter' : 200,

            'eigensolver' :'cg',      #["rmmdiis","plan","arpack","feast","psd","cg","cg_new","lobpcg","evolution"]
            'mixing' : 0.3,             # 0<mixing<=1
            'conv_reldens' : 1e-6,      # SCF calculation
            'smearing_func' :'semiconducting',
            'smearing' : 0.1   ,       # in eV
            'unit_box' : 'angstrom',
            'atoms': ['C', 'H'],
            'xc':{'option': 1, 'x':"", 'c':"", 'xc':""}
            } 

    gs_min = """
WorkDir = '{work_dir}'    
FromScratch = {scratch}  
ExperimentalFeatures = {exp}              
CalculationMode = gs
Dimensions = {dimension} 
TheoryLevel = {theory}
Unitsoutput = {out_unit}       
XYZCoordinates = '{geometry}'
BoxShape = {box[shape]}
Radius = {box[radius]}


Spacing = {spacing}*angstrom
SpinComponents = {spin_pol}
ExcessCharge = {charge}
Mixing = {mixing}
MaximumIter = {max_iter}
Eigensolver = {eigensolver}
Smearing = {smearing}
SmearingFunction = {smearing_func}
ConvRelDens = {conv_reldens}
ConvEnergy = {e_conv}
PseudopotentialSet = {pseudo}
    """
    
    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = user_input
        self.temp_dict = self.default_param 
        self.temp_dict['geometry']= str(Path(project_dir.name) / self.task_data['req'][0])
        self.temp_dict.update(self.user_input)
        # self.temp_dict = self.default_param
        # self.temp_dict.update(user_input)
        self.boxshape = self.temp_dict['box']['shape'] 
        self.xc_option = self.temp_dict['xc']['option']
        # self.atoms_list = self.temp_dict['atoms']
        self.pseudo = self.temp_dict['pseudo']
        self.check_unit()           
    
    def check_unit(self):
        if self.temp_dict['unit_box'] == "angstrom":
            box_dict = self.temp_dict['box']
            if self.boxshape not in ['cylinder', 'parallelepiped']:
                box_dict['radius'] = round(box_dict['radius']*ang_to_au, 2)
            elif self.boxshape == "cylinder":
                box_dict['radius'] = round(box_dict['radius']*ang_to_au, 2)
                box_dict['xlength'] = round(box_dict['xlength']*ang_to_au, 2)
            elif self.boxshape == "parallelepiped":
                box_dict['sizex'] = round(box_dict['sizex']*ang_to_au, 2) 
                box_dict['sizey'] = round(box_dict['sizey']*ang_to_au, 2)
                box_dict['sizez'] = round(box_dict['sizez']*ang_to_au, 2)        

    def add_boxshape_template(self):
        if self.boxshape not in ['cylinder', 'parallelepiped']: 
            template = self.gs_min.format(**self.temp_dict)
            return template 

        elif self.boxshape == "cylinder":
            tlines = self.gs_min.splitlines()
            tlines[11] = "Xlength = {box[xlength]}"
            temp = """\n""".join(tlines)
            template = temp.format(**self.temp_dict)
            return template

        elif self.boxshape == "parallelepiped":
            tlines = self.gs_min.splitlines()
            lx = round(self.temp_dict['box']['sizex']/2, 2)
            ly = round(self.temp_dict['box']['sizey']/2, 2)
            lz = round(self.temp_dict['box']['sizez']/2, 2)
            tlines[10] = "%LSize"
            tlines[11] = "{}|{}|{}".format(lx, ly, lz)
            tlines[12] = "%"
            temp = """\n""".join(tlines)
            template = temp.format(**self.temp_dict)
            return template 

    def add_xc_template(self):
        if self.xc_option == 1:
            xc_line = "XCFunctional = {}+{}".format(self.temp_dict['xc']['x'],self.temp_dict['xc']['c'])
        elif self.xc_option == 2:
            xc_line = "XCFunctional = {}".format(self.temp_dict['xc']['xc'])    
        return(xc_line)

    def add_pseudo_potential_template(self):
        import numpy
        x = numpy.array(self.atoms_list)
        atoms = numpy.unique(x)
        temp = ""
        for atom in numpy.nditer(atoms): 
            temp1 = " '{}' | species_pseudo | set | {}".format(atom, self.pseudo) 
            temp = '\n'.join([temp,temp1])
        
        temp1 = "%Species" 
        temp2 = "%"
    
        template = '\n'.join([temp1,temp,temp2])
        return(template)        
   
    def create_template(self):
        temp1 = self.add_boxshape_template()
        temp2 = self.add_xc_template()
        # temp2 = self.add_pseudo_potential_template()
        self.template = "\n".join([temp1, temp2])
        # print(template)
        
    def create_local_cmd(self, *args):
        return self.engine.create_command(*args)

    @staticmethod
    def get_network_job_cmd(np):
        job_script = f"""
##### LITESOPH Appended Comands###########
cd Octopus/
mpirun -np {np:d}  <Full Path of Octopus>/octopus > log
#mpirun -np {np:d}  /opt/apps/octopus/7.2/intel/bin/octopus > log\n"""
        return job_script
    # def format_template(self):
    #     if self.boxshape not in ['cylinder', 'parallelepiped']: 
    #         template = self.gs_min.format(**self.temp_dict)
    #         return template 

    #     elif self.boxshape == "cylinder":
    #         tlines = self.gs_min.splitlines()
    #         tlines[10] = "Xlength = {box[xlength]}"
    #         temp = """\n""".join(tlines)
    #         template = temp.format(**self.temp_dict)
    #         return template

    #     elif self.boxshape == "parallelepiped":
    #         tlines = self.gs_min.splitlines()
    #         lx = round(self.temp_dict['box']['sizex']/2, 2)
    #         ly = round(self.temp_dict['box']['sizey']/2, 2)
    #         lz = round(self.temp_dict['box']['sizez']/2, 2)
    #         tlines[9] = "%LSize"
    #         tlines[10] = "{}|{}|{}".format(lx, ly, lz)
    #         tlines[11] = "%"
    #         temp = """\n""".join(tlines)
    #         template = temp.format(**self.temp_dict)
    #         return template    

        
class OctTimedependentState(Task):

    task_data = octopus_data.rt_tddft_delta
    task_name = 'rt_tddft_delta'
    NAME = 'inp'

    default_param = {
            'work_dir' : ".",         # default 
            'scratch' : 'yes',
            'calc_mode':'gs',         # default calc mode
            'out_unit':'ev_angstrom', # default output unit
            'name':'H',               # name of species
            'geometry' : "coordinate.xyz",       
            'dimension' : 3, 
            'theory':'DFT' ,          # "DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"
            'pseudo_potential':'set|standard', # else 'file|pseudo potential filename'
            'mass' : 1.0,             # mass of species in atomic unit
            'box':{'shape':'minimum','radius':1.0,'xlength':0.0, 'sizex':0.0, 'sizey':0.0, 'sizez':0.0},
            'spacing': 0.0,           # spacing between points in the mesh
            'spin_pol': 'unpolarized',
            'charge': 0.0,
            'e_conv' : 0.0,
            'max_iter' : 200,


            'eigensolver' :'cg',      #["rmmdiis","plan","arpack","feast","psd","cg","cg_new","lobpcg","evolution"]
            'mixing' : {},
            'conv_reldens' : {},      # SCF calculation
            'smearing_func' : {},
            'smearing' : {},

            'max_step' : 200 ,            
            'time_step' : 0.002,      
            'td_propagator' : 'aetrs',
            'strength': {},
            'e_pol': [1,0,0]             
            }

    td = """
WorkDir = '.'    
FromScratch = yes               
CalculationMode = td
Dimensions = {dimension} 

Unitsoutput = ev_angstrom       
XYZCoordinates = '{geometry}'
BoxShape = {box[shape]}
Radius = {box[radius]}


Spacing = {spacing}*angstrom

TDPropagator = {td_propagator}
TDMaxSteps = {max_step}
TDTimeStep = {time_step}

TDDeltaStrength = {strength}


"""         

    tlines_pol = """
%TDPolarization
 {e_pol[0]} | {e_pol[1]} | {e_pol[2]}
 0 | 1 | 0
 0 | 0 | 1
%
TDPolarizationDirection = 1
"""
   

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = user_input
        self.temp_dict = self.default_param 
        self.temp_dict['geometry']= str(Path(project_dir.name) / self.task_data['req'][0])
        self.temp_dict.update(status.get_status('ground_state.param'))
        self.temp_dict.update(user_input)
        self.boxshape = self.temp_dict['box']['shape']         
        self.e_pol = self.temp_dict['e_pol']
        self.check_pol()
        self.convert_unit()

    def convert_unit(self):
        self.temp_dict['time_step'] = round(self.temp_dict['time_step']*as_to_au, 2)  
    
    def check_pol(self):
        if self.e_pol == [1,0,0]:
            self.temp_dict['e_dir'] = 1
        elif self.e_pol == [0,1,0]:
            self.temp_dict['e_dir'] = 2 
        elif self.e_pol == [0,0,1]:
            self.temp_dict['e_dir'] = 3
        else:
            self.temp_dict['e_dir'] = 0
            
    def format_pol(self):
        if self.temp_dict['e_dir'] in [1,2,3]:
            tlines = self.td.splitlines()
            tlines[19] = "TDPolarizationDirection = {e_dir}"
            temp = """\n""".join(tlines)
            return temp

        elif self.temp_dict['e_dir'] == 0:
            temp = "".join([self.td, self.tlines_pol])
            return temp

    def format_box(self):
        if self.boxshape not in ['cylinder', 'parallelepiped']: 
            return self.td

        elif self.boxshape == "cylinder":
            tlines = self.td.splitlines()
            tlines[10] = "Xlength = {box[xlength]}"
            temp = """\n""".join(tlines)
            return temp

        elif self.boxshape == "parallelepiped":
            tlines = self.td.splitlines()
            lx = round(self.temp_dict['box']['sizex']/2, 2)
            ly = round(self.temp_dict['box']['sizey']/2, 2)
            lz = round(self.temp_dict['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{}|{}|{}".format(lx, ly, lz)
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            return temp
    
    @staticmethod
    def get_network_job_cmd(np):
        job_script = f"""
##### LITESOPH Appended Comands###########
cd Octopus/
mpirun -np {np:d}  <Full Path of Octopus>/octopus > log
#mpirun -np {np:d}  /opt/apps/octopus/7.2/intel/bin/octopus > log\n"""
        return job_script

    def create_local_cmd(self, *args):
        return self.engine.create_command(*args)

    def create_template(self):
        self.td = self.format_box() 
        temp = self.format_pol()
        self.template = temp.format(**self.temp_dict)
        

class OctTimedependentLaser(Task):

    task_data = octopus_data.rt_tddft_laser
    task_name = 'rt_tddft_laser'
    NAME = 'inp'

    default_param = {
            'max_step' : 200 ,            
            'time_step' : 0.002,      
            'td_propagator' : 'aetrs',
            'strength': None,
            'e_pol': [1,0,0],
            'time0':None,
            'frequency': None,
            'sigma': None,
            'sincos':'sin',
            'envelope':'tdf_gaussian'  
    }

    td = """
WorkDir = '.'    
FromScratch = yes               
CalculationMode = td
Dimensions = {dimension} 

Unitsoutput = ev_angstrom       
XYZCoordinates = '{geometry}'
BoxShape = {box[shape]}
Radius = {box[radius]}


Spacing = {spacing}*angstrom

TDPropagator = {td_propagator}
TDMaxSteps = {max_step}
TDTimeStep = {time_step}

omega = {frequency}*eV

%TDExternalFields
 electric_field | {e_pol[0]} | {e_pol[1]} | {e_pol[2]} | omega | "envelope_gauss"
%

%TDFunctions
 "envelope_gauss" | {envelope} | {strength} | {sigma} | {time0}
%

""" 

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = user_input
        self.temp_dict = self.default_param
        self.temp_dict['geometry']= str(Path(project_dir.name) / self.task_data['req'][0])
        self.temp_dict.update(status.get_status('ground_state.param'))
        self.temp_dict.update(user_input)
        self.boxshape = self.temp_dict['box']['shape']         
        self.convert_unit()

    def convert_unit(self):
        self.temp_dict['time_step'] = round(self.temp_dict['time_step']*as_to_au, 2)
    
    def format_box(self):
        if self.boxshape not in ['cylinder', 'parallelepiped']: 
            return self.td

        elif self.boxshape == "cylinder":
            tlines = self.td.splitlines()
            tlines[10] = "Xlength = {box[xlength]}"
            temp = """\n""".join(tlines)
            return temp

        elif self.boxshape == "parallelepiped":
            tlines = self.td.splitlines()
            self.temp_dict['box']['sizex'] = round(self.temp_dict['box']['sizex']/2, 2)
            self.temp_dict['box']['sizey'] = round(self.temp_dict['box']['sizey']/2, 2)
            self.temp_dict['box']['sizez'] = round(self.temp_dict['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            return temp
    
    @staticmethod
    def get_network_job_cmd(np):
        job_script = f"""
##### LITESOPH Appended Comands###########
cd Octopus/
mpirun -np {np:d}  <Full Path of Octopus>/octopus > log
#mpirun -np {np:d} /opt/apps/octopus/7.2/intel/bin/octopus > log\n"""
        return job_script
  
    def create_local_cmd(self, *args):
        return self.engine.create_command(*args)

    def create_template(self):
        self.td = self.format_box() 
        #temp = self.format_pol()
        self.template = self.td.format(**self.temp_dict)
        

# class OctSpectrum:

#     NAME = 'inp'

#     spec = """  
# UnitsOutput = eV_angstrom
# """  

#     def __init__(self):
#         pass

#     def format_template(self):        
#         #template = self.td.format(**self.temp_dict)
#         template = self.spec
#         return(templ

class OctSpectrum(Task):

    task_data = octopus_data.spectrum
    task_name = 'spectrum'
    NAME = 'inp'

    default_param ={
        'e_min' : 0.0,
        'e_max'  : 30.0,
        'del_e'  : 0.05
    }

    spec = """  
UnitsOutput = eV_angstrom
PropagationSpectrumMinEnergy  =    {e_min}*eV
PropagationSpectrumMaxEnergy  =    {e_max}*eV
PropagationSpectrumEnergyStep =    {del_e}*eV
"""  

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = user_input
        self.temp_dict = self.default_param       
        self.temp_dict.update(user_input)
       

    def get_network_job_cmd(self,np):
        job_script = f"""
##### LITESOPH Appended Comands###########

mpirun -np {np:d}  <Full Path of Octopus>/oct-propagation_spectrum 

#mpirun -np {np:d}  /opt/apps/octopus/7.2/intel/bin/oct-propagation_spectrum\n"""  
        return job_script

    def create_local_cmd(self, *args):

        file = 'log'
        command = self.lsconfig.get('engine', 'octopus')
        cmd = 'oct-propagation_spectrum'
        if not command:
            command =  cmd
        else:
            command = Path(command).parent / cmd

        command = str(command) + ' ' + '>' + ' ' + str(file)
        return command

    # @staticmethod
    # def get_local_cmd():
    #     return 'oct-propagation_spectrum'

    def create_template(self):        
        #template = self.td.format(**self.temp_dict)
        self.template = self.spec.format(**self.temp_dict)
    
    def prepare_input(self):
        self.create_template()
        self.write_input()

    def plot_spectrum(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        pol =  self.status.get_status('rt_tddft_delta.param.pol_dir')
        spec_file = self.task_data['spectra_file'][pol[0]]
        file = Path(self.project_dir) / spec_file
        img = file.parent / f"spec_{pol[1]}.png"
        plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")