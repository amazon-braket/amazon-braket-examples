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

import json
from typing import Counter
from unittest.mock import patch

import numpy as np
import pytest

from braket.circuits import Observable, ResultType
from braket.ir import jaqcd
from braket.task_result import (
    AdditionalMetadata,
    GateModelTaskResult,
    ResultTypeValue,
    TaskMetadata,
)
from braket.tasks import GateModelQuantumTaskResult


@pytest.fixture
def task_metadata_shots():
    return TaskMetadata(**{"id": "task_arn", "deviceId": "default", "shots": 100})


@pytest.fixture
def task_metadata_zero_shots():
    return TaskMetadata(**{"id": "task_arn", "deviceId": "default", "shots": 0})


@pytest.fixture
def additional_metadata():
    program = jaqcd.Program(instructions=[jaqcd.CNot(control=0, target=1)])
    return AdditionalMetadata(action=program)


@pytest.fixture
def result_obj_1(task_metadata_shots, additional_metadata):
    return GateModelTaskResult(
        measurements=[[0, 0], [0, 1], [0, 1], [0, 1]],
        measuredQubits=[0, 1],
        taskMetadata=task_metadata_shots,
        additionalMetadata=additional_metadata,
    )


@pytest.fixture
def result_str_1(result_obj_1):
    return result_obj_1.json()


@pytest.fixture
def result_str_2(result_obj_1):
    result_obj_1.taskMetadata.id = "task_arn_2"
    return result_obj_1.json()


@pytest.fixture
def result_str_3(task_metadata_shots, additional_metadata):
    return GateModelTaskResult(
        measurementProbabilities={"011000": 0.9999999999999982},
        measuredQubits=list(range(6)),
        taskMetadata=task_metadata_shots,
        additionalMetadata=additional_metadata,
    ).json()


@pytest.fixture
def result_obj_4(task_metadata_zero_shots, additional_metadata):
    return GateModelTaskResult(
        resultTypes=[
            ResultTypeValue.construct(
                type=jaqcd.Probability(targets=[0]), value=np.array([0.5, 0.5])
            ),
            ResultTypeValue.construct(
                type=jaqcd.StateVector(),
                value=np.array([complex(0.70710678, 0), 0, 0, complex(0.70710678, 0)]),
            ),
            ResultTypeValue.construct(
                type=jaqcd.Expectation(observable=["y"], targets=[0]), value=0.0
            ),
            ResultTypeValue.construct(
                type=jaqcd.Variance(observable=["y"], targets=[0]), value=0.1
            ),
            ResultTypeValue.construct(
                type=jaqcd.Amplitude(states=["00"]), value={"00": complex(0.70710678, 0)}
            ),
        ],
        measuredQubits=list(range(2)),
        taskMetadata=task_metadata_zero_shots,
        additionalMetadata=additional_metadata,
    )


@pytest.fixture
def result_str_4(task_metadata_zero_shots, additional_metadata):
    result = GateModelTaskResult(
        resultTypes=[
            ResultTypeValue(type=jaqcd.Probability(targets=[0]), value=[0.5, 0.5]),
            ResultTypeValue(
                type=jaqcd.StateVector(), value=[(0.70710678, 0), (0, 0), (0, 0), (0.70710678, 0)]
            ),
            ResultTypeValue(type=jaqcd.Expectation(observable=["y"], targets=[0]), value=0.0),
            ResultTypeValue(type=jaqcd.Variance(observable=["y"], targets=[0]), value=0.1),
            ResultTypeValue(type=jaqcd.Amplitude(states=["00"]), value={"00": (0.70710678, 0)}),
        ],
        measuredQubits=list(range(2)),
        taskMetadata=task_metadata_zero_shots,
        additionalMetadata=additional_metadata,
    )
    return result.json()


@pytest.fixture
def result_obj_5(task_metadata_shots):
    return GateModelTaskResult(
        taskMetadata=task_metadata_shots,
        additionalMetadata=AdditionalMetadata(
            action=jaqcd.Program(
                instructions=[jaqcd.CNot(control=0, target=1), jaqcd.CNot(control=2, target=3)],
                results=[jaqcd.Probability(targets=[1]), jaqcd.Expectation(observable=["z"])],
            )
        ),
        measurements=[
            [0, 0, 1, 0],
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [0, 0, 1, 0],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [0, 0, 0, 1],
            [0, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 1],
        ],
        measuredQubits=[0, 1, 2, 3],
    )


