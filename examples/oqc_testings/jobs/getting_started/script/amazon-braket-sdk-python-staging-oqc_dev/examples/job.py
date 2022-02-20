# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
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

from braket.aws import AwsDevice, AwsQuantumJob
from braket.circuits import Circuit
from braket.jobs import save_job_result


def run_job():
    device = AwsDevice(os.environ.get("AMZN_BRAKET_DEVICE_ARN"))

    bell = Circuit().h(0).cnot(0, 1)
    num_tasks = 10
    results = []

    for i in range(num_tasks):
        task = device.run(bell, shots=100)
        result = task.result().measurement_counts
        results.append(result)
        print(f"iter {i}: {result}")

    save_job_result({"results": results})


if __name__ == "__main__":
    job = AwsQuantumJob.create(
        device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
        source_module="job.py",
        entry_point="job:run_job",
        wait_until_complete=True,
    )
    print(job.result())
