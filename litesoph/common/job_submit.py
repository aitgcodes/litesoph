import subprocess  
import pathlib
import sys
import paramiko
import socket
import pathlib
import subprocess
import re
from scp import SCPClient
import pexpect


def execute_cmd_local(command, directory):
    """
    Function to execute command locally

    Parameter:
    command: command to be run
    directory: directory in which command need to be run
    """
    
    result = {}
    
    if type(command).__name__ == 'str':
        command = [command]

    for cmd in command:
        out_dict = result[cmd] = {}
        try:
            job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory, shell=True)
            output = job.communicate()
        except Exception:
            raise 
        else:
            if job.returncode != 0:
                print("Error...")
            else:
                pass
            
            out_dict['returncode'] = job.returncode
            out_dict['pid'] = job.pid
            out_dict['output'] = output[0].decode(encoding='utf-8')
            out_dict['error'] = output[1].decode(encoding='utf-8')
    return result

def execute_cmd_remote(command,passwd, timeout=None):
    """
    Function to run command on remote machine through local machine, Thus function requires password of remote machine
    
    paramter:

    command: command to be run on remote machine
    password: password of remote machine
    timeout: timeperiod in seconds password prompt waits
    """
    intitial_response = ['Are you sure', 'assword','[#\$] ', pexpect.EOF]
    
    ssh = pexpect.spawn(command,timeout=timeout)
    i = ssh.expect(intitial_response)
    if i == 0 :
        T = ssh.read(100)
        ssh.sendline('yes')
        ssh.expect('assword:')
        ssh.sendline(passwd)
    elif i == 1:
        ssh.sendline(passwd)
    elif i==2:
        prompt = ssh.after  
    else:
        str1 = str(ssh.before)
        return (-3, 'Error: Unknown:'+ str1)

    possible_response = ['assword:', pexpect.EOF]
    i = ssh.expect(possible_response, timeout=5)

    if i == 0:
        return (-4, "Error: Incorrect password.")
    else:
        output = ssh.before.decode('utf-8')
        return (0, output)
    
class SubmitLocal:

    def __init__(self, task) -> None:
        self.task = task
        self.task_info = task.task_info
        self.project_dir = self.task.project_dir
        self.command = None     
        self.job_id=None              

    def run_job(self, cmd): 
        self.task_info.job_info.submit_mode = 'local' 
        result = execute_cmd_local(cmd, self.project_dir)
        self.task_info.job_info.id = result[cmd]['pid']
        self.task_info.job_info.job_returncode = result[cmd]['returncode']
        self.task_info.job_info.output = result[cmd]['output']
        self.task_info.job_info.error = result[cmd]['error']

    def get_job_status_local(self, job_id):   
        """
        get the running status of submitted job at remote
        """
        job_id= self.job_id
        cmd_check_running_process=f"ps aux | grep {job_id}|grep -v grep; if [ $? -eq 0 ]; then echo Job is running; else echo No Job found; fi"
        result=execute_cmd_local(cmd_check_running_process,self.project_dir)
        error=result[cmd_check_running_process]['error']    
        message=result[cmd_check_running_process]['output']         
        return (error, message)

    def check_job_status(self) -> bool:
        """returns true if the job is completed in remote machine"""
        # rpath = pathlib.Path(self.remote_path) / self.task.network_done_file.relative_to(self.project_dir.parent)
        # return self.network_sub.check_file(str(rpath))        
        job_id=self.task_info.uuid
        job_done_file = self.task.task_dir / f"Done_{job_id}"
        job_done_status = job_done_file.exists()
        return job_done_status
    
    def get_fileinfo_local(self):   
        """
        get the generated file information during runtime
        """
        cmd_filesize=f'find {self.project_dir}  -type f -exec du --human {{}} + | sort --human --reverse'
        result=execute_cmd_local(cmd_filesize,self.project_dir)
        error=result[cmd_filesize]['error']    
        message=result[cmd_filesize]['output']  

        cmd_project_size=f'cd {self.project_dir}; du -s'

        result= execute_cmd_local(cmd_project_size,self.project_dir)  
        error=result[cmd_project_size]['error']    
        message=result[cmd_project_size]['output']

        project_size= [int(s) for s in message.split() if s.isdigit()]
        self.project_size_GB=project_size[0]/(1024*1024)
    
        return (error, message)
    
    def generate_list_of_files_local(self):
        cmd=f'cd {self.project_dir}; find "$PWD"  -type f > listOfFiles_local.list'        
        result=execute_cmd_local(cmd,self.project_dir)
        error=result[cmd]['error']    
        message=result[cmd]['output']            
        return (error, message)

    def get_list_of_files_local(self):
        listOfFiles_path=f'{self.project_dir}/listOfFiles_local.list'   
        from litesoph.common.lfm_database import lfm_file_info_dict
        lfm_file_info=lfm_file_info_dict()
        file_info_dict=create_file_info(read_file_info_list(listOfFiles_path),lfm_file_info)        
        # files_dict=filter_dict(file_info_dict,{'file_type':['input_file','property_file']})        
        files_list=list(file_info_dict.keys())
        return files_list        

    def view_specific_file_local(self,file):
        cmd_view_local=f"cat {file}"
        result=execute_cmd_local(cmd_view_local,self.project_dir)
        error=result[cmd_view_local]['error']    
        message=result[cmd_view_local]['output']            
        return (error, message)
    
    def kill_job_local(self,job_id,scheduler,scheduler_stat_cmd,scheduler_kill_cmd):
        """
        kill the running job at local
        """
        if scheduler=='bash':
            cmd_kill=f"ps aux | grep -w {job_id}|grep -v grep; if [ $? -eq 0 ]; pkill -ecf {job_id}; then echo Job killed; else echo No Job found; fi"
        else:
            cmd_kill=f"{scheduler_stat_cmd} | grep -w {job_id}|grep -v grep; if [ $? -eq 0 ]; {scheduler_kill_cmd} {job_id}; then echo Job killed {job_id}; else echo No Job found; fi"        
        
        result=execute_cmd_local(cmd_kill,self.project_dir)
        error=result[cmd_kill]['error']    
        message=result[cmd_kill]['output']            
        return (error, message)       
        