@pytest.fixture
def malformatted_results_1(task_metadata_shots, additional_metadata):
    return GateModelTaskResult(
        measuredQubits=list(range(6)),
        taskMetadata=task_metadata_shots,
        additionalMetadata=additional_metadata,
    ).json()


@pytest.fixture
def malformatted_results_2(task_metadata_shots, additional_metadata):
    return GateModelTaskResult(
        measurementProbabilities={"011000": 0.9999999999999982},
        measuredQubits=[0],
        taskMetadata=task_metadata_shots,
        additionalMetadata=additional_metadata,
    ).json()


test_ir_results = [
    (jaqcd.Probability(targets=[1]), np.array([0.6, 0.4])),
    (jaqcd.Probability(targets=[1, 2]), np.array([0.4, 0.2, 0.0, 0.4])),
    (
        jaqcd.Probability(),
        np.array([0.1, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2]),
    ),
    (jaqcd.Sample(targets=[1], observable=["z"]), np.array([1, -1, 1, 1, -1, -1, 1, -1, 1, 1])),
    (
        jaqcd.Sample(targets=[1, 2], observable=["x", "y"]),
        np.array([-1, 1, 1, -1, 1, 1, 1, 1, 1, 1]),
    ),
    (
        jaqcd.Sample(observable=["z"]),
        [
            np.array([1, -1, -1, 1, -1, 1, 1, 1, 1, 1]),
            np.array([1, -1, 1, 1, -1, -1, 1, -1, 1, 1]),
            np.array([-1, -1, 1, -1, -1, -1, 1, -1, 1, 1]),
            np.array([1, -1, -1, 1, -1, -1, -1, -1, 1, -1]),
        ],
    ),
    (jaqcd.Expectation(targets=[1], observable=["z"]), 0.2),
    (jaqcd.Expectation(targets=[1], observable=[[[[-1, 0], [0, 0]], [[0, 0], [1, 0]]]]), -0.2),
    (jaqcd.Expectation(targets=[1, 2], observable=["z", "y"]), 0.6),
    (jaqcd.Expectation(observable=["z"]), [0.4, 0.2, -0.2, -0.4]),
    (jaqcd.Variance(targets=[1], observable=["z"]), 0.96),
    (jaqcd.Variance(targets=[1], observable=[[[[-1, 0], [0, 0]], [[0, 0], [1, 0]]]]), 0.96),
    (jaqcd.Variance(targets=[1, 2], observable=["z", "y"]), 0.64),
    (jaqcd.Variance(observable=["z"]), [0.84, 0.96, 0.96, 0.84]),
]


def test_measurement_counts_from_measurements():
    measurements: np.ndarray = np.array(
        [[1, 0, 1, 0], [0, 0, 0, 0], [1, 0, 1, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 1, 0]]
    )
    measurement_counts = GateModelQuantumTaskResult.measurement_counts_from_measurements(
        measurements
    )
    expected_counts: Counter = {"1010": 3, "0000": 1, "1000": 2}
    assert expected_counts == measurement_counts


def test_measurement_probabilities_from_measurement_counts():
    counts = {"00": 1, "01": 1, "10": 1, "11": 97}
    probabilities = {"00": 0.01, "01": 0.01, "10": 0.01, "11": 0.97}

    m_probabilities = GateModelQuantumTaskResult.measurement_probabilities_from_measurement_counts(
        counts
    )

    assert m_probabilities == probabilities


def test_measurements_from_measurement_probabilities():
    shots = 5
    probabilities = {"00": 0.2, "01": 0.2, "10": 0.2, "11": 0.4}
    measurements_list = [["0", "0"], ["0", "1"], ["1", "0"], ["1", "1"], ["1", "1"]]
    expected_results = np.asarray(measurements_list, dtype=int)

    measurements = GateModelQuantumTaskResult.measurements_from_measurement_probabilities(
        probabilities, shots
    )

    assert np.allclose(measurements, expected_results)


def test_from_string_measurements(result_str_1):
    result_obj = GateModelTaskResult.parse_raw(result_str_1)
    task_result = GateModelQuantumTaskResult.from_string(result_str_1)
    expected_measurements = np.asarray(result_obj.measurements, dtype=int)
    assert task_result.task_metadata == result_obj.taskMetadata
    assert task_result.additional_metadata == result_obj.additionalMetadata
    assert np.array2string(task_result.measurements) == np.array2string(expected_measurements)
    assert not task_result.measurement_counts_copied_from_device
    assert not task_result.measurement_probabilities_copied_from_device
    assert task_result.measurements_copied_from_device
    assert task_result.measured_qubits == result_obj.measuredQubits
    assert task_result.values == []
    assert task_result.result_types == []


