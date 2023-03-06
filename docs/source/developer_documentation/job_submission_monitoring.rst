========================================================
LITESOPH Job Submission, Monitoring and File Management
========================================================

Overview
========

LITESOPH Job Submission, Monitoring and File Management is a set of modules capable of handling tasks like submission of job to remote machine, tracking the status running job and transferring of files from remote to local machine.   

Features and Functionalities
============================

1. Job Submission module supports queue(qsub, sbatch etc) as well as non-queue(bash) based job submission on remote machine through password and passwordless approach. Passwordless approach is generally used to avoid typing password repeatively for every job submission. It can also help to bypass captcha based login authentication. See :doc:`./FAQs/pwless-ssh` 

2. Monitoring and File Management modules handles the job of tracking the status as well as terminating the  running job on remote machine. File Management module handles the downloading of all files as well as selective transfer the files from remote to local machine via different transfer methods (direct transfer along with compression and split transfer).