class SubmitNetwork:

    def __init__(self,task,
                    hostname: str,
                    username: str,
                    password: str,
                    port: int,
                    remote_path: str,
                    pkey_file:str, #
                    passwordless_ssh:bool,
                    ls_file_mgmt_mode=False,) -> None: 

        self.task = task
        self.task_info = task.task_info
        self.task_info.state.network = True
        self.project_dir = self.task.project_dir.parent 
        self.username = username
        self.hostname = hostname
        self.password = password
        self.pkey_file=pathlib.Path(pkey_file)
        self.port = port
        self.remote_path = remote_path
        self.passwordless_ssh=passwordless_ssh   
        self.ls_file_mgmt_mode=ls_file_mgmt_mode
        self.network_sub = NetworkJobSubmission(hostname, self.port)
        
        if passwordless_ssh==True:
            self.network_sub.ssh_connect(username,pkey_file)
        else:
            self.network_sub.ssh_connect(username, password)
        
        if self.network_sub.check_file(self.remote_path):
            self.task.add_proper_path(self.remote_path)
            self.upload_files()        
        else:
            raise FileNotFoundError(f"Remote path: {self.remote_path} not found.")
        self.task_info.job_info.submit_mode = 'remote'

    def upload_files(self):
        """uploads entire project directory to remote path"""

        include = ['*/','*.xyz', '*.sh', f'{self.task.NAME}/**']
        (error, message) = rsync_upload_files(ruser=self.username, rhost=self.hostname,port=self.port, password=self.password,
                                                source_dir=str(self.project_dir), dst_dir=str(self.remote_path),
                                                include=include, exclude='*')
        #self.network_sub.upload_files(str(self.project_dir), str(self.remote_path), recursive=True)
        if error != 0:
            raise Exception(message)

    def download_output_files(self):
        """Downloads entire project directory to local project dir."""
        remote_path = pathlib.Path(self.remote_path) / self.project_dir.name
        #self.network_sub.download_files(str(remote_path),str(self.project_dir.parent),  recursive=True)
        if (self.ls_file_mgmt_mode==False):
            (error, message) = rsync_download_files(ruser=self.username, rhost=self.hostname,port=self.port, password=self.password,
                                                source_dir=str(remote_path), dst_dir=str(self.project_dir.parent))
        
        elif (self.ls_file_mgmt_mode==True):
            (error, message)=download_files_from_remote(self.hostname,self.username,self.port,self.password,remote_path,self.project_dir)

        elif error != 0:
            raise Exception(message)

    def get_output_log(self):
        """Downloads engine log file for that particular task."""
        wfdir = pathlib.Path(self.task.project_dir)
        proj_name = pathlib.Path(self.project_dir).name
        wf_name = wfdir.name
        engine_log = pathlib.Path(self.task.task_info.output['txt_out'])
        # rpath = pathlib.Path(self.remote_path) / engine_log.relative_to(self.project_dir.parent)
        rpath = pathlib.Path(self.remote_path) / proj_name / wf_name / engine_log
        lpath = wfdir / engine_log
        # self.network_sub.download_files(str(rpath), str(engine_log))
        self.network_sub.download_files(str(rpath), str(lpath))
        
    def run_job(self, cmd):
        "This method creates the job submission command and executes the command on the cluster"
        remote_path = pathlib.Path(self.remote_path) / self.task.project_dir.relative_to(self.project_dir.parent)
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
        
        self.task_info.job_info.submit_returncode = exit_status
        self.task_info.job_info.submit_output= ssh_output.decode(encoding='utf-8')
        self.task_info.job_info.submit_error = ssh_error.decode(encoding='utf-8')

    def check_job_status(self) -> bool:
        """returns true if the job is completed in remote machine"""
        # rpath = pathlib.Path(self.remote_path) / self.task.network_done_file.relative_to(self.project_dir.parent)
        # return self.network_sub.check_file(str(rpath))        
        job_id=self.task_info.uuid    
        job_done_file = pathlib.Path(self.remote_path) / self.task.network_done_file.parent.relative_to(self.project_dir.parent)/ f"Done_{job_id}"
        job_done_status=self.network_sub.check_file(str(job_done_file))           
        return job_done_status

    def get_fileinfo_remote(self):   
        """
        get the generated file information during runtime
        """
        cmd_create_listOfFiles_at_remote=f'ssh -p {self.port} {self.username}@{self.hostname} "cd {self.remote_path}; find "$PWD"  -type f > listOfFiles.list"'     
        cmd_listOfFiles_to_local=f"rsync --rsh='ssh -p{self.port}' {self.username}@{self.hostname}:{self.remote_path}/listOfFiles.list {self.project_dir}"        
        (error, message)=execute_cmd_remote(cmd_create_listOfFiles_at_remote, self.password, timeout=None)
        (error, message)=execute_cmd_remote(cmd_listOfFiles_to_local, self.password, timeout=None)
  
        cmd_filesize=f'"cd {self.remote_path}; find "$PWD"  -type f -exec du --human {{}} + | sort --human --reverse"'
        cmd_filesize=f'ssh -p {self.port} {self.username}@{self.hostname} {cmd_filesize}'        
        (error, message)= execute_cmd_remote(cmd_filesize,self.password, timeout=None)  

        cmd_project_size=f'cd {self.remote_path}; du -s'
        cmd_project_size=f'ssh -p {self.port} {self.username}@{self.hostname} {cmd_project_size}'   
       
        (error, message)= execute_cmd_remote(cmd_project_size,self.password, timeout=None)  
        project_size= [int(s) for s in message.split() if s.isdigit()]
        self.project_size_GB=project_size[0]/(1024*1024)
        return (error, message)
            
    def get_job_status_remote(self):
        
        job_id=self.task_info.uuid        
        job_start_file = pathlib.Path(self.remote_path) / self.task.network_done_file.parent.relative_to(self.project_dir.parent) / f"Start_{job_id}"
        job_start_status=self.network_sub.check_file(str(job_start_file))
        job_done_file = pathlib.Path(self.remote_path) / self.task.network_done_file.parent.relative_to(self.project_dir.parent)/ f"Done_{job_id}"
        job_done_status=self.network_sub.check_file(str(job_done_file))
            
        if job_start_status==False:
            job_status="Job Not Started Yet"
        
        elif job_start_status==True and job_done_status==False: 
            job_status="Job in Progress"
        
        elif job_start_status==True and job_done_status==True:
            job_status="Job Done"    

        else:
            job_status="SSH session not active"

        return job_status

    def kill_job_remote(self,job_id,scheduler,scheduler_stat_cmd,scheduler_kill_cmd):
        """
        kill the running job at remote
        """
        if scheduler=='bash':
            cmd_kill=f"ps aux | grep -w {job_id}|grep -v grep; if [ $? -eq 0 ]; pkill -ecf {job_id}; then echo Job killed; else echo No Job found; fi"
            cmd=f'ssh -p {self.port} {self.username}@{self.hostname} {cmd_kill}'    
        else:
            cmd_kill=f"{scheduler_stat_cmd} | grep -w {job_id}|grep -v grep; if [ $? -eq 0 ]; {scheduler_kill_cmd} {job_id}; then echo Job killed {job_id}; else echo No Job found; fi"        
            cmd=f'ssh -p {self.port} {self.username}@{self.hostname} {cmd_kill}'            
        
        (error, message)=execute_cmd_remote(cmd,self.password)          
        return (error, message)

    def download_all_files_remote(self):
        """
        download all files from remote
        """
        remote_path = pathlib.Path(self.remote_path) / self.project_dir.name
        (error, message)=download_files_from_remote(self.hostname,self.username,self.port,self.password,remote_path,self.project_dir)
        return (error, message)

    def get_list_of_files_remote(self):
        listOfFiles_path=f'{self.project_dir}/listOfFiles.list'   
        from litesoph.common.lfm_database import lfm_file_info_dict
        lfm_file_info=lfm_file_info_dict()
        file_info_dict=create_file_info(read_file_info_list(listOfFiles_path),lfm_file_info)        
        # files_dict=filter_dict(file_info_dict,{'file_type':['input_file','property_file','script_generated_outfile']})        
        files_list=list(file_info_dict.keys())
        return files_list        

    def download_specific_file_remote(self,file_path,priority1_files_dict):
        """
        download specific file(s) from remote
        """
        (error, message)=file_transfer(file_path,priority1_files_dict,self.hostname,self.username,self.port,self.password,self.remote_path,self.project_dir)        
        return (error, message)

    def view_specific_file_remote(self,file):
        cmd_view_remote=f"cat {file}"
        cmd_view_remote=f'ssh -p {self.port} {self.username}@{self.hostname} {cmd_view_remote}'   
        (error, message)=execute_cmd_remote(cmd_view_remote, self.password)
        return (error, message)

