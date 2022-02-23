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

import numpy as np
import pytest

from braket.circuits.circuit import Circuit
from braket.circuits.gate import Gate
from braket.circuits.instruction import Instruction
from braket.circuits.moments import Moments
from braket.circuits.noise import Noise
from braket.circuits.noise_helpers import apply_noise_to_gates, apply_noise_to_moments
from braket.circuits.qubit_set import QubitSet

invalid_data_noise_type = [Gate.X(), None, 1.5]
invalid_data_target_gates_type = [[-1, "foo"], [1.5, None, -1], "X", [Gate.X, "CNot"]]
invalid_data_target_qubits_value = [-1]
invalid_data_target_qubits_type = [1.5, "foo", ["foo", 1]]
invalid_data_target_unitary_value = [np.array([[0, 0], [1, 0]])]
invalid_data_target_unitary_type = [[[0, 1], [1, 0]]]


@pytest.fixture
def circuit_2qubit():
    return Circuit().x(0).y(1).x(0).x(1).cnot(0, 1)


@pytest.fixture
def circuit_2qubit_parametrized():
    return Circuit().x(0).y(1).x(0).rx(1, np.pi).xy(0, 1, np.pi / 2)


@pytest.fixture
def circuit_2qubit_with_unitary():
    return Circuit().x(0).y(1).x(0).x(1).cnot(0, 1).unitary([0], matrix=np.array([[0, 1], [1, 0]]))


@pytest.fixture
def circuit_2qubit_not_dense():
    # there are some qubits and some time that are not occupied by a gate
    return Circuit().x(0).y(1).x(0).cnot(0, 1)


@pytest.fixture
def circuit_3qubit():
    return Circuit().x(0).y(1).cnot(0, 1).z(2).cz(2, 1).cnot(0, 2).cz(1, 2)


@pytest.fixture
def noise_1qubit():
    return Noise.BitFlip(probability=0.1)


@pytest.fixture
def noise_1qubit_2():
    return Noise.Depolarizing(probability=0.1)


@pytest.fixture
def noise_2qubit():
    E0 = np.sqrt(0.8) * np.eye(4)
    E1 = np.sqrt(0.2) * np.kron(np.array([[0, 1], [1, 0]]), np.array([[0, 1], [1, 0]]))
    return Noise.Kraus(matrices=[E0, E1])


@pytest.mark.xfail(raises=IndexError)
def test_apply_gate_noise_to_empty_circuit(noise_1qubit):
    Circuit().apply_gate_noise(noise_1qubit)


@pytest.mark.xfail(raises=IndexError)
def test_apply_initialization_noise_to_empty_circuit(noise_1qubit):
    Circuit().apply_initialization_noise(noise_1qubit)


@pytest.mark.xfail(raises=IndexError)
def test_apply_readout_noise_to_empty_circuit(noise_1qubit):
    Circuit().apply_readout_noise(noise_1qubit)


@pytest.mark.xfail(raises=ValueError)
def test_apply_gate_noise_with_target_gates_and_unitary(circuit_2qubit, noise_1qubit):
    circuit_2qubit.apply_gate_noise(
        noise_1qubit, target_gates=Gate.X, target_unitary=np.array([[0, 1], [1, 0]])
    )


@pytest.mark.xfail(raises=IndexError)
def test_apply_gate_noise_to_outside_qubit_range(circuit_2qubit, noise_1qubit):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_qubits=[0, 1, 2])


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("noise", invalid_data_noise_type)
def test_apply_gate_noise_invalid_noise_type(circuit_2qubit, noise):
    circuit_2qubit.apply_gate_noise(noise)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("noise", invalid_data_noise_type)
def test_apply_initialization_noise_invalid_noise_type(circuit_2qubit, noise):
    circuit_2qubit.apply_initialization_noise(noise)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("noise", invalid_data_noise_type)
def test_apply_readout_noise_invalid_noise_type(circuit_2qubit, noise):
    circuit_2qubit.apply_readout_noise(noise)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("target_gates", invalid_data_target_gates_type)
