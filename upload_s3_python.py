#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from botocore.exceptions import ClientError
import requests
import os

# Collecting information about EC2 instance from AWS metadata service
USER_DATA_URL = 'http://169.254.169.254/latest/user-data'
META_DATA_URL = 'http://169.254.169.254/latest/meta-data'
EC2_INS_DATA_FILE = 'ec2InsDatafile'

# Corrected dictionary with proper values
ec2_params = {
    'Instance ID': 'instance-id',
    'Reservation ID': 'reservation-id',
    'Public IP': 'public-ipv4',
    'Public Hostname': 'public-hostname',
    'Private IP': 'local-ipv4',
    'Security Groups': 'security-groups',
    'AMI ID': 'ami-id'
}

try:
    with open(EC2_INS_DATA_FILE, 'w') as fh:
        for param, value in ec2_params.items():
            try:
                response = requests.get(f"{META_DATA_URL}/{value}")
                response.raise_for_status()  # Raise an error for failed requests
                data = response.text
            except requests.RequestException as e:
                print(f"Error while making request for {param}: {e}")
                data = "N/A"

            # If response is a list, join elements with spaces
            if isinstance(data, list):
                print(f"{param}: is list")
                data = ' '.join(data)

            fh.write(f"{param}: {data}\n")

        # Getting OS-related info from system files
        os_name = os.popen("grep '^NAME' /etc/os-release | cut -d'=' -f2").read().strip()
        os_version = os.popen("grep '^VERSION=' /etc/os-release | cut -d'=' -f2").read().strip()
        os_users = os.popen("grep -E 'bash|sh' /etc/passwd | awk -F: '{print $1}' | xargs echo").read().strip()

        fh.write(f"OS NAME: {os_name}\n")
        fh.write(f"OS VERSION: {os_version}\n")
        fh.write(f"Login-able users: {os_users}\n")

except IOError as e:
    print(f"Error while writing to file: {e}")

# Upload file to S3 storage
S3_BUCKET_NAME = 'new-bucket-e05ab0e0'
s3_conn = boto3.client('s3')

try:
    # Check if the bucket exists
    s3_conn.head_bucket(Bucket=S3_BUCKET_NAME)

    # Get instance ID
    instance_id = requests.get(f"{META_DATA_URL}/instance-id").text.strip()

    # Upload file
    with open(EC2_INS_DATA_FILE, 'r') as fh:
        s3_conn.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"system_info_{instance_id}.txt",
            Body=fh.read()
        )

    print(f"File has been uploaded to {S3_BUCKET_NAME} S3 bucket with key: system_info_{instance_id}.txt")

except ClientError as e:
    print(f"Are you sure the destination bucket exists? Check it. Error: {e}")
