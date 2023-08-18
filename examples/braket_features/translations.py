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

CIRQ_NOISE_GATES = {
    "bit_flip": bit_flip,
    "phase_flip": PhaseFlipChannel,
    "depolarizing": DepolarizingChannel,
    "amplitude_damping": AmplitudeDampingChannel,
    "generalized_amplitude_damping": GeneralizedAmplitudeDampingChannel,
    "phase_damping": PhaseDampingChannel,
}


def get_cirq_qubits(qubits: Tuple[int]):
    return [cirq.LineQubit(int(qubit)) for qubit in qubits]
