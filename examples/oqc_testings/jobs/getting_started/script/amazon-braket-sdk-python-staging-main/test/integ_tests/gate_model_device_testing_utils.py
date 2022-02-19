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

import concurrent.futures
import math
from typing import Any, Dict, Union

import numpy as np

from braket.aws import AwsDevice
from braket.circuits import Circuit, Gate, Instruction, Observable, ResultType
from braket.circuits.quantum_operator_helpers import get_pauli_eigenvalues
from braket.devices import Device
from braket.ir.openqasm import Program as OpenQasmProgram
from braket.tasks import GateModelQuantumTaskResult


def get_tol(shots: int) -> Dict[str, float]:
    return {"atol": 0.1, "rtol": 0.15} if shots else {"atol": 0.01, "rtol": 0}


def qubit_ordering_testing(device: Device, run_kwargs: Dict[str, Any]):
    # |110> should get back value of "110"
    state_110 = Circuit().x(0).x(1).i(2)
    result = device.run(state_110, **run_kwargs).result()
    assert result.measurement_counts.most_common(1)[0][0] == "110"

    # |001> should get back value of "001"
    state_001 = Circuit().i(0).i(1).x(2)
    result = device.run(state_001, **run_kwargs).result()
    assert result.measurement_counts.most_common(1)[0][0] == "001"


def no_result_types_testing(
    program: Union[Circuit, OpenQasmProgram],
    device: Device,
    run_kwargs: Dict[str, Any],
    expected: Dict[str, float],
):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    result = device.run(program, **run_kwargs).result()
    probabilities = result.measurement_probabilities
    for bitstring in probabilities:
        assert np.allclose(probabilities[bitstring], expected[bitstring], **tol)
    assert len(result.measurements) == shots


def no_result_types_bell_pair_testing(device: Device, run_kwargs: Dict[str, Any]):
    no_result_types_testing(Circuit().h(0).cnot(0, 1), device, run_kwargs, {"00": 0.5, "11": 0.5})


def result_types_observable_not_in_instructions(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    bell = (
        Circuit()
        .h(0)
        .cnot(0, 1)
        .expectation(observable=Observable.X(), target=[2])
        .variance(observable=Observable.Y(), target=[3])
    )
    result = device.run(bell, **run_kwargs).result()
    assert np.allclose(result.values[0], 0, **tol)
    assert np.allclose(result.values[1], 1, **tol)


def result_types_zero_shots_bell_pair_testing(
    device: Device,
    include_state_vector: bool,
    run_kwargs: Dict[str, Any],
    include_amplitude: bool = True,
):
    circuit = (
        Circuit()
        .h(0)
        .cnot(0, 1)
        .expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
    )
    if include_amplitude:
        circuit.amplitude(["01", "10", "00", "11"])
    if include_state_vector:
        circuit.state_vector()
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 3 if include_state_vector else 2
    assert np.allclose(
        result.get_value_by_result_type(
            ResultType.Expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
        ),
        1 / np.sqrt(2),
    )
    if include_state_vector:
        assert np.allclose(
            result.get_value_by_result_type(ResultType.StateVector()),
            np.array([1, 0, 0, 1]) / np.sqrt(2),
        )
    if include_amplitude:
        assert result.get_value_by_result_type(ResultType.Amplitude(["01", "10", "00", "11"])) == {
            "01": 0j,
            "10": 0j,
            "00": (1 / np.sqrt(2)),
            "11": (1 / np.sqrt(2)),
        }


def result_types_bell_pair_full_probability_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    circuit = Circuit().h(0).cnot(0, 1).probability()
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 1
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability()), np.array([0.5, 0, 0, 0.5]), **tol
    )


def result_types_bell_pair_marginal_probability_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    circuit = Circuit().h(0).cnot(0, 1).probability(0)
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 1
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability(target=0)),
        np.array([0.5, 0.5]),
        **tol
    )


