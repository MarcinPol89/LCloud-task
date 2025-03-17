#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from botocore.exceptions import ClientError
import requests
import paramiko
import os

# EC2 metadata URLs
user_data = 'http://169.254.169.254/latest/user-data'
meta_data = 'http://169.254.169.254/latest/meta-data'
ec2InsDatafile = 'ec2InsDatafile'

# Corrected EC2 parameters dictionary
ec2_params = {
    'Instance ID': 'instance-id',
    'Reservation ID': 'reservation-id',
    'Public IP': 'public_ipv4',
    'Public Hostname': 'public_hostname',
    'Private IP':'local-ipv4',
    'Security Groups':'security-groups',
    'AMI ID': 'ami_id'
}

# Fetching EC2 instance metadata and writing to file
try:
    with open(ec2InsDatafile, 'w') as fh:
        for param, value in ec2_params.items():
            try:
                response = requests.get(f"{meta_data}/{value}")
                response.raise_for_status()
                data = response.text
            except requests.RequestException as e:
                print(f"Error while fetching {param}: {e}")
                data = "N/A"

            # If data is a list, join elements with spaces
            if isinstance(data, list):
                data = ' '.join(data)

            fh.write(f"{param}: {data}\n")
except IOError as e:
    print(f"File write error: {e}")

# SSH connection details
host = "79.125.60.146"
user = "ubuntu"
ssh_key_path = '/home/MarcinPol89/LCloud-task/r4p17_key.pem'

# Commands to get OS-related information
commands = {
    "OS Name": "grep '^NAME' /etc/os-release | cut -d'=' -f2",
    "OS Version": "grep '^VERSION=' /etc/os-release | cut -d'=' -f2",
    "Login-able Users": "grep -E 'bash|sh' /etc/passwd | awk -F: '{print $1}' | xargs echo"
}

# SSH connection and execution
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, key_filename=ssh_key_path)

    with open(ec2InsDatafile, 'a') as fh:
        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode().strip()
            fh.write(f"{key}: {output}\n")

    ssh.close()
except Exception as e:
    print(f"SSH connection error: {e}")

# Upload file to S3 storage
s3_bucket_name = 'applicant-task/r4p17/'
s3_conn = boto3.client('s3')

try:
    # Check if bucket exists
    s3_conn.head_bucket(Bucket=s3_bucket_name)

    # Get instance ID for unique S3 key
    instance_id = requests.get(f"{meta_data}/instance-id").text.strip()

    with open(ec2InsDatafile, 'r') as fh:
        s3_conn.put_object(
            Bucket=s3_bucket_name,
            Key=f"system_info_{instance_id}.txt",
            Body=fh.read()
        )

    print(f"File successfully uploaded to {s3_bucket_name} as system_info_{instance_id}.txt")
except ClientError as e:
    print(f"S3 upload error: {e}")
