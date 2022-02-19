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

import math
import random

import pytest
from gate_model_device_testing_utils import bell_pair_openqasm_testing, no_result_types_testing

from braket.aws import AwsDevice
from braket.circuits import Circuit

SHOTS = 1000
TN1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
SIMULATOR_ARNS = [TN1_ARN]


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_ghz(simulator_arn, aws_session, s3_destination_folder):
    num_qubits = 50
    circuit = _ghz(num_qubits)
    device = AwsDevice(simulator_arn, aws_session)
    no_result_types_testing(
        circuit,
        device,
        {"shots": SHOTS, "s3_destination_folder": s3_destination_folder},
        {"0" * num_qubits: 0.5, "1" * num_qubits: 0.5},
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_qft_iqft_h(simulator_arn, aws_session, s3_destination_folder):
    num_qubits = 24
    h_qubit = random.randint(0, num_qubits - 1)
    circuit = _inverse_qft(_qft(Circuit().h(h_qubit), num_qubits), num_qubits)
    device = AwsDevice(simulator_arn, aws_session)
    no_result_types_testing(
        circuit,
        device,
        {"shots": SHOTS, "s3_destination_folder": s3_destination_folder},
        {"0" * num_qubits: 0.5, "0" * h_qubit + "1" + "0" * (num_qubits - h_qubit - 1): 0.5},
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_bell_pair_openqasm(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    bell_pair_openqasm_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


def _ghz(num_qubits):
    circuit = Circuit()
    circuit.h(0)
    for qubit in range(num_qubits - 1):
        circuit.cnot(qubit, qubit + 1)
    return circuit


def _qft(circuit, num_qubits):
    for i in range(num_qubits):
        circuit.h(i)
        for j in range(1, num_qubits - i):
            circuit.cphaseshift(i + j, i, math.pi / (2**j))

    for qubit in range(math.floor(num_qubits / 2)):
        circuit.swap(qubit, num_qubits - qubit - 1)

    return circuit


def _inverse_qft(circuit, num_qubits):
    for qubit in range(math.floor(num_qubits / 2)):
        circuit.swap(qubit, num_qubits - qubit - 1)

    for i in reversed(range(num_qubits)):
        for j in reversed(range(1, num_qubits - i)):
            circuit.cphaseshift(i + j, i, -math.pi / (2**j))
        circuit.h(i)

    return circuit