def result_types_nonzero_shots_bell_pair_testing(device: Device, run_kwargs: Dict[str, Any]):
    circuit = (
        Circuit()
        .h(0)
        .cnot(0, 1)
        .expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
        .sample(observable=Observable.H() @ Observable.X(), target=[0, 1])
    )
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 2
    assert (
        0.6
        < result.get_value_by_result_type(
            ResultType.Expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
        )
        < 0.8
    )
    assert (
        len(
            result.get_value_by_result_type(
                ResultType.Sample(observable=Observable.H() @ Observable.X(), target=[0, 1])
            )
        )
        == run_kwargs["shots"]
    )


def result_types_hermitian_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.543
    array = np.array([[1, 2j], [-2j, 0]])

    circuit = (
        Circuit()
        .rx(0, theta)
        .variance(Observable.Hermitian(array), 0)
        .expectation(Observable.Hermitian(array), 0)
    )
    if shots:
        circuit.add_result_type(ResultType.Sample(Observable.Hermitian(array), 0))
    result = device.run(circuit, **run_kwargs).result()

    expected_mean = 2 * np.sin(theta) + 0.5 * np.cos(theta) + 0.5
    expected_var = 0.25 * (np.sin(theta) - 4 * np.cos(theta)) ** 2
    expected_eigs = np.linalg.eigvalsh(array)
    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_all_selected_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.543
    array = np.array([[1, 2j], [-2j, 0]])

    circuit = (
        Circuit()
        .rx(0, theta)
        .rx(1, theta)
        .variance(Observable.Hermitian(array))
        .expectation(Observable.Hermitian(array), 0)
    )
    if shots:
        circuit.add_result_type(ResultType.Sample(Observable.Hermitian(array), 1))
    result = device.run(circuit, **run_kwargs).result()

    expected_mean = 2 * np.sin(theta) + 0.5 * np.cos(theta) + 0.5
    var = 0.25 * (np.sin(theta) - 4 * np.cos(theta)) ** 2
    expected_var = [var, var]
    expected_eigs = np.linalg.eigvalsh(array)
    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots) -> Circuit:
    circuit = (
        Circuit()
        .rx(0, theta)
        .rx(1, phi)
        .rx(2, varphi)
        .cnot(0, 1)
        .cnot(1, 2)
        .variance(obs, obs_targets)
        .expectation(obs, obs_targets)
    )
    if shots:
        circuit.sample(obs, obs_targets)
    return circuit


def assert_variance_expectation_sample_result(
    result: GateModelQuantumTaskResult,
    shots: int,
    expected_var: float,
    expected_mean: float,
    expected_eigs: np.ndarray,
):
    tol = get_tol(shots)
    variance = result.values[0]
    expectation = result.values[1]
    if shots:
        samples = result.values[2]
        assert np.allclose(sorted(list(set(samples))), sorted(expected_eigs), **tol)
        assert np.allclose(np.mean(samples), expected_mean, **tol)
        assert np.allclose(np.var(samples), expected_var, **tol)
    assert np.allclose(expectation, expected_mean, **tol)
    assert np.allclose(variance, expected_var, **tol)


