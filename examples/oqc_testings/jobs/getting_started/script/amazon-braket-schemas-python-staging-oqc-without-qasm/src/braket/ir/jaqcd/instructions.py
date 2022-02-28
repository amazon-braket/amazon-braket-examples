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

from enum import Enum

from braket.ir.jaqcd.shared_models import (
    Angle,
    CompilerDirective,
    DampingProbability,
    DampingSingleProbability,
    DoubleControl,
    DoubleTarget,
    MultiProbability,
    MultiTarget,
    SingleControl,
    SingleProbability,
    SingleProbability_34,
    SingleProbability_1516,
    SingleTarget,
    TripleProbability,
    TwoDimensionalMatrix,
    TwoDimensionalMatrixList,
)

"""
Instructions that can be supplied to the braket.ir.jaqcd.Program.

To add a new instruction:
    - Implement a class in this module.
      - Class must contain a property, "type", that is an enum of the class implemented in the
        next step.
      - Implement a subclass, "Type", within this class that extends [str, enum].
        All enum values must be unique across all instructions, otherwise de-serialization
        will have undeterministic behaviors. These enums will be used to determine what type
        the instruction is, i.e. what class to use for deserializing.
      - NOTE: Due to how multiple inhertiance works in Python it is easiest to define a
        type enum class within each instruction, instead of calling the relevant parent
        constructors to initialize it correctly.
    - Inherit any classes from braket.ir.jaqcd.shared_models.
    - Write up docstrings to define the instruction, properties, and examples.
"""


class H(SingleTarget):
    """
    Hadamard gate.

    Attributes:
        type (str): The instruction type. default = "h". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> H(target=1)
    """

    class Type(str, Enum):
        h = "h"

    type = Type.h


class I(SingleTarget):  # noqa: E742, E261
    """
    Identity gate.

    Attributes:
        type (str): The instruction type. default = "i". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> I(target=1)
    """

    class Type(str, Enum):
        i = "i"

    type = Type.i


class X(SingleTarget):
    """
    Pauli-X gate.

    Attributes:
        type (str): The instruction type. default = "x". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> X(target=0)
    """

    class Type(str, Enum):
        x = "x"

    type = Type.x


class Y(SingleTarget):
    """
    Pauli-Y gate.

    Attributes:
        type (str): The instruction type. default = "y". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Y(target=0)
    """

    class Type(str, Enum):
        y = "y"

    type = Type.y


class Z(SingleTarget):
    """
    Pauli-Z gate.

    Attributes:
        type (str): The instruction type. default = "z". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Z(target=0)
    """

    class Type(str, Enum):
        z = "z"

    type = Type.z


class Rx(SingleTarget, Angle):
    """
    X-axis rotation gate.

    Attributes:
        type (str): The instruction type. default = "rx". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.

    Examples:
        >>> Rx(target=0, angle=0.15)
    """

    class Type(str, Enum):
        rx = "rx"

    type = Type.rx


class Ry(SingleTarget, Angle):
    """
    Y-axis rotation gate.

    Attributes:
        type (str): The instruction type. default = "ry". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.

    Examples:
        >>> Ry(target=0, angle=0.15)
    """

    class Type(str, Enum):
        ry = "ry"

    type = Type.ry


class Rz(SingleTarget, Angle):
    """
    Z-axis rotation gate.

    Attributes:
        type (str): The instruction type. default = "rz". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.

    Examples:
        >>> Rz(target=0, angle=0.15)
    """

    class Type(str, Enum):
        rz = "rz"

    type = Type.rz


class S(SingleTarget):
    """
    S gate. Applies a 90 degree rotation around the Z-axis.

    Attributes:
        type (str): The instruction type. default = "s". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> S(target=0)
    """

    class Type(str, Enum):
        s = "s"

    type = Type.s


class T(SingleTarget):
    """
    T gate. Applies a 45 degree rotation around the Z-axis.

    Attributes:
        type (str): The instruction type. default = "t". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> T(target=0)
    """

    class Type(str, Enum):
        t = "t"

    type = Type.t


class Si(SingleTarget):
    """
    Si gate. Conjugate transpose of S gate.

    Attributes:
        type (str): The instruction type. default = "si". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Si(target=0)
    """

    class Type(str, Enum):
        si = "si"

    type = Type.si


class Ti(SingleTarget):
    """
    Ti gate. Conjugate transpose of T gate.

    Attributes:
        type (str): The instruction type. default = "ti". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Ti(target=0)
    """

    class Type(str, Enum):
        ti = "ti"

    type = Type.ti


class Swap(DoubleTarget):
    """
    Swap gate. Swaps the state of the two qubits.

    Attributes:
        type (str): The instruction type. default = "swap". (type) is optional.
            This should be unique among all instruction types.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> Swap(targets=[0, 1])
    """

    class Type(str, Enum):
        swap = "swap"

    type = Type.swap


