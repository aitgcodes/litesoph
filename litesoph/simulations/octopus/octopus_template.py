from pathlib import Path
from typing import Any, Dict
import copy

from litesoph.utilities.units import ang_to_au, au_to_as, as_to_au
from litesoph.simulations.octopus import octopus_data
from litesoph.simulations.esmd import Task
from litesoph import config

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
            'theory':'kohn_sham' ,          # "DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"
            
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
            'extra_states' : 0,
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
ExtraStates = {extra_states}
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
        

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
      
        job_script = super().create_job_script()
        ofilename = Path(self.task_data['out_log']).relative_to('octopus')
        unocc_ofilename = Path(octopus_data.unoccupied_task['out_log']).relative_to('octopus')
        extra_cmd = ["cp inp gs.inp","perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp"]
        if remote:
            cmd = f"mpirun -np {np:d}  octopus > {str(ofilename)}"
            rpath = Path(remote_path) / self.project_dir.name / 'octopus'
            job_script.append(self.engine.get_engine_network_job_cmd())
            job_script.append(f"cd {str(rpath)}")
            job_script.append(cmd)
            if self.user_input['extra_states'] != 0:
                job_script.extend(extra_cmd)
                job_script.append(f"mpirun -np {np:d}  octopus > {str(unocc_ofilename)}")
        else:
            lpath = self.project_dir / 'octopus'
            job_script.append(f"cd {str(lpath)}")

            path_octopus = self.lsconfig.get('engine', 'octopus')
            if not path_octopus:
                path_octopus = 'octopus'
            command = path_octopus + ' ' + '>' + ' '
            if np > 1:
                cmd_mpi = config.get_mpi_command('octopus', self.lsconfig)
                command = cmd_mpi + ' ' + '-np' + ' ' + str(np) + ' ' + command
            job_script.append(command + str(ofilename))
            if self.user_input['extra_states'] != 0:
                job_script.extend(extra_cmd)
                job_script.append(command + str(unocc_ofilename))
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
    
        
class OctTimedependentState(Task):

    task_data = octopus_data.rt_tddft_delta
    task_name = 'rt_tddft_delta'
    NAME = 'inp'
    engine_log = str(Path(task_data['out_log']).relative_to('octopus'))

    default_param = {
            'work_dir' : ".",         # default 
            'scratch' : 'yes',
            'calc_mode':'gs',         # default calc mode
            'out_unit':'ev_angstrom', # default output unit
            'expt_feature': 'no',
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
            'extra_states' : {},

            'max_step' : 200 ,            
            'time_step' : 0.002,      
            'td_propagator' : 'aetrs',
            'strength': {},
            'e_pol': [1,0,0],
            'pol_block': [[1,0,0],[0,1,0],[0,0,1]],

            'analysis_tools': ['default'],
            'output_freq': 50 ,
            'par_states' : 'auto'          
            }

    property_dict = {
                    "default": ["energy", "multipoles"],
                    "ksd": ["td_occup"],
                    "population_correlation": []
                    }

    td_output = [("energy", "no"),
                ("multipoles", "no"),
                ("td_occup", "yes")
                ]                

    td = """
WorkDir = '.'    
FromScratch = yes               
CalculationMode = td
Dimensions = {dimension} 
ExperimentalFeatures = {expt_feature}    
Unitsoutput = ev_angstrom       
XYZCoordinates = '{geometry}'
BoxShape = {box[shape]}
Radius = {box[radius]}


Spacing = {spacing}*angstrom
ExtraStates = {extra_states}
TDPropagator = {td_propagator}
TDMaxSteps = {max_step}
TDTimeStep = {time_step}

TDDeltaStrength = {strength}
"""         

    tlines_pol = """
%TDPolarization
 {pol_block[0][0]} | {pol_block[0][1]} | {pol_block[0][2]}
 {pol_block[1][0]} | {pol_block[1][1]} | {pol_block[1][2]}
 {pol_block[2][0]} | {pol_block[2][1]} | {pol_block[2][2]}
%
TDPolarizationDirection = {e_dir}
"""
   

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = user_input
        self.temp_dict = copy.deepcopy(self.default_param)
        self.temp_dict['geometry']= str(Path(project_dir.name) / self.task_data['req'][0])
        self.temp_dict.update(status.get_status('octopus.ground_state.param'))
        self.temp_dict.update(user_input)
        self.initialise_input()

    def initialise_input(self):
        
        self.boxshape = self.temp_dict['box']['shape']         
        self.e_pol = self.temp_dict['e_pol']
        added_property = self.temp_dict['analysis_tools']
        self.convert_unit()
        self.check_pol()
        self.format_pol_block()
        self.property_list = ['default']
        for prop in added_property:            
            self.property_list.append(prop)
        self.td_out_list = self.get_td_output()  
        self.check_property_dependency(self.td_out_list)   

    def convert_unit(self):
        self.temp_dict['time_step'] = round(self.temp_dict['time_step']*as_to_au, 2)  
    
    def check_pol(self):
        if self.e_pol == [1,0,0]:
            self.dir_var = 1
        elif self.e_pol == [0,1,0]:
            self.dir_var = 2
        elif self.e_pol == [0,0,1]:
            self.dir_var = 3
        else:
            self.dir_var = 0

    def format_pol_block(self):
        if self.dir_var in [1,2,3]:
            self.temp_dict['e_dir'] = self.dir_var
            self.temp_dict['pol_block'] = self.default_param['pol_block']
            
        elif self.dir_var == 0:
            self.temp_dict['e_dir'] = 1
            self.temp_dict['pol_block'][0] = self.e_pol


    # def format_pol(self):
    #     if self.temp_dict['e_dir'] in [1,2,3]:
           
    #         tlines = self.td.splitlines()
    #         tlines[19] = "TDPolarizationDirection = {e_dir}"
    #         temp = """\n""".join(tlines)
    #         return temp

    #     elif self.temp_dict['e_dir'] == 0:
    #         temp = "".join([self.td, self.tlines_pol])
    #         return temp

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

    def check_property_dependency(self, property_list:list):
        """ Checks property dependency w/ ExptFeatures option"""

        for property in property_list:
            expt = self.get_dependent_features(property)   
            if expt == 'yes':
                value = expt
                break
            else:
                value = 'no'
        self.temp_dict['expt_feature'] = value

        for property in property_list:
            if property == 'td_occup':
                self.temp_dict['par_states'] = 'no'      
                
    def get_dependent_features(self, property_name):
        """Returns the dependent features corresponding to the property"""
        
        for item in self.td_output:
            if item[0] == property_name:
                return item[1] 

    def get_td_output(self):
        """Selects and returns the td_output & expt_features to be added as a list"""

        td_output_list = []

        for item in self.property_list:
            if item in self.property_dict.keys():            
                _list = self.property_dict[item]

                for property in _list:
                    td_output_list.append(property)

        return td_output_list

    def format_td_output_lines(self):
        """ Adds TDOutput keywords and returns the template"""

        line1 = "%TDOutput"
        property_temp = ""
        for prop in self.td_out_list:
            property_temp = "\n ".join([property_temp,prop])
            line2 = "%"
            td_block = "\n".join([line1, property_temp, line2]) 

        td_line = f"""
TDOutputComputeInterval = {self.temp_dict['output_freq']}
ParStates = {self.temp_dict['par_states']}"""
        td_out_temp = "\n".join([td_block, td_line])

        return td_out_temp

    # def create_template(self):
    #     self.td = self.format_box() 
    #     temp = self.format_pol()
    #     self.template = temp.format(**self.temp_dict)    

    def create_template(self):
        
        self.td = self.format_box()
        _temp = self.tlines_pol 
        # _temp = self.format_pol()
        td_temp = self.format_td_output_lines()
        temp = "\n".join([self.td,_temp, td_temp])

        self.template = temp.format(**self.temp_dict)
               
    
    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / 'octopus'
            job_script = self.engine.create_command(job_script, np, self.engine_log,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / 'octopus'
            job_script = self.engine.create_command(job_script, np, self.engine_log,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
    

class OctTimedependentLaser(Task):

    task_data = octopus_data.rt_tddft_laser
    task_name = 'rt_tddft_laser'
    NAME = 'inp'
    engine_log = str(Path(task_data['out_log']).relative_to('octopus'))

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
        self.temp_dict.update(status.get_status('octopus.ground_state.param'))
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

    def create_template(self):
        self.td = self.format_box() 
        self.template = self.td.format(**self.temp_dict)

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / 'octopus'
            job_script = self.engine.create_command(job_script, np, self.engine_log,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / 'octopus'
            job_script = self.engine.create_command(job_script, np, self.engine_log,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
    
        

class OctSpectrum(Task):

    task_data = octopus_data.spectrum
    task_name = 'spectrum'
    NAME = 'inp'
    engine_log = str(Path(task_data['out_log']).relative_to('octopus'))

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
       

    def create_cmd(self, remote=False):

        cmd = 'oct-propagation_spectrum'
        path_oct = self.lsconfig.get('engine', 'octopus')
        if remote :
            command = cmd + ' ' + '>' + ' ' + str(self.engine_log)
        else:
            if path_oct:
                cmd = Path(path_oct).parent / cmd

            command = str(cmd) + ' ' + '>' + ' ' + str(self.engine_log)
        return command


    def create_template(self):        
        self.template = self.spec.format(**self.temp_dict)
    
    def prepare_input(self):
        self.create_template()
        self.write_input()

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        path = self.project_dir / "octopus"
        if remote_path:
            path = Path(remote_path) / self.project_dir.name / "octopus"
           
        job_script.append(f"cd {str(path)}")
        job_script.append(self.create_cmd(remote))
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
    

    def plot(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        pol =  self.status.get_status('octopus.rt_tddft_delta.param.pol_dir')
        spec_file = self.task_data['spectra_file'][pol[0]]
        file = Path(self.project_dir) / spec_file
        img = file.parent / f"spec_{pol[1]}.png"
        plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")


class OctKSD(Task):

    task_data = octopus_data.ksd
    task_name = 'tcm'

    default_param = {
        'occ': 4,
        'unocc': 6,
        'nt': 100,
        'nbeg': 1,
        'nskp':1,
        'nproj':10,
        'proj_start':1,
        'proj_end': 10,
        'ni': 4,
        'na': 6,
        'e_pol': [1,0,0],
        'pop_value': True,
        'dmat_value': True,
        'pop': '',
        'dmat': ''
    }


    inp_temp = """
OCC {occ} UNOCC {unocc}
NT {nt} NBEG {nbeg} NSKP {nskp} NPROJ {nproj}
IPROJ {proj_start}-{proj_end}
NI {ni} NA {na}
AXIS {e_pol[0]} {e_pol[1]} {e_pol[2]}

DMAT
"""

    def __init__(self, status, project_dir, lsconfig, user_input:dict) -> None:
        import copy

        super().__init__('octopus',status, project_dir, lsconfig)
        # self.user_input = copy.deepcopy(user_input)
        self.status = status
        # self.temp_dict = self.default_param.copy() 
        self.temp_dict = copy.deepcopy(self.default_param)        
        self.user_input = self.temp_dict
        self.temp_dict.update(user_input)
        self.read_from_status()
        
        file = self.task_data['req'][0]
        info_file = Path(self.project_dir)/file
        self.read_info_file(info_file)
        self.update_keyword()
        
         
    def read_from_status(self):
        """ Updates default dict with status parameters """

        # self.unocc = self.status.get_status('octopus.ground_state.param.unocc')
        
        self.unocc = self.status.get_status('octopus.ground_state.param.ExtraStates')
        e_pol = self.status.get_status('octopus.rt_tddft_delta.param.TDPolarizationDirection')
        max_step = self.status.get_status('octopus.rt_tddft_delta.param.TDMaxSteps')
        output_freq = self.status.get_status('octopus.rt_tddft_delta.param.TDOutputComputeInterval') 
        nt = int(max_step/output_freq) 

        assign_pol_list ={
            1 : [1,0,0],
            2 : [0,1,0],
            3 : [0,0,1]
        }

        dict_to_update = {
            'unocc': self.unocc,
            'e_pol': assign_pol_list.get(e_pol),
            'nt': nt
        }
        # print(dict_to_update)
        self.temp_dict.update(dict_to_update) 

    def update_keyword(self):
        self.ni = int(self.temp_dict['ni'])
        self.na = int(self.temp_dict['na'])

        # if self.temp_dict['pop_value']:
        #     self.temp_dict['pop'] = "POP"
        # if self.temp_dict['dmat_value']:
        #     self.temp_dict['dmat'] = "DMAT" 

        self.temp_dict['nproj'] = self.ni + self.na
        self.temp_dict['proj_start'] = self.occ - self.ni
        self.temp_dict['proj_end'] = self.occ + self.na  

    def read_info_file(self, evfile):
        """ Gets number of occ states, HOMO/LUMO"""

        fp = open(evfile,"r")
        lines = fp.readlines()
        itr = 0
        for line in lines:
            if "Occupation" in line:
                itr_beg = itr
                break
            itr += 1 

        ### extracts number of occupied states from 'static/info' file
        occ_itr = 0
        for line in lines[itr_beg+1:]:            
            occ_value = float(line.strip().split()[3])
            occ_itr +=1 
            if occ_value == 0.0:  
                occ_end = occ_itr              
                break 

        self.occ = occ_end-1
        self.temp_dict['occ'] = self.occ 

        ### stores energy eigen values in a list
        evals = []
        itr_st = 0
        for line in lines[itr_beg+1:]:
            if itr_st == (self.occ + self.unocc):
                break
            evals.append(float(line.strip().split()[2]))
            itr_st += 1

    def create_template(self):
        """ Creates input template for KSD calculation"""

        self.template = self.inp_temp.format(**self.temp_dict)
        # return template

    def write_input(self, template=None):
        from litesoph.lsio.IO import write2file 
        
        if template:
            self.template = template
        # if not self.task_dir:
        #     self.create_task_dir()
        if not self.template:
            msg = 'Template not given or created'
            raise Exception(msg)
        self.ksd_dir = Path(self.project_dir)/'octopus/ksd' 
        # inp_file = Path(ksd_dir) / 'oct.inp'   
        self.engine.create_directory(self.ksd_dir)
        write2file(self.ksd_dir, 'oct.inp', self.template)

    def create_cmd(self, remote=False, plot_cmd=False):
        import pathlib

        self.fmin = self.user_input.get('fmin')
        self.fmax = self.user_input.get('fmax')
        self.axis_limit = self.user_input.get('axis_limit')

        info_file = self.task_data['req'][0]
        projection_file = self.task_data['req'][1]
        ksd_file = self.project_dir / self.task_data['ksd_file']
        ksd_inp_file = self.project_dir / self.task_data['inp']

        info_file = self.project_dir / info_file
        projection_file = self.project_dir / projection_file

        if not info_file.exists():
            raise FileNotFoundError(f' Required file {info_file} doesnot exists!')

        if not projection_file.exists():
            raise FileNotFoundError(f' Required file {projection_file} doesnot exists!')               
            
        path = pathlib.Path(__file__)

        if remote:
            path_python = 'python3'
        else:
            path_python = self.lsconfig.get('programs', 'python')

        path_tddenmat = str(path.parents[2]/ 'post_processing/octopus/tddenmat.py')
        path_plotdmat = str(path.parents[2]/ 'visualization/octopus/plotdmat.py')

        if plot_cmd:
            cmd = f'{path_python} {path_plotdmat} {ksd_file} {self.fmin} {self.fmax} {self.axis_limit} -i'
        else:
            cmd = f'{path_python} {path_tddenmat} {ksd_inp_file} {info_file} {projection_file}'
      
        return cmd

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        path = self.ksd_dir
        if remote_path:
            path = Path(remote_path) / self.project_dir.name / "octopus"
           
        job_script.append(f"cd {str(path)}")
        job_script.append(self.create_cmd(remote))
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

    def plot(self):
        from litesoph.utilities.job_submit import execute
        
        cmd =  self.create_cmd(plot_cmd=True)
        result = execute(cmd, self.ksd_dir)
        
        if result[cmd]['returncode'] != 0:
            raise Exception(f"{result[cmd]['error']}")
        