def result_types_tensor_x_y_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    obs = Observable.X() @ Observable.Y()
    obs_targets = [0, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)
    result = device.run(circuit, **run_kwargs).result()

    expected_mean = np.sin(theta) * np.sin(phi) * np.sin(varphi)
    expected_var = (
        8 * np.sin(theta) ** 2 * np.cos(2 * varphi) * np.sin(phi) ** 2
        - np.cos(2 * (theta - phi))
        - np.cos(2 * (theta + phi))
        + 2 * np.cos(2 * theta)
        + 2 * np.cos(2 * phi)
        + 14
    ) / 16
    expected_eigs = get_pauli_eigenvalues(1)

    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_tensor_z_z_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    obs = Observable.Z() @ Observable.Z()
    obs_targets = [0, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)
    result = device.run(circuit, **run_kwargs).result()

    expected_mean = 0.849694136476246
    expected_var = 0.27801987443788634
    expected_eigs = get_pauli_eigenvalues(1)

    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_tensor_hermitian_hermitian_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    matrix1 = np.array([[1, 2], [2, 4]])
    matrix2 = np.array(
        [
            [-6, 2 + 1j, -3, -5 + 2j],
            [2 - 1j, 0, 2 - 1j, -5 + 4j],
            [-3, 2 + 1j, 0, -4 + 3j],
            [-5 - 2j, -5 - 4j, -4 - 3j, -6],
        ]
    )
    obs = Observable.Hermitian(matrix1) @ Observable.Hermitian(matrix2)
    obs_targets = [0, 1, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)
    result = device.run(circuit, **run_kwargs).result()

    expected_mean = -4.30215023196904
    expected_var = 370.71292282796804
    expected_eigs = np.array([-70.90875406, -31.04969387, 0, 3.26468993, 38.693758])

    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_tensor_z_h_y_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    obs = Observable.Z() @ Observable.H() @ Observable.Y()
    obs_targets = [0, 1, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)

    result = device.run(circuit, **run_kwargs).result()

    expected_mean = -(np.cos(varphi) * np.sin(phi) + np.sin(varphi) * np.cos(theta)) / np.sqrt(2)
    expected_var = (
        3
        + np.cos(2 * phi) * np.cos(varphi) ** 2
        - np.cos(2 * theta) * np.sin(varphi) ** 2
        - 2 * np.cos(theta) * np.sin(phi) * np.sin(2 * varphi)
    ) / 4
    expected_eigs = get_pauli_eigenvalues(1)
    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_tensor_z_hermitian_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    array = np.array(
        [
            [-6, 2 + 1j, -3, -5 + 2j],
            [2 - 1j, 0, 2 - 1j, -5 + 4j],
            [-3, 2 + 1j, 0, -4 + 3j],
            [-5 - 2j, -5 - 4j, -4 - 3j, -6],
        ]
    )
    obs = Observable.Z() @ Observable.Hermitian(array)
    obs_targets = [0, 1, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)

    result = device.run(circuit, **run_kwargs).result()

    expected_mean = 0.5 * (
        -6 * np.cos(theta) * (np.cos(varphi) + 1)
        - 2 * np.sin(varphi) * (np.cos(theta) + np.sin(phi) - 2 * np.cos(phi))
        + 3 * np.cos(varphi) * np.sin(phi)
        + np.sin(phi)
    )
    expected_var = (
        1057
        - np.cos(2 * phi)
        + 12 * (27 + np.cos(2 * phi)) * np.cos(varphi)
        - 2 * np.cos(2 * varphi) * np.sin(phi) * (16 * np.cos(phi) + 21 * np.sin(phi))
        + 16 * np.sin(2 * phi)
        - 8 * (-17 + np.cos(2 * phi) + 2 * np.sin(2 * phi)) * np.sin(varphi)
        - 8 * np.cos(2 * theta) * (3 + 3 * np.cos(varphi) + np.sin(varphi)) ** 2
        - 24 * np.cos(phi) * (np.cos(phi) + 2 * np.sin(phi)) * np.sin(2 * varphi)
        - 8
        * np.cos(theta)
        * (
            4
            * np.cos(phi)
            * (
                4
                + 8 * np.cos(varphi)
                + np.cos(2 * varphi)
                - (1 + 6 * np.cos(varphi)) * np.sin(varphi)
            )
            + np.sin(phi)
            * (
                15
                + 8 * np.cos(varphi)
                - 11 * np.cos(2 * varphi)
                + 42 * np.sin(varphi)
                + 3 * np.sin(2 * varphi)
            )
        )
    ) / 16

    z_array = np.diag([1, -1])
    expected_eigs = np.linalg.eigvalsh(np.kron(z_array, array))
    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_tensor_y_hermitian_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    array = np.array(
        [
            [-6, 2 + 1j, -3, -5 + 2j],
            [2 - 1j, 0, 2 - 1j, -5 + 4j],
            [-3, 2 + 1j, 0, -4 + 3j],
            [-5 - 2j, -5 - 4j, -4 - 3j, -6],
        ]
    )
    obs = Observable.Y() @ Observable.Hermitian(array)
    obs_targets = [0, 1, 2]
    circuit = get_result_types_three_qubit_circuit(theta, phi, varphi, obs, obs_targets, shots)

    result = device.run(circuit, **run_kwargs).result()

    expected_mean = 1.4499810303182408
    expected_var = 74.03174647518193
    y_array = np.array([[0, -1j], [1j, 0]])
    expected_eigs = np.linalg.eigvalsh(np.kron(y_array, array))
    assert_variance_expectation_sample_result(
        result, shots, expected_var, expected_mean, expected_eigs
    )