class CSwap(SingleControl, DoubleTarget):
    """
    Controlled swap gate.

    Attributes:
        type (str): The instruction type. default = "cswap". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> Swap(control=0, targets=[1, 2])
    """

    class Type(str, Enum):
        cswap = "cswap"

    type = Type.cswap


class ISwap(DoubleTarget):
    """
    ISwap gate. Swaps the state of two qubits, applying a -i phase to q1 when it is in the 1 state
        and a -i phase to q2 when it is in the 0 state.

    This is equivalent to XY(pi)

    Attributes:
        type (str): The instruction type. default = "iswap". (type) is optional.
            This should be unique among all instruction types.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> ISwap(targets=[0, 1])
    """

    class Type(str, Enum):
        iswap = "iswap"

    type = Type.iswap


class PSwap(DoubleTarget, Angle):
    """
    Parameterized swap gate that takes in the angle of the phase to apply to the swapped gates.

    Attributes:
        type (str): The instruction type. default = "pswap". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> PSwap(targets=[0, 1], angle=0.15)
    """

    class Type(str, Enum):
        pswap = "pswap"

    type = Type.pswap


class XY(DoubleTarget, Angle):
    """
    Rotates between \\|01> and \\|10> by the given angle.

    Attributes:
        type (str): The instruction type. default = "xy". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> XY(targets=[0, 1], angle=0.15)
    """

    class Type(str, Enum):
        xy = "xy"

    type = Type.xy


class PhaseShift(SingleTarget, Angle):
    """
    Phase shift gate. Shifts the phase between \\|0> and \\|1> by a given angle.

    Attributes:
        type (str): The instruction type. default = "phaseshift". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> PhaseShift(target=1, angle=0.15)
    """

    class Type(str, Enum):
        phaseshift = "phaseshift"

    type = Type.phaseshift


class CPhaseShift(SingleTarget, SingleControl, Angle):
    """
    Controlled phase shift gate.

    Attributes:
        type (str): The instruction type. default = "cphaseshift". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CPhaseShift(control=0, target=1, angle=0.15)
    """

    class Type(str, Enum):
        cphaseshift = "cphaseshift"

    type = Type.cphaseshift


class CPhaseShift00(SingleTarget, SingleControl, Angle):
    """
    Controlled phase shift gate that phases the \\|00> state.

    Attributes:
        type (str): The instruction type. default = "cphaseshift00". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CPhaseShift00(control=0, target=1, angle=0.15)
    """

    class Type(str, Enum):
        cphaseshift00 = "cphaseshift00"

    type = Type.cphaseshift00


class CPhaseShift01(SingleTarget, SingleControl, Angle):
    """
    Controlled phase shift gate that phases the \\|01> state.

    Attributes:
        type (str): The instruction type. default = "cphaseshift01". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CPhaseShift01(control=0, target=1, angle=0.15)
    """

    class Type(str, Enum):
        cphaseshift01 = "cphaseshift01"

    type = Type.cphaseshift01


class CPhaseShift10(SingleTarget, SingleControl, Angle):
    """
    Controlled phase shift gate that phases the \\|10> state.

    Attributes:
        type (str): The instruction type. default = "cphaseshift10". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CPhaseShift10(control=0, target=1, angle=0.15)
    """

    class Type(str, Enum):
        cphaseshift10 = "cphaseshift10"

    type = Type.cphaseshift10


class CNot(SingleTarget, SingleControl):
    """
    Controlled not gate. Also known as the CX gate.

    Attributes:
        type (str): The instruction type. default = "cnot". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CNot(control=0, target=1)
    """

    class Type(str, Enum):
        cnot = "cnot"

    type = Type.cnot


class CCNot(SingleTarget, DoubleControl):
    """
    Doubly-controlled NOT gate. Also known as the Toffoli gate.

    Attributes:
        type (str): The instruction type. default = "ccnot". (type) is optional.
            This should be unique among all instruction types.
        controls (int): The control qubits.
            This is a list with two items and all items are int >= 0.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CCNot(control=[0,1], target=1)
    """

    class Type(str, Enum):
        ccnot = "ccnot"

    type = Type.ccnot


class CV(SingleTarget, SingleControl):
    """
    Controlled sqrt(NOT) gate. Also known as the CV gate.

    Attributes:
        type (str): The instruction type. default = "cv". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CV(control=0, target=1)
    """

    class Type(str, Enum):
        cv = "cv"

    type = Type.cv


class CY(SingleTarget, SingleControl):
    """
    Controlled Y-gate.

    Attributes:
        type (str): The instruction type. default = "cy". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CY(control=0, target=1)
    """

    class Type(str, Enum):
        cy = "cy"

    type = Type.cy


