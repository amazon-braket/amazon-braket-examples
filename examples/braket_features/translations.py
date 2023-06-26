from functools import singledispatch
from typing import Tuple

import cirq
from cirq import (
    bit_flip,
    PhaseFlipChannel,
    DepolarizingChannel,
    AmplitudeDampingChannel,
    GeneralizedAmplitudeDampingChannel,
    PhaseDampingChannel,
)

from braket.default_simulator.noise_operations import (
    BitFlip,
    PhaseFlip,
    GeneralizedAmplitudeDamping,
    PhaseDamping,
    AmplitudeDamping,
    Depolarizing,
)

# cirq.XX, cirq.YY, and cirq.ZZ gates are not the same as Braket gates
CIRQ_GATES = {
    "i": cirq.I,
    "h": cirq.H,
    "x": cirq.X,
    "y": cirq.Y,
    "z": cirq.Z,
    "cnot": cirq.CNOT,
    "cz": cirq.CZ,
    "s": cirq.S,
    "t": cirq.T,
    "cphaseshift": cirq.cphase,
    "rx": cirq.rx,
    "ry": cirq.ry,
    "rz": cirq.rz,
    "swap": cirq.SWAP,
    "iswap": cirq.ISWAP,
    "ccnot": cirq.CCNOT,
    "cswap": cirq.CSWAP,
    "ccz": cirq.CCZ,
    "ccx": cirq.CCX,
    "measure": cirq.MeasurementGate,
}


def get_cirq_qubits(qubits: Tuple[int]):
    return [cirq.LineQubit(int(qubit)) for qubit in qubits]


@singledispatch
def cirq_gate_to_instruction(noise):
    raise TypeError(f"Operation {type(noise).__name__} not supported")


@cirq_gate_to_instruction.register(BitFlip)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return bit_flip(noise.probability).on(*qubits)


@cirq_gate_to_instruction.register(PhaseFlip)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return PhaseFlipChannel(noise.probability).on(*qubits)


@cirq_gate_to_instruction.register(Depolarizing)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return DepolarizingChannel(noise.probability).on(*qubits)


@cirq_gate_to_instruction.register(AmplitudeDamping)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return AmplitudeDampingChannel(noise.gamma).on(*qubits)


@cirq_gate_to_instruction.register(GeneralizedAmplitudeDamping)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return GeneralizedAmplitudeDampingChannel(noise.probability, noise.gamma).on(
        *qubits
    )


@cirq_gate_to_instruction.register(PhaseDamping)
def _(noise):
    qubits = get_cirq_qubits(noise.targets)
    return PhaseDampingChannel(noise.gamma).on(*qubits)
