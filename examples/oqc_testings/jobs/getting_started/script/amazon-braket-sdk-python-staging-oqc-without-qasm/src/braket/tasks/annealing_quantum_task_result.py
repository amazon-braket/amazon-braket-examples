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

from __future__ import annotations

from dataclasses import dataclass

import numpy

from braket.annealing import ProblemType
from braket.task_result import AdditionalMetadata, AnnealingTaskResult, TaskMetadata


@dataclass
class AnnealingQuantumTaskResult:
    """
    Result of an annealing problem quantum task execution. This class is intended
    to be initialized by a QuantumTask class.

    Args:
        record_array (numpy.recarray): numpy array with keys 'solution' (numpy.ndarray)
            where row is solution, column is value of the variable, 'solution_count' (numpy.ndarray)
            the number of times the solutions occurred, and 'value' (numpy.ndarray) the
            output or energy of the solutions.
        variable_count (int): the number of variables
        problem_type (ProblemType): the type of annealing problem
        task_metadata (TaskMetadata): Task metadata.
        additional_metadata (AdditionalMetadata): Additional metadata about the task
    """

    record_array: numpy.recarray
    variable_count: int
    problem_type: ProblemType
    task_metadata: TaskMetadata
    additional_metadata: AdditionalMetadata

    def data(self, selected_fields=None, sorted_by="value", reverse=False):
        """
        Iterate over the data in record_array

        Args:
            selected_fields (List[str], optional, default=None): selected fields to return.
                Options are 'solution', 'value', and 'solution_count'
            sorted_by (str, optional, default='value'): Sorts the data by this field.
                Options are 'solution', 'value', and 'solution_count'
            reverse (bool, optional, default=False): If True, returns the data in reverse order.

        Yields:
            tuple: data in record_array
        """
        if selected_fields is None:
            selected_fields = ["solution", "value", "solution_count"]

        if sorted_by is None:
            order = numpy.arange(len(self.record_array))
        else:
            order = numpy.argsort(self.record_array[sorted_by])

        if reverse:
            order = numpy.flip(order)

        for i in order:
            yield tuple(self.record_array[field][i] for field in selected_fields)

    def __eq__(self, other) -> bool:
        if isinstance(other, AnnealingQuantumTaskResult):
            # __eq__ on numpy arrays results in an array of booleans and therefore can't use
            # the default dataclass __eq__ implementation. Override equals to check if all
            # elements in the array are equal.
            self_fields = (
                self.variable_count,
                self.problem_type,
                self.task_metadata,
                self.additional_metadata,
            )
            other_fields = (
                other.variable_count,
                other.problem_type,
                other.task_metadata,
                other.additional_metadata,
            )
            return (self.record_array == other.record_array).all() and self_fields == other_fields
        return NotImplemented

    @staticmethod
    def from_object(result: AnnealingTaskResult) -> AnnealingQuantumTaskResult:
        """
        Create AnnealingQuantumTaskResult from AnnealingTaskResult object

        Args:
            result (AnnealingTaskResult): AnnealingTaskResult object

        Returns:
            AnnealingQuantumTaskResult: An AnnealingQuantumTaskResult based on the
            given result object
        """
        return AnnealingQuantumTaskResult._from_object(result)

    @staticmethod
    def from_string(result: str) -> AnnealingQuantumTaskResult:
        """
        Create AnnealingQuantumTaskResult from string

        Args:
            result (str): JSON object string

        Returns:
            AnnealingQuantumTaskResult: An AnnealingQuantumTaskResult based on the given string
        """
        return AnnealingQuantumTaskResult._from_object(AnnealingTaskResult.parse_raw(result))

    @classmethod
    def _from_object(cls, result: AnnealingTaskResult):
        solutions = numpy.asarray(result.solutions, dtype=int)
        values = numpy.asarray(result.values, dtype=float)
        if not result.solutionCounts:
            solution_counts = numpy.ones(len(solutions), dtype=int)
        else:
            solution_counts = numpy.asarray(result.solutionCounts, dtype=int)
        record_array = AnnealingQuantumTaskResult._create_record_array(
            solutions, solution_counts, values
        )
        variable_count = result.variableCount
        problem_type = ProblemType[result.additionalMetadata.action.type.value]
        task_metadata = result.taskMetadata
        additional_metadata = result.additionalMetadata
        return cls(
            record_array=record_array,
            variable_count=variable_count,
            problem_type=problem_type,
            task_metadata=task_metadata,
            additional_metadata=additional_metadata,
        )

    @staticmethod
    def _create_record_array(
        solutions: numpy.ndarray, solution_counts: numpy.ndarray, values: numpy.ndarray
    ) -> numpy.recarray:
        """
        Create a solutions record for AnnealingQuantumTaskResult

        Args:
            solutions (numpy.ndarray): row is solution, column is value of the variable
            solution_counts (numpy.ndarray): list of number of times the solutions occurred
            values (numpy.ndarray): list of the output or energy of the solutions
        """
        num_solutions, variable_count = solutions.shape
        datatypes = [
            ("solution", solutions.dtype, (variable_count,)),
            ("value", values.dtype),
            ("solution_count", solution_counts.dtype),
        ]

        record = numpy.rec.array(numpy.zeros(num_solutions, dtype=datatypes))
        record["solution"] = solutions
        record["value"] = values
        record["solution_count"] = solution_counts
        return record