def result_types_noncommuting_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = 0
    theta = 0.432
    phi = 0.123
    varphi = -0.543
    array = np.array(
        [
            [-6, 2 + 1j, -3, -5 + 2j],
            [2 - 1j, 0, 2 - 1j, -5 + 4j],
            [-3, 2 + 1j, 0, -4 + 3j],
            [-5 - 2j, -5 - 4j, -4 - 3j, -6],
        ]
    )
    obs1 = Observable.X() @ Observable.Y()
    obs1_targets = [0, 2]
    obs2 = Observable.Z() @ Observable.Z()
    obs2_targets = [0, 2]
    obs3 = Observable.Y() @ Observable.Hermitian(array)
    obs3_targets = [0, 1, 2]
    circuit = (
        get_result_types_three_qubit_circuit(theta, phi, varphi, obs1, obs1_targets, shots)
        .expectation(obs2, obs2_targets)
        .expectation(obs3, obs3_targets)
    )
    result = device.run(circuit, **run_kwargs).result()

    expected_mean1 = np.sin(theta) * np.sin(phi) * np.sin(varphi)
    expected_var1 = (
        8 * np.sin(theta) ** 2 * np.cos(2 * varphi) * np.sin(phi) ** 2
        - np.cos(2 * (theta - phi))
        - np.cos(2 * (theta + phi))
        + 2 * np.cos(2 * theta)
        + 2 * np.cos(2 * phi)
        + 14
    ) / 16

    expected_mean2 = 0.849694136476246
    expected_mean3 = 1.4499810303182408
    assert np.allclose(result.values[0], expected_var1)
    assert np.allclose(result.values[1], expected_mean1)
    assert np.allclose(result.values[2], expected_mean2)
    assert np.allclose(result.values[3], expected_mean3)


def result_types_noncommuting_flipped_targets_testing(device: Device, run_kwargs: Dict[str, Any]):
    circuit = (
        Circuit()
        .h(0)
        .cnot(0, 1)
        .expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
        .expectation(observable=Observable.H() @ Observable.X(), target=[1, 0])
    )
    result = device.run(circuit, shots=0, **run_kwargs).result()
    assert np.allclose(result.values[0], np.sqrt(2) / 2)
    assert np.allclose(result.values[1], np.sqrt(2) / 2)


def result_types_noncommuting_all(device: Device, run_kwargs: Dict[str, Any]):
    array = np.array([[1, 2j], [-2j, 0]])
    circuit = (
        Circuit()
        .h(0)
        .cnot(0, 1)
        .expectation(observable=Observable.Hermitian(array))
        .expectation(observable=Observable.X())
    )
    result = device.run(circuit, shots=0, **run_kwargs).result()
    assert np.allclose(result.values[0], [0.5, 0.5])
    assert np.allclose(result.values[1], [0, 0])


def multithreaded_bell_pair_testing(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    bell = Circuit().h(0).cnot(0, 1)

    def run_circuit(circuit):
        task = device.run(circuit, **run_kwargs)
        return task.result()

    futures = []
    num_threads = 2

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for _ in range(num_threads):
            future = executor.submit(run_circuit, bell)
            futures.append(future)
    for future in futures:
        result = future.result()
        assert np.allclose(result.measurement_probabilities["00"], 0.5, **tol)
        assert np.allclose(result.measurement_probabilities["11"], 0.5, **tol)
        assert len(result.measurements) == shots


def noisy_circuit_1qubit_noise_full_probability(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    circuit = Circuit().x(0).x(1).bit_flip(0, 0.1).probability()
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 1
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability()),
        np.array([0.0, 0.1, 0, 0.9]),
        **tol
    )


