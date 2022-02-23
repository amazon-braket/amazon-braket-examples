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

from typing import Iterable

import numpy as np

import braket.ir.jaqcd as ir
from braket.circuits import circuit
from braket.circuits.angled_gate import AngledGate
from braket.circuits.gate import Gate
from braket.circuits.instruction import Instruction
from braket.circuits.quantum_operator_helpers import (
    is_unitary,
    verify_quantum_operator_matrix_dimensions,
)
from braket.circuits.qubit import QubitInput
from braket.circuits.qubit_set import QubitSet, QubitSetInput

"""
To add a new gate:
    1. Implement the class and extend `Gate`
    2. Add a method with the `@circuit.subroutine(register=True)` decorator. Method name
       will be added into the `Circuit` class. This method is the default way
       clients add this gate to a circuit.
    3. Register the class with the `Gate` class via `Gate.register_gate()`.
"""

# Single qubit gates #


class H(Gate):
    """Hadamard gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["H"])

    def to_ir(self, target: QubitSet):
        return ir.H.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return 1.0 / np.sqrt(2.0) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def h(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of H instructions.

        Examples:
            >>> circ = Circuit().h(0)
            >>> circ = Circuit().h([0, 1, 2])
        """
        return [Instruction(H(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(H)


class I(Gate):  # noqa: E742, E261
    """Identity gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["I"])

    def to_ir(self, target: QubitSet):
        return ir.I.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.eye(2, dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def i(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of I instructions.

        Examples:
            >>> circ = Circuit().i(0)
            >>> circ = Circuit().i([0, 1, 2])
        """
        return [Instruction(I(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(I)


class X(Gate):
    """Pauli-X gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["X"])

    def to_ir(self, target: QubitSet):
        return ir.X.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def x(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of X instructions.

        Examples:
            >>> circ = Circuit().x(0)
            >>> circ = Circuit().x([0, 1, 2])
        """
        return [Instruction(X(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(X)


class Y(Gate):
    """Pauli-Y gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["Y"])

    def to_ir(self, target: QubitSet):
        return ir.Y.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def y(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of Y instructions.

        Examples:
            >>> circ = Circuit().y(0)
            >>> circ = Circuit().y([0, 1, 2])
        """
        return [Instruction(Y(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Y)


class Z(Gate):
    """Pauli-Z gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["Z"])

    def to_ir(self, target: QubitSet):
        return ir.Z.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def z(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of Z instructions.

        Examples:
            >>> circ = Circuit().z(0)
            >>> circ = Circuit().z([0, 1, 2])
        """
        return [Instruction(Z(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Z)


class S(Gate):
    """S gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["S"])

    def to_ir(self, target: QubitSet):
        return ir.S.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:

        return np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def s(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of S instructions.

        Examples:
            >>> circ = Circuit().s(0)
            >>> circ = Circuit().s([0, 1, 2])
        """
        return [Instruction(S(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(S)


class Si(Gate):
    """Conjugate transpose of S gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["Si"])

    def to_ir(self, target: QubitSet):
        return ir.Si.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, -1j]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def si(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: Iterable of Si instructions.

        Examples:
            >>> circ = Circuit().si(0)
            >>> circ = Circuit().si([0, 1, 2])
        """
        return [Instruction(Si(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Si)


class T(Gate):
    """T gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["T"])

    def to_ir(self, target: QubitSet):
        return ir.T.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.0, np.exp(1j * np.pi / 4)]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def t(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of T instructions.

        Examples:
            >>> circ = Circuit().t(0)
            >>> circ = Circuit().t([0, 1, 2])
        """
        return [Instruction(T(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(T)


class Ti(Gate):
    """Conjugate transpose of T gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["Ti"])

    def to_ir(self, target: QubitSet):
        return ir.Ti.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.0, np.exp(-1j * np.pi / 4)]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def ti(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of Ti instructions.

        Examples:
            >>> circ = Circuit().ti(0)
            >>> circ = Circuit().ti([0, 1, 2])
        """
        return [Instruction(Ti(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Ti)


class V(Gate):
    """Square root of not gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["V"])

    def to_ir(self, target: QubitSet):
        return ir.V.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array([[0.5 + 0.5j, 0.5 - 0.5j], [0.5 - 0.5j, 0.5 + 0.5j]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def v(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of V instructions.

        Examples:
            >>> circ = Circuit().v(0)
            >>> circ = Circuit().v([0, 1, 2])
        """
        return [Instruction(V(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(V)


class Vi(Gate):
    """Conjugate transpose of square root of not gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["Vi"])

    def to_ir(self, target: QubitSet):
        return ir.Vi.construct(target=target[0])

    def to_matrix(self) -> np.ndarray:
        return np.array(([[0.5 - 0.5j, 0.5 + 0.5j], [0.5 + 0.5j, 0.5 - 0.5j]]), dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def vi(target: QubitSetInput) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)

        Returns:
            Iterable[Instruction]: `Iterable` of Vi instructions.

        Examples:
            >>> circ = Circuit().vi(0)
            >>> circ = Circuit().vi([0, 1, 2])
        """
        return [Instruction(Vi(), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Vi)


# Single qubit gates with rotation #


class Rx(AngledGate):
    """X-axis rotation gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(angle=angle, qubit_count=None, ascii_symbols=["Rx({:.3g})".format(angle)])

    def to_ir(self, target: QubitSet):
        return ir.Rx.construct(target=target[0], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        cos = np.cos(self.angle / 2)
        sin = np.sin(self.angle / 2)
        return np.array([[cos, -1j * sin], [-1j * sin, cos]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def rx(target: QubitInput, angle: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Iterable[Instruction]: Rx instruction.

        Examples:
            >>> circ = Circuit().rx(0, 0.15)
        """
        return [Instruction(Rx(angle), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Rx)


class Ry(AngledGate):
    """Y-axis rotation gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(angle=angle, qubit_count=None, ascii_symbols=["Ry({:.3g})".format(angle)])

    def to_ir(self, target: QubitSet):
        return ir.Ry.construct(target=target[0], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        cos = np.cos(self.angle / 2)
        sin = np.sin(self.angle / 2)
        return np.array([[cos, -sin], [+sin, cos]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def ry(target: QubitInput, angle: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Iterable[Instruction]: Ry instruction.

        Examples:
            >>> circ = Circuit().ry(0, 0.15)
        """
        return [Instruction(Ry(angle), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Ry)


class Rz(AngledGate):
    """Z-axis rotation gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(angle=angle, qubit_count=None, ascii_symbols=["Rz({:.3g})".format(angle)])

    def to_ir(self, target: QubitSet):
        return ir.Rz.construct(target=target[0], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [[np.exp(-1j * self.angle / 2), 0], [0, np.exp(1j * self.angle / 2)]], dtype=complex
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def rz(target: QubitInput, angle: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Iterable[Instruction]: Rz instruction.

        Examples:
            >>> circ = Circuit().rz(0, 0.15)
        """
        return [Instruction(Rz(angle), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(Rz)


class PhaseShift(AngledGate):
    """Phase shift gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle, qubit_count=None, ascii_symbols=["PHASE({:.3g})".format(angle)]
        )

    def to_ir(self, target: QubitSet):
        return ir.PhaseShift.construct(target=target[0], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.0, np.exp(1j * self.angle)]], dtype=complex)

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def phaseshift(target: QubitInput, angle: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Iterable[Instruction]: PhaseShift instruction.

        Examples:
            >>> circ = Circuit().phaseshift(0, 0.15)
        """
        return [Instruction(PhaseShift(angle), target=qubit) for qubit in QubitSet(target)]


Gate.register_gate(PhaseShift)


# Two qubit gates #


class CNot(Gate):
    """Controlled NOT gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "X"])

    def to_ir(self, target: QubitSet):
        return ir.CNot.construct(control=target[0], target=target[1])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cnot(control: QubitInput, target: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.

        Returns:
            Instruction: CNot instruction.

        Examples:
            >>> circ = Circuit().cnot(0, 1)
        """
        return Instruction(CNot(), target=[control, target])


Gate.register_gate(CNot)


class Swap(Gate):
    """Swap gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["SWAP", "SWAP"])

    def to_ir(self, target: QubitSet):
        return ir.Swap.construct(targets=[target[0], target[1]])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def swap(target1: QubitInput, target2: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: Swap instruction.

        Examples:
            >>> circ = Circuit().swap(0, 1)
        """
        return Instruction(Swap(), target=[target1, target2])


Gate.register_gate(Swap)


class ISwap(Gate):
    """ISwap gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["ISWAP", "ISWAP"])

    def to_ir(self, target: QubitSet):
        return ir.ISwap.construct(targets=[target[0], target[1]])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0j, 0.0],
                [0.0, 1.0j, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def iswap(target1: QubitInput, target2: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: ISwap instruction.

        Examples:
            >>> circ = Circuit().iswap(0, 1)
        """
        return Instruction(ISwap(), target=[target1, target2])


Gate.register_gate(ISwap)


class PSwap(AngledGate):
    """PSwap gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle,
            qubit_count=None,
            ascii_symbols=["PSWAP({:.3g})".format(angle), "PSWAP({:.3g})".format(angle)],
        )

    def to_ir(self, target: QubitSet):
        return ir.PSwap.construct(targets=[target[0], target[1]], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, np.exp(1j * self.angle), 0.0],
                [0.0, np.exp(1j * self.angle), 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def pswap(target1: QubitInput, target2: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: PSwap instruction.

        Examples:
            >>> circ = Circuit().pswap(0, 1, 0.15)
        """
        return Instruction(PSwap(angle), target=[target1, target2])


Gate.register_gate(PSwap)


class XY(AngledGate):
    """XY gate.

    Reference: https://arxiv.org/abs/1912.04424v1

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle,
            qubit_count=None,
            ascii_symbols=["XY({:.3g})".format(angle), "XY({:.3g})".format(angle)],
        )

    def to_ir(self, target: QubitSet):
        return ir.XY.construct(targets=[target[0], target[1]], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        cos = np.cos(self.angle / 2)
        sin = np.sin(self.angle / 2)
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, cos, 1.0j * sin, 0.0],
                [0.0, 1.0j * sin, cos, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def xy(target1: QubitInput, target2: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: XY instruction.

        Examples:
            >>> circ = Circuit().xy(0, 1, 0.15)
        """
        return Instruction(XY(angle), target=[target1, target2])


Gate.register_gate(XY)


class CPhaseShift(AngledGate):
    """Controlled phase shift gate.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle, qubit_count=None, ascii_symbols=["C", "PHASE({:.3g})".format(angle)]
        )

    def to_ir(self, target: QubitSet):
        return ir.CPhaseShift.construct(control=target[0], target=target[1], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.diag([1.0, 1.0, 1.0, np.exp(1j * self.angle)])

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cphaseshift(control: QubitInput, target: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Instruction: CPhaseShift instruction.

        Examples:
            >>> circ = Circuit().cphaseshift(0, 1, 0.15)
        """
        return Instruction(CPhaseShift(angle), target=[control, target])


Gate.register_gate(CPhaseShift)


class CPhaseShift00(AngledGate):
    """Controlled phase shift gate for phasing the \\|00> state.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle, qubit_count=None, ascii_symbols=["C", "PHASE00({:.3g})".format(angle)]
        )

    def to_ir(self, target: QubitSet):
        return ir.CPhaseShift00.construct(control=target[0], target=target[1], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.diag([np.exp(1j * self.angle), 1.0, 1.0, 1.0])

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cphaseshift00(control: QubitInput, target: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Instruction: CPhaseShift00 instruction.

        Examples:
            >>> circ = Circuit().cphaseshift00(0, 1, 0.15)
        """
        return Instruction(CPhaseShift00(angle), target=[control, target])


Gate.register_gate(CPhaseShift00)


class CPhaseShift01(AngledGate):
    """Controlled phase shift gate for phasing the \\|01> state.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle, qubit_count=None, ascii_symbols=["C", "PHASE01({:.3g})".format(angle)]
        )

    def to_ir(self, target: QubitSet):
        return ir.CPhaseShift01.construct(control=target[0], target=target[1], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.diag([1.0, np.exp(1j * self.angle), 1.0, 1.0])

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cphaseshift01(control: QubitInput, target: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Instruction: CPhaseShift01 instruction.

        Examples:
            >>> circ = Circuit().cphaseshift01(0, 1, 0.15)
        """
        return Instruction(CPhaseShift01(angle), target=[control, target])


Gate.register_gate(CPhaseShift01)


class CPhaseShift10(AngledGate):
    """Controlled phase shift gate for phasing the \\|10> state.

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle, qubit_count=None, ascii_symbols=["C", "PHASE10({:.3g})".format(angle)]
        )

    def to_ir(self, target: QubitSet):
        return ir.CPhaseShift10.construct(control=target[0], target=target[1], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.diag([1.0, 1.0, np.exp(1j * self.angle), 1.0])

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cphaseshift10(control: QubitInput, target: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.
            angle (float): Angle in radians.

        Returns:
            Instruction: CPhaseShift10 instruction.

        Examples:
            >>> circ = Circuit().cphaseshift10(0, 1, 0.15)
        """
        return Instruction(CPhaseShift10(angle), target=[control, target])


Gate.register_gate(CPhaseShift10)


class CV(Gate):
    """Controlled Sqrt of NOT gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "V"])

    def to_ir(self, target: QubitSet):
        return ir.CV.construct(control=target[0], target=target[1])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.5 + 0.5j, 0.5 - 0.5j],  # if the control bit, then apply the V gate
                [0.0, 0.0, 0.5 - 0.5j, 0.5 + 0.5j],  # which is the sqrt(NOT) gate.
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cv(control: QubitInput, target: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.

        Returns:
            Instruction: CV instruction.

        Examples:
            >>> circ = Circuit().cv(0, 1)
        """
        return Instruction(CV(), target=[control, target])


Gate.register_gate(CV)


class CY(Gate):
    """Controlled Pauli-Y gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "Y"])

    def to_ir(self, target: QubitSet):
        return ir.CY.construct(control=target[0], target=target[1])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, -1.0j],
                [0.0, 0.0, +1.0j, 0.0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cy(control: QubitInput, target: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.

        Returns:
            Instruction: CY instruction.

        Examples:
            >>> circ = Circuit().cy(0, 1)
        """
        return Instruction(CY(), target=[control, target])


Gate.register_gate(CY)


class CZ(Gate):
    """Controlled Pauli-Z gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "Z"])

    def to_ir(self, target: QubitSet):
        return ir.CZ.construct(control=target[0], target=target[1])

    def to_matrix(self) -> np.ndarray:
        return np.diag([complex(1.0), 1.0, 1.0, -1.0])

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def cz(control: QubitInput, target: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index.
            target (Qubit or int): Target qubit index.

        Returns:
            Instruction: CZ instruction.

        Examples:
            >>> circ = Circuit().cz(0, 1)
        """
        return Instruction(CZ(), target=[control, target])


Gate.register_gate(CZ)


class ECR(Gate):
    """An echoed RZX(pi/2) gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["ECR", "ECR"])

    def to_ir(self, target: QubitSet):
        return ir.ECR.construct(targets=[target[0], target[1]])

    def to_matrix(self) -> np.ndarray:
        return (
            1
            / np.sqrt(2)
            * np.array(
                [[0, 1, 0, 1.0j], [1, 0, -1.0j, 0], [0, 1.0j, 0, 1], [-1.0j, 0, 1, 0]],
                dtype=complex,
            )
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def ecr(target1: QubitInput, target2: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: ECR instruction.

        Examples:
            >>> circ = Circuit().ecr(0, 1)
        """
        return Instruction(ECR(), target=[target1, target2])


Gate.register_gate(ECR)


class XX(AngledGate):
    """Ising XX coupling gate.

    Reference: https://arxiv.org/abs/1707.06356

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle,
            qubit_count=None,
            ascii_symbols=["XX({:.3g})".format(angle), "XX({:.3g})".format(angle)],
        )

    def to_ir(self, target: QubitSet):
        return ir.XX.construct(targets=[target[0], target[1]], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        cos = np.cos(self.angle / 2)
        isin = 1.0j * np.sin(self.angle / 2)
        return np.array(
            [
                [cos, 0.0, 0.0, -isin],
                [0.0, cos, -isin, 0.0],
                [0.0, -isin, cos, 0.0],
                [-isin, 0.0, 0.0, cos],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def xx(target1: QubitInput, target2: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.
            angle (float): Angle in radians.

        Returns:
            Instruction: XX instruction.

        Examples:
            >>> circ = Circuit().xx(0, 1, 0.15)
        """
        return Instruction(XX(angle), target=[target1, target2])


Gate.register_gate(XX)


class YY(AngledGate):
    """Ising YY coupling gate.

    Reference: https://arxiv.org/abs/1707.06356

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle,
            qubit_count=None,
            ascii_symbols=["YY({:.3g})".format(angle), "YY({:.3g})".format(angle)],
        )

    def to_ir(self, target: QubitSet):
        return ir.YY.construct(targets=[target[0], target[1]], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        cos = np.cos(self.angle / 2)
        isin = 1.0j * np.sin(self.angle / 2)
        return np.array(
            [
                [cos, 0.0, 0.0, isin],
                [0.0, cos, -isin, 0.0],
                [0.0, -isin, cos, 0.0],
                [isin, 0.0, 0.0, cos],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def yy(target1: QubitInput, target2: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.
            angle (float): Angle in radians.

        Returns:
            Instruction: YY instruction.

        Examples:
            >>> circ = Circuit().yy(0, 1, 0.15)
        """
        return Instruction(YY(angle), target=[target1, target2])


Gate.register_gate(YY)


class ZZ(AngledGate):
    """Ising ZZ coupling gate.

    Reference: https://arxiv.org/abs/1707.06356

    Args:
        angle (float): angle in radians.
    """

    def __init__(self, angle: float):
        super().__init__(
            angle=angle,
            qubit_count=None,
            ascii_symbols=["ZZ({:.3g})".format(angle), "ZZ({:.3g})".format(angle)],
        )

    def to_ir(self, target: QubitSet):
        return ir.ZZ.construct(targets=[target[0], target[1]], angle=self.angle)

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [np.exp(-1j * (self.angle / 2)), 0.0, 0.0, 0.0],
                [0.0, np.exp(1j * (self.angle / 2)), 0.0, 0.0],
                [0.0, 0.0, np.exp(1j * (self.angle / 2)), 0.0],
                [0.0, 0.0, 0.0, np.exp(-1j * (self.angle / 2))],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def zz(target1: QubitInput, target2: QubitInput, angle: float) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.
            angle (float): Angle in radians.

        Returns:
            Instruction: ZZ instruction.

        Examples:
            >>> circ = Circuit().zz(0, 1, 0.15)
        """
        return Instruction(ZZ(angle), target=[target1, target2])


Gate.register_gate(ZZ)


# Three qubit gates #


class CCNot(Gate):
    """CCNOT gate or Toffoli gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "C", "X"])

    def to_ir(self, target: QubitSet):
        return ir.CCNot.construct(controls=[target[0], target[1]], target=target[2])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 1, 0],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 3

    @staticmethod
    @circuit.subroutine(register=True)
    def ccnot(control1: QubitInput, control2: QubitInput, target: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control1 (Qubit or int): Control qubit 1 index.
            control2 (Qubit or int): Control qubit 2 index.
            target (Qubit or int): Target qubit index.

        Returns:
            Instruction: CCNot instruction.

        Examples:
            >>> circ = Circuit().ccnot(0, 1, 2)
        """
        return Instruction(CCNot(), target=[control1, control2, target])


Gate.register_gate(CCNot)


class CSwap(Gate):
    """Controlled Swap gate."""

    def __init__(self):
        super().__init__(qubit_count=None, ascii_symbols=["C", "SWAP", "SWAP"])

    def to_ir(self, target: QubitSet):
        return ir.CSwap.construct(control=target[0], targets=[target[1], target[2]])

    def to_matrix(self) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
            ],
            dtype=complex,
        )

    @staticmethod
    def fixed_qubit_count() -> int:
        return 3

    @staticmethod
    @circuit.subroutine(register=True)
    def cswap(control: QubitInput, target1: QubitInput, target2: QubitInput) -> Instruction:
        """Registers this function into the circuit class.

        Args:
            control (Qubit or int): Control qubit index
            target1 (Qubit or int): Target qubit 1 index.
            target2 (Qubit or int): Target qubit 2 index.

        Returns:
            Instruction: CSwap instruction.

        Examples:
            >>> circ = Circuit().cswap(0, 1, 2)
        """
        return Instruction(CSwap(), target=[control, target1, target2])


Gate.register_gate(CSwap)


class Unitary(Gate):
    """Arbitrary unitary gate

    Args:
        matrix (numpy.ndarray): Unitary matrix which defines the gate.
        display_name (str): Name to be used for an instance of this unitary gate
            for circuit diagrams. Defaults to `U`.

    Raises:
        ValueError: If `matrix` is not a two-dimensional square matrix,
            or has a dimension length that is not a positive power of 2,
            or is not unitary.
    """

    def __init__(self, matrix: np.ndarray, display_name: str = "U"):
        verify_quantum_operator_matrix_dimensions(matrix)
        self._matrix = np.array(matrix, dtype=complex)
        qubit_count = int(np.log2(self._matrix.shape[0]))

        if not is_unitary(self._matrix):
            raise ValueError(f"{self._matrix} is not unitary")

        super().__init__(qubit_count=qubit_count, ascii_symbols=[display_name] * qubit_count)

    def to_matrix(self):
        return np.array(self._matrix)

    def to_ir(self, target: QubitSet):
        return ir.Unitary.construct(
            targets=[qubit for qubit in target],
            matrix=Unitary._transform_matrix_to_ir(self._matrix),
        )

    def __eq__(self, other):
        if isinstance(other, Unitary):
            return self.matrix_equivalence(other)
        return NotImplemented

    @staticmethod
    def _transform_matrix_to_ir(matrix: np.ndarray):
        return [[[element.real, element.imag] for element in row] for row in matrix.tolist()]

    @staticmethod
    @circuit.subroutine(register=True)
    def unitary(targets: QubitSet, matrix: np.ndarray, display_name: str = "U") -> Instruction:
        """Registers this function into the circuit class.

        Args:
            targets (QubitSet): Target qubits.
            matrix (numpy.ndarray): Unitary matrix which defines the gate. Matrix should be
                compatible with the supplied targets, with `2 ** len(targets) == matrix.shape[0]`.
            display_name (str): Name to be used for an instance of this unitary gate
                for circuit diagrams. Defaults to `U`.

        Returns:
            Instruction: Unitary instruction.

        Raises:
            ValueError: If `matrix` is not a two-dimensional square matrix,
                or has a dimension length that is not compatible with the `targets`,
                or is not unitary,

        Examples:
            >>> circ = Circuit().unitary(matrix=np.array([[0, 1],[1, 0]]), targets=[0])
        """
        if 2 ** len(targets) != matrix.shape[0]:
            raise ValueError("Dimensions of the supplied unitary are incompatible with the targets")

        return Instruction(Unitary(matrix, display_name), target=targets)


Gate.register_gate(Unitary)
