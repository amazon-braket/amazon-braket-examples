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

import json
from dataclasses import dataclass
from typing import Any, Callable, Counter, Dict, List, Optional, TypeVar, Union

import numpy as np

from braket.circuits import Observable, ResultType, StandardObservable
from braket.circuits.observables import TensorProduct, observable_from_ir
from braket.ir.jaqcd import Expectation, Probability, Sample, Variance
from braket.task_result import (
    AdditionalMetadata,
    GateModelTaskResult,
    ResultTypeValue,
    TaskMetadata,
)

T = TypeVar("T")


@dataclass
class GateModelQuantumTaskResult:
    """
    Result of a gate model quantum task execution. This class is intended
    to be initialized by a QuantumTask class.

    Args:
        task_metadata (TaskMetadata): Task metadata.
        additional_metadata (AdditionalMetadata): Additional metadata about the task
        result_types (List[Dict[str, Any]]): List of dictionaries where each dictionary
            has two keys: 'Type' (the result type in IR JSON form) and
            'Value' (the result value for this result type).
            This can be an empty list if no result types are specified in the IR.
            This is calculated from `measurements` and
            the IR of the circuit program when `shots>0`.
        values (List[Any]): The values for result types requested in the circuit.
            This can be an empty list if no result types are specified in the IR.
            This is calculated from `measurements` and
            the IR of the circuit program when `shots>0`.
        measurements (numpy.ndarray, optional): 2d array - row is shot and column is qubit.
            Default is None. Only available when shots > 0. The qubits in `measurements`
            are the ones in `GateModelQuantumTaskResult.measured_qubits`.
        measured_qubits (List[int], optional): The indices of the measured qubits. Default
            is None. Only available when shots > 0. Indicates which qubits are in
            `measurements`.
        measurement_counts (Counter, optional): A `Counter` of measurements. Key is the measurements
            in a big endian binary string. Value is the number of times that measurement occurred.
            Default is None. Only available when shots > 0. Note that the keys in `Counter` are
            unordered.
        measurement_probabilities (Dict[str, float], optional):
            A dictionary of probabilistic results.
            Key is the measurements in a big endian binary string.
            Value is the probability the measurement occurred.
            Default is None. Only available when shots > 0.
        measurements_copied_from_device (bool, optional): flag whether `measurements`
            were copied from device. If false, `measurements` are calculated from device data.
            Default is None. Only available when shots > 0.
        measurement_counts_copied_from_device (bool, optional): flag whether `measurement_counts`
            were copied from device. If False, `measurement_counts` are calculated from device data.
            Default is None. Only available when shots > 0.
        measurement_probabilities_copied_from_device (bool, optional): flag whether
            `measurement_probabilities` were copied from device. If false,
            `measurement_probabilities` are calculated from device data. Default is None.
            Only available when shots > 0.
    """

    task_metadata: TaskMetadata
    additional_metadata: AdditionalMetadata
    result_types: List[ResultTypeValue] = None
    values: List[Any] = None
    measurements: np.ndarray = None
    measured_qubits: List[int] = None
    measurement_counts: Counter = None
    measurement_probabilities: Dict[str, float] = None
    measurements_copied_from_device: bool = None
    measurement_counts_copied_from_device: bool = None
    measurement_probabilities_copied_from_device: bool = None

    _result_types_indices: Dict[str, int] = None

    def __post_init__(self):
        if self.result_types is not None:
            self._result_types_indices = dict(
                (GateModelQuantumTaskResult._result_type_hash(rt.type), i)
                for i, rt in enumerate(self.result_types)
            )
        else:
            self._result_types_indices = {}

    def get_value_by_result_type(self, result_type: ResultType) -> Any:
        """
        Get value by result type. The result type must have already been
        requested in the circuit sent to the device for this task result.

        Args:
            result_type (ResultType): result type requested

        Returns:
            Any: value of the result corresponding to the result type

        Raises:
            ValueError: If result type is not found in result.
                Result types must be added to the circuit before the circuit is run on a device.
        """
        rt_ir = result_type.to_ir()
        try:
            rt_hash = GateModelQuantumTaskResult._result_type_hash(rt_ir)
            result_type_index = self._result_types_indices[rt_hash]
            return self.values[result_type_index]
        except KeyError:
            raise ValueError(
                "Result type not found in result. "
                + "Result types must be added to circuit before circuit is run on device."
            )

    def __eq__(self, other) -> bool:
        if isinstance(other, GateModelQuantumTaskResult):
            return self.task_metadata.id == other.task_metadata.id
        return NotImplemented

    @staticmethod
    def measurement_counts_from_measurements(measurements: np.ndarray) -> Counter:
        """
        Creates measurement counts from measurements

        Args:
            measurements (numpy.ndarray): 2d array - row is shot and column is qubit.

        Returns:
            Counter: A Counter of measurements. Key is the measurements in a big endian binary
                string. Value is the number of times that measurement occurred.
        """
        bitstrings = []
        for j in range(len(measurements)):
            bitstrings.append("".join([str(element) for element in measurements[j]]))
        return Counter(bitstrings)

    @staticmethod
    def measurement_probabilities_from_measurement_counts(
        measurement_counts: Counter,
    ) -> Dict[str, float]:
        """
        Creates measurement probabilities from measurement counts

        Args:
            measurement_counts (Counter): A Counter of measurements. Key is the measurements
                in a big endian binary string. Value is the number of times that measurement
                occurred.

        Returns:
            Dict[str, float]: A dictionary of probabilistic results. Key is the measurements
                in a big endian binary string. Value is the probability the measurement occurred.
        """
        measurement_probabilities = {}
        shots = sum(measurement_counts.values())

        for key, count in measurement_counts.items():
            measurement_probabilities[key] = count / shots
        return measurement_probabilities

    @staticmethod
    def measurements_from_measurement_probabilities(
        measurement_probabilities: Dict[str, float], shots: int
    ) -> np.ndarray:
        """
        Creates measurements from measurement probabilities

        Args:
            measurement_probabilities (Dict[str, float]): A dictionary of probabilistic results.
                Key is the measurements in a big endian binary string.
                Value is the probability the measurement occurred.
            shots (int): number of iterations on device

        Returns:
            Dict[str, float]: A dictionary of probabilistic results.
                Key is the measurements in a big endian binary string.
                Value is the probability the measurement occurred.
        """
        measurements_list = []
        for bitstring in measurement_probabilities:
            measurement = list(bitstring)
            individual_measurement_list = [measurement] * int(
                round(measurement_probabilities[bitstring] * shots)
            )
            measurements_list.extend(individual_measurement_list)
        return np.asarray(measurements_list, dtype=int)

    @staticmethod
    def from_object(result: GateModelTaskResult):
        """
        Create GateModelQuantumTaskResult from GateModelTaskResult object.

        Args:
            result (GateModelTaskResult): GateModelTaskResult object

        Returns:
            GateModelQuantumTaskResult: A GateModelQuantumTaskResult based on the given dict

        Raises:
            ValueError: If neither "Measurements" nor "MeasurementProbabilities" is a key
                in the result dict
        """
        return GateModelQuantumTaskResult._from_object_internal(result)

    @staticmethod
    def from_string(result: str) -> GateModelQuantumTaskResult:
        """
        Create GateModelQuantumTaskResult from string.

        Args:
            result (str): JSON object string, with GateModelQuantumTaskResult attributes as keys.

        Returns:
            GateModelQuantumTaskResult: A GateModelQuantumTaskResult based on the given string

        Raises:
            ValueError: If neither "Measurements" nor "MeasurementProbabilities" is a key
                in the result dict
        """
        obj = GateModelTaskResult.parse_raw(result)
        GateModelQuantumTaskResult.cast_result_types(obj)
        return GateModelQuantumTaskResult._from_object_internal(obj)

    @classmethod
    def _from_object_internal(cls, result: GateModelTaskResult):
        if result.taskMetadata.shots > 0:
            return GateModelQuantumTaskResult._from_object_internal_computational_basis_sampling(
                result
            )
        else:
            return GateModelQuantumTaskResult._from_dict_internal_simulator_only(result)

    @classmethod
    def _from_object_internal_computational_basis_sampling(cls, result: GateModelTaskResult):
        task_metadata = result.taskMetadata
        additional_metadata = result.additionalMetadata
        if result.measurements:
            measurements = np.asarray(result.measurements, dtype=int)
            m_counts = GateModelQuantumTaskResult.measurement_counts_from_measurements(measurements)
            m_probs = GateModelQuantumTaskResult.measurement_probabilities_from_measurement_counts(
                m_counts
            )
            measurements_copied_from_device = True
            m_counts_copied_from_device = False
            m_probabilities_copied_from_device = False
        elif result.measurementProbabilities:
            shots = task_metadata.shots
            m_probs = result.measurementProbabilities
            measurements = GateModelQuantumTaskResult.measurements_from_measurement_probabilities(
                m_probs, shots
            )
            m_counts = GateModelQuantumTaskResult.measurement_counts_from_measurements(measurements)
            measurements_copied_from_device = False
            m_counts_copied_from_device = False
            m_probabilities_copied_from_device = True
        else:
            raise ValueError(
                'One of "measurements" or "measurementProbabilities" must be populated in',
                " the result obj",
            )
        measured_qubits = result.measuredQubits
        if len(measured_qubits) != measurements.shape[1]:
            raise ValueError(
                f"Measured qubits {measured_qubits} is not equivalent to number of qubits "
                + f"{measurements.shape[1]} in measurements"
            )
        result_types = (
            result.resultTypes
            if result.resultTypes
            else GateModelQuantumTaskResult._calculate_result_types(
                additional_metadata.action.json(), measurements, measured_qubits
            )
        )
        values = [rt.value for rt in result_types]
        return cls(
            task_metadata=task_metadata,
            additional_metadata=additional_metadata,
            result_types=result_types,
            values=values,
            measurements=measurements,
            measured_qubits=measured_qubits,
            measurement_counts=m_counts,
            measurement_probabilities=m_probs,
            measurements_copied_from_device=measurements_copied_from_device,
            measurement_counts_copied_from_device=m_counts_copied_from_device,
            measurement_probabilities_copied_from_device=m_probabilities_copied_from_device,
        )

    @classmethod
    def _from_dict_internal_simulator_only(cls, result: GateModelTaskResult):
        task_metadata = result.taskMetadata
        additional_metadata = result.additionalMetadata
        result_types = result.resultTypes
        values = [rt.value for rt in result_types]
        return cls(
            task_metadata=task_metadata,
            additional_metadata=additional_metadata,
            result_types=result_types,
            values=values,
        )

    @staticmethod
    def cast_result_types(gate_model_task_result: GateModelTaskResult) -> None:
        """
        Casts the result types to the types expected by the SDK.

        Args:
            gate_model_task_result (GateModelTaskResult): GateModelTaskResult representing the
                results.
        """
        if gate_model_task_result.resultTypes:
            for result_type in gate_model_task_result.resultTypes:
                type = result_type.type.type
                if type == "probability":
                    result_type.value = np.array(result_type.value)
                elif type == "statevector":
                    result_type.value = np.array([complex(*value) for value in result_type.value])
                elif type == "amplitude":
                    for state in result_type.value:
                        result_type.value[state] = complex(*result_type.value[state])

    @staticmethod
    def _calculate_result_types(
        ir_string: str, measurements: np.ndarray, measured_qubits: List[int]
    ) -> List[ResultTypeValue]:
        ir = json.loads(ir_string)
        result_types = []
        if not ir.get("results"):
            return result_types
        for result_type in ir["results"]:
            ir_observable = result_type.get("observable")
            observable = observable_from_ir(ir_observable) if ir_observable else None
            targets = result_type.get("targets")
            rt_type = result_type["type"]
            if rt_type == "probability":
                value = GateModelQuantumTaskResult._probability_from_measurements(
                    measurements, measured_qubits, targets
                )
                casted_result_type = Probability(targets=targets)
            elif rt_type == "sample":
                value = GateModelQuantumTaskResult._calculate_for_targets(
                    GateModelQuantumTaskResult._samples_from_measurements,
                    measurements,
                    measured_qubits,
                    observable,
                    targets,
                )
                casted_result_type = Sample(targets=targets, observable=ir_observable)
            elif rt_type == "variance":
                value = GateModelQuantumTaskResult._calculate_for_targets(
                    GateModelQuantumTaskResult._variance_from_measurements,
                    measurements,
                    measured_qubits,
                    observable,
                    targets,
                )
                casted_result_type = Variance(targets=targets, observable=ir_observable)
            elif rt_type == "expectation":
                value = GateModelQuantumTaskResult._calculate_for_targets(
                    GateModelQuantumTaskResult._expectation_from_measurements,
                    measurements,
                    measured_qubits,
                    observable,
                    targets,
                )
                casted_result_type = Expectation(targets=targets, observable=ir_observable)
            else:
                raise ValueError(f"Unknown result type {rt_type}")
            result_types.append(ResultTypeValue.construct(type=casted_result_type, value=value))
        return result_types

    @staticmethod
    def _selected_measurements(
        measurements: np.ndarray, measured_qubits: List[int], targets: Optional[List[int]]
    ) -> np.ndarray:
        if targets is not None and targets != measured_qubits:
            # Only some qubits targeted
            columns = [measured_qubits.index(t) for t in targets]
            measurements = measurements[:, columns]
        return measurements

    @staticmethod
    def _calculate_for_targets(
        calculate_function: Callable[[np.ndarray, List[int], Observable, List[int]], T],
        measurements: np.ndarray,
        measured_qubits: List[int],
        observable: Observable,
        targets: List[int],
    ) -> Union[T, List[T]]:
        if targets:
            return calculate_function(measurements, measured_qubits, observable, targets)
        else:
            return [
                calculate_function(measurements, measured_qubits, observable, [i])
                for i in measured_qubits
            ]

    @staticmethod
    def _measurements_base_10(measurements: np.ndarray) -> np.ndarray:
        # convert samples from a list of 0, 1 integers, to base 10 representation
        two_powers = 2 ** np.arange(measurements.shape[-1])[::-1]  # 2^(n-1), ..., 2, 1
        return measurements @ two_powers

    @staticmethod
    def _probability_from_measurements(
        measurements: np.ndarray, measured_qubits: List[int], targets: Optional[List[int]]
    ) -> np.ndarray:
        measurements = GateModelQuantumTaskResult._selected_measurements(
            measurements, measured_qubits, targets
        )
        shots, num_measured_qubits = measurements.shape
        # convert measurements from a list of 0, 1 integers, to base 10 representation
        indices = GateModelQuantumTaskResult._measurements_base_10(measurements)

        # count the basis state occurrences, and construct the probability vector
        basis_states, counts = np.unique(indices, return_counts=True)
        probabilities = np.zeros([2**num_measured_qubits], dtype=np.float64)
        probabilities[basis_states] = counts / shots
        return probabilities

    @staticmethod
    def _variance_from_measurements(
        measurements: np.ndarray,
        measured_qubits: List[int],
        observable: Observable,
        targets: List[int],
    ) -> float:
        samples = GateModelQuantumTaskResult._samples_from_measurements(
            measurements, measured_qubits, observable, targets
        )
        return np.var(samples)

    @staticmethod
    def _expectation_from_measurements(
        measurements: np.ndarray,
        measured_qubits: List[int],
        observable: Observable,
        targets: List[int],
    ) -> float:
        samples = GateModelQuantumTaskResult._samples_from_measurements(
            measurements, measured_qubits, observable, targets
        )
        return np.mean(samples)

    @staticmethod
    def _samples_from_measurements(
        measurements: np.ndarray,
        measured_qubits: List[int],
        observable: Observable,
        targets: List[int],
    ) -> np.ndarray:
        measurements = GateModelQuantumTaskResult._selected_measurements(
            measurements, measured_qubits, targets
        )
        if isinstance(observable, StandardObservable):
            # Process samples for observables with eigenvalues {1, -1}
            return 1 - 2 * measurements.flatten()
        # Replace the basis state in the computational basis with the correct eigenvalue.
        # Extract only the columns of the basis samples required based on ``targets``.
        indices = GateModelQuantumTaskResult._measurements_base_10(measurements)
        if isinstance(observable, TensorProduct):
            return np.array([observable.eigenvalue(index).real for index in indices])
        return observable.eigenvalues[indices].real

    @staticmethod
    def _result_type_hash(rt_type):
        return repr(dict(sorted(dict(rt_type).items(), key=lambda x: x[0])))