class CZ(SingleTarget, SingleControl):
    """
    Controlled Z-gate.

    Attributes:
        type (str): The instruction type. default = "cz". (type) is optional.
            This should be unique among all instruction types.
        control (int): The control qubit. This is an int >= 0.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> CZ(control=0, target=1)
    """

    class Type(str, Enum):
        cz = "cz"

    type = Type.cz


class ECR(DoubleTarget):
    """
    An echoed RZX(pi/2) gate.

    Attributes:
        type (str): The instruction type. default = "ecr". (type) is optional.
            This should be unique among all instruction types.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> ECR(targets=[0, 1])
    """

    class Type(str, Enum):
        ecr = "ecr"

    type = Type.ecr


class XX(DoubleTarget, Angle):
    """
    The Ising (XX) gate.

    Attributes:
        type (str): The instruction type. default = "xx". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> XX(targets=[0, 1], angle=0.15)
    """

    class Type(str, Enum):
        xx = "xx"

    type = Type.xx


class YY(DoubleTarget, Angle):
    """
    The Ising (YY) gate.

    Attributes:
        type (str): The instruction type. default = "yy". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> YY(targets=[0, 1], angle=0.15)
    """

    class Type(str, Enum):
        yy = "yy"

    type = Type.yy


class ZZ(DoubleTarget, Angle):
    """
    The Ising (ZZ) gate.

    Attributes:
        type (str): The instruction type. default = "zz". (type) is optional.
            This should be unique among all instruction types.
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.
        targets (List[int]): The target qubits.
            This is a list with two items and all items are int >= 0.

    Examples:
        >>> ZZ(targets=[0, 1], angle=0.15)
    """

    class Type(str, Enum):
        zz = "zz"

    type = Type.zz


class V(SingleTarget):
    """
    Square root of NOT gate.

    Attributes:
        type (str): The instruction type. default = "v". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> V(target=0)
    """

    class Type(str, Enum):
        v = "v"

    type = Type.v


class Vi(SingleTarget):
    """
    Conjugate transpose of square root of NOT gate.

    Attributes:
        type (str): The instruction type. default = "vi". (type) is optional.
            This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Vi(target=0)
    """

    class Type(str, Enum):
        vi = "vi"

    type = Type.vi


class Unitary(TwoDimensionalMatrix, MultiTarget):
    """
    Arbitrary unitary matrix gate

    Attributes:
        type (str): The instruction type. default = "unitary". (type) is optional.
            This should be unique among all instruction types.
        targets (List[int]): The target qubits. This is a list with ints and all ints >= 0.
        matrix (List[List[List[float]]]): The unitary matrix specifying the behavior of the gate.

    Examples:
        >>> Unitary(targets=[0], matrix=[[[0, 0], [1, 0]],[[1, 0], [0, 1]]])
    """

    class Type(str, Enum):
        unitary = "unitary"

    type = Type.unitary


class BitFlip(SingleTarget, SingleProbability):
    """
    Bit Flip noise channel.

    Attributes:
        type (str): The instruction type. default = "bit_flip". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> BitFlip(target=1, probability=0.1)
    """

    class Type(str, Enum):
        bit_flip = "bit_flip"

    type = Type.bit_flip


class PhaseFlip(SingleTarget, SingleProbability):
    """
    Phase Flip noise channel.

    Attributes:
        type (str): The instruction type. default = "phase_flip". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> PhaseFlip(target=1, probability=0.1)
    """

    class Type(str, Enum):
        phase_flip = "phase_flip"

    type = Type.phase_flip


class PauliChannel(SingleTarget, TripleProbability):
    """
    A single qubit Pauli noise channel.

    Attributes:
        type (str): The instruction type. default = "pauli_channel". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> PauliChannel(target=1, probX=0.1, probY=0.2, probZ=0.3)
    """

    class Type(str, Enum):
        pauli_channel = "pauli_channel"

    type = Type.pauli_channel


class MultiQubitPauliChannel(MultiTarget, MultiProbability):
    """
    Multi-qubit Pauli noise channel.

    Attributes:
        type (str): The instruction type. default = "multi_qubit_pauli_channel". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit(s). This is list of intergers >= 0.
        The length of the list must match the length of the Pauli strings provided.

    Examples:
        >>> MultiQubitPauliChannel(target=1, probabilities={"X": 0.1})
        >>> MultiQubitPauliChannel(target=[0,1], probabilities={"XY": 0.1})
        >>> MultiQubitPauliChannel(target=[0,1,2], probabilities={"XYZ": 0.1})
    """

    class Type(str, Enum):
        multi_qubit_pauli_channel = "multi_qubit_pauli_channel"

    type = Type.multi_qubit_pauli_channel


class Depolarizing(SingleTarget, SingleProbability_34):
    """
    Depolarizing noise channel.

    Attributes:
        type (str): The instruction type. default = "depolarizing". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> Depolarizing(target=1, probability=0.1)
    """

    class Type(str, Enum):
        depolarizing = "depolarizing"

    type = Type.depolarizing


