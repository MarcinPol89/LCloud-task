#!/usr/bin/env python
# -*- coding: utf8 -*-"

import boto_3
from botocore.client import ClientError
import requests
import subprocess
import os

# Collecting information about EC2 instance from AWS service

user_data = 'http://169.254.169.254/latest/user-data'
meta_data = 'http://169.254.169.254/latest/meta-data'
ec2InsDatafile = 'ec2InsDatafile'
ec2_params = {
    'Instance ID': 'instance-id',
    'Reservation ID': 'reservation-id'
    'Public IP': 'public_ipv4',
    'Public Hostname': 'public_hostname',
    'Private IP':'local-ipv4'
    'Security Groups':'security-groups',
    'AMI ID': 'ami_id'
}

try:
    fh = open(ec2InsDatafile, 'w')
except:
    print 'Error while opening file for write'

for param, value in ec2_params.items():
    try:
        responce = requests.get(meta_data +'/' + value)
    except:
        print "Error while making request"
    if isinstance(responce.text,list):
        print responce.text +': is list'
        data = ' '.joint(responce.text)
    else:
        data = param +":"+responce.text
    try:
          fh.write(data+'\r\n')
    except:
        print('Error during writing to file')
        print data

#Getting  OS related if from system files

os_vers = "grep '^VERSION=' /etc/os-release |cut -d'=' -f2"
os_name = "grep '^NAME' /etc/os-release |cut -d'=' -f2"
os_name_val ='OS NAME: '+ os.popen(os_name).read().rstrip()
os_vers_val ='OS VERSION: '+ os.popen(os_vers).read().rstrip()
os_usrs = "grep -E 'bash|sh' /etc/passwd |awk -F : '{print $1}|xargs echo  "
os_usrs_val = 'Login able users: '+ os.popen(os_usrs).read().rstrip()
try:
    fh.write(os_name_val+'\r\n')
    fh.write(os_vers_val+'\r\n')
    fh.write(os_usrs_val+'\r\n')
except:
    print "Error during write to file"
    fh.close()


# Upload file to s3 storage
s3_bucket_name = 'new-bucket-e05ab0e0'
s3_conn = boto3.client('s3')

try:
    s3.meta.client.head_bucket(Bucket=s3_bucket_name)

    with (ec2InsDatafile, 'r') as fh:
        s3_conn.put_object(
            Bucket=s3_bucket_name,
            Key='system_info' + requests.get(meta_data +'/' + instance_id) + '.txt',
            Body=fh.read()
        )
    print("File has been uploaded into " + s3_bucket_name + " S3 bucket with instance_id key.")
except ClientError:
    "Are you sure the destination bucket exist? Check it."