class NetworkJobSubmission:
    """This class contain methods connect to remote cluster through ssh and perform common
    uploadig and downloading of files and also to execute command on the remote cluster."""
    def __init__(self,
                host,
                port,
                ls_file_mgmt_mode=True):
        
        self.client = None
        self.host = host
        self.port = port
        self.ls_file_mgmt_mode=ls_file_mgmt_mode
                 
    def ssh_connect(self, username, password=None, pkey_file=None):
        "connects to the cluster through ssh."
        try:
            print("Establishing ssh connection")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if pkey_file:
                # private_key = paramiko.RSAKey.from_private_key(pkey)
                private_key = paramiko.RSAKey.from_private_key_file(pkey_file)
                
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
            print("output :",ssh_output)

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


def rsync_upload_files(ruser, rhost,port, password, source_dir, dst_dir, include=None, exclude= None):

    return rsync_cmd(ruser, rhost, port, password, source_dir, dst_dir, include=include, exclude=exclude)

def rsync_download_files(ruser, rhost, port, password, source_dir, dst_dir, include=None, exclude=None):
    
    return rsync_cmd(ruser, rhost, port, password, source_dir, dst_dir, include=include, exclude=exclude,upload=False)

def rsync_cmd(ruser, rhost, port, password, source_dir, dst_dir,include=None, exclude=None, upload=True):
    
    cmd = []
    cmd.append(f'''rsync -av -e "ssh -p {port}"''') 

    def append(name, option):
        if type(option) == str:
            option = [option]
        cmd.append(((f"--{name}=" + "'{}' ") * len(option)).format(*option))

    if bool(include) and bool(exclude):
        for name, option in [('include', include), ('exclude', exclude)]:
            append(name, option)
   
    if upload:
        cmd.append(f"{source_dir} {ruser}@{rhost}:{dst_dir}")   
    else:
        cmd.append(f"{ruser}@{rhost}:{source_dir} {dst_dir}")
    
    cmd = ' '.join(cmd)
    (error, message) = execute_cmd_remote(cmd, passwd=password)
    
    return (error, message)