class TwoQubitDepolarizing(DoubleTarget, SingleProbability_1516):
    """
    Two-Qubit Depolarizing noise channel.

    Attributes:
        type (str): The instruction type. default = "two_qubit_depolarizing".
            (type) is optional. This should be unique among all instruction types.
        target (int): The target qubits. This is an int >= 0.

    Examples:
        >>> TwoQubitDepolarizing(target1=0, target2=1, probability=0.1)
    """

    class Type(str, Enum):
        two_qubit_depolarizing = "two_qubit_depolarizing"

    type = Type.two_qubit_depolarizing


class TwoQubitDephasing(DoubleTarget, SingleProbability_34):
    """
    Two-Qubit Dephasing noise channel.

    Attributes:
        type (str): The instruction type. default = "two_qubit_dephasing".
            (type) is optional. This should be unique among all instruction types.
        target (int): The target qubits. This is an int >= 0.

    Examples:
        >>> TwoQubitDephasing(target1=0, target2=1, probability=0.1)
    """

    class Type(str, Enum):
        two_qubit_dephasing = "two_qubit_dephasing"

    type = Type.two_qubit_dephasing


class AmplitudeDamping(SingleTarget, DampingProbability):
    """
    Amplitude Damping noise channel.

    Attributes:
        type (str): The instruction type. default = "amplitude_damping". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> AmplitudeDamping(target=1, gamma=0.1)
    """

    class Type(str, Enum):
        amplitude_damping = "amplitude_damping"

    type = Type.amplitude_damping


class GeneralizedAmplitudeDamping(SingleTarget, DampingProbability, DampingSingleProbability):
    """
    Generalized Amplitude Damping noise channel.

    Attributes:
        type (str): The instruction type. default = "generalized_amplitude_damping". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> GeneralizedAmplitudeDamping(target=1, gamma=0.1, probability=0.9)
    """

    class Type(str, Enum):
        generalized_amplitude_damping = "generalized_amplitude_damping"

    type = Type.generalized_amplitude_damping


class PhaseDamping(SingleTarget, DampingProbability):
    """
    Phase Damping noise channel.

    Attributes:
        type (str): The instruction type. default = "phase_damping". (type) is
            optional. This should be unique among all instruction types.
        target (int): The target qubit. This is an int >= 0.

    Examples:
        >>> PhaseDamping(target=1, gamma=0.1)
    """

    class Type(str, Enum):
        phase_damping = "phase_damping"

    type = Type.phase_damping


class Kraus(TwoDimensionalMatrixList, MultiTarget):
    """
    Arbitrary quantum channel defined by the input matrices.

    Attributes:
        type (str): The instruction type. default = "kraus". (type) is optional.
            This should be unique among all instruction types.
        targets (List[int]): The target qubits. This is a list with ints and all ints >= 0.
        matrices (List[List[List[List[float]]]]): A list of matrices specifying
            the quantum channel. A complex number is represented as a list of 2
            real numbers. So each matrix has type List[List[List[float]]].

    Examples:
        >>> matrix1 = [[[1/sqrt(2), 0],[0, 0]],[[0, 0],[1/sqrt(2), 0]]]
        >>> matrix2 = [[[0, 0],[1/sqrt(2), 0]],[[1/sqrt(2), 0],[0, 0]]]
        >>> matrices = [matrix1, matrix2]
        >>> Kraus(targets=[0], matrices=matrices)
    """

    class Type(str, Enum):
        kraus = "kraus"

    type = Type.kraus


class StartVerbatimBox(CompilerDirective):
    """
    StartVerbatimBox is a compiler instruction to start a portion of code that
    will preserve the instruction within StartVerbatimBox and EndVerbatimBox
    from being modified in any way by the compiler.

    Attributes:
        type (str): The instruction type. default = "start_verbatim_box". (type) is optional.
            This should be unique among all instruction types.

    Examples:
        >>> StartVerbatimBox()
    """

    class Type(str, Enum):
        start_verbatim_box = "start_verbatim_box"

    type = Type.start_verbatim_box

    directive: str = "StartVerbatimBox"


class EndVerbatimBox(CompilerDirective):
    """
    EndVerbatimBox is a compiler instruction to mark the end of a portion of code
    that preserves the instruction within StartVerbatimBox and EndVerbatimBox
    from being  modified in any way by the compiler.

    Attributes:
        type (str): The instruction type. default = "end_verbatim_box". (type) is optional.
            This should be unique among all instruction types.

    Examples:
        >>> EndVerbatimBox()
    """

    class Type(str, Enum):
        end_verbatim_box = "end_verbatim_box"

    type = Type.end_verbatim_box

    directive: str = "EndVerbatimBox"
