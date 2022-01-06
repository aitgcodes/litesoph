from pathlib import Path
from typing import Any, Dict

###################### Starting of Ground State default and template #############################

class NwchemGroundState:


    default_gs_param = {
            'mode':'gaussian',
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

    def __init__(self, user_input) -> None:
        pass

    def calcscf(self):
        maxiter = self.default_gs_param['maxiter']
        scf = """
scf
  maxiter {}
end
    """.format(maxiter)
        return scf 

    def calcdft(self):
        multip = self.default_gs_param['multip']
        xc = self.default_gs_param['xc']
        maxiter = self.default_gs_param['maxiter']
        tolerances = self.default_gs_param['tolerance']
        energy = self.default_gs_param['energy']
        density = self.default_gs_param['density']
        dft = """
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
        return dft


    def calc_task(self):
        if self.default_gs_param['theory'] == 'scf':
            self.default_gs_param['calc'] = self.calcscf()
        else:
            self.default_gs_param['calc'] = self.calcdft()

    def check(self, user_param)-> bool:
        """checks whether user given input parameters is compatable with with nwchem ground state calculation"""

        if user_param['mode'] not in ['gaussian', 'pw'] and  user_param['engine'] == 'nwchem':
            raise ValueError('This mode is not compatable with nwchem use gaussian or paw')

        if user_param['engine'] == 'nwchem':
            return  True
        else:
            return False

    def update(self, user_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in user_input.keys():
            if key in user_input[key] is not None:
                parameters[key] = user_input[key]
        return parameters
     
    def format_template(self, input_param:dict):
        self.calc_task()
        template = self.gs_temp.format(**input_param)
        return template


#################################### Starting of Optimisastion default and template ################

class NwchemOptimisation:
 
    default_opt_param= {
            'mode':'gaussian',
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

    def __init__(self, user_input) -> None:
        pass

    def calcscf(self):
        maxiter = self.default_opt_param['maxiter']
        scf = """
scf
  maxiter {}
end
    """.format(maxiter)
        return scf 

    def calcdft(self):
        multip = self.default_opt_param['multip']
        xc = self.default_opt_param['xc']
        maxiter = self.default_opt_param['maxiter']
        tolerances = self.default_opt_param['tolerance']
        energy = self.default_opt_param['energy']
        density = self.default_opt_param['density']
        dft = """
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
        return dft
    
   

    def calc_task(self):
        if self.default_opt_param['theory'] == 'scf':
            self.default_opt_param['calc'] = self.calcscf()
        else:
            self.default_opt_param['calc'] = self.calcdft()
 
    def update(self, user_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in user_input.keys():
            if key in user_input[key] is not None:
                parameters[key] = user_input[key]
        return parameters

    def format_template(self, input_param:dict):
        self.calc_task()
        template = self.opt_temp.format(**input_param)
        return template

#################################### Starting of Delta Kick default and template ################

class NwchemDeltaKick: 

    default_delta_param= {
            'name': None,
            'title':None,
            'tmax': 200.0,
            'dt': 0.2,
            'max':0.0001,
            'polx':None,
            'poly':'y',
            'polz':None, 
            'kick':None,
            }
     
    delta_temp = """echo
restart gs
title "LITESOPH NWCHEM Delta Kick Calculations"

geometry "system" units angstroms nocenter noautoz noautosym 
  load coordinate.xyz 
end

set geometry "system"

{kick}

              """ 

    def __init__(self, user_input) -> None:
        pass

    def kickx(self):
        tmax = self.default_delta_param['tmax']
        dt = self.default_delta_param['dt']
        polx = self.default_delta_param['polx']
        max = self.default_delta_param['max']
        x_kick = """
unset rt_tddft:*
rt_tddft
  tmax {}
  dt {}

  tag "kick_x"

  field "kick"
    type delta
    polarization {}
    max {}
  end

  excite "system" with "kick"
  print dipole
end
task dft rt_tddft
    """.format(tmax, dt, polx, max)
        return x_kick

    def kicky(self):
        tmax = self.default_delta_param['tmax']
        dt = self.default_delta_param['dt']
        poly = self.default_delta_param['poly']
        max = self.default_delta_param['max']
        y_kick = """
unset rt_tddft:*
rt_tddft
  tmax {}
  dt {}

  tag "kick_y"

  field "kick"
    type delta
    polarization {}
    max {}
  end

  excite "system" with "kick"
  print dipole
end
task dft rt_tddft
    """.format(tmax, dt, poly, max)
        return y_kick

    def kickz(self):
        tmax = self.default_delta_param['tmax']
        dt = self.default_delta_param['dt']
        polz = self.default_delta_param['polz']
        max = self.default_delta_param['max']
        z_kick = """
unset rt_tddft:*
rt_tddft
  tmax {}
  dt {}

  tag "kick_z"

  field "kick"
    type delta
    polarization {}
    max {}
  end

  excite "system" with "kick"
  print dipole
end
task dft rt_tddft
    """.format(tmax, dt, polz, max)
        return z_kick


    def kick_task(self):
        if self.default_delta_param['polx'] == 'x':
            self.default_delta_param['kick'] = self.kickx()
        if self.default_delta_param['poly'] == 'y':
            self.default_delta_param['kick'] = self.kicky()
        if self.default_delta_param['polz'] == 'z':
            self.default_delta_param['kick'] = self.kickz()

    def update(self, user_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in user_input.keys():
            if key in user_input[key] is not None:
                parameters[key] = user_input[key]
        return parameters

    def format_template(self, input_param:dict):
        self.kick_task()
        template = self.delta_temp.format(**input_param)
        return template

#################################### Starting of Gaussian Pulse default and template ################

class NwchemGaussianPulse:
   
    default_gp_param= {
            'name': None,
            'title':None,
            'tmax': 200.0,
            'dt': 0.2,
            'pol': None,
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

    def __init__(self, user_input) -> None:
        pass

    def update(self, user_input: Dict[str, Any], default_param: Dict[str, Any])-> Dict[str, Any]:

        parameters = default_param

        for key in user_input.keys():
            if key in user_input[key] is not None:
                parameters[key] = user_input[key]
        return parameters

    def format_template(self, input_param:dict):
        template = self.gp_temp.format(**input_param)
        return template
         
