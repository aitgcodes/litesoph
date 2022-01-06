
class OctGroundState:

    default_param = {
            'work_dir' : ".",         # default 
            'scratch' : 'yes',
            'calc_mode':'gs',         # default calc mode
            'out_unit':'ev_angstrom', # default output unit
            'name':'H',               # name of species
            'geom_file' : "coordinate.xyz",       
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
            } 

    gs_min = """
WorkDir = {work_dir}    
FromScratch = {scratch}                
CalculationMode = gs
Dimension = {dimension} 

Unitsoutput = {out_unit}       
XYZCoordinates = '{geom_file}'
BoxShape = {box[shape]}
Radius ={box[radius]}*angstrom


Spacing = {spacing}*angstrom
SpinComponents = {spin_pol}
ExcessCharge = {charge}

ConvEnergy = {e_conv}
MaximumIter = {max_iter}
    """
    
    def __init__(self, user_input) -> None:
        self.default_param.update(user_input)
        self.boxshape = self.default_param['box']['shape']        

    def check(self):
        pass

    def format_template(self):
        if self.boxshape not in ['cylinder', 'paralellopiped']: 
            template = self.gs_min.format(**self.default_param)
            return template 

        elif self.boxshape == "cylinder":
            tlines = self.gs_min.splitlines()
            tlines[9] = "Xlength = {box[xlength]}"
            template = """\n""".join(tlines)
            print(template)
            template = self.gs_min.format(**self.default_param)
            return template

        elif self.boxshape == "paralellopiped":
            tlines = self.gs_min.splitlines()
            tlines[8] = "%LSize"
            tlines[9] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[10] = "%"
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
            'geom_file' : "coordinate.xyz",       
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
            'e_pol': 1             
            }

    td = """
WorkDir = {work_dir}    
FromScratch = {scratch}                
CalculationMode = td
Dimension = {dimension} 

Unitsoutput = {out_unit}       
XYZCoordinates = '{geom_file}'
BoxShape = {box[shape]}
Radius = {box[radius]}*angstrom


Spacing = {spacing}*angstrom

TDPropagator = {td_propagator}
TDMaxSteps = {max_step}
TDTimeStep = {time_step}/eV

TDDeltaStrength = {strength}/angstrom
TDPolarizationDirection = {e_pol}
"""         

    def __init__(self, user_input) -> None:
        self.default_param.update(user_input)
        self.boxshape = self.default_param['box']['shape']         

    def check(self):
        pass

    def format_template(self):
        if self.boxshape not in ['cylinder', 'paralellopiped']: 
            template = self.td.format(**self.default_param)
            return template 

        elif self.boxshape == "cylinder":
            tlines = self.td.splitlines()
            tlines[9] = "Xlength = {box[xlength]}"
            template = """\n""".join(tlines)
            print(template)
            template = self.td.format(**self.default_param)
            return template

        elif self.boxshape == "paralellopiped":
            tlines = self.td.splitlines()
            tlines[8] = "%LSize"
            tlines[9] = "{box[sizex]}|{box[sizey]}|{box[sizez]}"
            tlines[10] = "%"
            temp = """\n""".join(tlines)
            template = temp.format(**self.default_param)
            return template    