def test_apply_gate_noise_invalid_target_gates_type(circuit_2qubit, noise_1qubit, target_gates):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_gates=target_gates)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("target_unitary", invalid_data_target_unitary_type)
def test_apply_gate_noise_invalid_target_unitary_type(circuit_2qubit, noise_1qubit, target_unitary):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_unitary=target_unitary)


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("target_unitary", invalid_data_target_unitary_value)
def test_apply_gate_noise_invalid_target_unitary_value(
    circuit_2qubit, noise_1qubit, target_unitary
):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_unitary=target_unitary)


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_value)
def test_apply_gate_noise_invalid_target_qubits_value(circuit_2qubit, noise_1qubit, target_qubits):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_qubits=target_qubits, target_gates=[])


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_value)
def test_apply_initialization_noise_invalid_target_qubits_value(
    circuit_2qubit, noise_1qubit, target_qubits
):
    circuit_2qubit.apply_initialization_noise(noise_1qubit, target_qubits=target_qubits)


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_value)
def test_apply_readout_noise_invalid_target_qubits_value(
    circuit_2qubit, noise_1qubit, target_qubits
):
    circuit_2qubit.apply_readout_noise(noise_1qubit, target_qubits=target_qubits)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_type)
def test_apply_gate_noise_invalid_target_qubits_type(circuit_2qubit, noise_1qubit, target_qubits):
    circuit_2qubit.apply_gate_noise(noise_1qubit, target_qubits=target_qubits)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_type)
def test_apply_initialization_noise_invalid_target_qubits_type(
    circuit_2qubit, noise_1qubit, target_qubits
):
    circuit_2qubit.apply_initialization_noise(noise_1qubit, target_qubits=target_qubits)


@pytest.mark.xfail(raises=TypeError)
@pytest.mark.parametrize("target_qubits", invalid_data_target_qubits_type)
def test_apply_readout_noise_invalid_target_qubits_type(
    circuit_2qubit, noise_1qubit, target_qubits
):
    circuit_2qubit.apply_readout_noise(noise_1qubit, target_qubits=target_qubits)


@pytest.mark.xfail(raises=ValueError)
def test_apply_gate_noise_fixed_qubit_count_not_implemented(noise_2qubit):
    circ = Circuit().unitary([0, 1], matrix=np.eye(4))
    circ.apply_gate_noise(noise_2qubit, target_gates=Gate.Unitary)


@pytest.mark.xfail(raises=ValueError)
def test_apply_gate_noise_mismatch_qubit_count_with_target_gates(noise_2qubit):
    circ = Circuit().cswap(0, 1, 2)
    circ.apply_gate_noise(noise_2qubit, target_gates=Gate.CSwap)


@pytest.mark.xfail(raises=ValueError)
def test_apply_initialization_noise_mismatch_qubit_count_with_target_qubits(noise_2qubit):
    circ = Circuit().cswap(0, 1, 2)
    circ.apply_initialization_noise(noise_2qubit, target_qubits=[0, 1, 2])


@pytest.mark.xfail(raises=ValueError)
def test_apply_readout_noise_mismatch_qubit_count_with_target_qubits(noise_2qubit):
    circ = Circuit().cswap(0, 1, 2)
    circ.apply_readout_noise(noise_2qubit, target_qubits=[0, 1, 2])


def test_apply_gate_noise_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = circuit_2qubit.apply_gate_noise(
        noise_1qubit,
        target_gates=[Gate.X, Gate.Z],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_gate_noise_1QubitNoise_parametrized(circuit_2qubit_parametrized, noise_1qubit):
    circ = circuit_2qubit_parametrized.apply_gate_noise(
        noise_1qubit,
        target_gates=[Gate.X, Gate.Rx],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Rx(np.pi), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.XY(np.pi / 2), [0, 1]))
    )

    assert circ == expected


def test_apply_gate_noise_2QubitNoise(circuit_2qubit, noise_2qubit):
    circ = circuit_2qubit.apply_gate_noise(
        noise_2qubit,
        target_gates=[Gate.CNot],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
    )

    assert circ == expected


def test_apply_gate_noise_2QubitNoise2_parametrized(circuit_2qubit_parametrized, noise_2qubit):
    circ = circuit_2qubit_parametrized.apply_gate_noise(
        noise_2qubit,
        target_gates=[Gate.XY],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Rx(np.pi), 1))
        .add_instruction(Instruction(Gate.XY(np.pi / 2), [0, 1]))
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
    )

    assert circ == expected