def download_files_from_remote(host,username,port,passwd,remote_proj_dir,local_proj_dir):   
    """
   1. get the list of files from remote directory
   2. convert the list of files into file-metadata-dictionary 
   3. filter the dictionary into sub-dictionary of priority-levels
   3. give each file priority level according to the assigned tags of files 
   4. classify the files on the basis of priority and transfer priority1 files first
   4. determine the method to transfer the files
   5. transfer the file
    """
    print("\nlitesoph file management activated !!")

    from litesoph.common.lfm_database import lfm_file_info_dict
    lfm_file_info=lfm_file_info_dict()

    cmd_create_listOfFiles_at_remote=f'ssh -p {port} {username}@{host} "cd {remote_proj_dir}; find "$PWD"  -type f > listOfFiles_remote.list"'     
    cmd_listOfFiles_to_local=f"rsync --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/listOfFiles_remote.list {local_proj_dir}"
    # cmd_remove_listOfFiles_remote=f'ssh -p {port} {username}@{host} "cd {remote_proj_dir}; rm listOfFiles.list'

    (error, message)=execute_cmd_remote(cmd_create_listOfFiles_at_remote, passwd)
    (error, message)=execute_cmd_remote(cmd_listOfFiles_to_local, passwd)
    # (error, message)=execute_cmd_remote(cmd_remove_listOfFiles_remote, passwd)
    
    listOfFiles_path=f'{local_proj_dir}/listOfFiles_remote.list'    
    file_info_dict=create_file_info(read_file_info_list(listOfFiles_path),lfm_file_info)

    # if keys_exists(file_info_dict,'file_relevance')==False:

    priority1_files_dict=filter_dict(file_info_dict,{'file_relevance':['very_impt']})
    priority2_files_dict=filter_dict(file_info_dict,{'file_relevance':['impt']})
    
    for file in list(priority1_files_dict.keys()):
        (error, message)=file_transfer(file,priority1_files_dict,host,username,port,passwd,remote_proj_dir,local_proj_dir)
    
    for file in list(priority2_files_dict.keys()):
        (error, message)=file_transfer(file,priority2_files_dict,host,username,port,passwd,remote_proj_dir,local_proj_dir)

    # cmd_remove_listOfFiles_local=f'rm {local_proj_dir}/listOfFiles.list'
    # (error, message)=execute_cmd_remote(cmd_remove_listOfFiles_local, passwd)
    
    return (error, message)
    