def test_from_object_result_types(result_obj_5):
    result_obj = result_obj_5
    task_result = GateModelQuantumTaskResult.from_object(result_obj)
    expected_measurements = np.asarray(result_obj.measurements, dtype=int)
    assert np.array2string(task_result.measurements) == np.array2string(expected_measurements)
    assert np.allclose(task_result.values[0], np.array([0.6, 0.4]))
    assert task_result.values[1] == [0.4, 0.2, -0.2, -0.4]
    assert task_result.result_types[0].type == jaqcd.Probability(targets=[1])
    assert task_result.result_types[1].type == jaqcd.Expectation(observable=["z"])


def test_from_string_measurement_probabilities(result_str_3):
    result_obj = GateModelTaskResult.parse_raw(result_str_3)
    task_result = GateModelQuantumTaskResult.from_string(result_str_3)
    assert task_result.measurement_probabilities == result_obj.measurementProbabilities
    shots = 100
    measurement_list = [list("011000") for _ in range(shots)]
    expected_measurements = np.asarray(measurement_list, dtype=int)
    assert np.allclose(task_result.measurements, expected_measurements)
    assert task_result.measurement_counts == Counter(["011000" for x in range(shots)])
    assert not task_result.measurement_counts_copied_from_device
    assert task_result.measurement_probabilities_copied_from_device
    assert not task_result.measurements_copied_from_device


def test_from_object_equal_to_from_string(result_obj_1, result_str_1, result_str_3):
    assert GateModelQuantumTaskResult.from_object(
        result_obj_1
    ) == GateModelQuantumTaskResult.from_string(result_str_1)
    assert GateModelQuantumTaskResult.from_object(
        GateModelTaskResult.parse_raw(result_str_3)
    ) == GateModelQuantumTaskResult.from_string(result_str_3)


def test_equality(result_str_1, result_str_2):
    result_1 = GateModelQuantumTaskResult.from_string(result_str_1)
    result_2 = GateModelQuantumTaskResult.from_string(result_str_1)
    other_result = GateModelQuantumTaskResult.from_string(result_str_2)
    non_result = "not a quantum task result"

    assert result_1 == result_2
    assert result_1 is not result_2
    assert result_1 != other_result
    assert result_1 != non_result


def test_from_string_simulator_only(result_obj_4, result_str_4):
    result_obj = result_obj_4
    result = GateModelQuantumTaskResult.from_string(result_str_4)
    assert len(result.result_types) == len(result_obj.resultTypes)
    for i in range(len(result.result_types)):
        rt = result.result_types[i]
        expected_rt = result_obj.resultTypes[i]
        assert rt.type == expected_rt.type
        if isinstance(rt.value, np.ndarray):
            assert np.allclose(rt.value, expected_rt.value)
        else:
            assert rt.value == expected_rt.value


def test_get_value_by_result_type(result_obj_4):
    result = GateModelQuantumTaskResult.from_object(result_obj_4)
    assert np.allclose(
        result.get_value_by_result_type(ResultType.Probability(target=0)), result.values[0]
    )
    assert np.allclose(result.get_value_by_result_type(ResultType.StateVector()), result.values[1])
    assert (
        result.get_value_by_result_type(ResultType.Expectation(observable=Observable.Y(), target=0))
        == result.values[2]
    )
    assert (
        result.get_value_by_result_type(ResultType.Variance(observable=Observable.Y(), target=0))
        == result.values[3]
    )
    assert result.get_value_by_result_type(ResultType.Amplitude(state=["00"])) == result.values[4]


@pytest.mark.xfail(raises=ValueError)
def test_get_value_by_result_type_value_error(result_obj_4):
    result = GateModelQuantumTaskResult.from_object(result_obj_4)
    result.get_value_by_result_type(ResultType.Probability(target=[0, 1]))


@pytest.mark.xfail(raises=ValueError)
def test_shots_no_measurements_no_measurement_probs(malformatted_results_1):
    GateModelQuantumTaskResult.from_string(malformatted_results_1)


@pytest.mark.xfail(raises=ValueError)
def test_measurements_measured_qubits_mismatch(malformatted_results_2):
    GateModelQuantumTaskResult.from_string(malformatted_results_2)


