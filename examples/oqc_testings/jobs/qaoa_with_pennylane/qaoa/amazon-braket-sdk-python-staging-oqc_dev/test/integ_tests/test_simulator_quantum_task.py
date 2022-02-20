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

import pytest
from gate_model_device_testing_utils import (
    batch_bell_pair_testing,
    bell_pair_openqasm_testing,
    get_tol,
    many_layers,
    multithreaded_bell_pair_testing,
    no_result_types_bell_pair_testing,
    openqasm_noisy_circuit_1qubit_noise_full_probability,
    openqasm_result_types_bell_pair_testing,
    qubit_ordering_testing,
    result_types_all_selected_testing,
    result_types_bell_pair_full_probability_testing,
    result_types_bell_pair_marginal_probability_testing,
    result_types_hermitian_testing,
    result_types_noncommuting_all,
    result_types_noncommuting_flipped_targets_testing,
    result_types_noncommuting_testing,
    result_types_nonzero_shots_bell_pair_testing,
    result_types_observable_not_in_instructions,
    result_types_tensor_hermitian_hermitian_testing,
    result_types_tensor_x_y_testing,
    result_types_tensor_y_hermitian_testing,
    result_types_tensor_z_h_y_testing,
    result_types_tensor_z_hermitian_testing,
    result_types_tensor_z_z_testing,
    result_types_zero_shots_bell_pair_testing,
)

from braket.aws import AwsDevice

SHOTS = 8000
SV1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
DM1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/dm1"
SIMULATOR_ARNS = [SV1_ARN, DM1_ARN]
ARNS_WITH_SHOTS = [(SV1_ARN, SHOTS), (SV1_ARN, 0), (DM1_ARN, SHOTS), (DM1_ARN, 0)]


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_no_result_types_bell_pair(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    no_result_types_bell_pair_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_qubit_ordering(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    qubit_ordering_testing(device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder})


@pytest.mark.parametrize(
    "simulator_arn, include_amplitude", list(zip(SIMULATOR_ARNS, [True, False]))
)
def test_result_types_no_shots(
    simulator_arn, include_amplitude, aws_session, s3_destination_folder
):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_zero_shots_bell_pair_testing(
        device,
        False,
        {"shots": 0, "s3_destination_folder": s3_destination_folder},
        include_amplitude,
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_nonzero_shots_bell_pair(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_nonzero_shots_bell_pair_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_bell_pair_full_probability(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_bell_pair_full_probability_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_bell_pair_marginal_probability(
    simulator_arn, aws_session, s3_destination_folder
):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_bell_pair_marginal_probability_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_x_y(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_x_y_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_z_h_y(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_z_h_y_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_hermitian(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_hermitian_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_z_z(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_z_z_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_hermitian_hermitian(
    simulator_arn, shots, aws_session, s3_destination_folder
):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_hermitian_hermitian_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_y_hermitian(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_y_hermitian_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_tensor_z_hermitian(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_tensor_z_hermitian_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_all_selected(simulator_arn, shots, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_all_selected_testing(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_noncommuting(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_noncommuting_testing(device, {"s3_destination_folder": s3_destination_folder})


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_noncommuting_flipped_targets(
    simulator_arn, aws_session, s3_destination_folder
):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_noncommuting_flipped_targets_testing(
        device, {"s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_result_types_noncommuting_all(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_noncommuting_all(device, {"s3_destination_folder": s3_destination_folder})


@pytest.mark.parametrize("simulator_arn,shots", ARNS_WITH_SHOTS)
def test_result_types_observable_not_in_instructions(
    simulator_arn, shots, aws_session, s3_destination_folder
):
    device = AwsDevice(simulator_arn, aws_session)
    result_types_observable_not_in_instructions(
        device, {"shots": shots, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_multithreaded_bell_pair(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    multithreaded_bell_pair_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_batch_bell_pair(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    batch_bell_pair_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_bell_pair_openqasm(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    bell_pair_openqasm_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_bell_pair_openqasm_results(simulator_arn, aws_session, s3_destination_folder):
    device = AwsDevice(simulator_arn, aws_session)
    openqasm_result_types_bell_pair_testing(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


def test_openqasm_probability_results(aws_session, s3_destination_folder):
    device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/dm1", aws_session)
    openqasm_noisy_circuit_1qubit_noise_full_probability(
        device, {"shots": SHOTS, "s3_destination_folder": s3_destination_folder}
    )


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
@pytest.mark.parametrize("num_layers", [50, 100, 500, 1000])
def test_many_layers(simulator_arn, num_layers, aws_session, s3_destination_folder):
    num_qubits = 10
    circuit = many_layers(num_qubits, num_layers)
    device = AwsDevice(simulator_arn, aws_session)

    tol = get_tol(SHOTS)
    result = device.run(circuit, shots=SHOTS, s3_destination_folder=s3_destination_folder).result()
    probabilities = result.measurement_probabilities
    probability_sum = 0
    for bitstring in probabilities:
        assert probabilities[bitstring] >= 0
        probability_sum += probabilities[bitstring]
    assert math.isclose(probability_sum, 1, rel_tol=tol["rtol"], abs_tol=tol["atol"])
    assert len(result.measurements) == SHOTS
