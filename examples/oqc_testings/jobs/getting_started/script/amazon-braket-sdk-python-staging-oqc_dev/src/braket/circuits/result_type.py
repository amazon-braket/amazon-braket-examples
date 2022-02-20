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

from typing import Any, Dict, List

from braket.circuits.observable import Observable
from braket.circuits.qubit import QubitInput
from braket.circuits.qubit_set import QubitSet, QubitSetInput


class ResultType:
    """
    Class `ResultType` represents a requested result type for the circuit.
    This class is considered the result type definition containing
    the metadata that defines what a requested result type is and what it does.
    """

    def __init__(self, ascii_symbols: List[str]):
        """
        Args:
            ascii_symbols (List[str]): ASCII string symbols for the result type. This is used when
                printing a diagram of circuits.

        Raises:
            ValueError: `ascii_symbols` is `None`
        """

        if ascii_symbols is None:
            raise ValueError("ascii_symbols must not be None")

        self._ascii_symbols = ascii_symbols

    @property
    def ascii_symbols(self) -> List[str]:
        """List[str]: Returns the ascii symbols for the requested result type."""
        return self._ascii_symbols

    @property
    def name(self) -> str:
        """
        Returns the name of the result type

        Returns:
            The name of the result type as a string
        """
        return self.__class__.__name__

    def to_ir(self, *args, **kwargs) -> Any:
        """Returns IR object of the result type

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            IR object of the result type
        """
        raise NotImplementedError("to_ir has not been implemented yet.")

    def copy(
        self, target_mapping: Dict[QubitInput, QubitInput] = None, target: QubitSetInput = None
    ):
        """
        Return a shallow copy of the result type.

        Note:
            If `target_mapping` is specified, then `self.target` is mapped to the specified
            qubits. This is useful apply an instruction to a circuit and change the target qubits.

        Args:
            target_mapping (dictionary[int or Qubit, int or Qubit], optional): A dictionary of
                qubit mappings to apply to the target. Key is the qubit in this `target` and the
                value is what the key is changed to. Default = `None`.
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits for the new
                instruction.

        Returns:
            ResultType: A shallow copy of the result type.

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.

        Examples:
            >>> result_type = ResultType.Probabilities(targets=[0])
            >>> new_result_type = result_type.copy()
            >>> new_result_type.targets
            QubitSet(Qubit(0))
            >>> new_result = result_type.copy(target_mapping={0: 5})
            >>> new_result_type.target
            QubitSet(Qubit(5))
            >>> new_result = result_type.copy(target=[5])
            >>> new_result_type.target
            QubitSet(Qubit(5))
        """
        copy = self.__copy__()
        if target_mapping and target is not None:
            raise TypeError("Only 'target_mapping' or 'target' can be supplied, but not both.")
        elif target is not None:
            if hasattr(copy, "target"):
                copy.target = target
        elif hasattr(copy, "target"):
            copy.target = self._target.map(target_mapping or {})
        return copy

    @classmethod
    def register_result_type(cls, result_type: "ResultType"):
        """Register a result type implementation by adding it into the `ResultType` class.

        Args:
            result_type (ResultType): `ResultType` instance to register.
        """
        setattr(cls, result_type.__name__, result_type)

    def __repr__(self) -> str:
        return f"{self.name}()"

    def __hash__(self) -> int:
        return hash(repr(self))


class ObservableResultType(ResultType):
    """
    Result types with observables and targets.
    If no targets are specified, the observable must only operate on 1 qubit and it
    will be applied to all qubits in parallel. Otherwise, the number of specified targets
    must be equivalent to the number of qubits the observable can be applied to.

    See :mod:`braket.circuits.observables` module for all of the supported observables.
    """

    def __init__(
        self, ascii_symbols: List[str], observable: Observable, target: QubitSetInput = None
    ):
        """
        Args:
            observable (Observable): the observable for the result type
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits that the
                result type is requested for. Default is `None`, which means the observable must
                only operate on 1 qubit and it will be applied to all qubits in parallel

        Raises:
            ValueError: if target=None and the observable's qubit count is not 1.
                Or, if `target!=None` and the observable's qubit count and the number of target
                qubits are not equal. Or, if `target!=None` and the observable's qubit count and
                the number of `ascii_symbols` are not equal.
        """
        super().__init__(ascii_symbols)
        self._observable = observable
        self._target = QubitSet(target)
        if not self._target:
            if self._observable.qubit_count != 1:
                raise ValueError(
                    f"Observable {self._observable} must only operate on 1 qubit for target=None"
                )
        else:
            if self._observable.qubit_count != len(self._target):
                raise ValueError(
                    f"Observable's qubit count {self._observable.qubit_count} and "
                    f"the size of the target qubit set {self._target} must be equal"
                )
            if self._observable.qubit_count != len(self.ascii_symbols):
                raise ValueError(
                    "Observable's qubit count and the number of ASCII symbols must be equal"
                )

    @property
    def observable(self) -> Observable:
        return self._observable

    @property
    def target(self) -> QubitSet:
        return self._target

    @target.setter
    def target(self, target: QubitSetInput) -> None:
        self._target = QubitSet(target)

    def __eq__(self, other) -> bool:
        if isinstance(other, ObservableResultType):
            return (
                self.name == other.name
                and self.target == other.target
                and self.observable == other.observable
            )
        return NotImplemented

    def __repr__(self) -> str:
        return f"{self.name}(observable={self.observable}, target={self.target})"

    def __copy__(self) -> ObservableResultType:
        return type(self)(observable=self.observable, target=self.target)

    def __hash__(self) -> int:
        return super().__hash__()
