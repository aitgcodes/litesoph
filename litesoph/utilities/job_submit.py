from configparser import ConfigParser
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

class JobSubmit:
    
    def __init__(self, engine: EngineStrategy, configs: ConfigParser, keyword:str=None) -> None:
        self.engine = engine
        self.configs = configs
        if configs.items('mpi'):
            self.mpi_cmd = list(configs.items('mpi'))[0][1]
            self.mpi_cmd = [self.mpi_cmd, '-np']
        
    def run_job(self, command, directory):
        job = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory)
        
        return job
      
    
class SubmitLocal(JobSubmit):

    def __init__(self, engine: EngineStrategy, configs: ConfigParser, nprocessors:int) -> None:
        super().__init__(engine, configs)
        self.np = nprocessors
        self.command = []
        if self.np > 1:
            self.command.extend(self.mpi_cmd)
            self.command.append(str(self.np))
           
    def create_command(self):
        self.command = self.engine.create_command(self.command)
    
    def run_job(self,directory):
        self.j = super().run_job(self.command, directory)
        self.result = self.j.communicate()[1]
       

# class SubmitNetwork(JobSubmit):
#     pass            



class NetworkJobSubmission():
    def __init__(self, host, user, pswd, mast_dic):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Establish SSH connection
        client.connect(host, username=user, password=pswd)

        # copy the file across
        with SCPClient(client.get_transport()) as scp:
            scp.put(mast_dic['run_script'], mast_dic['remote_path'])
            scp.put(mast_dic['inp'], mast_dic['remote_path'])
            # copy data from remote cluster to the local machine
            # scp.get(mast_dic['remote_path'], mast_dic['local_path'])


        # Submit Engine job by running a remote 'qsub' command over SSH
        stdin, stdout, stderr = client.exec_command(mast_dic['cd']+ '\n'+ mast_dic['cmd'])

        # Show the standard output and error of our job
        print("Standard output:")
        print(stdout.read())
        print("Standard error:")
        print(stderr.read())
        print("Exit status: {}".format(stdout.channel.recv_exit_status()))

        client.close()