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

import itertools
from typing import Dict, Iterable

import numpy as np

import braket.ir.jaqcd as ir
from braket.circuits import circuit
from braket.circuits.instruction import Instruction
from braket.circuits.noise import (
    DampingNoise,
    GeneralizedAmplitudeDampingNoise,
    MultiQubitPauliNoise,
    Noise,
    PauliNoise,
    SingleProbabilisticNoise,
    SingleProbabilisticNoise_34,
    SingleProbabilisticNoise_1516,
)
from braket.circuits.quantum_operator_helpers import (
    is_cptp,
    verify_quantum_operator_matrix_dimensions,
)
from braket.circuits.qubit import QubitInput
from braket.circuits.qubit_set import QubitSet, QubitSetInput

"""
To add a new Noise implementation:
    1. Implement the class and extend `Noise`
    2. Add a method with the `@circuit.subroutine(register=True)` decorator. Method name
       will be added into the `Circuit` class. This method is the default way clients add
       this noise to a circuit.
    3. Register the class with the `Noise` class via `Noise.register_noise()`.
"""


class BitFlip(SingleProbabilisticNoise):
    """Bit flip noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math:: \\rho \\Rightarrow (1-p) \\rho + p X \\rho X^{\\dagger}
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        X = \\left(
                \\begin{matrix}
                    0 & 1 \\\\
                    1 & 0
                \\end{matrix}
            \\right)

        p = \\text{probability}

    This noise channel is shown as `BF` in circuit diagrams.
    """

    def __init__(self, probability: float):
        super().__init__(
            probability=probability,
            qubit_count=None,
            ascii_symbols=["BF({:.2g})".format(probability)],
        )

    def to_ir(self, target: QubitSet):
        return ir.BitFlip.construct(target=target[0], probability=self.probability)

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.sqrt(1 - self.probability) * np.eye(2, dtype=complex)
        K1 = np.sqrt(self.probability) * np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        return [K0, K1]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def bit_flip(target: QubitSetInput, probability: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)
            probability (float): Probability of bit flipping.

        Returns:
            Iterable[Instruction]: `Iterable` of BitFlip instructions.

        Examples:
            >>> circ = Circuit().bit_flip(0, probability=0.1)
        """
        return [
            Instruction(Noise.BitFlip(probability=probability), target=qubit)
            for qubit in QubitSet(target)
        ]


Noise.register_noise(BitFlip)


class PhaseFlip(SingleProbabilisticNoise):
    """Phase flip noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math:: \\rho \\Rightarrow (1-p) \\rho + p X \\rho X^{\\dagger}
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

        p = \\text{probability}

    This noise channel is shown as `PF` in circuit diagrams.
    """

    def __init__(self, probability: float):
        super().__init__(
            probability=probability,
            qubit_count=None,
            ascii_symbols=["PF({:.2g})".format(probability)],
        )

    def to_ir(self, target: QubitSet):
        return ir.PhaseFlip.construct(target=target[0], probability=self.probability)

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.sqrt(1 - self.probability) * np.eye(2, dtype=complex)
        K1 = np.sqrt(self.probability) * np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        return [K0, K1]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def phase_flip(target: QubitSetInput, probability: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)
            probability (float): Probability of phase flipping.

        Returns:
            Iterable[Instruction]: `Iterable` of PhaseFlip instructions.

        Examples:
            >>> circ = Circuit().phase_flip(0, probability=0.1)
        """
        return [
            Instruction(Noise.PhaseFlip(probability=probability), target=qubit)
            for qubit in QubitSet(target)
        ]


Noise.register_noise(PhaseFlip)


