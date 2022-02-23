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

import json
import os

from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.jobs import save_job_checkpoint, save_job_result
from braket.jobs_data import PersistedJobDataFormat


def start_here():
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file, "r") as f:
        hyperparameters = json.load(f)

    if hyperparameters["test_case"] == "completed":
        completed_job_script()
    else:
        failed_job_script()


def failed_job_script():
    print("Test job started!!!!!")
    assert 0


def completed_job_script():
    print("Test job started!!!!!")

    # Use the device declared in the Orchestration Script
    device = AwsDevice(os.environ["AMZN_BRAKET_DEVICE_ARN"])

    bell = Circuit().h(0).cnot(0, 1)
    for count in range(5):
        task = device.run(bell, shots=100)
        print(task.result().measurement_counts)
        save_job_result({"converged": True, "energy": -0.2})
        save_job_checkpoint({"some_data": "abc"}, checkpoint_file_suffix="plain_data")
        save_job_checkpoint({"some_data": "abc"}, data_format=PersistedJobDataFormat.PICKLED_V4)

    print("Test job completed!!!!!")