def test_apply_gate_noise_1QubitNoise_1_unitary(circuit_2qubit_with_unitary, noise_1qubit):
    circ = circuit_2qubit_with_unitary.apply_gate_noise(
        noise_1qubit,
        target_unitary=np.array([[0, 1], [1, 0]]),
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(Gate.Unitary(np.array([[0, 1], [1, 0]]), "U"), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
    )

    assert circ == expected


def test_apply_noise_to_gates_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_gates(
        circuit_2qubit,
        [noise_1qubit],
        target_gates=[Gate.X],
        target_qubits=QubitSet([0, 1]),
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_gates_1QubitNoise_2(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_gates(
        circuit_2qubit,
        [noise_1qubit],
        target_gates=[Gate.X],
        target_qubits=QubitSet(0),
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_gates_2QubitNoise_1(circuit_3qubit, noise_2qubit):
    circ = apply_noise_to_gates(
        circuit_3qubit,
        [noise_2qubit],
        target_gates=[Gate.CNot],
        target_qubits=QubitSet([0, 1, 2]),
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
        .add_instruction(Instruction(Gate.Z(), 2))
        .add_instruction(Instruction(Gate.CZ(), [2, 1]))
        .add_instruction(Instruction(Gate.CNot(), [0, 2]))
        .add_instruction(Instruction(noise_2qubit, [0, 2]))
        .add_instruction(Instruction(Gate.CZ(), [1, 2]))
    )

    assert circ == expected


def test_apply_noise_to_gates_2QubitNoise_2(
    circuit_3qubit, noise_2qubit, noise_1qubit, noise_1qubit_2
):
    circ = apply_noise_to_gates(
        circuit_3qubit,
        [noise_1qubit, noise_2qubit, noise_1qubit_2],
        target_gates=[Gate.CZ],
        target_qubits=QubitSet([1, 2]),
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(Gate.Z(), 2))
        .add_instruction(Instruction(Gate.CZ(), [2, 1]))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(noise_1qubit, 2))
        .add_instruction(Instruction(noise_2qubit, [2, 1]))
        .add_instruction(Instruction(noise_1qubit_2, 1))
        .add_instruction(Instruction(noise_1qubit_2, 2))
        .add_instruction(Instruction(Gate.CNot(), [0, 2]))
        .add_instruction(Instruction(Gate.CZ(), [1, 2]))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(noise_1qubit, 2))
        .add_instruction(Instruction(noise_2qubit, [1, 2]))
        .add_instruction(Instruction(noise_1qubit_2, 1))
        .add_instruction(Instruction(noise_1qubit_2, 2))
    )

    assert circ == expected


def test_apply_noise_to_gates_2QubitNoise_3(
    circuit_3qubit, noise_2qubit, noise_1qubit, noise_1qubit_2
):
    circ = apply_noise_to_gates(
        circuit_3qubit,
        [noise_1qubit, noise_2qubit, noise_1qubit_2],
        target_gates=[Gate.Z],
        target_qubits=QubitSet([1, 2]),
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(Gate.Z(), 2))
        .add_instruction(Instruction(noise_1qubit, 2))
        .add_instruction(Instruction(noise_1qubit_2, 2))
        .add_instruction(Instruction(Gate.CZ(), [2, 1]))
        .add_instruction(Instruction(Gate.CNot(), [0, 2]))
        .add_instruction(Instruction(Gate.CZ(), [1, 2]))
    )

    assert circ == expected


