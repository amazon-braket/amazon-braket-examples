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

from braket.ir.annealing import Problem
from braket.task_result import (
    AdditionalMetadata,
    AnnealingTaskResult,
    DwaveMetadata,
    DwaveTiming,
    TaskMetadata,
)
from braket.tasks import AnnealingQuantumTaskResult


@pytest.fixture
def solutions():
    return [[-1, -1, -1, -1], [1, -1, 1, 1], [1, -1, -1, 1]]


@pytest.fixture
def values():
    return [0.0, 1.0, 2.0]


@pytest.fixture
def variable_count():
    return 4


@pytest.fixture
def solution_counts():
    return [3, 2, 4]


@pytest.fixture
def problem_type():
    return "ISING"


@pytest.fixture
def task_metadata():
    return TaskMetadata(**{"id": "task_arn", "deviceId": "arn1", "shots": 100})


@pytest.fixture
def dwave_metadata():
    return DwaveMetadata(
        activeVariables=[0],
        timing=DwaveTiming(
            qpuSamplingTime=100,
            qpuAnnealTimePerSample=20,
            qpuReadoutTimePerSample=274,
            qpuAccessTime=10917,
            qpuAccessOverheadTime=3382,
            qpuProgrammingTime=9342,
            qpuDelayTimePerSample=21,
            totalPostProcessingTime=117,
            postProcessingOverheadTime=117,
            totalRealTime=10917,
            runTimeChip=1575,
            annealTimePerRun=20,
            readoutTimePerRun=274,
        ),
    )


@pytest.fixture
def additional_metadata(problem_type, dwave_metadata):
    problem = Problem(
        type=problem_type,
        linear={0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333},
        quadratic={"0,4": 0.667, "0,5": -1, "1,4": 0.667, "1,5": 0.667},
    )
    return AdditionalMetadata(action=problem, dwaveMetadata=dwave_metadata)


@pytest.fixture
def result_str_1(
    solutions, values, solution_counts, variable_count, task_metadata, additional_metadata
):
    result = AnnealingTaskResult(
        solutions=solutions,
        variableCount=variable_count,
        values=values,
        solutionCounts=solution_counts,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata,
    )
    return result.json()


@pytest.fixture
def result_str_2(solutions, values, variable_count, task_metadata, additional_metadata):
    result = AnnealingTaskResult(
        solutions=solutions,
        variableCount=variable_count,
        values=values,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata,
    )
    return result.json()


@pytest.fixture
def result_str_3(solutions, values, variable_count, task_metadata, additional_metadata):
    result = AnnealingTaskResult(
        solutionCounts=[],
        solutions=solutions,
        variableCount=variable_count,
        values=values,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata,
    )
    return result.json()


@pytest.fixture
def annealing_result(
    solutions,
    values,
    solution_counts,
    variable_count,
    problem_type,
    additional_metadata,
    task_metadata,
):
    solutions = np.asarray(solutions, dtype=int)
    values = np.asarray(values, dtype=float)
    solution_counts = np.asarray(solution_counts, dtype=int)
    record_array = AnnealingQuantumTaskResult._create_record_array(
        solutions, solution_counts, values
    )
    return AnnealingQuantumTaskResult(
        record_array=record_array,
        variable_count=variable_count,
        problem_type=problem_type,
        task_metadata=task_metadata,
        additional_metadata=additional_metadata,
    )


def test_from_object(
    result_str_1,
    solutions,
    values,
    solution_counts,
    variable_count,
    problem_type,
    task_metadata,
    additional_metadata,
):
    result = AnnealingQuantumTaskResult.from_object(AnnealingTaskResult.parse_raw(result_str_1))
    solutions = np.asarray(solutions, dtype=int)
    values = np.asarray(values, dtype=float)
    solution_counts = np.asarray(solution_counts, dtype=int)
    assert result.variable_count == variable_count
    assert result.problem_type == problem_type
    assert result.task_metadata == task_metadata
    assert result.additional_metadata == additional_metadata
    np.testing.assert_equal(
        result.record_array,
        AnnealingQuantumTaskResult._create_record_array(solutions, solution_counts, values),
    )


def test_from_string(
    result_str_1,
    solutions,
    values,
    solution_counts,
    variable_count,
    problem_type,
    task_metadata,
    additional_metadata,
):
    result = AnnealingQuantumTaskResult.from_string(result_str_1)
    solutions = np.asarray(solutions, dtype=int)
    values = np.asarray(values, dtype=float)
    solution_counts = np.asarray(solution_counts, dtype=int)
    assert result.variable_count == variable_count
    assert result.problem_type == problem_type
    assert result.task_metadata == task_metadata
    assert result.additional_metadata == additional_metadata
    np.testing.assert_equal(
        result.record_array,
        AnnealingQuantumTaskResult._create_record_array(solutions, solution_counts, values),
    )


def test_from_string_solution_counts_none(result_str_2, solutions):
    result = AnnealingQuantumTaskResult.from_string(result_str_2)
    np.testing.assert_equal(result.record_array.solution_count, np.ones(len(solutions), dtype=int))


def test_from_string_solution_counts_empty_list(result_str_3, solutions):
    result = AnnealingQuantumTaskResult.from_string(result_str_3)
    np.testing.assert_equal(result.record_array.solution_count, np.ones(len(solutions), dtype=int))


def test_data_sort_by_none(annealing_result, solutions, values, solution_counts):
    d = list(annealing_result.data(sorted_by=None))
    for i in range(len(solutions)):
        assert (d[i][0] == solutions[i]).all()
        assert d[i][1] == values[i]
        assert d[i][2] == solution_counts[i]


def test_data_selected_fields(annealing_result, solutions, values, solution_counts):
    d = list(annealing_result.data(selected_fields=["value"]))
    for i in range(len(solutions)):
        assert d[i] == tuple([values[i]])


def test_data_reverse(annealing_result, solutions, values, solution_counts):
    d = list(annealing_result.data(reverse=True))
    num_solutions = len(solutions)
    for i in range(num_solutions):
        assert (d[i][0] == solutions[num_solutions - i - 1]).all()
        assert d[i][1] == values[num_solutions - i - 1]
        assert d[i][2] == solution_counts[num_solutions - i - 1]


def test_data_sort_by(annealing_result, solutions, values, solution_counts):
    d = list(annealing_result.data(sorted_by="solution_count"))
    min_index = np.argmin(solution_counts)
    assert (d[0][0] == solutions[min_index]).all()
    assert d[0][1] == values[min_index]
    assert d[0][2] == solution_counts[min_index]


def test_from_object_equal_to_from_string(result_str_1):
    assert AnnealingQuantumTaskResult.from_object(
        AnnealingTaskResult.parse_raw(result_str_1)
    ) == AnnealingQuantumTaskResult.from_string(result_str_1)


def test_equality(result_str_1, result_str_2):
    result_1 = AnnealingQuantumTaskResult.from_string(result_str_1)
    result_2 = AnnealingQuantumTaskResult.from_string(result_str_1)
    other_result = AnnealingQuantumTaskResult.from_string(result_str_2)
    non_result = "not a quantum task result"

    assert result_1 == result_2
    assert result_1 is not result_2
    assert result_1 != other_result
    assert result_1 != non_result
