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
from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric
from braket.tracking import Tracker

cost_tracker = Tracker().start()

print("Test job started!!!!!")

# Use the device declared in the creation script
device = AwsDevice(os.environ["AMZN_BRAKET_DEVICE_ARN"])

counts_list = []
angle_list = []
for i in range(5):
    angle = np.pi * np.random.randn()
    random_circuit = Circuit().rx(0, angle)

    task = device.run(random_circuit, shots=100)
    counts = task.result().measurement_counts

    angle_list.append(angle)
    counts_list.append(counts)
    print(counts)

    braket_tasks_cost = float(cost_tracker.simulator_tasks_cost() + cost_tracker.qpu_tasks_cost())
    log_metric(metric_name="braket_tasks_cost", value=braket_tasks_cost, iteration_number=i)


save_job_result(
    {
        "counts": counts_list,
        "angles": angle_list,
        "task summary": cost_tracker.quantum_tasks_statistics(),
        "estimated cost": braket_tasks_cost,
    }
)

print("Test job completed!!!!!")
