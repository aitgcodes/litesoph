from pathlib import Path
import pathlib
from typing import Any, Dict
from litesoph.utilities.units import as_to_au, eV_to_au

from litesoph.simulations.nwchem import nwchem_data
from litesoph.simulations.esmd import Task

#################################### Starting of Optimisastion default and template ################

class NwchemOptimisation(Task):

    task_data = nwchem_data.ground_state

    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)

    default_param= {
            'mode':'gaussian',
            'name':'gs',
            'permanent_dir':'',
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
start {name}

permanent_dir {permanent_dir}
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

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__(status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)


    def create_template(self):
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

class NwchemGroundState(Task):

    task_data = nwchem_data.ground_state
    task_name = 'ground_state'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)

    default_param = {
            'mode':'gaussian',
            'name':'gs',
            'permanent_dir':'',
            'geometry':'coordinate.xyz',
            'charge': 0,
            'basis': '6-31g',
            'multip': 1,
            'xc': None,
            'maxiter': 300,
            'energy': 1.0e-7,
            'density': 1.0e-5, 
            'theory':'dft',

            } 

    gs_temp = """
echo
start {name}

permanent_dir {permanent_dir}
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
 {xc}
 iterations {maxiter}
 convergence energy {energy}
 convergence density {density}
end

task {theory} energy 
               """

    xc = {
               'B3LYP'     :'xc b3lyp',
               'PBE0'      :'xc pbe0',
               'PBE96'     :'xc xpbe96 cpbe96',
               'BHLYP'     :'xc bhlyp',
               'PW91'      :'xc xperdew91 perdew91',
               'BP86'      :'xc becke88 perdew86',
               'BP91'      :'xc becke88 perdew91',
               'BLYP'      :'xc becke88 lyp',
               'M05'       :'xc m05',
               'M05-2X'    :'xc m05-2x',
               'M06'       :'xc m06',
               'M06-HF'    :'xc m06-hf',
               'M08-SO'    :'xc m08-so',
               'M11'       :'xc m11',
               'CAM-B3LYP' :'xc xcamb88 1.00 lyp 0.81 vwn_5 0.19 hfexch 1.00 \n cam 0.33 cam_alpha 0.19 cam_beta 0.46',
               'LC-BLYP'   :'xc xcamb88 1.00 lyp 1.0 hfexch 1.00 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
               'LC-PBE'    :'xc xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.0 cam_beta 1.0',
               'LC-wPBE'   :'xc xwpbe 1.00 cpbe96 1.0 hfexch 1.00 \n cam 0.4 cam_alpha 0.00 cam_beta 1.00',
               'CAM-PBE0'  :'xc xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.25 cam_beta 0.75',
               'rCAM-B3LYP':'xc xcamb88 1.00 lyp 1.0 vwn_5 0. hfexch 1.00 becke88 nonlocal 0.13590 \n cam 0.33 cam_alpha 0.18352 cam_beta 0.94979',
               'HSE03'     :'xc xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
               'HSE06'     :'xc xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.11 cam_alpha 0.0 cam_beta 1.0',
    }

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('nwchem',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.user_input['geometry']= str(pathlib.Path(project_dir.name) / self.task_data['req'][0])
        self.user_input['permanent_dir'] = str(pathlib.Path(project_dir.name) /nwchem_data.restart)
        xc_str = self.xc[user_input['xc']]
        self.user_input['xc'] = xc_str
        #self.xc = self.user_input['xc']
 
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


     
    def create_template(self):
        self.template = self.gs_temp.format(**self.user_input)
        #if self.xc and 'xc' in self.xc:
            #print(xc[1])
            #tlines = template.splitlines()
            #tlines[20] = 
            #template = """\n""".join(tlines)

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

#################################### Starting of Delta Kick default and template ################

class NwchemDeltaKick(Task): 

    task_data = nwchem_data.rt_tddft_delta
    task_name = 'rt_tddft_delta'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)

    default_param= {
            'name':'gs',
            'permanent_dir':'',
            'geometry':'coordinate.xyz',
            'tmax': 200.0,
            'dt': 0.2,
            'max':0.0001,
            'e_pol':[1,0,0],
            'extra_prop':None,
            'nrestart':0,
            'pol_dir':None,
            }
     
    delta_temp = """
echo
restart {name}

permanent_dir {permanent_dir}
title "LITESOPH NWCHEM Delta Kick Calculations"

geometry "system" units angstroms nocenter noautoz noautosym 
  load {geometry} 
end

set geometry "system"

{kick}
              """ 

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('nwchem',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        gs_inp = status.get_status('nwchem.ground_state.param')
        self.user_input.update(gs_inp)
        self.convert_unit()
        self.prop = self.user_input['extra_prop']
 
    def convert_unit(self):
        self.user_input['dt'] = round(self.user_input['dt']*as_to_au, 2)
        self.user_input['tmax'] = round(self.user_input['tmax']*as_to_au, 2)
 
    def kickx(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        x_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_x"

  field "kick"
    type delta
    polarization x
    max {}
  end

  excite "system" with "kick"
  print dipole
   
end
task dft rt_tddft
    """.format(tmax, dt, max)
        return x_kick

    def kicky(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        y_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_y"

  field "kick"
    type delta
    polarization y
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max)
        return y_kick

    def kickz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        z_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_z"

  field "kick"
    type delta
    polarization z
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max)
        return z_kick

    def kickxy(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        xy_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_x"

  field "kick"
    type delta
    polarization x 
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
    polarization y
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max, tmax, dt, max)
        return xy_kick

    def kickyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        yz_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_y"

  field "kick"
    type delta
    polarization y
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
    polarization z
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max, tmax, dt, max)
        return yz_kick

    def kickxz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        xz_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_x"

  field "kick"
    type delta
    polarization x 
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
    polarization z
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max, tmax, dt, max)
        return xz_kick

    def kickxyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
        max = self.user_input['max']
        xyz_kick = """
rt_tddft
  tmax {}
  dt {}

  tag "kick_x"

  field "kick"
    type delta
    polarization x
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
    polarization y
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
    polarization z
    max {}
  end

  excite "system" with "kick"
  print dipole

end
task dft rt_tddft
    """.format(tmax, dt, max, tmax, dt, max, tmax, dt, max)
        return xyz_kick

    def kick_task(self):
        if self.user_input['e_pol'] == [1,0,0]:
            self.user_input['kick'] = self.kickx()
            self.pol_index = 1
        if self.user_input['e_pol'] == [0,1,0]:
            self.user_input['kick'] = self.kicky()
            self.pol_index = 2 
        if self.user_input['e_pol'] == [0,0,1]:
            self.user_input['kick'] = self.kickz()
            self.pol_index = 3
        if self.user_input['e_pol'] == [1,1,0]:
            self.user_input['kick'] = self.kickxy()
            self.pol_index = 4
        if self.user_input['e_pol'] == [0,1,1]:
            self.user_input['kick'] = self.kickyz()
            self.pol_index = 5
        if self.user_input['e_pol'] == [1,0,1]:
            self.user_input['kick'] = self.kickxz() 
            self.pol_index = 6
        if self.user_input['e_pol'] == [1,1,1]:
            self.user_input['kick'] = self.kickxyz()
            self.pol_index = 7

    
 
    def create_template(self):
        self.kick_task()
        template = self.delta_temp.format(**self.user_input)
        nrestart = self.user_input['nrestart']
        if self.user_input['nrestart'] != 0:
            tlines = template.splitlines()
            tlines[18] = "  nrestarts {}".format(nrestart)
            template = """\n""".join(tlines)
        if self.pol_index == 1 or 2 or 3:
            if self.prop and "moocc" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc"
                template = """\n""".join(tlines)
            if self.prop and "charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole field energy s2 charge"
                template = """\n""".join(tlines)
            if self.prop and "mooc&charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc field energy s2 charge"
                template = """\n""".join(tlines)
        if self.pol_index == 4 or 5 or 6:
            if self.prop and "moocc" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc"
                tlines[45] = "  print dipole moocc"
                template = """\n""".join(tlines)
            if self.prop and "charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole field energy s2 charge"
                tlines[45] = "  print dipole field energy s2 charge"
                template = """\n""".join(tlines)
            if self.prop and "mooc&charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc field energy s2 charge"
                tlines[45] = "  print dipole moocc field energy s2 charge"
                template = """\n""".join(tlines)    
        if self.pol_index == 7:
            if self.prop and "moocc" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc"
                tlines[45] = "  print dipole moocc"
                tlines[63] = "  print dipole moocc"
                template = """\n""".join(tlines)
            if self.prop and "charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole field energy s2 charge"
                tlines[45] = "  print dipole field energy s2 charge"
                tlines[63] = "  print dipole field energy s2 charge"
                template = """\n""".join(tlines)
            if self.prop and "mooc&charge" in self.prop:
                tlines = template.splitlines()
                tlines[27] = "  print dipole moocc field energy s2 charge"
                tlines[45] = "  print dipole moocc field energy s2 charge"
                tlines[63] = "  print dipole moocc field energy s2 charge"
                template = """\n""".join(tlines)
        self.template = template

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)


#################################### Starting of Gaussian Pulse default and template ################

class NwchemGaussianPulse(Task):
   
    task_data = nwchem_data.rt_tddft_laser
    task_name = 'rt_tddft_laser'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)
    
    default_param= {
            'name':'gs',
            'permanent_dir':'',
            'geometry':'coordinate.xyz',
            'tmax': 200.0,
            'dt': 0.2,
            'e_pol':[1,0,0],
            'max':0.0001,
            'freq': '',
            'center': '',
            'width': '',
            }

    gp_temp = """echo
restart {name}

permanent_dir {permanent_dir}
title "LITESOPH NWCHEM Gaussian Pulse Calculation"

geometry "system" units angstroms nocenter noautoz noautosym
load {geometry}
end

set geometry "system"

{pulse}

              """

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('nwchem',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        gs_inp = status.get_status('nwchem.ground_state.param')
        self.user_input.update(gs_inp)
        self.convert_unit()
        print(self.user_input)
   
    def convert_unit(self):
        self.user_input['dt'] = round(self.user_input['dt']*as_to_au, 1)
        self.user_input['tmax'] = round(self.user_input['tmax']*as_to_au, 2)
        self.user_input['freq'] = round(self.user_input['freq']*eV_to_au, 3)

    def pulsex(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization x
    frequency {} 
    center {}  
    width {}     
    max {}
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
    """.format(tmax, dt, freq, center, width, max)
        return x_pulse

 
    def pulsey(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization y
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
  
    """.format(tmax, dt, freq, center, width, max)
        return y_pulse

    def pulsez(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization z
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
  
    """.format(tmax, dt, freq, center, width, max)
        return z_pulse
    
    def pulsexy(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization x 
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
    polarization y
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

      """.format(tmax, dt, freq, center, width, max, tmax, dt, freq, center, width, max)
        return xy_pulse

    def pulseyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization y
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
    polarization z
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

  
    """.format(tmax, dt, freq, center, width, max, tmax, dt, freq, center, width, max)
        return yz_pulse
  
    def pulsexz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization x 
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
    polarization z
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft

      """.format(tmax, dt, freq, center, width, max, tmax, dt, freq, center, width, max)
        return xz_pulse
 
    def pulsexyz(self):
        tmax = self.user_input['tmax']
        dt = self.user_input['dt']
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
    polarization x 
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
    polarization y
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
    polarization z
    frequency {} 
    center {}  
    width {}     
    max {}        
  end
  excite "system" with "gpulse" 
end

task dft rt_tddft
  
    """.format(tmax, dt, freq, center, width, max, tmax, dt, freq, center, width, max, tmax, dt, freq, center, width, max)
        return xyz_pulse

    def pulse_task(self):
        if self.user_input['e_pol'] == [1,0,0]:
            self.user_input['pulse'] = self.pulsex()
        if self.user_input['e_pol'] == [0,1,0]:
            self.user_input['pulse'] = self.pulsey()
        if self.user_input['e_pol'] == [0,0,1]:
            self.user_input['pulse'] = self.pulsez()
        if self.user_input['e_pol'] == [1,1,0]:
            self.user_input['pulse'] = self.pulsexy()
        if self.user_input['e_pol'] == [0,1,1]:
            self.user_input['pulse'] = self.pulseyz()
        if self.user_input['e_pol'] == [1,0,1]:
            self.user_input['pulse'] = self.pulsexz() 
        if self.user_input['e_pol'] == [1,1,1]:
            self.user_input['pulse'] = self.pulsexyz()

    def create_template(self):
        self.pulse_task()
        self.template = self.gp_temp.format(**self.user_input)

    def create_job_script(self, np, remote_path=None, remote=False) -> list:
        
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

class NwchemSpectrum(Task):

    task_data = nwchem_data.spectrum
    task_name = 'spectrum'

    path = pathlib.Path(task_data['spec_dir_path'])

    def __init__(self, status, project_dir: pathlib.Path, lsconfig, user_input) -> None:
        super().__init__('nwchem', status, project_dir, lsconfig)
        self.user_input = user_input
        self.pol =  self.status.get_status('nwchem.rt_tddft_delta.param.pol_dir')
    
    def prepare_input(self):

        self.task_dir = self.project_dir / self.task_data['spec_dir_path']
        self.engine.create_directory(self.task_dir)

    def create_cmd(self, remote=False ):

        dm_file = self.task_data['out_log']

        dm_file = self.project_dir / dm_file

        if  not dm_file.exists():
            raise FileNotFoundError(f' Required file {dm_file} doesnot exists!')
            
        path = pathlib.Path(__file__)

        if remote:
            path_python = 'python3'
        else:
            path_python = self.lsconfig.get('programs', 'python')

        nw_rtparse = str(path.parent /'nw_rtparse.py')
        rot = str(path.parent / 'rotate_fft.py')
        fft = str(path.parent / 'fft1d.py')
        
        x_get_dm_cmd = f'{path_python} {nw_rtparse} -xdipole -px -tkick_x {dm_file} > x.dat'
        y_get_dm_cmd = f'{path_python} {nw_rtparse} -xdipole -py -tkick_y {dm_file} > y.dat'
        z_get_dm_cmd = f'{path_python} {nw_rtparse} -xdipole -pz -tkick_z {dm_file} > z.dat'

        x_f_cmd = f'{path_python} {fft} x.dat xw.dat'
        y_f_cmd = f'{path_python} {fft} y.dat yw.dat'
        z_f_cmd = f'{path_python} {fft} z.dat zw.dat'

        x_r_cmd = f'{path_python} {rot} xw.dat x'
        y_r_cmd = f'{path_python} {rot} yw.dat y'
        z_r_cmd = f'{path_python} {rot} zw.dat z'
        
        if self.pol[1] == 'x':
            return [x_get_dm_cmd, x_f_cmd, x_r_cmd]

        elif self.pol[1] == 'y':
            return [y_get_dm_cmd, y_f_cmd, y_r_cmd]

        elif self.pol[1] == 'z':
            return [z_get_dm_cmd, z_f_cmd, z_r_cmd]

    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = super().create_job_script()

        path = self.project_dir / self.path
        if remote_path:
            path = Path(remote_path) / self.project_dir.name / self.path
           
        job_script.append(f"cd {str(path)}")
        job_script.extend(self.create_cmd(remote))
        
        
        self.job_script = "\n".join(job_script)
        return self.job_script
        

    def run_job_local(self, cmd):
        cmd = cmd + ' ' + self.BASH_filename
        self.write_job_script(self.job_script)
        self.sumbit_local.run_job(cmd)


    def plot(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        pol =  self.status.get_status('nwchem.rt_tddft_delta.param.pol_dir')
        spec_file = self.task_data['spectra_file'][pol[0]]
        file = pathlib.Path(self.project_dir) / spec_file
        img = file.parent / f"spec_{pol[1]}.png"
        plot_spectrum(file,img,0, 2, "Energy","Strength")


def nwchem_compute_moocc(project_dir :pathlib.Path, pol):
    import os
    from subprocess import Popen, PIPE

    moocc_file = 'nwchem/TD_Delta/td.nwo'

    cwd = project_dir / 'nwchem' / 'Population'

    moocc_file = project_dir / moocc_file

    if not moocc_file.exists():
        raise FileNotFoundError(f' Required file {moocc_file} doesnot exists!')


    path = pathlib.Path(__file__)

    extract_mo = str(path.parent /'extract.sh')
    homo_to_lumo = str(path.parent / 'homo_to_lumo.py')
    population = str(path.parent / 'population_correlation.py')
   
