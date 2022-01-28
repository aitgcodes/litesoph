from pathlib import Path
from typing import Any, Dict


#################################### Starting of Optimisastion default and template ################

class NwchemOptimisation:

    NAME = 'optimize.nwi'
    default_opt_param= {
            'mode':'gaussian',
            'pr_dir':'',
            'charge': 0,
            'basis': '6-31g',
            'geometry':'coordinate.xyz',
            'multip': 1,
            'xc': 'PBE0',
            'maxiter': 300,
            'tolerance': 'tight',
            'energy': 1.0e-7,
            'density': 1.0e-5,
            'theory':'dft',
            'properties':'optimize',
            }
   
 
    opt_temp = """echo
start gs

permanent_dir {pr_dir}
title "LITESOPH NWCHEM Optimisation"

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
 tolerances {tolerance}
 convergence energy {energy}
 convergence density {density}
end

task {theory} optimize
               
                """

    def __init__(self, user_input) -> None:
        self.user_input = self.default_opt_param
        self.user_input.update(user_input)


    def format_template(self):
        if self.default_opt_param['properties'] == 'optimize':
           template = self.opt_temp.format(**self.user_input)
           return template
        if self.default_opt_param['properties'] == 'optimize+frequency':
           tlines = self.opt_temp.splitlines()
           tlines[25] = "task dft freq"
           temp = """\n""".join(tlines)
           template = temp.format(**self.user_input)
           return template

###################### Starting of Ground State default and template #############################

class NwchemGroundState:

    NAME = 'gs.nwi'

    default_gs_param = {
            'mode':'gaussian',
            'pr_dir':'',
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

permanent_dir {pr_dir}
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

    NAME = 'td.nwi'

    default_delta_param= {
            'pr_dir':'',
            'geometry':'coordinate.xyz',
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

permanent_dir {pr_dir}
title "LITESOPH NWCHEM Delta Kick Calculations"

geometry "system" units angstroms nocenter noautoz noautosym 
  load {geometry} 
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

    def kickxy(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        poly = self.user_input['poly']
        max = self.user_input['max']
        xy_kick = """

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
    """.format(tmax, dt, polx, max, tmax, dt, poly, max)
        return xy_kick

    def kickyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        poly = self.user_input['poly']
        polz = self.user_input['polz']
        max = self.user_input['max']
        yz_kick = """
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
    """.format(tmax, dt, poly, max, tmax, dt, polz, max)
        return yz_kick

    def kickxz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        polz = self.user_input['polz']
        max = self.user_input['max']
        yz_kick = """
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
    """.format(tmax, dt, polx, max, tmax, dt, polz, max)
        return xz_kick

    def kickxyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        poly = self.user_input['poly']
        polz = self.user_input['polz']
        max = self.user_input['max']
        xyz_kick = """
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
    """.format(tmax, dt, polx, max, tmax, dt, poly, max, tmax, dt, polz, max)
        return xyz_kick

    def kick_task(self):
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == None and self.user_input['polz'] == None:
            self.user_input['kick'] = self.kickx()
        if self.user_input['polx'] == None and self.user_input['poly'] == 'y' and self.user_input['polz'] == None:
            self.user_input['kick'] = self.kicky()
        if self.user_input['polx'] == None and self.user_input['poly'] == None and self.user_input['polz'] == 'z':
            self.user_input['kick'] = self.kickz()
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == 'y' and self.user_input['polz'] == None:
            self.user_input['kick'] = self.kickxy()
        if self.user_input['polx'] == None and self.user_input['poly'] == 'y' and self.user_input['polz'] == 'z':
            self.user_input['kick'] = self.kickyz()
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == None and self.user_input['polz'] == 'z':
            self.user_input['kick'] = self.kickxz() 
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == 'y' and self.user_input['polz'] == 'z':
            self.user_input['kick'] = self.kickxyz()

    def format_template(self):
        self.kick_task()
        template = self.delta_temp.format(**self.user_input)
        return template

#################################### Starting of Gaussian Pulse default and template ################

class NwchemGaussianPulse:
   
    NAME = 'tdlaser.nwi'
    
    default_gp_param= {
            'pr_dir':'',
            'geometry':'coordinate.xyz',
            'tmax': 200.0,
            'dt': 0.2,
            'polx': None,
            'poly': None,
            'polz': None,
            'max':0.0001,
            'freq': '',
            'center': '',
            'width': '',
            'pulse': None,
            }

    gp_temp = """echo
restart gs

permanent_dir {pr_dir}
title "LITESOPH NWCHEM Gaussian Pulse Calculation"

geometry "system" units angstroms nocenter noautoz noautosym
load {geometry}
end

set geometry "system"

{pulse}

              """

    def __init__(self, user_input) -> None:
        self.user_input = self.default_gp_param
        self.user_input.update(user_input)

    def pulsex(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        x_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
    """.format(tmax, dt, polx, freq, center, width, max)
        return x_pulse

 
    def pulsey(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        poly = self.user_input['poly']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        y_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
  
    """.format(tmax, dt, poly, freq, center, width, max)
        return y_pulse

    def pulsez(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polz = self.user_input['polz']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        z_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
  
    """.format(tmax, dt, polz, freq, center, width, max)
        return z_pulse
    
    def pulsexy(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        poly = self.user_input['poly']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        xy_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

      """.format(tmax, dt, polx, freq, center, width, max, tmax, dt, poly, freq, center, width, max)
        return xy_pulse

    def pulseyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        poly = self.user_input['poly']
        polz = self.user_input['polz']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        yz_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

  
    """.format(tmax, dt, poly, freq, center, width, max, tmax, dt, polz, freq, center, width, max)
        return yz_pulse
  
    def pulsexz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        polz = self.user_input['polz']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        xz_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

      """.format(tmax, dt, polx, freq, center, width, max, tmax, dt, polz, freq, center, width, max)
        return xz_pulse
 
    def pulsexyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        polx = self.user_input['polx']
        poly = self.user_input['poly']
        polz = self.user_input['polz']
        max = self.user_input['max']
        freq = self.user_input['freq']
        center = self.user_input['center']
        width = self.user_input['width']
        xyz_pulse = """
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

rt_tddft
  tmax {}
  dt {}

  field "gpulse"
    type gaussian
    polarization {}
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
    """.format(tmax, dt, polx, freq, center, width, max, tmax, dt, poly, freq, center, width, max, tmax, dt, polz, freq, center, width, max)
        return xyz_pulse

    def pulse_task(self):
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == None and self.user_input['polz'] == None:
            self.user_input['pulse'] = self.pulsex()
        if self.user_input['polx'] == None and self.user_input['poly'] == 'y' and self.user_input['polz'] == None:
            self.user_input['pulse'] = self.pulsey()
        if self.user_input['polx'] == None and self.user_input['poly'] == None and self.user_input['polz'] == 'z':
            self.user_input['pulse'] = self.pulsez()
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == 'y' and self.user_input['polz'] == None:
            self.user_input['pulse'] = self.pulsexy()
        if self.user_input['polx'] == None and self.user_input['poly'] == 'y' and self.user_input['polz'] == 'z':
            self.user_input['pulse'] = self.pulseyz()
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == None and self.user_input['polz'] == 'z':
            self.user_input['pulse'] = self.pulsexz() 
        if self.user_input['polx'] == 'x' and self.user_input['poly'] == 'y' and self.user_input['polz'] == 'z':
            self.user_input['pulse'] = self.pulsexyz()

    def format_template(self):
        self.pulse_task()
        template = self.gp_temp.format(**self.user_input)
        return template
         
