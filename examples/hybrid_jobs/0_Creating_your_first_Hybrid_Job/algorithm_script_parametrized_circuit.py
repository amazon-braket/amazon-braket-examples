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
from braket.circuits import Circuit, FreeParameter
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric
from braket.tracking import Tracker

cost_tracker = Tracker().start()

print("Test job started!!!!!")

# Use the device declared in the creation script
device = AwsDevice(os.environ["AMZN_BRAKET_DEVICE_ARN"])

theta = FreeParameter("theta")
parametrized_circuit = Circuit().rx(0, theta)

counts_list = []
theta_list = []
for i in range(5):
    theta_value = np.pi * np.random.randn()
    
    task = device.run(parametrized_circuit, shots=100, inputs={"theta": theta_value})
    counts = task.result().measurement_counts

    theta_list.append(theta_value)
    counts_list.append(counts)
    print(counts)

    braket_tasks_cost = float(cost_tracker.simulator_tasks_cost() + cost_tracker.qpu_tasks_cost())
    log_metric(metric_name="braket_tasks_cost", value=braket_tasks_cost, iteration_number=i)


save_job_result(
    {
        "counts": counts_list,
        "theta": theta_list,
        "task summary": cost_tracker.quantum_tasks_statistics(),
        "estimated cost": braket_tasks_cost,
    }
)

print("Test job completed!!!!!")
