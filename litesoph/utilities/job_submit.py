from configparser import ConfigParser, NoOptionError
from re import T
from litesoph.simulations.engine import EngineStrategy
import subprocess  
import pathlib

import paramiko
import pathlib
import subprocess
from scp import SCPClient

def get_submit_class(network=None, **kwargs):
    
    if network:
        return SubmitNetwork(**kwargs)
    else:
        return SubmitLocal(**kwargs)

def get_mpi_command(engine: EngineStrategy, configs: ConfigParser):
    
    name = type(engine).__name__.lower()
    name = name[6:]  
    name = name + '_mpi'
    
    if configs.items('mpi'):
        try:
            mpi = configs.get('mpi', name)
        except NoOptionError:
            print("engine specific mpi is not given first option from mpi section will used.")
            mpi = list(configs.items('mpi'))[0][1]
        finally:
            return mpi
    else:
        print("Please set path to mpi in lsconfig.ini")


class JobSubmit:
    
    def __init__(self, engine: EngineStrategy, configs: ConfigParser, keyword:str=None) -> None:
        self.engine = engine
        self.configs = configs
        
    def run_job(self):
        pass
      
    
class SubmitLocal(JobSubmit):

    def __init__(self, engine: EngineStrategy, configs: ConfigParser, nprocessors:int) -> None:
        super().__init__(engine, configs)
        self.np = nprocessors
        self.command = None
        if self.np > 1:
            mpi = get_mpi_command(engine, configs)
            self.command = mpi + ' ' + '-np' + ' ' + str(self.np)
            
           
    def create_command(self):
        self.command = self.engine.create_command(self.command)
    
    def run_job(self,directory):
        job = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory, shell=True)
        result = job.communicate()
        print("Job started with command:", self.command)
        print("returncode =", job.returncode)
       
        if job.returncode != 0:
            print("Error...")
            for line in result[1].decode(encoding='utf-8').split('\n'):
                print(line)
        else:
            print("job done..")
            if result[0]:
                print("Output...")
                for line in result[0].decode(encoding='utf-8').split('\n'):
                    print(line)
        return result
       
       

class SubmitNetwork(JobSubmit):

    def __init__(self, engine: EngineStrategy, configs: ConfigParser, nprocessors:int) -> None:
        super().__init__(engine, configs)
        self.np = nprocessors
        self.command = None
    


class NetworkJobSubmission:

    def __init__(self ,mast_dic):

        self.mast_dic = mast_dic
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
             
    def ssh_connect(self,host,user,password):
        self.client.connect(host, username=user, password=password)

    def close(self):
        self.client.close()

    def transfer_files(self):

        with SCPClient(self.client.get_transport()) as scp:
            scp.put(self.mast_dic['run_script'], self.mast_dic['remote_path'])
            scp.put(self.mast_dic['inp'], self.mast_dic['remote_path'])
            # copy data from remote cluster to the local machine
            # scp.get(mast_dic['remote_path'], mast_dic['local_path'])

    def submit_job(self):

        # Submit Engine job by running a remote 'qsub' command over SSH
        stdin, stdout, stderr = self.client.exec_command(self.mast_dic['cd']+ '\n'+ self.mast_dic['cmd'])

        # Show the standard output and error of our job
        print("Standard output:")
        print(stdout.read())
        print("Standard error:")
        print(stderr.read())
        print("Exit status: {}".format(stdout.channel.recv_exit_status()))