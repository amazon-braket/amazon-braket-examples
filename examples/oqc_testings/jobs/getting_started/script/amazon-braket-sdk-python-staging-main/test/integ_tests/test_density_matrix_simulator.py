import math

import pytest
from gate_model_device_testing_utils import get_tol

from braket.aws import AwsDevice
from braket.circuits import Circuit, Noise, Observable

SHOTS = 1000
DM1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/dm1"
SIMULATOR_ARNS = [DM1_ARN]


@pytest.mark.parametrize("simulator_arn", SIMULATOR_ARNS)
def test_mixed_states(simulator_arn, aws_session, s3_destination_folder):
    num_qubits = 10
    circuit = _mixed_states(num_qubits)
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


def _mixed_states(n_qubits: int) -> Circuit:
    noise = Noise.PhaseFlip(probability=0.2)
    circ = Circuit()
    for qubit in range(0, n_qubits - 2, 3):
        circ.x(qubit).y(qubit + 1).cnot(qubit, qubit + 2).x(qubit + 1).z(qubit + 2)
        circ.apply_gate_noise(noise, target_qubits=[qubit, qubit + 2])

    # attach the result types
    circ.probability()
    circ.expectation(observable=Observable.Z(), target=0)

    return circ
