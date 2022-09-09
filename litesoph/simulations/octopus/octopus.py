import os
from pathlib import Path
import subprocess
from litesoph.post_processing.octopus.oct_projections import Projections
from litesoph.simulations.octopus.octopus_input import generate_input

class Octopus:
    def __init__(self,infile=None, outfile=None, 
                directory=".", cmd=None, **kwargs) -> None:
        if infile:
            self.infile = infile
        else:
            self.infile = 'inp'
        self.outfile = outfile
        self.directory = directory
        self.cmd = cmd
        self.parameters = kwargs
        
    def create_input(self):
        self.template = generate_input(self.parameters)
        return self.template

    def write_input(self, template=None):
        if template:
            self.template = template

        self.infile_path = self.directory / self.infile
        self.outfile_path = self.directory / self.outfile
        # self.infolder = pathlib.Path(self.infile_path).parent()
        # self.outfolder = pathlib.Path(self.outfolder).parent()
        
        if self.directory == ".":
            self.directory = Path.cwd()

        if self.directory != Path.cwd() and not Path(self.directory).is_dir():
            os.makedirs(self.directory)

        with open(self.infile_path, 'w+') as f:
            f.write(self.template)   

    def run(self):
        if not self.cmd:
            self.cmd = 'octopus'

        self.outfile_path = self.directory / self.outfile   
        self.create_input()
        self.write_input() 

        command = f"{self.cmd} &> {self.outfile}"
        stdout, stderr = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True,
                                      shell=True, cwd=self.directory).communicate()

        print(stdout.strip(), stderr.strip()) 
        
        
    def read_info(self, info_file:Path=None, num_unoccupied:int=None):
        """ Returns number of un/occupied states and eigen values"""

        if not info_file:
            info_file = self.directory / Path('static/info')

        with open(info_file, "r") as fp:
            lines = fp.readlines()

        itr = 0
        for line in lines:
            if "Occupation" in line:
                itr_beg = itr
                break
            itr += 1
        
        itr = 0
        for line in lines:
            if "Energy" in line:
                itr_energy = itr
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
        
        if not num_unoccupied:
            num_states = itr_energy-itr_beg-2 
            self.unocc = num_states-self.occ
        else:
            self.unocc = num_unoccupied

        ### stores energy eigen values in a list
        evals = []
        itr_st = 0
        for line in lines[itr_beg+1:]:
            if itr_st == (self.occ + self.unocc):
                break
            evals.append(float(line.strip().split()[2]))
            itr_st += 1

        return [self.occ, self.unocc, evals]

    def calculate_eigen_difference(self):
        """ Returns eigen values of HOMO,LUMO and all others with HOMO as origin """

        [num_occupied, num_unoccupied, eigen_val] = self.read_info()
        print(num_occupied, num_unoccupied, eigen_val)

        homo = eigen_val[num_occupied-1]
        lumo = eigen_val[num_unoccupied-1]
        eigen_diff = [eval - homo for eval in eigen_val]

        print(homo, lumo, eigen_diff)
        return [homo, lumo, eigen_diff]

    def energy_range_to_states(self, emin, emax):
        pass

    def read_projections(self, projection_file=None,**kwargs):
        """ Reads and stores projections for given arguments

        Arguments: time_start = start of time steps, time_end = end of time steps
                   number_of_proj_(un/)occupied = number of un/occupied states to project,
                   axis = polarization vector for TD simulation as list
        """
        ########## if total occ,nunocc number not present, calculate from static/info

        from litesoph.post_processing.octopus.oct_projections import Projections

        if not projection_file:
            projection_file = self.directory / Path('td.general/projections')

        ### inputs to extract projections
        start_of_time_steps = kwargs.get('time_start', 0)
        end_of_time_steps = kwargs.get('time_end')                
        number_of_proj_occupied = kwargs.get('number_of_proj_occupied', self.occ)
        number_of_proj_unoccupied = kwargs.get('number_of_proj_unoccupied', self.unocc)
        number_of_time_steps = end_of_time_steps - start_of_time_steps + 1

        ### extra inputs to store
        axis = kwargs.get('axis', [1,0,0])

        ### gets the list of projected states from input dictionary or define the list 
        ibeg = self.occ-number_of_proj_occupied+1
        iend = self.occ+number_of_proj_unoccupied

        iproj = []
        for i in range(ibeg, iend+1):
            iproj.append(i-1)
        list_of_projected = kwargs.get('iproj', iproj)            

        ##################################################################################

        projection = Projections(number_of_time_steps, self.occ, self.unocc)
        projection.num_proj_occ = number_of_proj_occupied
        projection.num_proj_unocc = number_of_proj_unoccupied
        projection.states_projected = list_of_projected
        projection.axis = axis
        
        with open(projection_file, 'r') as f:
            projection.extract(f, start_of_time_steps)
        return projection

    def compute_populations(self, out_file, proj:Projections=None, **kwargs):
        
        ### Computing
        projection_file_path = self.directory / Path('td.general/projections')
        if not proj:
            proj = self.read_projections(projection_file_path, **kwargs)       
        popln = proj.populations(proj.states_projected)

        ### Writing to file
        with open(out_file,"w") as fp:
            proj.write_pop(popln,fp)

        return [proj,popln]

    def compute_ksd(self, proj:Projections, out_directory:Path, **kwargs):
        """ arguments: polarization axis for TD simulation"""

        import numpy as np

        ### Computing
        eigen_val = self.read_info()[2]
        (stocc, stunocc, t, dmat) = proj.denmat(proj.num_proj_occ,proj.num_proj_unocc)

        axis = kwargs.get('axis', proj.axis)
        nus, dmatw, strengthKS, transwt, strength = proj.ft_dmat(dmat.real,stocc,stunocc,axis)
       
        nus = 2.0*np.pi*nus     ## Converted to omega       

	    ## Writing to file
        enocc = []
        enuocc = []
       
        for ix in stocc:
                enocc.append(eigen_val[ix])
       
        for ix in stunocc:
                enuocc.append(eigen_val[ix])

        dmat_path = out_directory / Path("dmat.dat")
        dmatw_path = out_directory / Path("dmatw.dat")
        strength_path = out_directory / Path("strength.dat")
        transwt_path = out_directory / Path("transwt.dat")
        spectrum_prop_path = out_directory / Path("spectrum_prop.dat")
       
        fp=open(dmat_path,"w")	
        proj.write_dmat(t,dmat,enocc,enuocc,fp)
        fp.close()
       
        # axis = kwargs.get('axis', [1,0,0])
        # nus, dmatw, strengthKS, transwt, strength = proj.ft_dmat(dmat.real,stocc,stunocc,axis)
       
        # nus = 2.0*np.pi*nus     ## Convert to omega       
	   
        fp=open(dmatw_path,"w")
        proj.write_dmat(nus,dmatw,enocc,enuocc,fp)
        fp.close()

        fp=open(strength_path,"w")
        proj.write_dmatr(nus,strengthKS,enocc,enuocc,fp)
        fp.close()
       
        fp=open(transwt_path,"w")
        proj.write_dmatr(nus,transwt,enocc,enuocc,fp)
        fp.close()
       
#######  Plot the particle-hole resolved strength function 
        fp=open(spectrum_prop_path,"w")
        nuspos = np.where(nus >=0)[0]
        for iw in range(nuspos.size):
             fp.write("%10.6f %10.6f \n" %(nuspos[iw],strength[iw]))
        fp.close()
        
    def compute_dos(self, proj:Projections, out_dir:Path):
        pass
