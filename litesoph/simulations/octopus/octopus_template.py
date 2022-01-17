from pathlib import Path
from typing import Any, Dict
from litesoph.utilities.units import ang_to_au

from matplotlib.pyplot import box

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
            'smearing' : 0.1          # in eV
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
        self.default_param.update(user_input)
        self.boxshape = self.default_param['box']['shape'] 
        self.check_unit()          
    
    def check_unit(self):
        if self.default_param['unit_box'] == "angstrom":
            box_dict = self.default_param['box']
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
            template = self.gs_min.format(**self.default_param)
            return template 

        elif self.boxshape == "cylinder":
            tlines = self.gs_min.splitlines()
            tlines[10] = "Xlength = {box[xlength]}"
            temp = """\n""".join(tlines)
            template = temp.format(**self.default_param)
            return template

        elif self.boxshape == "parallelepiped":
            tlines = self.gs_min.splitlines()
            self.default_param['box']['sizex'] = round(self.default_param['box']['sizex']/2, 2)
            self.default_param['box']['sizey'] = round(self.default_param['box']['sizey']/2, 2)
            self.default_param['box']['sizez'] = round(self.default_param['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            template = temp.format(**self.default_param)
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
WorkDir = '{work_dir}'    
FromScratch = {scratch}                
CalculationMode = td
Dimensions = {dimension} 

Unitsoutput = {out_unit}       
XYZCoordinates = '{geometry}'
BoxShape = {box[shape]}
Radius = {box[radius]}


Spacing = {spacing}*angstrom

TDPropagator = {td_propagator}
TDMaxSteps = {max_step}
TDTimeStep = {time_step}

TDDeltaStrength = {strength}/angstrom

"""         

    tlines_pol = """
%TDPolarization
 {e_pol[0]} | {e_pol[1]} | {e_pol[2]}
 0 | 1 | 0
 0 | 0 | 1
%
TDPolarizationDirection = 1
"""

    def __init__(self, user_input) -> None:
        self.default_param.update(user_input)
        self.boxshape = self.default_param['box']['shape']         
        self.e_pol = self.default_param['e_pol']
        self.check_pol()
        
    def check_pol(self):
        if self.e_pol == [1,0,0]:
            self.default_param['e_dir'] = 1
        elif self.e_pol == [0,1,0]:
            self.default_param['e_dir'] = 2 
        elif self.e_pol == [0,0,1]:
            self.default_param['e_dir'] = 3
        else:
            self.default_param['e_dir'] = 0
            
    def format_pol(self):
        if self.default_param['e_dir'] in [1,2,3]:
            tlines = self.td.splitlines()
            tlines[19] = "TDPolarizationDirection = {e_dir}"
            temp = """\n""".join(tlines)
            return temp

        elif self.default_param['e_dir'] == 0:
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
            self.default_param['box']['sizex'] = round(self.default_param['box']['sizex']/2, 2)
            self.default_param['box']['sizey'] = round(self.default_param['box']['sizey']/2, 2)
            self.default_param['box']['sizez'] = round(self.default_param['box']['sizez']/2, 2)
            tlines[9] = "%LSize"
            tlines[10] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[11] = "%"
            temp = """\n""".join(tlines)
            return temp

    def format_template(self):
        self.td = self.format_box() 
        temp = self.format_pol()
        template = temp.format(**self.default_param)
        return(template)
