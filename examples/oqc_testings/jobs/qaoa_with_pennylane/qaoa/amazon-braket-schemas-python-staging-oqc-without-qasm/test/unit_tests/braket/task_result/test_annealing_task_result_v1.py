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

import pytest
from pydantic import ValidationError

from braket.task_result.annealing_task_result_v1 import AnnealingTaskResult


@pytest.fixture
def values():
    return [0.3, 1.0]


@pytest.fixture
def solutions():
    return [[1, 0], [1, 0]]


@pytest.fixture
def solution_counts():
    return [1, 2]


@pytest.fixture
def variable_count():
    return 5


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    AnnealingTaskResult()


def test_correct_result(
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    result = AnnealingTaskResult(
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )
    assert result.values == values
    assert result.solutions == solutions
    assert result.solutionCounts == solution_counts
    assert result.variableCount == variable_count
    assert result.taskMetadata == task_metadata
    assert result.additionalMetadata == additional_metadata_annealing
    assert AnnealingTaskResult.parse_raw(result.json()) == result
    assert result == AnnealingTaskResult.parse_raw_schema(result.json())


@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_header(
    braket_schema_header,
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    AnnealingTaskResult(
        braketSchemaHeader=braket_schema_header,
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )


@pytest.mark.parametrize("solution_counts", [([-1], 2)])
@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_solution_counts(
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    AnnealingTaskResult(
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )


@pytest.mark.parametrize("solutions", [(1), ([[]]), ([[-2]]), ([[500, 299]])])
@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_solutions(
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    AnnealingTaskResult(
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )


@pytest.mark.parametrize("values", [(1), ([[]])])
@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_values(
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    AnnealingTaskResult(
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )


@pytest.mark.parametrize("variable_count", [(-2), ([[]])])
@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_variable_count(
    task_metadata,
    additional_metadata_annealing,
    values,
    solutions,
    solution_counts,
    variable_count,
):
    AnnealingTaskResult(
        values=values,
        solutions=solutions,
        solutionCounts=solution_counts,
        variableCount=variable_count,
        taskMetadata=task_metadata,
        additionalMetadata=additional_metadata_annealing,
    )
