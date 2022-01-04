from pathlib import Path
from typing import Any, Dict

###################### Starting of Ground State default and template #############################

class gs_input:


    default_gs_param = {
            'name': None,
            'title':None,
            'charge': 0,
            'basis': '',
            'multip': 1,
            'xc': 'PBE0',
            'maxiter': 300,
            'tolerance': 'tight',
            'energy': 1.0e-7,
            'density': 1.0e-5, 
            'calc': None,
            'theory':'dft',
            'properties':'energy',

            } 

    gs_temp = """echo
start gs 
title "LITESOPH NWCHEM Calculations"

charge {charge}

geometry 
  load coordinate.xyz 
end

basis 
  * library {basis}
end

{calc}

task {theory} {properties}
               """

    def calcscf(self):
        maxiter = self.default_gs_param['maxiter']
        a = """
scf
  maxiter {}
end
    """.format(maxiter)
        return a 

    def calcdft(self):
        multip = self.default_gs_param['multip']
        xc = self.default_gs_param['xc']
        maxiter = self.default_gs_param['maxiter']
        tolerances = self.default_gs_param['tolerance']
        energy = self.default_gs_param['energy']
        density = self.default_gs_param['density']
        b = """
dft
 direct
 mult {}
 xc {}
 iterations {}
 tolerances {}
 convergence energy {}
 convergence density {}
end
    """.format(multip,xc,maxiter,tolerances,energy,density)
        return b

    def calc_task(self):
        if self.default_gs_param['theory'] == 'scf':
            self.default_gs_param['calc'] = self.calcscf()
        else:
            self.default_gs_param['calc'] = self.calcdft()
 
    def update(self, new_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in new_input.keys():
            if key in new_input[key] is not None:
                parameters[key] = new_input[key]
        return parameters
     
    def fromat(self, input_param):
        template = self.template.format(**input_param)
        return template

        
#################################### Starting of Optimisastion default and template ################

class opt_input:
 
    default_opt_param= {
            'name': None,
            'title':None,
            'charge': 0,
            'basis': '',
            'multip': 1,
            'xc': 'PBE0',
            'maxiter': 300,
            'tolerance': 'tight',
            'energy': 1.0e-7,
            'density': 1.0e-5,
            'theory':'dft',
            'calc': None,
            'properties':'optimize',
            }
   
 
    opt_temp = """echo
start opt
title "LITESOPH NWCHEM Optimisation"

charge {charge}

geometry 
  load coordinate.xyz 
end

basis 
  * library {basis}
end
    
{calc}

task {theory} optimize
               
                """

    def calcscf(self):
        maxiter = self.default_opt_param['maxiter']
        a = """
scf
  maxiter {}
end
    """.format(maxiter)
        return a 

    def calcdft(self):
        multip = self.default_opt_param['multip']
        xc = self.default_opt_param['xc']
        maxiter = self.default_opt_param['maxiter']
        tolerances = self.default_opt_param['tolerance']
        energy = self.default_opt_param['energy']
        density = self.default_opt_param['density']
        b = """
dft
 direct
 mult {}
 xc {}
 iterations {}
 tolerances {}
 convergence energy {}
 convergence density {}
end
    """.format(multip,xc,maxiter,tolerances,energy,density)
        return b

    def calc_task(self):
        if self.default_opt_param['theory'] == 'scf':
            self.default_opt_param['calc'] = self.calcscf()
        else:
            self.default_opt_param['calc'] = self.calcdft()
 
    def update(self, new_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in new_input.keys():
            if key in new_input[key] is not None:
                parameters[key] = new_input[key]
        return parameters

    def format(self, input_param):
        template = self.template.format(**input_param)
        return template
       

#################################### Starting of Delta Kick default and template ################

class delta_kick: 

    default_delta_param= {
            'name': None,
            'title':None,
            'tmax': 200.0,
            'dt': 0.2,
            'max':0.0001,
            'polx':None,
            'poly':None,
            'polz':None, 
            }
     
    delta_temp = """echo
restart gs
title "LITESOPH NWCHEM Delta Kick Calculations"

geometry 
  load coordinate.xyz 
end

set geometry "system"
rt_tddft
  tmax {tmax}
  dt {dt}

  tag "kick_x"

  field "kick"
    type delta
    polarization {pol}
    max {max}
  end

  excite "system" with "kick"
  print dipole
end

task dft rt_tddft

unset rt_tddft:*
rt_tddft
  tmax {tmax}
  dt {dt}

  tag "kick_y"

  field "kick"
    type delta
    polarization {pol}
    max {max}
  end

  excite "system" with "kick"
  print dipole
end
task dft rt_tddft

unset rt_tddft:*
rt_tddft
  tmax {tmax}
  dt {dt}

  tag "kick_z"

  field "kick"
    type delta
    polarization {pol}
    max {max}
  end

  excite "system" with "kick"
  print dipole
end
task dft rt_tddft

              """ 

    def format(self, input_param):
        template = self.template.format(**input_param)
        return template


#################################### Starting of Gaussian Pulse default and template ################

class gaussian_pulse:
   
    default_gp_param= {
            'name': None,
            'title':None,
            'tmax': 200.0,
            'dt': 0.2,
            'pol': '',
            'max':0.0001,
            'freq': '',
            'center': '',
            'width': '',
            }

    gp_temp = """echo
restart gs
title "LITESOPH NWCHEM Gaussin Pulse Calculation"

geometry "system" units angstroms nocenter noautoz noautosym
load coordinate.xyz
end

set geometry "system"

rt_tddft
  tmax {tmax}
  dt {dt}

  field "driver"
    type gaussian
    polarization {pol}
    frequency {freq} 
    center {center}  
    width {width}     
    max {max}        
end
    print *

   excite "system" with "driver"
end

task dft rt_tddft

              """
    def format(self, input_param):
        template = self.template.format(**input_param)
        return template
         

