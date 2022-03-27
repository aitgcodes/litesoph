import subprocess  
import pathlib
import sys
import paramiko
import socket
import pathlib
import subprocess
import re
from scp import SCPClient
from litesoph.simulations.esmd import Task
from litesoph.config import get_mpi_command


def get_submit_class(network=None, **kwargs):
    
    if network:
        return SubmitNetwork(**kwargs)
    else:
        return SubmitLocal(**kwargs)
    
class SubmitLocal:

    def __init__(self, task: Task , nprocessors:int) -> None:
        self.task = task
        self.engine = self.task.engine
        self.np = nprocessors
        self.command = None
        if self.np > 1:
            mpi = get_mpi_command(self.engine.NAME, self.task.lsconfig)
            print(mpi)
            self.command = mpi + ' ' + '-np' + ' ' + str(self.np)
                   
    def create_command(self):
        """creates creates the command to run the job"""
        self.command = self.engine.create_command(self.command)
    
    def prepare_input(self, path):
        """this adds in the proper path to the data file required for the job"""
        filename = self.task.project_dir.parent / self.task.filename
        path = pathlib.Path(path)
        try:
            self.input_data_files = getattr(self.task.engine, self.task.task_name)
            self.input_data_files = self.input_data_files['req']
        except AttributeError as e:
            raise AttributeError(e)

        with open(filename , 'r+') as f:
            text = f.read()
            for item in self.input_data_files:
                item = pathlib.Path(path.name) / item
                data_path = path.parent / item
                
                print(str(item))
                if data_path.is_file() or data_path.is_dir():
                    #item = item.split('/')[-1]
                    text = re.sub(str(item), str(data_path), text)
                else:
                    raise FileNotFoundError(f"The required file for this job {str(data_path)} not found.")
            f.seek(0)
            f.write(text)
            f.truncate() 

    def run_job(self):
        self.create_command()
        returncode,  result = self.execute(self.task.task_dir)
        self.task.local_cmd_out = (returncode, result[0], result[1])
        print(result)

    def execute(self, directory):
        
        print("Job started with command:", self.command)
        try:
            job = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory, shell=True)
            result = job.communicate()
        except Exception as e:
            raise Exception(e)
        else:
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
            return job.returncode, result

class SubmitNetwork:

    def __init__(self,task: Task,
                        hostname: str,
                        username: str,
                        password: str,
                        remote_path: str) -> None:

        self.task = task
        self.project_dir = self.task.project_dir
        self.engine = self.task.engine
       
        self.remote_path = remote_path

        self.network_sub = NetworkJobSubmission(hostname)
        self.network_sub.ssh_connect(username, password)
        if self.network_sub.check_file(self.remote_path):
            self.prepare_input(self.remote_path)
            self.upload_files()
        else:
            raise FileNotFoundError()
    
    def prepare_input(self, path):
        """this adds in the proper path to the data file required for the job"""
        filename = self.task.project_dir.parent / self.task.filename
        path = pathlib.Path(path)
        try:
            self.input_data_files = getattr(self.task.engine, self.task.task_name)
            self.input_data_files = self.input_data_files['req']
        except AttributeError as e:
            raise AttributeError(e)

        with open(filename , 'r+') as f:
            text = f.read()
            for item in self.input_data_files:
                item = pathlib.Path(self.task.project_dir.name) / item
                data_path = path / item
                
                text = re.sub(str(item), str(data_path), text)
            f.seek(0)
            f.write(text)
            f.truncate() 

    def upload_files(self):
        """uploads entire project directory to remote path"""
        # upload_files = [self.task.filename, self.task.bash_filename]
        # upload_files.extend(self.task.input_data_files)

        # remote_path = pathlib.Path(self.remote_path) 
        #file = pathlib.Path(self.task.project_dir.parent) / file
            
        self.network_sub.upload_files(str(self.project_dir), str(self.remote_path), recursive=True)
     

    def download_output_files(self):
        """Downloads entire project directory to local project dir."""
        remote_path = pathlib.Path(self.remote_path) / self.project_dir.name
        self.network_sub.download_files(str(remote_path),str(self.project_dir.parent),  recursive=True)

    def get_output_log(self):
        """Downloads engine log file for that particular task."""
        remote_path = pathlib.Path(self.remote_path) / self.task.output_log_file
        local_path = self.project_dir.parent / self.task.output_log_file
        self.network_sub.download_files(str(remote_path), str(local_path))


    def run_job(self, cmd):
        "This method creates the job submission command and executes the command on the cluster"
        bash_filename = pathlib.Path(self.task.bash_filename).name
        remote_path = pathlib.Path(self.remote_path) / self.task.project_dir.name
        self.command = f"cd {str(remote_path)} && {cmd} {bash_filename}"
        
        
        exit_status, ssh_output, ssh_error = self.network_sub.execute_command(self.command)
        if exit_status != 0:
            print("Error...")
            for line in ssh_error.decode(encoding='utf-8').split('\n'):
                print(line)
        else:
            print("Job submitted successfully!...")
            for line in ssh_output.decode(encoding='utf-8').split('\n'):
                print(line)

        self.task.net_cmd_out = (exit_status, ssh_output, ssh_error)
    
    def check_job_status(self) -> bool:
        """returns true if the job is completed in remote machine"""
        remote_path = pathlib.Path(self.remote_path) / self.task.filename.parent / 'Done'
        print("Checking for job completion..")
        return self.network_sub.check_file(str(remote_path))

