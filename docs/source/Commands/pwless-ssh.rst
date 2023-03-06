How to access passwordless SSH?
===============================

Step 1: Check or Create Authentication SSH-Keygen Keys on local machine
	
>>> $ ls -al ~/.ssh/id_*.pub  #check existing key, if key exists goto step 2
>>> $ ssh-keygen -t rsa      # Keep pressing enter


.. image:: ./terminal.png
   :width: 1000
   :alt: terminal


Step 2: Upload SSH Key to remote machine
	
>>> $ ssh-copy-id username@hostname -p xxxx   #Enter the password
	
If above step failed, try the command given below with your credential

>>> $ cat ~/.ssh/id_rsa.pub | ssh remote_username@server_ip_address "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

Step 3: Test SSH Passwordless Login from local  machine to remote

>>> $ ssh remote_username@server_ip_address



