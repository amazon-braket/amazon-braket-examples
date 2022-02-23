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

from typing import Dict, Tuple

from braket.circuits.operator import Operator
from braket.circuits.quantum_operator import QuantumOperator
from braket.circuits.qubit import QubitInput
from braket.circuits.qubit_set import QubitSet, QubitSetInput

# InstructionOperator is a type alias, and it can be expanded to include other operators
InstructionOperator = Operator


class Instruction:
    """
    An instruction is a quantum directive that describes the task to perform on a quantum device.
    """

    def __init__(self, operator: InstructionOperator, target: QubitSetInput = None):
        """
        InstructionOperator includes objects of type `Gate` only.

        Args:
            operator (InstructionOperator): Operator for the instruction.
            target (int, Qubit, or iterable of int / Qubit): Target qubits that the operator is
                applied to.

        Raises:
            ValueError: If `operator` is empty or any integer in `target` does not meet the `Qubit`
                or `QubitSet` class requirements. Also, if operator qubit count does not equal
                the size of the target qubit set.
            TypeError: If a `Qubit` class can't be constructed from `target` due to an incorrect
                `typing`.

        Examples:
            >>> Instruction(Gate.CNot(), [0, 1])
            Instruction('operator': CNOT, 'target': QubitSet(Qubit(0), Qubit(1)))
            >>> instr = Instruction(Gate.CNot()), QubitSet([0, 1])])
            Instruction('operator': CNOT, 'target': QubitSet(Qubit(0), Qubit(1)))
            >>> instr = Instruction(Gate.H(), 0)
            Instruction('operator': H, 'target': QubitSet(Qubit(0),))
            >>> instr = Instruction(Gate.Rx(0.12), 0)
            Instruction('operator': Rx, 'target': QubitSet(Qubit(0),))
        """
        if not operator:
            raise ValueError("Operator cannot be empty")
        target_set = QubitSet(target)
        if isinstance(operator, QuantumOperator) and len(target_set) != operator.qubit_count:
            raise ValueError(
                f"Operator qubit count {operator.qubit_count} must be equal to"
                f" size of target qubit set {target_set}"
            )
        self._operator = operator
        self._target = target_set

    @property
    def operator(self) -> InstructionOperator:
        """Operator: The operator for the instruction, for example, `Gate`."""
        return self._operator

    @property
    def target(self) -> QubitSet:
        """
        QubitSet: Target qubits that the operator is applied to.

        Note:
            Don't mutate this property, any mutations can have unexpected consequences.
        """
        return self._target

    def to_ir(self):
        """
        Converts the operator into the canonical intermediate representation.
        If the operator is passed in a request, this method is called before it is passed.
        """
        return self._operator.to_ir([int(qubit) for qubit in self._target])

    @property
    def ascii_symbols(self) -> Tuple[str, ...]:
        """Tuple[str, ...]: Returns the ascii symbols for the instruction's operator."""
        return self._operator.ascii_symbols

    def copy(
        self, target_mapping: Dict[QubitInput, QubitInput] = None, target: QubitSetInput = None
    ) -> Instruction:
        """
        Return a shallow copy of the instruction.

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
            Instruction: A shallow copy of the instruction.

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.

        Examples:
            >>> instr = Instruction(Gate.H(), 0)
            >>> new_instr = instr.copy()
            >>> new_instr.target
            QubitSet(Qubit(0))
            >>> new_instr = instr.copy(target_mapping={0: 5})
            >>> new_instr.target
            QubitSet(Qubit(5))
            >>> new_instr = instr.copy(target=[5])
            >>> new_instr.target
            QubitSet(Qubit(5))
        """
        if target_mapping and target is not None:
            raise TypeError("Only 'target_mapping' or 'target' can be supplied, but not both.")
        elif target is not None:
            return Instruction(self._operator, target)
        else:
            return Instruction(self._operator, self._target.map(target_mapping or {}))

    def __repr__(self):
        return f"Instruction('operator': {self._operator}, 'target': {self._target})"

    def __eq__(self, other):
        if isinstance(other, Instruction):
            return (self._operator, self._target) == (other._operator, other._target)
        return NotImplemented
