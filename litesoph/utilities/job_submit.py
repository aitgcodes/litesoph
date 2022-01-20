from configparser import ConfigParser, NoOptionError

from matplotlib.pyplot import vlines
from litesoph.simulations.engine import EngineStrategy
import subprocess  
import pathlib

import paramiko
import socket
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

    def __init__(self, engine: EngineStrategy,
                        configs: ConfigParser, 
                        hostname: str,
                        username: str,
                        password: str,
                        remote_path: str,
                        upload_files: dict) -> None:

        super().__init__(engine, configs)
       
        self.remote_path = remote_path
        self.upload_files = upload_files
        self.validate_upload_files()

        self.network_sub = NetworkJobSubmission(hostname, username, password=password)
        self.transfer_files()

        

    def validate_upload_files(self):
        self.upfiles = []
        for key, value in self.upload_files.items():
            if isinstance(value, list):
                self.upfiles.extend(value)
            else:
                self.upfiles.append(value)

        for item in self.upfiles:
            if not pathlib.Path(item).is_file():
                raise FileNotFoundError(f"Unable to find {value} ")
    
    def transfer_files(self):
        for file in self.upfiles:
            if self.network_sub.upload_files(file, self.remote_path):
                print(f"{file} uploaded to remote path {self.remote_path} of cluster")


    def run_job(self):

        bash_filename = pathlib.Path(self.upload_files['run_script']).name
        bash_filename = pathlib.Path(self.remote_path) / bash_filename
        self.command = [f"cd {self.remote_path} \n qsub {bash_filename}"]

        if self.network_sub.execute_command(self.command):
            if self.network_sub.exit_status != 0:
                print("Error...")
                for line in self.network_sub.ssh_error.decode(encoding='utf-8').split('\n'):
                    print(line)
            else:
                print("Job submitted successfully!...")
                for line in self.network_sub.ssh_output.decode(encoding='utf-8').split('\n'):
                    print(line)

class NetworkJobSubmission:

    def __init__(self,
                host,
                username,
                password=None,
                pkey = None,
                time_out = None,
                port=None):
        
        self.client = None
        self.host = host
        self.username = username
        self.password = password
        self.pkey = pkey
        self.time_out = time_out

        if port:
            self.port = port
        else:
            self.port = 22

        self.ssh_output = None
        self.ssh_error = None
        self.exit_status = None
        # self.mast_dic = mast_dic
        # self.run_script = pathlib.Path(self.mast_dic['run_script']).name
             
    def ssh_connect(self):
        "Login to cluster"
        try:
            print("Establishing ssh connection")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if not self.password:
                private_key = paramiko.RSAKey.from_private_key(self.pkey)
                self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=private_key, timeout=self.time_out, allow_agent=False, look_for_keys=False)
                print("connected to the server", self.host)
            else:    
                self.client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password, timeout=self.time_out, allow_agent=False, look_for_keys=False)
                print("connected to the server", self.host)

        except paramiko.AuthenticationException:
            print("Authentication failed, please verfiy your credentials")
            result_flag = False
        except paramiko.SSHException as sshException:
            print(f"Could not establish SSH connection: {sshException} ")
            result_flag = False
        except socket.timeout as e:
            print("Connection timed out")
            result_flag = False
        except Exception as e:
            print("Exception in connecting to the server")
            print(e)
            result_flag = False
            self.client.close()
        else:
            result_flag = True
        
        return result_flag

    def upload_files(self, local_file_path, remote_file_path, recursive=False):
        "This method uploads the file to remote server"
        result_flag = True
        try:
            if self.ssh_connect():
                with SCPClient(self.client.get_transport()) as scp:
                    scp.put(local_file_path, remote_file_path, recursive)
                self.client.close()
            else:
                print("Could not establish SSH connection")
                result_flag = False

        except Exception as e:
            print("\nUnable to upload the file to the remote server", local_file_path)
            print(e)
            result_flag = False
            self.client.close()

        return result_flag

    
    def download_file(self, remote_file_path, local_file_path,  recursive=False):
        "This method downloads the file from cluster"
        result_flag = True
        try:
            if self.ssh_connect():
                with SCPClient(self.client.get_transport()) as scp:
                    scp.get(remote_file_path, local_file_path,  recursive)
                self.client.close()
            else:
                print("Could not establish SSH connection")
                result_flag = False

        except Exception as e:
            print("\nUnable to download the file to the remote server", remote_file_path)
            print(e)
            result_flag = False
            self.client.close()

        return result_flag



    def execute_command(self, commands):
        """Execute a command on the remote host.
        Return a tuple containing retruncode, stdout and stderr
        from the command."""
        
        self.ssh_output = None
        result_flag = True
        try:
            if self.ssh_connect():
                for command in commands:
                    print(f"Executing command --> {command}")
                    stdin, stdout, stderr = self.client.exec_command(command, timeout=10)
                    self.ssh_output = stdout.read()
                    self.ssh_error = stderr.read()
                    self.exit_status = stdout.channel.recv_exit_status()
                    if self.ssh_error:
                        print(f"Problem occurred while running command: {command} The error is {self.ssh_error}")
                        result_flag = False
                    else:
                        print("Command execution completed successfully", command)
                self.client.close()
            else:
                print("Could not establish SSH connection")
                result_flag = False
        except socket.timeout as e:
            print("Command timed out.", command)
            self.client.close()
            result_flag = False
        except paramiko.SSHException:
            print("Failed to execute the command!", command)
            self.client.close()
            result_flag = False

        return result_flag
        