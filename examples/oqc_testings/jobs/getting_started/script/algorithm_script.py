# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os

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
