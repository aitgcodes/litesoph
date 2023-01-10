import paramiko
import socket
from pathlib import Path


def ssh_connect_pkey(username, host,port,pkey_path):
        "connects to the cluster through ssh."
        try:
            print("Establishing ssh connection")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())                        
            private_key = paramiko.RSAKey.from_private_key_file(pkey_path)
            client.connect(hostname=host, port=port, username=username, pkey=private_key,banner_timeout=200)
            print("connected to the server", host)
    
        except paramiko.AuthenticationException:
            raise Exception("Authentication failed, please verfiy your credentials")
        except paramiko.SSHException as sshException:
            raise Exception(f"Could not establish SSH connection: {sshException} ")
        except socket.timeout as e:
            raise Exception("Connection timed out")
        except Exception as e:     
           raise Exception(f"Exception in connecting to the server {e}")



username='varadharajans'
host='paramshivay.iitbhu.ac.in'
port='4422'
pkey_path=Path('/home/anandsahu/.ssh/id_rsa')

ssh_connect_pkey(username, host,port,pkey_path)