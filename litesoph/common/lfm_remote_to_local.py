import pexpect
from subprocess import Popen, PIPE
import pathlib
from pathlib import Path
import sys

file_tag_dict={ 
                '.out':{'file_relevance':'very_impt','file_lifetime':'None', 'transfer_method':{'method':'compress_transfer','compress_method':'zstd','split_size':'500k'}},
                '.log':{'file_relevance':'very_impt','file_lifetime':'','transfer_method':{'method':'direct_transfer','compress_method':'zstd','split_size':''}},
                '.cube':{'file_relevance':'very_impt','file_lifetime':'','transfer_method':{'method':'compress_transfer','compress_method':'zstd','split_size':''}},
                '.ulm':{'file_relevance':'very_impt','file_lifetime':'','transfer_method':{'method':'split_transfer','compress_method':'zstd','split_size':'200M'}},

                 }


def run_command_local(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE,shell=True, encoding='utf-8')
    message, error = p.communicate()
    return error,message
    
def execute_cmd_lfm(cmd, passwd):
    """
    function to execute the command in local
    """    
    intitial_response = ['Are you sure', 'assword','[#\$] ', pexpect.EOF]
    
    ssh = pexpect.spawn(cmd,timeout=None)
    i = ssh.expect(intitial_response)
    if i == 0 :
        T = ssh.read(100)
        ssh.sendline('yes')
        ssh.expect('assword:')
        ssh.sendline(passwd)
    elif i == 1:
        ssh.sendline(passwd)
    elif i==2:
        print('Connected Successfully.')
        prompt = ssh.after
        print('Shell Command Prompt:', prompt.decode(encoding='utf-8'))
    else:
        str1 = str(ssh.before)
        return (-3, 'Error: Unknown:'+ str1)

    possible_response = ['assword:', pexpect.EOF]
    i = ssh.expect(possible_response)

    if i == 0:
        return (-4, "Error: Incorrect password.")
    else:
        output = str(ssh.before)
        for text in ssh.before.decode(encoding='utf-8',errors='ignore').split('\n'):
            print(text)
        return (0, output)

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = {}
    dict[key] = value
    
def create_file_info(list_of_files_in_remote_dir):

    file_info_dict={}
    default_metadata={'file_relevance':'very_impt','file_lifetime':'',
                     'transfer_method':{'method':'direct_transfer','compress_method':'zstd','split_size':''}}
    
    for i in range(len(list_of_files_in_remote_dir)):
        file_extension = pathlib.Path(list_of_files_in_remote_dir[i]).suffix

        if file_extension in list(file_tag_dict.keys()):
            metadata=file_tag_dict[file_extension]
            add_element(file_info_dict, list_of_files_in_remote_dir[i], metadata)
        else:
            add_element(file_info_dict, list_of_files_in_remote_dir[i], default_metadata)
    
    return file_info_dict

def filter_dict(dictionary,filter_key,filter_value):
    """
    function to filter dictionary using key-value pairs
    """
    filtered_dict=[dictionary for d in dictionary.values() if d[filter_key] == filter_value]
    from collections import ChainMap
    filtered_dict = dict(ChainMap(*filtered_dict)) 
    return filtered_dict

def read_file_info_list(filepath_file_list):
    "create python list from listOfFiles.list"    
    data = [line.strip() for line in open(filepath_file_list, 'r')]
    return data