def add_element(dict, key, value):
    if key not in dict:
        dict[key] = {}
    dict[key] = value
    
def create_file_info(list_of_files_in_remote_dir,lfm_file_info):

    file_info_dict={}
    default_metadata={'file_relevance':None,
                    'file_lifetime':None,
                    'file_type':None,
                     'transfer_method':None}
    
    for i in range(len(list_of_files_in_remote_dir)):
        file_extension = pathlib.Path(list_of_files_in_remote_dir[i]).suffix

        if file_extension in list(lfm_file_info.keys()):
            metadata=lfm_file_info[file_extension]
            add_element(file_info_dict, list_of_files_in_remote_dir[i], metadata)
        else:
            add_element(file_info_dict, list_of_files_in_remote_dir[i], default_metadata)
    
    return file_info_dict

def keys_exists(dictionary, keys):
    """function to check if keys exist or not in a dictionary
    
    parameter:

    dictionary: dictionary on which keys needs to be check
    keys: list of keys
    
    """
    nested_dict = dictionary
    for key in keys:
        try:
            nested_dict = nested_dict[key]
        except KeyError:
            return False
    return True

def filter_dict(dictionary,dict_filter_key_value):
    """
    function to filter dictionary using key-value pairs
    """
    filtered_dict={}
    for key in dictionary.keys():
        for filter_key in list(dict_filter_key_value.keys()):
            for subkey in dict_filter_key_value[filter_key]:
                if dictionary[key][filter_key]==subkey:
                    filtered_dict[key]=dictionary[key]
    return filtered_dict

def read_file_info_list(filepath_file_list):
    "create python list from listOfFiles.list"    
    file=open(filepath_file_list, 'r')
    data = [line.strip() for line in file]
    data = [x for x in data if not re.search(r'listOfFiles', x)]    
    file.close()
    return data

