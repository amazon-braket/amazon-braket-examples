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

from typing import Any, Optional, Sequence, Tuple

import numpy as np

from braket.circuits.operator import Operator


class QuantumOperator(Operator):
    """A quantum operator is the definition of a quantum operation for a quantum device."""

    def __init__(self, qubit_count: Optional[int], ascii_symbols: Sequence[str]):
        """
        Args:
            qubit_count (int, optional): Number of qubits this quantum operator acts on.
                If all instances of the operator act on the same number of qubits, this argument
                should be ``None``, and ``fixed_qubit_count`` should be implemented to return
                the qubit count; if ``fixed_qubit_count`` is implemented and an int is passed in,
                it must equal ``fixed_qubit_count``, or instantiation will raise a ValueError.
                An int must be passed in if instances can have a varying number of qubits,
                in which case ``fixed_qubit_count`` should not be implemented,
            ascii_symbols (Sequence[str]): ASCII string symbols for the quantum operator.
                These are used when printing a diagram of circuits.
                Length must be the same as `qubit_count`, and index ordering is expected
                to correlate with target ordering on the instruction.
                For instance, if CNOT instruction has the control qubit on the first index and
                target qubit on the second index. Then ASCII symbols would have ["C", "X"] to
                correlate a symbol with that index.

        Raises:
            TypeError: `qubit_count` is not an int
            ValueError: `qubit_count` is less than 1, `ascii_symbols` are `None`,
                ``fixed_qubit_count`` is implemented and and not equal to ``qubit_count``,
                or ``len(ascii_symbols) != qubit_count``
        """

        fixed_qubit_count = self.fixed_qubit_count()
        if fixed_qubit_count is NotImplemented:
            self._qubit_count = qubit_count
        else:
            if qubit_count and qubit_count != fixed_qubit_count:
                raise ValueError(
                    f"Provided qubit count {qubit_count}"
                    "does not equal fixed qubit count {fixed_qubit_count}"
                )
            self._qubit_count = fixed_qubit_count

        if not isinstance(self._qubit_count, int):
            raise TypeError(f"qubit_count, {self._qubit_count}, must be an integer")

        if self._qubit_count < 1:
            raise ValueError(f"qubit_count, {self._qubit_count}, must be greater than zero")

        if ascii_symbols is None:
            raise ValueError("ascii_symbols must not be None")

        if len(ascii_symbols) != self._qubit_count:
            msg = (
                f"ascii_symbols, {ascii_symbols},"
                f" length must equal qubit_count, {self._qubit_count}"
            )
            raise ValueError(msg)
        self._ascii_symbols = tuple(ascii_symbols)

    @staticmethod
    def fixed_qubit_count() -> int:
        """
        Returns the number of qubits this quantum operator acts on,
        if instances are guaranteed to act on the same number of qubits.

        If different instances can act on a different number of qubits,
        this method returns ``NotImplemented``.

        Returns:
            int: The number of qubits this quantum operator acts on.
        """
        return NotImplemented

    @property
    def qubit_count(self) -> int:
        """int: The number of qubits this quantum operator acts on."""
        return self._qubit_count

    @property
    def ascii_symbols(self) -> Tuple[str, ...]:
        """Tuple[str, ...]: Returns the ascii symbols for the quantum operator."""
        return self._ascii_symbols

    @property
    def name(self) -> str:
        """
        Returns the name of the quantum operator

        Returns:
            The name of the quantum operator as a string
        """
        return self.__class__.__name__

    def to_ir(self, *args, **kwargs) -> Any:
        """Returns IR representation of quantum operator

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        raise NotImplementedError("to_ir has not been implemented yet.")

    def to_matrix(self, *args, **kwargs) -> np.ndarray:
        """Returns a matrix representation of the quantum operator

        Returns:
            np.ndarray: A matrix representation of the quantum operator
        """
        raise NotImplementedError("to_matrix has not been implemented yet.")

    def matrix_equivalence(self, other: QuantumOperator) -> bool:
        """
        Whether the matrix form of two quantum operators are equivalent

        Args:
            other (QuantumOperator): Quantum operator instance to compare this quantum operator to

        Returns:
            bool: If matrix forms of this quantum operator and the other quantum operator
            are equivalent
        """
        if not isinstance(other, QuantumOperator):
            return False
        try:
            return np.allclose(self.to_matrix(), other.to_matrix())
        except ValueError:
            return False

    def __repr__(self):
        return f"{self.name}('qubit_count': {self.qubit_count})"
