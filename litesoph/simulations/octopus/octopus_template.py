from pathlib import Path
from typing import Any, Dict
from litesoph.utilities.units import ang_to_au, au_to_as, as_to_au


class OctGroundState:

    default_param = {
            'work_dir' : ".",         # default 
            'scratch' : 'yes',
            'calc_mode':'gs',         # default calc mode
            'out_unit':'ev_angstrom', # default output unit
            'name':'H',               # name of species
            'geometry' : "coordinate.xyz",       
            'dimension' : 3, 
            'theory':'dft' ,          # "DFT", "INDEPENDENT_PARTICLES","HARTREE_FOCK","HARTREE","RDMFT"
            'xc': 'lda_x + lda_c_pz_mod',
            'pseudo_potential':'set|standard', # else 'file|pseudo potential filename'
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
            'unit_box' : 'angstrom'
            } 

    gs_min = """
WorkDir = '{work_dir}'    
FromScratch = {scratch}                
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
XCFunctional = {xc}
Mixing = {mixing}
MaximumIter = {max_iter}
Eigensolver = {eigensolver}
Smearing = {smearing}
SmearingFunction = {smearing_func}
ConvRelDens = {conv_reldens}
ConvEnergy = {e_conv}
    """
    
    def __init__(self, user_input) -> None:
        self.temp_dict = self.default_param
        self.temp_dict.update(user_input)
        self.boxshape = self.temp_dict['box']['shape'] 
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

    def format_template(self):
        if self.boxshape not in ['cylinder', 'parallelepiped']: 
            template = self.gs_min.format(**self.temp_dict)
            return template 

        elif self.boxshape == "cylinder":
            tlines = self.gs_min.splitlines()
            tlines[10] = "Xlength = {box[xlength]}"
            temp = """\n""".join(tlines)
            template = temp.format(**self.temp_dict)
            return template

        elif self.boxshape == "parallelepiped":
            tlines = self.gs_min.splitlines()
            self.temp_dict['box']['sizex'] = round(self.temp_dict['box']['sizex']/2, 2)
            self.temp_dict['box']['sizey'] = round(self.temp_dict['box']['sizey']/2, 2)
            self.temp_dict['box']['sizez'] = round(self.temp_dict['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            template = temp.format(**self.temp_dict)
            return template    

        
class OctTimedependentState:

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
   

    def __init__(self, user_input, status) -> None:
        self.status = status
        self.temp_dict = self.status.get_value('gs_dict')
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
            self.temp_dict['box']['sizex'] = round(self.temp_dict['box']['sizex']/2, 2)
            self.temp_dict['box']['sizey'] = round(self.temp_dict['box']['sizey']/2, 2)
            self.temp_dict['box']['sizez'] = round(self.temp_dict['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            return temp

    def format_template(self):
        self.td = self.format_box() 
        temp = self.format_pol()
        template = temp.format(**self.temp_dict)
        return(template)

class OctTimedependentLaser:

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

    def __init__(self, user_input, status=None) -> None:
        if status is not None:
            self.status = status
            self.temp_dict = self.status.get_status('octopus.gs.param')
        else:
            self.temp_dict = self.default_param
       
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

    def format_template(self):
        self.td = self.format_box() 
        #temp = self.format_pol()
        template = self.td.format(**self.temp_dict)
        return(template)