def check_available_compress_methd(local_proj_dir,host,username,port,passwd):
    """function to check the available compression method in local and remote machine"""
    from litesoph.common.lfm_database import compression_algo_dict
    
    available_methods_local=[]
    available_methods_remote=[]

    try:
        for key in compression_algo_dict.keys():
            cmd=f'which {key}'
            result=execute_cmd_local(cmd, local_proj_dir)
            error=result[cmd]['error']
            message=result[cmd]['output'] 

            if f'/bin/{key}' in message:
                available_methods_local.append(key)
            
            cmd_remote=f'ssh -p {port} {username}@{host} {cmd}'   
            (error, message)=execute_cmd_remote(cmd_remote, passwd)
            
            if f'/bin/{key}' in message:
                available_methods_remote.append(key)

        available_methods_local_remote=list(set(available_methods_local) & set(available_methods_remote))
    except:
        raise error

    return available_methods_local_remote
        
def file_transfer(file,priority_files_dict,host,username,port,passwd,remote_proj_dir,local_proj_dir):
    """
    function to selectively transfer files from remote to local    
    """    
    if keys_exists(priority_files_dict,'transfer_method')==True:
        file_transfer_method=priority_files_dict[file]['transfer_method']['method']
        
        if file_transfer_method=="compress_transfer":
            from litesoph.common.lfm_database import compression_algo_dict

            list_of_compression_methd=check_available_compress_methd(local_proj_dir,host,username,port,passwd)
            
            if keys_exists(priority_files_dict[file],'compress_method')==False:
                compression_method=list_of_compression_methd[0]
            else:
                compression_method=priority_files_dict[file]['compress_method']
                if compression_method in list_of_compression_methd:                 
                    compressed_file_ext= compression_algo_dict[compression_method]
                else:
                    compression_method=list_of_compression_methd[0]
                    compressed_file_ext= compression_algo_dict[compression_method]
            
            file_folder=str(pathlib.Path(file).parent)
            file_name=str(pathlib.Path(file).name)
            file = str(file).replace(str(remote_proj_dir), '')        
            cmd_compress_file_at_remote=f'ssh -p {port} {username}@{host} "cd {file_folder}; {compression_method} -f {file_name}"'
            cmd_compress_transfer=f"rsync -R --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file}{compressed_file_ext} {local_proj_dir}"                
            file_folder=str(pathlib.Path(file).parent)
            cmd_decompress_file_at_local=f'cd {local_proj_dir}{file_folder}; {compression_method} -d -f {file_name}{compressed_file_ext}; rm  {file_name}{compressed_file_ext}'
            
            (error, message)=execute_cmd_remote(cmd_compress_file_at_remote, passwd)         
            (error, message)=execute_cmd_remote(cmd_compress_transfer, passwd)

            result=execute_cmd_local(cmd_decompress_file_at_local, local_proj_dir)        
            error=result[cmd_decompress_file_at_local]['output']
            message=result[cmd_decompress_file_at_local]['error'] 
            return (error, message)
                    
        elif file_transfer_method=="split_transfer":

            split_size=priority_files_dict[file]['transfer_method']['split_size']                
            file_folder=str(pathlib.Path(file).parent)
            file_name=str(pathlib.Path(file).name)
            file = str(file).replace(str(remote_proj_dir), '')        
            cmd_split_file_at_remote=f'ssh -p {port} {username}@{host} "cd {file_folder}; split -b {split_size} {file_name} {file_name}."'
            cmd_split_files_transfer=f"rsync -R --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file}.?? {local_proj_dir}"                
            file_folder=str(pathlib.Path(file).parent)
            cmd_unsplit_file_at_local=f'cd {local_proj_dir}{file_folder}; cat {file_name}.?? > {file_name}; rm -r {file_name}.*'
            
            (error, message)=execute_cmd_remote(cmd_split_file_at_remote, passwd)  
            (error, message)=execute_cmd_remote(cmd_split_files_transfer, passwd)    
            result=execute_cmd_local(cmd_unsplit_file_at_local, local_proj_dir)        
            error=result[cmd_unsplit_file_at_local]['output']
            message=result[cmd_unsplit_file_at_local]['error']    
            return (error, message)        
        else:
            file = str(file).replace(str(remote_proj_dir), '')
            cmd_direct_transfer=f"rsync -vR --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file} {local_proj_dir}"
            print("\nTransferring File :",file)
            (error, message)=execute_cmd_remote(cmd_direct_transfer, passwd)    
            return (error, message)    
    else:
        file = str(file).replace(str(remote_proj_dir), '')
        cmd_direct_transfer=f"rsync -vR --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file} {local_proj_dir}"
        print("\nTransferring File :",file)
        (error, message)=execute_cmd_remote(cmd_direct_transfer, passwd)    
        return (error, message)
