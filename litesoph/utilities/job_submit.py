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
import pexpect


def get_submit_class(network=None, **kwargs):
    
    if network:
        return SubmitNetwork(**kwargs)
    else:
        return SubmitLocal(**kwargs)

def execute(command, directory):
    
    result = {}
    
    if type(command).__name__ == 'str':
        command = [command]

    for cmd in command:
        out_dict = result[cmd] = {}
        print("Job started with command:", cmd)
        try:
            job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory, shell=True)
            output = job.communicate()
        except Exception as e:
            raise Exception(e)
        else:
            print("returncode =", job.returncode)
    
            if job.returncode != 0:
                print("Error...")
                for line in output[1].decode(encoding='utf-8').split('\n'):
                    print(line)
            else:
                print("job done..")
                if output[0]:
                    print("Output...")
                    for line in output[0].decode(encoding='utf-8').split('\n'):
                        print(line)
            out_dict['returncode'] = job.returncode
            out_dict['output'] = output[0]
            out_dict['error'] = output[1]
    return result
    
class SubmitLocal:

    def __init__(self, task: Task , nprocessors:int) -> None:
        self.task = task
        self.engine = self.task.engine
        self.project_dir = self.task.project_dir
        self.np = nprocessors
        self.command = None                   

    def add_proper_path(self):
        # Remove this method.
        """this adds in the proper path to the data file required for the job"""
        filename = self.project_dir.parent / self.task.filename

        with open(filename , 'r+') as f:
            text = f.read()
            for item in self.task.input_data_files:
                data_path = self.project_dir.parent / item                
                if not re.search(str(data_path), text):
                    text = re.sub(str(item), str(data_path), text)
                
            f.seek(0)
            f.write(text)
            f.truncate() 
        print('done preparing')

    def run_job(self, cmd):    
        result = execute(cmd, self.project_dir)
        self.task.local_cmd_out = (result[cmd]['returncode'], result[cmd]['output'], result[cmd]['error'])
        print(result)

class SubmitNetwork:

    def __init__(self,task: Task,
                        hostname: str,
                        username: str,
                        password: str,
                        port: int,
                        remote_path: str) -> None:

        self.task = task
        self.project_dir = self.task.project_dir

        self.username = username
        self.hostname = hostname
        self.password = password
        self.port = port
        self.remote_path = remote_path
        
        self.network_sub = NetworkJobSubmission(hostname, self.port)
        self.network_sub.ssh_connect(username, password)
        if self.network_sub.check_file(self.remote_path):
            self.add_proper_path(self.remote_path)
            self.upload_files()
        else:
            raise Exception(f"Remote path: {self.remote_path} not found.")
    
    def add_proper_path(self, path):
        """this adds in the proper path to the data file required for the job"""
        
        #Remove if statement, by using add_proper_path method in all engine 
        if "NwchemTask" == type(self.task).__name__:
            self.task.add_proper_path(self.remote_path)
            return

        filename = self.task.project_dir.parent / self.task.filename
        path = pathlib.Path(path)

        with open(filename , 'r+') as f:
            text = f.read()
            for item in self.task.input_data_files:
                data_path = path / item
                if not re.search(str(data_path), text):
                    text = re.sub(str(item), str(data_path), text)
            f.seek(0)
            f.write(text)
            f.truncate() 

    def upload_files(self):
        """uploads entire project directory to remote path"""

        (error, message) = rsync_upload_files(ruser=self.username, rhost=self.hostname,port=self.port, password=self.password,
                                                source_dir=str(self.project_dir), dst_dir=str(self.remote_path))
        #self.network_sub.upload_files(str(self.project_dir), str(self.remote_path), recursive=True)
        if error != 0:
            raise Exception(message)

    def download_output_files(self):
        """Downloads entire project directory to local project dir."""
        remote_path = pathlib.Path(self.remote_path) / self.project_dir.name
        #self.network_sub.download_files(str(remote_path),str(self.project_dir.parent),  recursive=True)
        (error, message) = rsync_download_files(ruser=self.username, rhost=self.hostname,port=self.port, password=self.password,
                                                source_dir=str(remote_path), dst_dir=str(self.project_dir.parent))
        if error != 0:
            raise Exception(message)

    def get_output_log(self):
        """Downloads engine log file for that particular task."""
        remote_path = pathlib.Path(self.remote_path) / self.task.output_log_file
        local_path = self.project_dir.parent / self.task.output_log_file
        self.network_sub.download_files(str(remote_path), str(local_path))


    def run_job(self, cmd):
        "This method creates the job submission command and executes the command on the cluster"
        remote_path = pathlib.Path(self.remote_path) / self.task.project_dir.name
        self.command = f"cd {str(remote_path)} && {cmd} {self.task.BASH_filename}"
        
        
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
        return self.network_sub.check_file(str(remote_path))

class NetworkJobSubmission:
    """This class contain methods connect to remote cluster through ssh and perform common
    uploadig and downloading of files and also to execute command on the remote cluster."""
    def __init__(self,
                host,
                port):
        
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
                private_key = paramiko.RSAKey.from_private_key(pkey)
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
        sys.stdout.write(f"{filename}'s progress: {float(sent)/float(size)*100 : .2f}   \r") 

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
            stdin, stdout, stderr = self.client.exec_command(command)
            ssh_output = stdout.read()
            ssh_error = stderr.read()
            exit_status = stdout.channel.recv_exit_status()

            try:
                if exit_status:
                    pass
            except Exception as e:
                exit_status = -1

            if ssh_error:
                print(ssh_error)
                #raise Exception(f"Problem occurred while running command: {command} The error is {ssh_error}")
        except socket.timeout as e:
            exit_status = -1
            pass
            #raise Exception("Command timed out.", command)
        except paramiko.SSHException:
            raise Exception("Failed to execute the command!", command)

        return exit_status, ssh_output, ssh_error

def rsync_upload_files(ruser, rhost,port, password, source_dir, dst_dir):
    
    cmd = f'''rsync -av -e "ssh -p {port}" {source_dir} {ruser}@{rhost}:{dst_dir}'''
    print(cmd)
    (error, message) = execute_rsync(cmd, passwd=password)
    return (error, message)

def rsync_download_files(ruser, rhost,port, password, source_dir, dst_dir):
    
    cmd = f'''rsync -av -e "ssh -p {port}" {ruser}@{rhost}:{source_dir} {dst_dir}'''

    (error, message) = execute_rsync(cmd, passwd=password)
    return (error, message)

def execute_rsync(cmd,passwd, timeout=3600):
    intitial_response = ['Are you sure', 'password:', pexpect.EOF]
    
    ssh = pexpect.spawn(cmd,timeout=timeout)
    i = ssh.expect(intitial_response, timeout=10)
    if i == 0 :
        T = ssh.read(100)
        ssh.sendline('yes')
        ssh.expect('password:', Timeout=10)
        ssh.sendline(passwd)
    elif i == 1:
        ssh.sendline(passwd)
    else:
        str1 = str(ssh.before)
        return (-3, 'Error: Unknown:'+ str1)

    possible_response = ['password:', pexpect.EOF]
    i = ssh.expect(possible_response, timeout=5)

    if i == 0:
        return (-4, "Error: Incorrect password.")
    else:
        output = str(ssh.before)
        return (0, output)
    
        
       