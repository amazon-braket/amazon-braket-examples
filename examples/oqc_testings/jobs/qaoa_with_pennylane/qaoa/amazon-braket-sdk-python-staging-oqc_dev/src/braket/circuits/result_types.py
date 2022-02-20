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

import re
from typing import List

import braket.ir.jaqcd as ir
from braket.circuits import circuit
from braket.circuits.observable import Observable
from braket.circuits.qubit_set import QubitSet, QubitSetInput
from braket.circuits.result_type import ObservableResultType, ResultType

"""
To add a new result type:
    1. Implement the class and extend `ResultType`
    2. Add a method with the `@circuit.subroutine(register=True)` decorator. Method name
       is added into the `Circuit` class. This method is the default way
       clients add this result type to a circuit.
    3. Register the class with the `ResultType` class via `ResultType.register_result_type()`.
"""


class StateVector(ResultType):
    """
    The full state vector as a requested result type.
    This is available on simulators only when `shots=0`.
    """

    def __init__(self):
        super().__init__(ascii_symbols=["StateVector"])

    def to_ir(self) -> ir.StateVector:
        return ir.StateVector.construct()

    @staticmethod
    @circuit.subroutine(register=True)
    def state_vector() -> ResultType:
        """Registers this function into the circuit class.

        Returns:
            ResultType: state vector as a requested result type

        Examples:
            >>> circ = Circuit().state_vector()
        """
        return ResultType.StateVector()

    def __eq__(self, other) -> bool:
        if isinstance(other, StateVector):
            return True
        return False

    def __copy__(self) -> StateVector:
        return type(self)()

    # must redefine __hash__ since __eq__ is overwritten
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    def __hash__(self) -> int:
        return super().__hash__()


ResultType.register_result_type(StateVector)


class DensityMatrix(ResultType):
    """
    The full density matrix as a requested result type.
    This is available on simulators only when `shots=0`.
    """

    def __init__(self, target: QubitSetInput = None):
        """
        Args:
            target (int, Qubit, or iterable of int / Qubit, optional): The target qubits
                of the reduced density matrix. Default is `None`, and the
                full density matrix is returned.

        Examples:
            >>> ResultType.DensityMatrix(target=[0, 1])
        """
        self._target = QubitSet(target)
        ascii_symbols = ["DensityMatrix"] * len(self._target) if self._target else ["DensityMatrix"]
        super().__init__(ascii_symbols=ascii_symbols)

    @property
    def target(self) -> QubitSet:
        return self._target

    @target.setter
    def target(self, target: QubitSetInput) -> None:
        self._target = QubitSet(target)

    def to_ir(self) -> ir.DensityMatrix:
        if self.target:
            # convert qubits to int as required by the ir type
            return ir.DensityMatrix.construct(targets=[int(qubit) for qubit in self.target])
        else:
            return ir.DensityMatrix.construct()

    @staticmethod
    @circuit.subroutine(register=True)
    def density_matrix(target: QubitSetInput = None) -> ResultType:
        """Registers this function into the circuit class.
        Args:
            target (int, Qubit, or iterable of int / Qubit, optional): The target qubits
                of the reduced density matrix. Default is `None`, and the
                full density matrix is returned.

        Returns:
            ResultType: density matrix as a requested result type

        Examples:
            >>> circ = Circuit().density_matrix(target=[0, 1])
        """
        return ResultType.DensityMatrix(target=target)

    def __eq__(self, other) -> bool:
        if isinstance(other, DensityMatrix):
            return self.target == other.target
        return False

    def __repr__(self) -> str:
        return f"DensityMatrix(target={self.target})"

    def __copy__(self) -> DensityMatrix:
        return type(self)(target=self.target)

    # must redefine __hash__ since __eq__ is overwritten
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    def __hash__(self) -> int:
        return super().__hash__()


ResultType.register_result_type(DensityMatrix)