@pytest.mark.parametrize("ir_result,expected_result", test_ir_results)
def test_calculate_ir_results(ir_result, expected_result):
    ir_string = jaqcd.Program(
        instructions=[jaqcd.H(target=i) for i in range(4)], results=[ir_result]
    ).json()
    measured_qubits = [0, 1, 2, 3]
    measurements = np.array(
        [
            [0, 0, 1, 0],
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [0, 0, 1, 0],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [0, 0, 0, 1],
            [0, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 1],
        ]
    )
    result_types = GateModelQuantumTaskResult._calculate_result_types(
        ir_string, measurements, measured_qubits
    )
    assert len(result_types) == 1
    assert result_types[0].type == ir_result
    assert np.allclose(result_types[0].value, expected_result)


@pytest.mark.xfail(raises=ValueError)
def test_calculate_ir_results_value_error():
    ir_string = json.dumps({"results": [{"type": "foo"}]})
    measured_qubits = [0]
    measurements = np.array([[0]])
    GateModelQuantumTaskResult._calculate_result_types(ir_string, measurements, measured_qubits)


@pytest.mark.parametrize(
    "observable_1, observable_2",
    [
        (
            jaqcd.Expectation(targets=[1, 2], observable=["x"]),
            jaqcd.Expectation(observable=["x"], targets=[1, 2]),
        ),
        pytest.param(
            jaqcd.Expectation(observable=["x"], targets=[1, 2]),
            jaqcd.Expectation(observable=["x"], targets=[2, 1]),
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            jaqcd.Expectation(observable=["x"], targets=[1, 2]),
            jaqcd.Sample(observable=["x"], targets=[2, 1]),
            marks=pytest.mark.xfail,
        ),
        (
            jaqcd.Expectation(
                observable=[
                    [[[0, 0], [0.512345, 0]], [[0.543215, 0], [0, 0]]],
                    [[[1, 0], [1, 0]], [[1, 0], [-1, 0]]],
                ],
                targets=[1, 2],
            ),
            jaqcd.Expectation(
                observable=[
                    [[[0, 0], [0.512345, 0]], [[0.543215, 0], [0, 0]]],
                    [[[1, 0], [1, 0]], [[1, 0], [-1, 0]]],
                ],
                targets=[1, 2],
            ),
        ),
        (
            jaqcd.Expectation(observable=["y", "z"], targets=[1, 2]),
            jaqcd.Expectation(observable=["y", "z"], targets=[1, 2]),
        ),
    ],
)
def test_hash_result_types(observable_1, observable_2):
    assert GateModelQuantumTaskResult._result_type_hash(
        observable_1
    ) == GateModelQuantumTaskResult._result_type_hash(observable_2)


@patch(
    "braket.tasks.gate_model_quantum_task_result.GateModelQuantumTaskResult._calculate_result_types"
)
def test_result_type_skips_computation_already_populated(calculate_result_types_mocked):
    result_str = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.gate_model_task_result",
                "version": "1",
            },
            "measurements": [[0]],
            "resultTypes": [
                {"type": {"observable": ["z"], "targets": [0], "type": "variance"}, "value": 12.0}
            ],
            "measuredQubits": [0],
            "taskMetadata": {
                "braketSchemaHeader": {"name": "braket.task_result.task_metadata", "version": "1"},
                "id": "arn:aws:braket:us-east-1:1234567890:quantum-task/22a238b2-ae96",
                "shots": 1,
                "deviceId": "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
                "deviceParameters": {
                    "braketSchemaHeader": {
                        "name": "braket.device_schema.simulators."
                        "gate_model_simulator_device_parameters",
                        "version": "1",
                    },
                    "paradigmParameters": {
                        "braketSchemaHeader": {
                            "name": "braket.device_schema.gate_model_parameters",
                            "version": "1",
                        },
                        "qubitCount": 1,
                        "disableQubitRewiring": False,
                    },
                },
                "createdAt": "2022-01-12T06:05:22.633Z",
                "endedAt": "2022-01-12T06:05:24.136Z",
                "status": "COMPLETED",
            },
            "additionalMetadata": {
                "action": {
                    "braketSchemaHeader": {"name": "braket.ir.openqasm.program", "version": "1"},
                    "source": "\nqubit[1] q;\nh q[0];\n#pragma braket result variance z(q[0])\n",
                },
                "simulatorMetadata": {
                    "braketSchemaHeader": {
                        "name": "braket.task_result.simulator_metadata",
                        "version": "1",
                    },
                    "executionDuration": 16,
                },
            },
        }
    )
    res = GateModelQuantumTaskResult.from_string(result_str)
    assert (
        res.get_value_by_result_type(ResultType.Variance(observable=Observable.Z(), target=[0]))
        == 12
    )
    calculate_result_types_mocked.assert_not_called()
