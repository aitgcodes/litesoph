from pathlib import Path
from typing import Any, Dict


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
        self.user_input = self.default_opt_param
        self.user_input.update(user_input)


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
 

    def format_template(self, input_param:dict):
        self.calc_task()
        template = self.opt_temp.format(**input_param)
        return template


###################### Starting of Ground State default and template #############################

class NwchemGroundState:


    default_gs_param = {
            'mode':'gaussian',
            'geometry':'coordinate.xyz',
            'charge': 0,
            'basis': '6-31g',
            'multip': 1,
            'xc': 'PBE0',
            'maxiter': 300,
            'tolerances': 'tight',
            'energy': 1.0e-7,
            'density': 1.0e-5, 
            'theory':'dft',

            } 

    gs_temp = """echo
start gs
title "LITESOPH NWCHEM Calculations"

charge {charge}

geometry 
  load  {geometry}
end

basis 
  * library {basis}
end

dft
 direct
 mult {multip}
 xc {xc}
 iterations {maxiter}
 tolerances {tolerances}
 convergence energy {energy}
 convergence density {density}
end

task {theory} energy 
               """

    def __init__(self, user_input) -> None:
        self.user_input = self.default_gs_param
        self.user_input.update(user_input)


    def calcscf(self):
        maxiter = self.user_input['maxiter']
        scf = """
scf
  maxiter {}
end
    """.format(maxiter)
        return scf 

    def calcdft(self):
        multip = self.user_input['multip']
        xc = self.user_input['xc']
        maxiter = self.user_input['maxiter']
        tolerances = self.user_input['tolerance']
        energy = self.user_input['energy']
        density = self.user_input['density']
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
        if self.user_input['theory'] == 'scf':
            self.user_input['calc'] = self.calcscf()
        else:
            self.user_input['calc'] = self.calcdft()


     
    def format_template(self):
        template = self.gs_temp.format(**self.user_input)
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
        self.user_input = self.default_delta_param
        self.user_input.update(user_input)

    def kickx(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        max = self.user_input['max']
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
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        poly = self.user_input['poly']
        max = self.user_input['max']
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
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polz = self.user_input['polz']
        max = self.user_input['max']
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
        if self.user_input['polx'] == 'x':
            self.user_input['kick'] = self.kickx()
        if self.user_input['poly'] == 'y':
            self.user_input['kick'] = self.kicky()
        if self.user_input['polz'] == 'z':
            self.user_input['kick'] = self.kickz()


    def format_template(self):
        self.kick_task()
        template = self.delta_temp.format(**self.user_input)
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
        self.user_input = self.user_input
        self.user_input.update(user_input)


    def format_template(self, input_param:dict):
        template = self.gp_temp.format(**input_param)
        return template
         