def noisy_circuit_2qubit_noise_full_probability(device: Device, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    K0 = np.eye(4) * np.sqrt(0.9)
    K1 = np.kron(np.array([[0.0, 1.0], [1.0, 0.0]]), np.array([[0.0, 1.0], [1.0, 0.0]])) * np.sqrt(
        0.1
    )
    circuit = Circuit().x(0).x(1).kraus((0, 1), [K0, K1]).probability()
    result = device.run(circuit, **run_kwargs).result()
    assert len(result.result_types) == 1
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability()),
        np.array([0.1, 0.0, 0, 0.9]),
        **tol
    )


def batch_bell_pair_testing(device: AwsDevice, run_kwargs: Dict[str, Any]):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    circuits = [Circuit().h(0).cnot(0, 1) for _ in range(10)]

    batch = device.run_batch(circuits, max_parallel=5, **run_kwargs)
    results = batch.results()
    for result in results:
        assert np.allclose(result.measurement_probabilities["00"], 0.5, **tol)
        assert np.allclose(result.measurement_probabilities["11"], 0.5, **tol)
        assert len(result.measurements) == shots
    assert [task.result() for task in batch.tasks] == results


def bell_pair_openqasm_testing(device: AwsDevice, run_kwargs: Dict[str, Any]):
    openqasm_string = (
        "OPENQASM 3;"
        "qubit[2] q;"
        "bit[2] c;"
        "h q[0];"
        "cnot q[0], q[1];"
        "c[0] = measure q[0];"
        "c[1] = measure q[1];"
    )
    no_result_types_testing(
        OpenQasmProgram(source=openqasm_string), device, run_kwargs, {"00": 0.5, "11": 0.5}
    )


def openqasm_noisy_circuit_1qubit_noise_full_probability(
    device: Device, run_kwargs: Dict[str, Any]
):
    shots = run_kwargs["shots"]
    tol = get_tol(shots)
    openqasm_string = (
        "OPENQASM 3;"
        "qubit[2] q;"
        "x q[0];"
        "x q[1];"
        "#pragma braket noise bit_flip(0.1) q[0]"
        "#pragma braket result probability q[0], q[1]"
    )
    result = device.run(OpenQasmProgram(source=openqasm_string), **run_kwargs).result()
    assert len(result.result_types) == 1
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability(target=[0, 1])),
        np.array([0.0, 0.1, 0, 0.9]),
        **tol
    )


def openqasm_result_types_bell_pair_testing(device: Device, run_kwargs: Dict[str, Any]):
    openqasm_string = (
        "OPENQASM 3;"
        "qubit[2] q;"
        "h q[0];"
        "cnot q[0], q[1];"
        "#pragma braket result expectation h(q[0]) @ x(q[1])"
        "#pragma braket result sample h(q[0]) @ x(q[1])"
    )
    result = device.run(OpenQasmProgram(source=openqasm_string), **run_kwargs).result()
    assert len(result.result_types) == 2
    assert (
        0.6
        < result.get_value_by_result_type(
            ResultType.Expectation(observable=Observable.H() @ Observable.X(), target=[0, 1])
        )
        < 0.8
    )
    assert (
        len(
            result.get_value_by_result_type(
                ResultType.Sample(observable=Observable.H() @ Observable.X(), target=[0, 1])
            )
        )
        == run_kwargs["shots"]
    )


def many_layers(n_qubits: int, n_layers: int) -> Circuit:
    """
    Function to return circuit with many layers.

    :param int n_qubits: number of qubits
    :param int n_layers: number of layers
    :return: Constructed easy circuit
    :rtype: Circuit
    """
    qubits = range(n_qubits)
    circuit = Circuit()  # instantiate circuit object
    for q in range(n_qubits):
        circuit.h(q)
    for layer in range(n_layers):
        if (layer + 1) % 100 != 0:
            for qubit in range(len(qubits)):
                angle = np.random.uniform(0, 2 * math.pi)
                gate = np.random.choice(
                    [Gate.Rx(angle), Gate.Ry(angle), Gate.Rz(angle), Gate.H()], 1, replace=True
                )[0]
                circuit.add_instruction(Instruction(gate, qubit))
        else:
            for q in range(0, n_qubits, 2):
                circuit.cnot(q, q + 1)
            for q in range(1, n_qubits - 1, 2):
                circuit.cnot(q, q + 1)
    return circuit
