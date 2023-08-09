# general imports
import math

import numpy as np

# AWS imports: Import Braket SDK modules
from braket.circuits import Circuit, circuit


# QFT subroutine without swaps
def qft_no_swap(qubits):
    """
    Subroutine of the QFT excluding the final SWAP gates, applied to the qubits argument.
    Returns the a circuit object.

    Args:
        qubits (int): The list of qubits on which to apply the QFT
    """

    # On a single qubit, the QFT is just a Hadamard.
    if len(qubits) == 1:
        return Circuit().h(qubits)

    # For more than one qubit, we define the QFT recursively (as shown on the right half of the image above):
    else:
        qftcirc = Circuit()

        # First add a Hadamard gate
        qftcirc.h(qubits[0])

        # Then apply the controlled rotations, with weights (angles) defined by the distance to the control qubit.
        for k, qubit in enumerate(qubits[1:]):
            qftcirc.cphaseshift(qubit, qubits[0], 2 * math.pi / (2 ** (k + 2)))

        # Now apply the above gates recursively to the rest of the qubits
        qftcirc.add(qft_no_swap(qubits[1:]))

    return qftcirc


# To complete the full QFT, add swap gates to reverse the order of the qubits
@circuit.subroutine(register=True)
def qft_recursive(qubits):
    """
    Construct a circuit object corresponding to the Quantum Fourier Transform (QFT)
    algorithm, applied to the argument qubits.

    Args:
        qubits (int): The list of qubits on which to apply the QFT
    """
    qftcirc = Circuit()

    # First add the QFT subroutine above
    qftcirc.add(qft_no_swap(qubits))

    # Then add SWAP gates to reverse the order of the qubits:
    for i in range(math.floor(len(qubits) / 2)):
        qftcirc.swap(qubits[i], qubits[-i - 1])

    return qftcirc


# Non-recursive definition of the QFT
def qft(qubits):
    """
    Construct a circuit object corresponding to the Quantum Fourier Transform (QFT)
    algorithm, applied to the argument qubits.  Does not use recursion to generate the QFT.

    Args:
        qubits (int): The list of qubits on which to apply the QFT
    """
    qftcirc = Circuit()

    # get number of qubits
    num_qubits = len(qubits)

    for k in range(num_qubits):
        # First add a Hadamard gate
        qftcirc.h(qubits[k])

        # Then apply the controlled rotations, with weights (angles) defined by the distance to the control qubit.
        # Start on the qubit after qubit k, and iterate until the end.  When num_qubits==1, this loop does not run.
        for j in range(1, num_qubits - k):
            angle = 2 * math.pi / (2 ** (j + 1))
            qftcirc.cphaseshift(qubits[k + j], qubits[k], angle)

    # Then add SWAP gates to reverse the order of the qubits:
    for i in range(math.floor(num_qubits / 2)):
        qftcirc.swap(qubits[i], qubits[-i - 1])

    return qftcirc


# inverse QFT
@circuit.subroutine(register=True)
def inverse_qft(qubits):
    """
    Construct a circuit object corresponding to the inverse Quantum Fourier Transform (QFT)
    algorithm, applied to the argument qubits.  Does not use recursion to generate the circuit.

    Args:
        qubits (int): The list of qubits on which to apply the inverse QFT
    """
    # Instantiate circuit object
    qftcirc = Circuit()

    # Fet number of qubits
    num_qubits = len(qubits)

    # First add SWAP gates to reverse the order of the qubits:
    for i in range(math.floor(num_qubits / 2)):
        qftcirc.swap(qubits[i], qubits[-i - 1])

    # Start on the last qubit and work to the first.
    for k in reversed(range(num_qubits)):

        # Apply the controlled rotations, with weights (angles) defined by the distance to the control qubit.
        # These angles are the negative of the angle used in the QFT.
        # Start on the last qubit and iterate until the qubit after k.
        # When num_qubits==1, this loop does not run.
        for j in reversed(range(1, num_qubits - k)):
            angle = -2 * math.pi / (2 ** (j + 1))
            qftcirc.cphaseshift(qubits[k + j], qubits[k], angle)

        # Then add a Hadamard gate
        qftcirc.h(qubits[k])

    return qftcirc