class NetworkJobSubmission:
    """This class contain methods connect to remote cluster through ssh and perform common
    uploadig and downloading of files and also to execute command on the remote cluster."""
    def __init__(self,
                host,
                port=22):
        
        self.client = None
        self.host = host
        self.port = port
             
    def ssh_connect(self, username, password=None, pkey=None):
        "connects to the cluster through ssh."
        try:
            print("Establishing ssh connection")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if pkey:
                private_key = paramiko.RSAKey.from_private_key(self.pkey)
                self.client.connect(hostname=self.host, port=self.port, username=username, pkey=private_key)
                print("connected to the server", self.host)
            else:    
                self.client.connect(hostname=self.host, port=self.port, username=username, password=password)
                print("connected to the server", self.host)

        except paramiko.AuthenticationException:
            raise Exception("Authentication failed, please verfiy your credentials")
        except paramiko.SSHException as sshException:
            raise Exception(f"Could not establish SSH connection: {sshException} ")
        except socket.timeout as e:
            raise Exception("Connection timed out")
        except Exception as e:
     
           raise Exception(f"Exception in connecting to the server {e}")
    
    @property
    def scp(self):
        self._check_connection()
        return SCPClient(self.client.get_transport(), progress= self.progress)
    
    def disconnect(self):
        "closes the ssh session with the cluster."
        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()

    def _check_connection(self):
        "This checks whether ssh connection is active or not."
        transport = self.client.get_transport()
        if not transport.is_active() and transport.is_authenticated():
            raise Exception('Not connected to a cluster')

    def upload_files(self, local_file_path, remote_path, recursive=False):
        """This method uploads the file to remote server."""
       
        self._check_connection()
        
        try:
            self.scp.put(local_file_path, remote_path=remote_path, recursive=recursive)
        except Exception as e:
            print(e)
            raise Exception(f"Unable to upload the file to the remote server {remote_path}")

    def progress(self, filename, size, sent):
        sys.stdout.write(f"{filename}'s progress: {float(sent)/float(size)*100 : .2f}   \n") 

    def download_files(self, remote_file_path, local_path, recursive=False):
        "This method downloads the file from cluster"
        
        self._check_connection()
        try:
           self.scp.get( remote_file_path, local_path, recursive=recursive)
        except Exception as e:
            raise Exception(f"Unable to download the file from the remote server {remote_file_path}")

    def check_file(self, remote_file_path):
        "checks if the file exists in the remote path"
        self._check_connection()
        sftp = self.client.open_sftp()
        try:
           sftp.stat(remote_file_path)
        except FileNotFoundError:
            return False
        return True

    def execute_command(self, command):
        """Execute a command on the remote host.
        Return a tuple containing retruncode, stdout and stderr
        from the command."""
        
        self._check_connection()
        try:
            print(f"Executing command --> {command}")
            stdin, stdout, stderr = self.client.exec_command(command, timeout=10)
            ssh_output = stdout.read()
            ssh_error = stderr.read()
            exit_status = stdout.channel.recv_exit_status()
            if ssh_error:
                raise Exception(f"Problem occurred while running command: {command} The error is {self.ssh_error}")
        except socket.timeout as e:
            raise Exception("Command timed out.", command)
        except paramiko.SSHException:
            raise Exception("Failed to execute the command!", command)

        return exit_status, ssh_output, ssh_error



   