class Amplitude(ResultType):
    """
    The amplitude of the specified quantum states as a requested result type.
    This is available on simulators only when `shots=0`.
    """

    def __init__(self, state: List[str]):
        """
        Args:
            state (List[str]): list of quantum states as strings with "0" and "1"

        Raises:
            ValueError: If state is `None` or an empty list, or
                state is not a list of strings of '0' and '1'

        Examples:
            >>> ResultType.Amplitude(state=['01', '10'])
        """
        if (
            not state
            or not isinstance(state, List)
            or not all(
                isinstance(amplitude, str) and re.fullmatch("^[01]+$", amplitude)
                for amplitude in state
            )
        ):
            raise ValueError(
                "A non-empty list of states must be specified in binary encoding e.g. ['01', '10']"
            )
        super().__init__(ascii_symbols=[f"Amplitude({','.join(state)})"])
        self._state = state

    @property
    def state(self) -> List[str]:
        return self._state

    def to_ir(self) -> ir.Amplitude:
        return ir.Amplitude.construct(states=self.state)

    @staticmethod
    @circuit.subroutine(register=True)
    def amplitude(state: List[str]) -> ResultType:
        """Registers this function into the circuit class.

        Args:
            state (List[str]): list of quantum states as strings with "0" and "1"

        Returns:
            ResultType: state vector as a requested result type

        Examples:
            >>> circ = Circuit().amplitude(state=["01", "10"])
        """
        return ResultType.Amplitude(state=state)

    def __eq__(self, other):
        if isinstance(other, Amplitude):
            return self.state == other.state
        return False

    def __repr__(self):
        return f"Amplitude(state={self.state})"

    def __copy__(self):
        return type(self)(state=self.state)

    def __hash__(self) -> int:
        return super().__hash__()


ResultType.register_result_type(Amplitude)


class Probability(ResultType):
    """Probability in the computational basis as the requested result type.

    It can be the probability of all states if no targets are specified, or the marginal
    probability of a restricted set of states if only a subset of all qubits are specified as
    targets.

    For `shots>0`, this is calculated by measurements. For `shots=0`, this is supported
    only on simulators and represents the exact result.
    """

    def __init__(self, target: QubitSetInput = None):
        """
        Args:
            target (int, Qubit, or iterable of int / Qubit, optional): The target qubits that the
                result type is requested for. Default is `None`, which means all qubits for the
                circuit.

        Examples:
            >>> ResultType.Probability(target=[0, 1])
        """
        self._target = QubitSet(target)
        ascii_symbols = ["Probability"] * len(self._target) if self._target else ["Probability"]
        super().__init__(ascii_symbols=ascii_symbols)

    @property
    def target(self) -> QubitSet:
        return self._target

    @target.setter
    def target(self, target: QubitSetInput) -> None:
        self._target = QubitSet(target)

    def to_ir(self) -> ir.Probability:
        if self.target:
            # convert qubits to int as required by the ir type
            return ir.Probability.construct(targets=[int(qubit) for qubit in self.target])
        else:
            return ir.Probability.construct()

    @staticmethod
    @circuit.subroutine(register=True)
    def probability(target: QubitSetInput = None) -> ResultType:
        """Registers this function into the circuit class.

        Args:
            target (int, Qubit, or iterable of int / Qubit, optional): The target qubits that the
                result type is requested for. Default is `None`, which means all qubits for the
                circuit.

        Returns:
            ResultType: probability as a requested result type

        Examples:
            >>> circ = Circuit().probability(target=[0, 1])
        """
        return ResultType.Probability(target=target)

    def __eq__(self, other) -> bool:
        if isinstance(other, Probability):
            return self.target == other.target
        return False

    def __repr__(self) -> str:
        return f"Probability(target={self.target})"

    def __copy__(self) -> Probability:
        return type(self)(target=self.target)

    def __hash__(self) -> int:
        return super().__hash__()


ResultType.register_result_type(Probability)


class Expectation(ObservableResultType):
    """Expectation of the specified target qubit set and observable as the requested result type.

    If no targets are specified, the observable must operate only on 1 qubit and it
    is applied to all qubits in parallel. Otherwise, the number of specified targets
    must be equivalent to the number of qubits the observable can be applied to.

    For `shots>0`, this is calculated by measurements. For `shots=0`, this is supported
    only by simulators and represents the exact result.

    See :mod:`braket.circuits.observables` module for all of the supported observables.
    """

    def __init__(self, observable: Observable, target: QubitSetInput = None):
        """
        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                operate only on 1 qubit and it is applied to all qubits in parallel.

        Raises:
            ValueError: If the observable's qubit count does not equal the number of target
                qubits, or if `target=None` and the observable's qubit count is not 1.

        Examples:
            >>> ResultType.Expectation(observable=Observable.Z(), target=0)

            >>> tensor_product = Observable.Y() @ Observable.Z()
            >>> ResultType.Expectation(observable=tensor_product, target=[0, 1])
        """
        super().__init__(
            ascii_symbols=[f"Expectation({obs_ascii})" for obs_ascii in observable.ascii_symbols],
            observable=observable,
            target=target,
        )

    def to_ir(self) -> ir.Expectation:
        if self.target:
            return ir.Expectation.construct(
                observable=self.observable.to_ir(), targets=[int(qubit) for qubit in self.target]
            )
        else:
            return ir.Expectation.construct(observable=self.observable.to_ir())

    @staticmethod
    @circuit.subroutine(register=True)
    def expectation(observable: Observable, target: QubitSetInput = None) -> ResultType:
        """Registers this function into the circuit class.

        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                operate only on 1 qubit and it is applied to all qubits in parallel.

        Returns:
            ResultType: expectation as a requested result type

        Examples:
            >>> circ = Circuit().expectation(observable=Observable.Z(), target=0)
        """
        return ResultType.Expectation(observable=observable, target=target)


