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

import math
from typing import Optional, Sequence

from braket.circuits.gate import Gate


class AngledGate(Gate):
    """
    Class `AngledGate` represents a quantum gate that operates on N qubits and an angle.
    """

    def __init__(self, angle: float, qubit_count: Optional[int], ascii_symbols: Sequence[str]):
        """
        Args:
            angle (float): The angle of the gate in radians.
            qubit_count (int, optional): The number of qubits that this gate interacts with.
            ascii_symbols (Sequence[str]): ASCII string symbols for the gate. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.
                For instance, if a CNOT instruction has the control qubit on the first index and
                target qubit on the second index, the ASCII symbols should have `["C", "X"]` to
                correlate a symbol with that index.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, or `angle` is `None`
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)
        if angle is None:
            raise ValueError("angle must not be None")
        self._angle = float(angle)  # explicit casting in case angle is e.g. np.float32

    @property
    def angle(self) -> float:
        """
        Returns the angle for the gate

        Returns:
            angle (float): The angle of the gate in radians
        """
        return self._angle

    def __eq__(self, other):
        if isinstance(other, AngledGate):
            return self.name == other.name and math.isclose(self.angle, other.angle)
        return NotImplemented

    def __repr__(self):
        return f"{self.name}('angle': {self.angle}, 'qubit_count': {self.qubit_count})"
