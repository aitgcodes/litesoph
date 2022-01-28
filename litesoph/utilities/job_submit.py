from configparser import ConfigParser, NoOptionError

from litesoph.simulations.engine import EngineStrategy
import subprocess  
import pathlib

import paramiko
import socket
import pathlib
import subprocess

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
            print("Engine specific mpi is not given, first option from mpi section will be used.")
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

        self.network_sub = NetworkJobSubmission(hostname)
        self.network_sub.ssh_connect(username, password)
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
            try:
                self.network_sub.upload_files(file, self.remote_path)
                print(f"{file} uploaded to remote path {self.remote_path} of cluster")
            except Exception as e:
                raise(e)


    def run_job(self):
        "This method creates the job submission command and executes the command on the cluster"
        bash_filename = pathlib.Path(self.upload_files['run_script']).name
        #bash_filename = pathlib.Path(self.remote_path) / bash_filename
        self.command = f"cd {self.remote_path} \n qsub {bash_filename}"

        self.network_sub.execute_command(self.command)
        if self.network_sub.exit_status != 0:
            print("Error...")
            for line in self.network_sub.ssh_error.decode(encoding='utf-8').split('\n'):
                print(line)
        else:
            print("Job submitted successfully!...")
            for line in self.network_sub.ssh_output.decode(encoding='utf-8').split('\n'):
                print(line)

class NetworkJobSubmission:
    """This class contain methods connect to remote cluster through ssh and perform common
    uploadig and downloading of files and also to execute command on the remote cluster."""
    def __init__(self,
                host,
                port=22):
        
        self._client = None
        self.host = host
        self.port = port
        self.ssh_output = None
        self.ssh_error = None
        self.exit_status = None
             
    def ssh_connect(self, username, password=None, pkey=None):
        "connects to the cluster through ssh."
        try:
            print("Establishing ssh connection")
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if pkey:
                private_key = paramiko.RSAKey.from_private_key(self.pkey)
                self._client.connect(hostname=self.host, port=self.port, username=username, pkey=private_key)
                print("connected to the server", self.host)
            else:    
                self._client.connect(hostname=self.host, port=self.port, username=username, password=password)
                print("connected to the server", self.host)

        except paramiko.AuthenticationException:
            raise Exception("Authentication failed, please verfiy your credentials")
        except paramiko.SSHException as sshException:
            raise Exception(f"Could not establish SSH connection: {sshException} ")
        except socket.timeout as e:
            raise Exception("Connection timed out")
        except Exception as e:
            raise Exception(f"Exception in connecting to the server {e}")
    
    def close(self):
        "closes the ssh session with the cluster."
        self._client.close()

    def _check_connection(self):
        "This checks whether ssh connection is active or not."
        transport = self._client.get_transport()
        if not transport.is_active() and transport.is_authenticated():
            raise Exception('Not connected to a cluster')

    def upload_files(self, local_file_path, remote_path):
        """This method uploads the file to remote server."""
       
        self._check_connection()
        sftp = self._client.open_sftp()
        
        try:
            filename = pathlib.Path(local_file_path).name
            remote_path = pathlib.Path(remote_path) 
            for directory in remote_path.parts:
                if directory not in sftp.listdir():
                    sftp.mkdir(directory)
                sftp.chdir(directory)
            sftp.put(local_file_path, filename)  # for the put function to work file name should be added to the remote path
        except Exception as e:
            print(e)
            raise Exception(f"Unable to upload the file to the remote server {remote_path}")

    
    def download_file(self, remote_file_path, local_path):
        "This method downloads the file from cluster"
        
        self._check_connection()
        sftp = self._client.open_sftp()
        try:
            sftp.get(local_path, remote_file_path)
        except Exception as e:
            raise Exception(f"Unable to download the file to the remote server {remote_file_path}")

    def check_file(self, remote_file_path):
        "checks if the file exists in the remote path"
        self._check_connection()
        sftp = self._client.open_sftp()
        try:
            sftp.stat(remote_file_path)
        except FileNotFoundError:
            return False
        return True

    def execute_command(self, command):
        """Execute a command on the remote host.
        Return a tuple containing retruncode, stdout and stderr
        from the command."""
        
        self.ssh_output = None
        self._check_connection()
        try:
            print(f"Executing command --> {command}")
            stdin, stdout, stderr = self._client.exec_command(command, timeout=10)
            self.ssh_output = stdout.read()
            self.ssh_error = stderr.read()
            self.exit_status = stdout.channel.recv_exit_status()
            if self.ssh_error:
                raise Exception(f"Problem occurred while running command: {command} The error is {self.ssh_error}")
        except socket.timeout as e:
            raise Exception("Command timed out.", command)
        except paramiko.SSHException:
            raise Exception("Failed to execute the command!", command)

        