ResultType.register_result_type(Expectation)


class Sample(ObservableResultType):
    """Sample of specified target qubit set and observable as the requested result type.

    If no targets are specified, the observable must operate only on 1 qubit and it
    is applied to all qubits in parallel. Otherwise, the number of specified targets
    must equal the number of qubits the observable can be applied to.

    This is only available for `shots>0`.

    See :mod:`braket.circuits.observables` module for all of the supported observables.
    """

    def __init__(self, observable: Observable, target: QubitSetInput = None):
        """
        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                operate only on 1 qubit and it is applied to all qubits in parallel.

        Raises:
            ValueError: If the observable's qubit count is not equal to the number of target
                qubits, or if `target=None` and the observable's qubit count is not 1.

        Examples:
            >>> ResultType.Sample(observable=Observable.Z(), target=0)

            >>> tensor_product = Observable.Y() @ Observable.Z()
            >>> ResultType.Sample(observable=tensor_product, target=[0, 1])
        """
        super().__init__(
            ascii_symbols=[f"Sample({obs_ascii})" for obs_ascii in observable.ascii_symbols],
            observable=observable,
            target=target,
        )

    def to_ir(self) -> ir.Sample:
        if self.target:
            return ir.Sample.construct(
                observable=self.observable.to_ir(), targets=[int(qubit) for qubit in self.target]
            )
        else:
            return ir.Sample.construct(observable=self.observable.to_ir())

    @staticmethod
    @circuit.subroutine(register=True)
    def sample(observable: Observable, target: QubitSetInput = None) -> ResultType:
        """Registers this function into the circuit class.

        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                operate only on 1 qubit and it is applied to all qubits in parallel.

        Returns:
            ResultType: sample as a requested result type

        Examples:
            >>> circ = Circuit().sample(observable=Observable.Z(), target=0)
        """
        return ResultType.Sample(observable=observable, target=target)


ResultType.register_result_type(Sample)


class Variance(ObservableResultType):
    """Variance of specified target qubit set and observable as the requested result type.

    If no targets are specified, the observable must operate only on 1 qubit and it
    is applied to all qubits in parallel. Otherwise, the number of targets specified
    must equal the number of qubits that the observable can be applied to.

    For `shots>0`, this is calculated by measurements. For `shots=0`, this is supported
    only by simulators and represents the exact result.

    See :mod:`braket.circuits.observables` module for all of the supported observables.
    """

    def __init__(self, observable: Observable, target: QubitSetInput = None):
        """
        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                operate only on 1 qubit and it is applied to all qubits in parallel.

        Raises:
            ValueError: If the observable's qubit count does not equal the number of target
                qubits, or if `target=None` and the observable's qubit count is not 1.

        Examples:
            >>> ResultType.Variance(observable=Observable.Z(), target=0)

            >>> tensor_product = Observable.Y() @ Observable.Z()
            >>> ResultType.Variance(observable=tensor_product, target=[0, 1])
        """
        super().__init__(
            ascii_symbols=[f"Variance({obs_ascii})" for obs_ascii in observable.ascii_symbols],
            observable=observable,
            target=target,
        )

    def to_ir(self) -> ir.Variance:
        if self.target:
            return ir.Variance.construct(
                observable=self.observable.to_ir(), targets=[int(qubit) for qubit in self.target]
            )
        else:
            return ir.Variance.construct(observable=self.observable.to_ir())

    @staticmethod
    @circuit.subroutine(register=True)
    def variance(observable: Observable, target: QubitSetInput = None) -> ResultType:
        """Registers this function into the circuit class.

        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                only operate on 1 qubit and it will be applied to all qubits in parallel

        Returns:
            ResultType: variance as a requested result type

        Examples:
            >>> circ = Circuit().variance(observable=Observable.Z(), target=0)
        """
        return ResultType.Variance(observable=observable, target=target)


ResultType.register_result_type(Variance)
