import numpy as np
from braket.circuits import Circuit


def phase_estimation_circuit(n_precision_qubits: int, target_phase_in_resolution: int) -> Circuit:
    """Phase estimation circuit. The circuit has 1 query qubit and `n_precision_qubits`
    precision qubits. The resolution of phase estimation is `(1/2**n_precision_qubits)*2*pi`.
    The circuit has `n_precision_qubits+1` qubits. To make benchmark easier, the target phase
    is integer multiple of the phase resolution, `(fraction/2**n_precision_qubits)*2*pi`.
    For example, if `n_precision_qubits=3` and `fraction=3`, the target phase is `(3/8)*2*pi`.

    Args:
        n_precision_qubits (int): Number of precision qubits.
        target_phase_in_resolution (int): Number of fraction, (1/2**n_precision_qubits)*2*pi.
            The oracle phase is (fraction/2**n_precision_qubits)*2*pi.
    """
    q_precision = range(n_precision_qubits)
    q_query = [n_precision_qubits]

    circ = Circuit()
    circ.h(q_precision)
    circ.x(q_query)

    theta = 2 * np.pi * (target_phase_in_resolution / 2 ** len(q_precision))
    for ii, qubit in enumerate(reversed(q_precision)):
        circ.add(_custom_control_phase(qubit, q_query, theta * 2**ii))

    qft_circuit = _inverse_quantum_fourier_transform_circuit(len(q_precision))
    circ.add(qft_circuit)

    return circ


def _custom_control_phase(control: int, target: int, angle: float) -> Circuit:
    """Custom decomposition of cphaseshift gate into CNot and Rz gates.

    Args:
        control (int): control qubit
        target (int): target qubit
        angle (float): angle of controlled-phaseshift
    """
    circuit = Circuit()
    circuit.rz(control, angle / 2).cnot(control, target)
    circuit.rz(target, -angle / 2).cnot(control, target).rz(target, angle / 2)
    return circuit


def _inverse_quantum_fourier_transform_circuit(num_qubits: int) -> Circuit:
    """Construct a circuit object implementing the inverse Quantum Fourier Transform (QFT)
    algorithm, applied to the argument qubits. Does not use recursion to generate the circuit.

    Args:
        num_qubits (int): number of qubits on which to apply the inverse QFT
    """
    qft_circ = Circuit()
    qubits = list(range(num_qubits))

    for i in range(num_qubits // 2):
        qft_circ.swap(qubits[i], qubits[-i - 1])

    for k in reversed(range(num_qubits)):
        for j in reversed(range(1, num_qubits - k)):
            angle = -2 * np.pi / (2 ** (j + 1))
            qft_circ.add(_custom_control_phase(qubits[k + j], qubits[k], angle))

        qft_circ.h(qubits[k])

    return qft_circ