def test_apply_initialization_noise_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = circuit_2qubit.apply_initialization_noise(
        [noise_1qubit],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_moments_initialization_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_1qubit],
        target_qubits=QubitSet([0, 1]),
        position="initialization",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_moments_initialization_2QubitNoise_1(circuit_2qubit, noise_2qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_2qubit],
        target_qubits=QubitSet([0, 1]),
        position="initialization",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_moments_initialization_2QubitNoise_2(
    circuit_2qubit, noise_2qubit, noise_1qubit, noise_1qubit_2
):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_1qubit, noise_2qubit, noise_1qubit_2],
        target_qubits=QubitSet([0, 1]),
        position="initialization",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
        .add_instruction(Instruction(noise_1qubit_2, 0))
        .add_instruction(Instruction(noise_1qubit_2, 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_readout_noise_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = circuit_2qubit.apply_readout_noise(
        [noise_1qubit],
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
    )

    assert circ == expected


def test_noise_not_applied_1QubitNoise_1(circuit_2qubit, noise_2qubit):
    circ = circuit_2qubit.apply_gate_noise(
        [noise_2qubit],
        target_qubits=[1],
        target_gates=[],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_multiple_noise_1QubitNoise_1(circuit_2qubit, noise_1qubit, noise_1qubit_2):
    circ = circuit_2qubit.apply_gate_noise(noise_1qubit).apply_readout_noise(
        noise_1qubit_2,
        target_qubits=[0, 1],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(noise_1qubit_2, 0))
        .add_instruction(Instruction(noise_1qubit_2, 1))
    )

    assert circ == expected


def test_apply_multiple_noise_1QubitNoise_2(circuit_2qubit, noise_1qubit, noise_1qubit_2):
    circ = circuit_2qubit.apply_gate_noise(noise_1qubit, target_gates=[Gate.X],).apply_gate_noise(
        noise_1qubit_2,
        target_qubits=[0],
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit_2, 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(noise_1qubit_2, 0))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit_2, 0))
    )

    assert circ == expected


def test_apply_noise_to_moments_readout_1QubitNoise_1(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_1qubit],
        target_qubits=QubitSet([0, 1]),
        position="readout",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
    )

    assert circ == expected


def test_apply_noise_to_moments_readout_1QubitNoise_3(circuit_2qubit, noise_1qubit, noise_1qubit_2):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        noise=[noise_1qubit, noise_1qubit_2],
        target_qubits=QubitSet([0, 1]),
        position="readout",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit, 0))
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(noise_1qubit_2, 0))
        .add_instruction(Instruction(noise_1qubit_2, 1))
    )

    assert circ == expected


def test_apply_noise_to_moments_readout_2QubitNoise_1(circuit_2qubit, noise_2qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_2qubit],
        target_qubits=QubitSet([0, 1]),
        position="readout",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_2qubit, [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_moments_initialization_1QubitNoise_2(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_1qubit],
        target_qubits=QubitSet(1),
        position="initialization",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(noise_1qubit, 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
    )

    assert circ == expected


def test_apply_noise_to_moments_readout_1QubitNoise_2(circuit_2qubit, noise_1qubit):
    circ = apply_noise_to_moments(
        circuit_2qubit,
        [noise_1qubit],
        target_qubits=QubitSet(1),
        position="readout",
    )

    expected = (
        Circuit()
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.Y(), 1))
        .add_instruction(Instruction(Gate.X(), 0))
        .add_instruction(Instruction(Gate.X(), 1))
        .add_instruction(Instruction(Gate.CNot(), [0, 1]))
        .add_instruction(Instruction(noise_1qubit, 1))
    )

    assert circ == expected


def test_apply_noise_to_gates_1QubitNoise_not_dense(circuit_2qubit_not_dense, noise_1qubit):
    circ = apply_noise_to_gates(
        circuit_2qubit_not_dense,
        [noise_1qubit],
        target_qubits=QubitSet([0, 1]),
        target_gates=None,
    )

    expected_moments = Moments()
    expected_moments._add(Instruction(Gate.X(), 0), noise_index=1)
    expected_moments.add_noise(Instruction(noise_1qubit, 0), "gate_noise", 1)
    expected_moments._add(Instruction(Gate.Y(), 1), noise_index=1)
    expected_moments.add_noise(Instruction(noise_1qubit, 1), "gate_noise", 1)
    expected_moments._add(Instruction(Gate.X(), 0), noise_index=1)
    expected_moments.add_noise(Instruction(noise_1qubit, 0), "gate_noise", 1)
    expected_moments._add(Instruction(Gate.CNot(), [0, 1]), noise_index=2)
    expected_moments.add_noise(Instruction(noise_1qubit, 0), "gate_noise", 1)
    expected_moments.add_noise(Instruction(noise_1qubit, 1), "gate_noise", 2)

    assert circ.moments == expected_moments
