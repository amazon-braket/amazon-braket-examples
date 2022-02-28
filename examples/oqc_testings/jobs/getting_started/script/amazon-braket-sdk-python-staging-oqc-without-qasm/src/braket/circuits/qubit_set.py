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

from typing import Dict, Iterable, Union

from boltons.setutils import IndexedSet

from braket.circuits.qubit import Qubit, QubitInput

QubitSetInput = Union[QubitInput, Iterable[QubitInput]]


class QubitSet(IndexedSet):
    """
    An ordered, unique set of quantum bits.

    Note:
        QubitSet implements `__hash__()` but is a mutable object, therefore be careful when
        mutating this object.
    """

    def __init__(self, qubits: QubitSetInput = None):
        """
        Args:
            qubits (int, Qubit, or iterable of int / Qubit, optional): Qubits to be included in
                the `QubitSet`. Default is `None`.

        Examples:
            >>> qubits = QubitSet([0, 1])
            >>> for qubit in qubits:
            ...     print(qubit)
            ...
            Qubit(0)
            Qubit(1)

            >>> qubits = QubitSet([0, 1, [2, 3]])
            >>> for qubit in qubits:
            ...     print(qubit)
            ...
            Qubit(0)
            Qubit(1)
            Qubit(2)
            Qubit(3)
        """

        def _flatten(other):
            if isinstance(other, Iterable) and not isinstance(other, str):
                for item in other:
                    yield from _flatten(item)
            else:
                yield other

        _qubits = [Qubit.new(qubit) for qubit in _flatten(qubits)] if qubits is not None else None
        super().__init__(_qubits)

    def map(self, mapping: Dict[QubitInput, QubitInput]) -> QubitSet:
        """
        Creates a new `QubitSet` where this instance's qubits are mapped to the values in `mapping`.
        If this instance contains a qubit that is not in the `mapping` that qubit is not modified.

        Args:
            mapping (dictionary[int or Qubit, int or Qubit]): A dictionary of qubit mappings to
                apply. Key is the qubit in this instance to target, and the value is what
                the key will be changed to.

        Returns:
            QubitSet: A new QubitSet with the `mapping` applied.

        Examples:
            >>> qubits = QubitSet([0, 1])
            >>> mapping = {0: 10, Qubit(1): Qubit(11)}
            >>> qubits.map(mapping)
            QubitSet([Qubit(10), Qubit(11)])
        """

        new_qubits = [mapping.get(qubit, qubit) for qubit in self]

        return QubitSet(new_qubits)

    def __hash__(self):
        return hash(tuple(self))