class PauliChannel(PauliNoise):
    """Pauli noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math::
        \\rho \\Rightarrow (1-probX-probY-probZ) \\rho
            + probX X \\rho X^{\\dagger}
            + probY Y \\rho Y^{\\dagger}
            + probZ Z \\rho Z^{\\dagger}
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        X = \\left(
                \\begin{matrix}
                    0 & 1 \\\\
                    1 & 0
                \\end{matrix}
            \\right)

        Y = \\left(
                \\begin{matrix}
                    0 & -i \\\\
                    i &  0
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

    This noise channel is shown as `PC` in circuit diagrams.
    """

    def __init__(self, probX: float, probY: float, probZ: float):
        super().__init__(
            probX=probX,
            probY=probY,
            probZ=probZ,
            qubit_count=None,
            ascii_symbols=["PC({:.2g},{:.2g},{:.2g})".format(probX, probY, probZ)],
        )

    def to_ir(self, target: QubitSet):
        return ir.PauliChannel.construct(
            target=target[0], probX=self.probX, probY=self.probY, probZ=self.probZ
        )

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.sqrt(1 - self.probX - self.probY - self.probZ) * np.eye(2, dtype=complex)
        K1 = np.sqrt(self.probX) * np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        K2 = np.sqrt(self.probY) * 1j * np.array([[0.0, -1.0], [1.0, 0.0]], dtype=complex)
        K3 = np.sqrt(self.probZ) * np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        return [K0, K1, K2, K3]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def pauli_channel(
        target: QubitSetInput, probX: float, probY: float, probZ: float
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)
                probability List[float]: Probabilities for the Pauli X, Y and Z noise
                happening in the Kraus channel.

        Returns:
            Iterable[Instruction]: `Iterable` of PauliChannel instructions.

        Examples:
            >>> circ = Circuit().pauli_channel(0,probX=0.1,probY=0.2,probZ=0.3)
        """
        return [
            Instruction(Noise.PauliChannel(probX=probX, probY=probY, probZ=probZ), target=qubit)
            for qubit in QubitSet(target)
        ]


Noise.register_noise(PauliChannel)


class Depolarizing(SingleProbabilisticNoise_34):
    """Depolarizing noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math::
        \\rho \\Rightarrow (1-p) \\rho
            + p/3 X \\rho X^{\\dagger}
            + p/3 Y \\rho Y^{\\dagger}
            + p/3 Z \\rho Z^{\\dagger}
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        X = \\left(
                \\begin{matrix}
                    0 & 1 \\\\
                    1 & 0
                \\end{matrix}
            \\right)

        Y = \\left(
                \\begin{matrix}
                    0 & -i \\\\
                    i &  0
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

        p = \\text{probability}

    This noise channel is shown as `DEPO` in circuit diagrams.
    """

    def __init__(self, probability: float):
        super().__init__(
            probability=probability,
            qubit_count=None,
            ascii_symbols=["DEPO({:.2g})".format(probability)],
        )

    def to_ir(self, target: QubitSet):
        return ir.Depolarizing.construct(target=target[0], probability=self.probability)

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.sqrt(1 - self.probability) * np.eye(2, dtype=complex)
        K1 = np.sqrt(self.probability / 3) * np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        K2 = np.sqrt(self.probability / 3) * 1j * np.array([[0.0, -1.0], [1.0, 0.0]], dtype=complex)
        K3 = np.sqrt(self.probability / 3) * np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        return [K0, K1, K2, K3]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def depolarizing(target: QubitSetInput, probability: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)
            probability (float): Probability of depolarizing.

        Returns:
            Iterable[Instruction]: `Iterable` of Depolarizing instructions.

        Examples:
            >>> circ = Circuit().depolarizing(0, probability=0.1)
        """
        return [
            Instruction(Noise.Depolarizing(probability=probability), target=qubit)
            for qubit in QubitSet(target)
        ]


Noise.register_noise(Depolarizing)


class TwoQubitDepolarizing(SingleProbabilisticNoise_1516):
    """Two-Qubit Depolarizing noise channel which transforms a
        density matrix :math:`\\rho` according to:

    .. math::
        \\rho \\Rightarrow (1-p) \\rho + p/15 (
          IX \\rho IX^{\\dagger} + IY \\rho IY^{\\dagger} + IZ \\rho IZ^{\\dagger}
        + XI \\rho XI^{\\dagger} + XX \\rho XX^{\\dagger} + XY \\rho XY^{\\dagger}
        + XZ \\rho XZ^{\\dagger} + YI \\rho YI^{\\dagger} + YX \\rho YX^{\\dagger}
        + YY \\rho YY^{\\dagger} + YZ \\rho YZ^{\\dagger} + ZI \\rho ZI^{\\dagger}
        + ZX \\rho ZX^{\\dagger} + ZY \\rho ZY^{\\dagger} + ZZ \\rho ZZ^{\\dagger})
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        X = \\left(
                \\begin{matrix}
                    0 & 1 \\\\
                    1 & 0
                \\end{matrix}
            \\right)

        Y = \\left(
                \\begin{matrix}
                    0 & -i \\\\
                    i &  0
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

        p = \\text{probability}

    This noise channel is shown as `DEPO` in circuit diagrams.
    """

    def __init__(self, probability: float):
        super().__init__(
            probability=probability,
            qubit_count=None,
            ascii_symbols=["DEPO({:.2g})".format(probability)] * 2,
        )

    def to_ir(self, target: QubitSet):
        return ir.TwoQubitDepolarizing.construct(
            targets=[target[0], target[1]], probability=self.probability
        )

    def to_matrix(self) -> Iterable[np.ndarray]:

        SI = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
        SX = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        SY = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
        SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

        K_list_single = [SI, SX, SY, SZ]
        K_list = [np.kron(i, j) for i in K_list_single for j in K_list_single]

        K_list[0] *= np.sqrt(1 - self._probability)

        K_list[1:] = [np.sqrt(self._probability / 15) * i for i in K_list[1:]]

        return K_list

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def two_qubit_depolarizing(
        target1: QubitInput, target2: QubitInput, probability: float
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubits
            probability (float): Probability of two-qubit depolarizing.

        Returns:
            Iterable[Instruction]: `Iterable` of Depolarizing instructions.

        Examples:
            >>> circ = Circuit().two_qubit_depolarizing(0, 1, probability=0.1)
        """
        return [
            Instruction(
                Noise.TwoQubitDepolarizing(probability=probability), target=[target1, target2]
            )
        ]


Noise.register_noise(TwoQubitDepolarizing)


class TwoQubitDephasing(SingleProbabilisticNoise_34):
    """Two-Qubit Dephasing noise channel which transforms a
        density matrix :math:`\\rho` according to:

    .. math::
        \\rho \\Rightarrow (1-p) \\rho + p/3 (
          IZ \\rho IZ^{\\dagger} + ZI \\rho ZI^{\\dagger} + ZZ \\rho ZZ^{\\dagger})
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

        p = \\text{probability}

    This noise channel is shown as `DEPH` in circuit diagrams.
    """

    def __init__(self, probability: float):
        super().__init__(
            probability=probability,
            qubit_count=None,
            ascii_symbols=["DEPH({:.2g})".format(probability)] * 2,
        )

    def to_ir(self, target: QubitSet):
        return ir.TwoQubitDephasing.construct(
            targets=[target[0], target[1]], probability=self.probability
        )

    def to_matrix(self) -> Iterable[np.ndarray]:

        SI = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
        SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        K0 = np.sqrt(1 - self._probability) * np.kron(SI, SI)
        K1 = np.sqrt(self._probability / 3) * np.kron(SI, SZ)
        K2 = np.sqrt(self._probability / 3) * np.kron(SZ, SI)
        K3 = np.sqrt(self._probability / 3) * np.kron(SZ, SZ)

        return [K0, K1, K2, K3]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def two_qubit_dephasing(
        target1: QubitInput, target2: QubitInput, probability: float
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubits
            probability (float): Probability of two-qubit dephasing.

        Returns:
            Iterable[Instruction]: `Iterable` of Dephasing instructions.

        Examples:
            >>> circ = Circuit().two_qubit_dephasing(0, 1, probability=0.1)
        """
        return [
            Instruction(Noise.TwoQubitDephasing(probability=probability), target=[target1, target2])
        ]


Noise.register_noise(TwoQubitDephasing)


class TwoQubitPauliChannel(MultiQubitPauliNoise):
    """Two-Qubit Pauli noise channel which transforms a
        density matrix :math:`\\rho` according to:

    .. math::
        \\rho \\Rightarrow (1-p) \\rho +
            p_{IX} IX \\rho IX^{\\dagger} +
            p_{IY} IY \\rho IY^{\\dagger} +
            p_{IZ} IZ \\rho IZ^{\\dagger} +
            p_{XI} XI \\rho XI^{\\dagger} +
            p_{XX} XX \\rho XX^{\\dagger} +
            p_{XY} XY \\rho XY^{\\dagger} +
            p_{XZ} XZ \\rho XZ^{\\dagger} +
            p_{YI} YI \\rho YI^{\\dagger} +
            p_{YX} YX \\rho YX^{\\dagger} +
            p_{YY} YY \\rho YY^{\\dagger} +
            p_{YZ} YZ \\rho YZ^{\\dagger} +
            p_{ZI} ZI \\rho ZI^{\\dagger} +
            p_{ZX} ZX \\rho ZX^{\\dagger} +
            p_{ZY} ZY \\rho ZY^{\\dagger} +
            p_{ZZ} ZZ \\rho ZZ^{\\dagger})
    where

    .. math::
        I = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & 1
                \\end{matrix}
            \\right)

        X = \\left(
                \\begin{matrix}
                    0 & 1 \\\\
                    1 & 0
                \\end{matrix}
            \\right)

        Y = \\left(
                \\begin{matrix}
                    0 & -i \\\\
                    i &  0
                \\end{matrix}
            \\right)

        Z = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & -1
                \\end{matrix}
            \\right)

        p = \\text{sum of all probabilities}

    This noise channel is shown as `PC_2({"pauli_string": probability})` in circuit diagrams.
    """

    _paulis = {
        "I": np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex),
        "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
        "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex),
        "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
    }
    _tensor_products_strings = itertools.product(_paulis.keys(), repeat=2)
    _names_list = ["".join(x) for x in _tensor_products_strings]

    def __init__(self, probabilities: Dict[str, float]):
        super().__init__(
            probabilities=probabilities,
            qubit_count=None,
            ascii_symbols=[
                f"PC2({probabilities})",
                f"PC2({probabilities})",
            ],
        )

        total_prob = sum(self.probabilities.values())

        K_list = [np.sqrt(1 - total_prob) * np.identity(4)]  # "II" element
        for pstring in self._names_list[1:]:  # ignore "II"
            if pstring in self.probabilities:
                mat = np.sqrt(self.probabilities[pstring]) * np.kron(
                    self._paulis[pstring[0]], self._paulis[pstring[1]]
                )
                K_list.append(mat)
            else:
                K_list.append(np.zeros((4, 4)))
        self._matrix = K_list

    def to_ir(self, target: QubitSet):
        return ir.MultiQubitPauliChannel.construct(
            targets=[target[0], target[1]], probabilities=self.probabilities
        )

    def to_matrix(self) -> Iterable[np.ndarray]:
        return self._matrix

    @staticmethod
    def fixed_qubit_count() -> int:
        return 2

    @staticmethod
    @circuit.subroutine(register=True)
    def two_qubit_pauli_channel(
        target1: QubitInput, target2: QubitInput, probabilities: Dict[str, float]
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubits
            probability (float): Probability of two-qubit Pauli channel.

        Returns:
            Iterable[Instruction]: `Iterable` of Depolarizing instructions.

        Examples:
            >>> circ = Circuit().two_qubit_pauli_channel(0, 1, {"XX": 0.1})
        """
        return [
            Instruction(
                Noise.TwoQubitPauliChannel(probabilities=probabilities),
                target=[target1, target2],
            )
        ]


Noise.register_noise(TwoQubitPauliChannel)


class AmplitudeDamping(DampingNoise):
    """AmplitudeDamping noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math:: \\rho \\Rightarrow E_0 \\rho E_0^{\\dagger} + E_1 \\rho E_1^{\\dagger}
    where

    .. math::
        E_0 = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & \\sqrt{1-\\gamma}
                \\end{matrix}
              \\right)

        E_1 = \\left(
                \\begin{matrix}
                    0 & \\sqrt{\\gamma} \\\\
                    0 & 0
                \\end{matrix}
              \\right)

    This noise channel is shown as `AD` in circuit diagrams.
    """

    def __init__(self, gamma: float):
        super().__init__(
            gamma=gamma,
            qubit_count=None,
            ascii_symbols=["AD({:.2g})".format(gamma)],
        )

    def to_ir(self, target: QubitSet):
        return ir.AmplitudeDamping.construct(target=target[0], gamma=self.gamma)

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1 - self.gamma)]], dtype=complex)
        K1 = np.array([[0.0, np.sqrt(self.gamma)], [0.0, 0.0]], dtype=complex)
        return [K0, K1]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def amplitude_damping(target: QubitSetInput, gamma: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s).
            gamma (float): decaying rate of the amplitude damping channel.

        Returns:
            Iterable[Instruction]: `Iterable` of AmplitudeDamping instructions.

        Examples:
            >>> circ = Circuit().amplitude_damping(0, gamma=0.1)
        """
        return [
            Instruction(Noise.AmplitudeDamping(gamma=gamma), target=qubit)
            for qubit in QubitSet(target)
        ]


Noise.register_noise(AmplitudeDamping)


class GeneralizedAmplitudeDamping(GeneralizedAmplitudeDampingNoise):
    """Generalized AmplitudeDamping noise channel which transforms a
        density matrix :math:`\\rho` according to:

    .. math:: \\rho \\Rightarrow E_0 \\rho E_0^{\\dagger} + E_1 \\rho E_1^{\\dagger}
                + E_2 \\rho E_2^{\\dagger} + E_3 \\rho E_3^{\\dagger}
    where

    .. math::
        E_0 = \\sqrt(probability)\\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & \\sqrt{1-\\gamma}
                \\end{matrix}
              \\right)

        E_1 = \\sqrt(probability)\\left(
                \\begin{matrix}
                    0 & \\sqrt{\\gamma} \\\\
                    0 & 0
                \\end{matrix}
              \\right)
        E_2 = \\sqrt(1-probability)\\left(
                \\begin{matrix}
                    \\sqrt{1-\\gamma} & 0 \\\\
                    0 & 1
                \\end{matrix}
              \\right)
        E_3 = \\sqrt(1-probability)\\left(
                \\begin{matrix}
                    0 & 0 \\\\
                    \\sqrt{\\gamma} & 0
                \\end{matrix}
              \\right)

    This noise channel is shown as `GAD` in circuit diagrams.
    """

    def __init__(self, gamma: float, probability: float):
        super().__init__(
            gamma=gamma,
            probability=probability,
            qubit_count=None,
            ascii_symbols=["GAD({:.2g},{:.2g})".format(gamma, probability)],
        )

    def to_ir(self, target: QubitSet):
        return ir.GeneralizedAmplitudeDamping.construct(
            target=target[0], gamma=self.gamma, probability=self.probability
        )

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.sqrt(self.probability) * np.array(
            [[1.0, 0.0], [0.0, np.sqrt(1 - self.gamma)]], dtype=complex
        )
        K1 = np.sqrt(self.probability) * np.array(
            [[0.0, np.sqrt(self.gamma)], [0.0, 0.0]], dtype=complex
        )
        K2 = np.sqrt(1 - self.probability) * np.array([[np.sqrt(1 - self.gamma), 0.0], [0.0, 1.0]])
        K3 = np.sqrt(1 - self.probability) * np.array([[0.0, 0.0], [np.sqrt(self.gamma), 0.0]])
        return [K0, K1, K2, K3]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def generalized_amplitude_damping(
        target: QubitSetInput, gamma: float, probability: float
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s).
            p(float): Probability of the system being excited by the environment.
            gamma (float): The damping rate of the amplitude damping channel.

        Returns:
            Iterable[Instruction]: `Iterable` of GeneralizedAmplitudeDamping instructions.

        Examples:
            >>> circ = Circuit().generalized_amplitude_damping(0, probability = 0.9, gamma=0.1)
        """
        return [
            Instruction(
                Noise.GeneralizedAmplitudeDamping(gamma=gamma, probability=probability),
                target=qubit,
            )
            for qubit in QubitSet(target)
        ]


Noise.register_noise(GeneralizedAmplitudeDamping)


class PhaseDamping(DampingNoise):
    """Phase damping noise channel which transforms a density matrix :math:`\\rho` according to:

    .. math:: \\rho \\Rightarrow E_0 \\rho E_0^{\\dagger} + E_1 \\rho E_1^{\\dagger}
    where

    .. math::
        E_0 = \\left(
                \\begin{matrix}
                    1 & 0 \\\\
                    0 & \\sqrt{1-gamma}
                \\end{matrix}
              \\right)

        E_1 = \\left(
                \\begin{matrix}
                    0 & 0 \\\\
                    0 & \\sqrt{gamma}
                \\end{matrix}
              \\right)

        p = \\text{probability}

    This noise channel is shown as `PD` in circuit diagrams.
    """

    def __init__(self, gamma: float):
        super().__init__(
            gamma=gamma,
            qubit_count=None,
            ascii_symbols=["PD({:.2g})".format(gamma)],
        )

    def to_ir(self, target: QubitSet):
        return ir.PhaseDamping.construct(target=target[0], gamma=self.gamma)

    def to_matrix(self) -> Iterable[np.ndarray]:
        K0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1 - self.gamma)]], dtype=complex)
        K1 = np.array([[0.0, 0.0], [0.0, np.sqrt(self.gamma)]], dtype=complex)
        return [K0, K1]

    @staticmethod
    def fixed_qubit_count() -> int:
        return 1

    @staticmethod
    @circuit.subroutine(register=True)
    def phase_damping(target: QubitSetInput, gamma: float) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            target (Qubit, int, or iterable of Qubit / int): Target qubit(s)
            gamma (float): Probability of phase damping.

        Returns:
            Iterable[Instruction]: `Iterable` of PhaseDamping instructions.

        Examples:
            >>> circ = Circuit().phase_damping(0, gamma=0.1)
        """
        return [
            Instruction(Noise.PhaseDamping(gamma=gamma), target=qubit) for qubit in QubitSet(target)
        ]


Noise.register_noise(PhaseDamping)


class Kraus(Noise):
    """User-defined noise channel that uses the provided matrices as Kraus operators
    This noise channel is shown as `NK` in circuit diagrams.

    Args:
        matrices (Iterable[np.array]): A list of matrices that define a noise
            channel. These matrices need to satisfy the requirement of CPTP map.
        display_name (str): Name to be used for an instance of this general noise
            channel for circuit diagrams. Defaults to `KR`.

    Raises:
        ValueError: If any matrix in `matrices` is not a two-dimensional square
            matrix,
            or has a dimension length which is not a positive exponent of 2,
            or the `matrices` do not satisfy CPTP condition.
    """

    def __init__(self, matrices: Iterable[np.ndarray], display_name: str = "KR"):

        for matrix in matrices:
            verify_quantum_operator_matrix_dimensions(matrix)
            if not int(np.log2(matrix.shape[0])) == int(np.log2(matrices[0].shape[0])):
                raise ValueError(f"all matrices in {matrices} must have the same shape")
        self._matrices = [np.array(matrix, dtype=complex) for matrix in matrices]
        qubit_count = int(np.log2(self._matrices[0].shape[0]))
        if qubit_count > 2:
            raise ValueError("Kraus operators with more than two qubits are not supported.")
        if len(matrices) > 2 ** (2 * qubit_count):
            raise ValueError("The number of Kraus operators is beyond limit.")

        if not is_cptp(self._matrices):
            raise ValueError(
                "The input matrices do not define a completely-positive trace-preserving map."
            )

        super().__init__(qubit_count=qubit_count, ascii_symbols=[display_name] * qubit_count)

    def to_matrix(self) -> Iterable[np.ndarray]:
        return self._matrices

    def to_ir(self, target: QubitSet):
        return ir.Kraus.construct(
            targets=[qubit for qubit in target],
            matrices=Kraus._transform_matrix_to_ir(self._matrices),
        )

    @staticmethod
    def _transform_matrix_to_ir(matrices: Iterable[np.ndarray]):
        serializable = []
        for matrix in matrices:
            matrix_as_list = [
                [[element.real, element.imag] for element in row] for row in matrix.tolist()
            ]
            serializable.append(matrix_as_list)
        return serializable

    @staticmethod
    @circuit.subroutine(register=True)
    def kraus(
        targets: QubitSetInput, matrices: Iterable[np.array], display_name: str = "KR"
    ) -> Iterable[Instruction]:
        """Registers this function into the circuit class.

        Args:
            targets (Qubit, int, or iterable of Qubit / int): Target qubit(s)
            matrices (Iterable[np.array]): Matrices that define a general noise channel.

        Returns:
            Iterable[Instruction]: `Iterable` of Kraus instructions.

        Examples:
            >>> K0 = np.eye(4) * sqrt(0.9)
            >>> K1 = np.kron([[1., 0.],[0., 1.]], [[0., 1.],[1., 0.]]) * sqrt(0.1)
            >>> circ = Circuit().kraus(0, matrices=[K0, K1])
        """
        if 2 ** len(targets) != matrices[0].shape[0]:
            raise ValueError(
                "Dimensions of the supplied Kraus matrices are incompatible with the targets"
            )

        return Instruction(
            Noise.Kraus(matrices=matrices, display_name=display_name), target=targets
        )


Noise.register_noise(Kraus)
