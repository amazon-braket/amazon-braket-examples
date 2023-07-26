import numpy as np
from braket.circuits import Circuit


def phase_estimation_circuit(n_qubits: int, phase: float) -> Circuit:
    """Phase estimation circuit.

    Args:
        n_qubits (int): Number of total qubits in the circuit.
        phase (float): Phase in radians.

    Returns:
        Circuit: Circuit for phase estimation.
    """
    n_precision_qubits = n_qubits - 1

    q_precision = range(n_precision_qubits)
    q_query = [n_precision_qubits]

    circ = Circuit()
    circ.h(q_precision)
    circ.x(q_query)

    for i, qubit in enumerate(reversed(q_precision)):
        circ.add(_custom_control_phase(qubit, q_query, phase * 2**i))

    iqft_circuit = _inverse_quantum_fourier_transform_circuit(n_precision_qubits)
    circ.add(iqft_circuit)

    return circ


def _custom_control_phase(control: int, target: int, angle: float) -> Circuit:
    """Custom control phase shift using CNots and Rz rotations.

    Args:
        control (int): Control qubit
        target (int): Target qubit
        angle (float): Angle of controlled-phaseshift.

    Returns:
        Circuit: Circuit for control phase shift.
    """
    circuit = Circuit()
    circuit.rz(control, angle / 2).cnot(control, target)
    circuit.rz(target, -angle / 2).cnot(control, target).rz(target, angle / 2)
    return circuit


def _inverse_quantum_fourier_transform_circuit(n_qubits: int) -> Circuit:
    """Inverse quanutm Fourier transform (iQFT).

    Args:
        n_qubits (int): Number of qubits.

    Returns:
        Circuit: inverse QFT circuit.
    """
    qft_circ = Circuit()
    qubits = list(range(n_qubits))

    for i in range(n_qubits // 2):
        qft_circ.swap(qubits[i], qubits[-i - 1])

    for k in reversed(range(n_qubits)):
        for j in reversed(range(1, n_qubits - k)):
            angle = -2 * np.pi / (2 ** (j + 1))
            qft_circ.add(_custom_control_phase(qubits[k + j], qubits[k], angle))

        qft_circ.h(qubits[k])

    return qft_circ
