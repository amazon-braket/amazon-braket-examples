# first install packages (work around for pre-launch)
import os
import subprocess

os.chdir("/opt/ml/code/customer_code/extracted/script/amazon-braket-schemas-python-staging-main")
subprocess.run(["pip", "install", "."])
os.chdir("/opt/ml/code/customer_code/extracted/script/amazon-braket-sdk-python-staging-main")
subprocess.run(["pip", "install", "."])
os.chdir("/")


import numpy as np
from braket.aws import AwsDevice, AwsQuantumTask
from braket.circuits import Circuit
from braket.jobs import save_job_result



print("Test job started!!!!!")


# work around for Gamma
import boto3
from braket.aws import AwsQuantumTask, AwsSession
region_name = "eu-west-2"
endpoint_url = "https://braket-gamma.eu-west-2.amazonaws.com"
braket_client = boto3.client("braket", region_name=region_name, endpoint_url=endpoint_url)
aws_session = AwsSession(braket_client=braket_client)

print("AWS session set!!!!!")



# Use the device declared in the creation script
device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
device = AwsDevice(device_arn, aws_session=aws_session)
# device = AwsDevice(device_arn)

counts_list = []
angle_list = []

angle = np.pi/2
for _ in range(5):
    random_circuit = Circuit().rx(0, angle)

    task = device.run(random_circuit, shots=100)
#     task = AwsQuantumTask.create(aws_session, device_arn, random_circuit, s3_folder, shots=500)

    counts = task.result().measurement_counts

    angle_list.append(angle)
    counts_list.append(counts)
    print(counts)
    
    angle = counts['1'] / 100 * np.pi

save_job_result({"counts": counts_list, "angles": angle_list})

print("Test job completed!!!!!")