def file_transfer(file,priority_files_dict,host,username,port,passwd,remote_proj_dir,local_proj_dir):
    """
    function to selectively transfer files from remote to local    
    """    
    file_transfer_method=priority_files_dict[file]['transfer_method']['method']
    
    if file_transfer_method=="compress_transfer":
        
        algo_dict={'lz4':'.lz4', 'zstd':'.zst', 'lzop':'.lzo', 'gzip':'.gz', 'bzip2':'.bz2','p7zip':'.7z',
        'xz':'.xz','pigz':'.gz','plzip':'.lz','pbzip2':'.bz2','lbzip2':'.bz2'}
                    
        compression_method=priority_files_dict[file]['transfer_method']['compress_method']
        compressed_file_ext= algo_dict[compression_method]
        
        file_folder=str(Path(file).parent)
        file_name=str(Path(file).name)
        file = str(file).replace(str(remote_proj_dir), '')        
        cmd_compress_file_at_remote=f'ssh -p {port} {username}@{host} "cd {file_folder}; {compression_method} -f {file_name}"'
        cmd_compress_transfer=f"rsync -R --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file}{compressed_file_ext} {local_proj_dir}"                
        file_folder=str(Path(file).parent)
        cmd_decompress_file_at_remote=f'cd {local_proj_dir}{file_folder}; {compression_method} -d -f {file_name}{compressed_file_ext}; rm  {file_name}{compressed_file_ext}'
        
        (error, message)=execute_cmd_lfm(cmd_compress_file_at_remote, passwd)         
        (error, message)=execute_cmd_lfm(cmd_compress_transfer, passwd)
        (error, message)=run_command_local(cmd_decompress_file_at_remote)
        return (error, message)
                
    elif file_transfer_method=="split_transfer":

        split_size=priority_files_dict[file]['transfer_method']['split_size']                
        file_folder=str(Path(file).parent)
        file_name=str(Path(file).name)
        file = str(file).replace(str(remote_proj_dir), '')        
        cmd_split_file_at_remote=f'ssh -p {port} {username}@{host} "cd {file_folder}; split -b {split_size} {file_name} {file_name}."'
        cmd_split_files_transfer=f"rsync -R --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file}.?? {local_proj_dir}"                
        file_folder=str(Path(file).parent)
        cmd_unsplit_file_at_local=f'cd {local_proj_dir}{file_folder}; cat {file_name}.?? > {file_name}; rm -r {file_name}.*'
        
        (error, message)=execute_cmd_lfm(cmd_split_file_at_remote, passwd)  
        (error, message)=execute_cmd_lfm(cmd_split_files_transfer, passwd)    
        (error, message)=run_command_local(cmd_unsplit_file_at_local)      
        return (error, message)
        
    else:
        file = str(file).replace(str(remote_proj_dir), '')
        cmd_direct_transfer=f"rsync -R --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/.{file} {local_proj_dir}"
        (error, message)=execute_cmd_lfm(cmd_direct_transfer, passwd)    
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

    cmd_create_listOfFiles_at_remote=f'ssh -p {port} {username}@{host} "cd {remote_proj_dir}; find "$PWD"  -type f > listOfFiles.list"'     
    cmd_listOfFiles_to_local=f"rsync --rsh='ssh -p{port}' {username}@{host}:{remote_proj_dir}/listOfFiles.list {local_proj_dir}"
    (error, message)=execute_cmd_lfm(cmd_create_listOfFiles_at_remote, passwd)
    (error, message)=execute_cmd_lfm(cmd_listOfFiles_to_local, passwd)
    listOfFiles_path=f'{local_proj_dir}/listOfFiles.list'    
    file_info_dict=create_file_info(read_file_info_list(listOfFiles_path))
        
    priority1_files_dict=filter_dict(file_info_dict,'file_relevance','very_impt')
    priority2_files_dict=filter_dict(file_info_dict,'file_relevance','impt')
    
    for file in list(priority1_files_dict.keys()):
        (error, message)=file_transfer(file,priority1_files_dict,host,username,port,passwd,remote_proj_dir,local_proj_dir)

    return (error, message)
    
    


# paramshivay
# host='paramshivay.iitbhu.ac.in'
# username='varadharajans'
# port='4422'
# passwd='pkv86@Phy'
# python_env_cmd=''
# remote_proj_dir='/home/varadharajans/Pramod/anand'
# local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/lfm-testing'

#aryabhatta
# host='172.28.49.150'
# username='vpramod'
# port='22'
# passwd='pkv86@Phy'
# python_env_cmd='conda activate gpaw'
# remote_proj_dir='/pfshome/vpramod/anand/test-3Dec22-2'
# local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/lfm-testing'


#jaber
# host='172.28.2.85'
# username='jaber'
# port='22'
# passwd='jaber.123'
# python_env_cmd='conda activate gpaw-env'
# remote_proj_dir='/home/jaber/Anand/3Jan22-15'
# local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/lfm-testing'

# niel
host='172.28.2.63'
username='niel'
port='22'
passwd='iiserb2022'
python_env_cmd='conda activate lite'
remote_proj_dir='/home/niel/anand/4Jan22-3'
# local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/lfm-testing'
local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/4Jan22-3'


#heisenberg
# host='172.28.2.58'
# username='yogesh'
# port='22'
# passwd='alexander@24'
# python_env_cmd='conda activate /home/yogesh/apps/GPAW-22.8.0'
# remote_proj_dir='/home/niel/anand/4Jan22-3'
# local_proj_dir='/home/anandsahu/myproject/aitg/ls/sample_ls_project/lfm-testing'


download_files_from_remote(host,username,port,passwd,remote_proj_dir,local_proj_dir)


# def run_command_local(cmd):
#     p = Popen(cmd, stdout=PIPE, stderr=PIPE,shell=True, encoding='utf-8')
#     message, error = p.communicate()
#     return error,message

# cmd=' cd /home/anandsahu/myproject/aitg/ls/sample_ls_project/4Jan22-3/workflow_1/gpaw/TaskTypes.GROUND_STATE; zstd -d -f gs.out.zst'
# output, error=run_command_local(cmd)
# print(output,error)
