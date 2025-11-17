import numpy as np
import pennylane as qml
from typing import Callable, List, Tuple
from scipy.linalg import null_space
from afqmc.utils.linalg import reortho
from openfermion.linalg.givens_rotations import givens_decomposition_square

#----------------------------------------------------------------------------------
# The following are miscellaneous functions wrt circuit construction and execution

def givens_block_circuit(givens: Tuple):
    """This function defines the Givens rotation circuit from a single givens tuple
    Args:
        givens: (i, j, \theta, \varphi)
    """
    (i, j, theta, varphi) = givens

    qml.RZ(-varphi, wires=j)
    qml.CNOT(wires=[j, i])

    # implement the cry rotation
    qml.RY(theta, wires=j)
    qml.CNOT(wires=[i, j])
    qml.RY(-theta, wires=j)
    qml.CNOT(wires=[i, j])

    qml.CNOT(wires=[j, i])


def prepare_slater_circuit(circuit_description: Tuple):
    """Creating Givens rotation circuit to prepare arbitrary Slater determinant.
    Args:
        circuit_description (List[Tuple]): list of tuples containing Givens rotation
        (i, j, theta, phi) in reversed order.
    """
    for parallel_ops in circuit_description:
        for givens in parallel_ops:
            qml.adjoint(givens_block_circuit)(givens)


def construct_slater(walker):
    """Construct the circuit to prepare a Slater determinant
    Args:
        walker (np.ndarray): orthonormalized walker state
    """
    num_qubits, num_particles = walker.shape
    for i in range(num_particles):
        qml.PauliX(wires=i)
        
    complement = null_space(walker.T)
    W, _ = reortho(np.hstack((walker, complement)))
    
    decomposition, diagonal = givens_decomposition_square(W.T)
    circuit_description = list(reversed(decomposition))
    
    for i in range(len(diagonal)):
        qml.RZ(np.angle(diagonal[i]), wires=i)
        
    prepare_slater_circuit(circuit_description)            
            
            
def circuit_first_half(phi: np.ndarray):
    """Construct the first half of the vacuum reference circuit
    Args:
        phi (np.ndarray): orthonormalized walker state
    """
    num_qubits, num_particles = phi.shape
    qml.Hadamard(wires=0)

    if num_particles > 1.0:
        for i in range(1, num_particles):
            qml.CNOT(wires=[0, i])
            
    complement = null_space(phi.T)
    W, _ = reortho(np.hstack((phi, complement)))
    decomposition, diagonal = givens_decomposition_square(W.T)
    circuit_description = list(reversed(decomposition))

    for i in range(len(diagonal)):
        qml.RZ(np.angle(diagonal[i]), wires=i)

    prepare_slater_circuit(circuit_description)


def circuit_second_half_real(phi: np.ndarray, q_trial: Callable):
    """Construct the second half of the vacuum reference circuit (for real expectation values)
    Args:
        phi (np.ndarray): orthonormalized walker state
        q_trial (function): quantum trial circuit from Pennylane
    """
    num_qubits, num_particles = phi.shape
    qml.adjoint(q_trial)()
    
    if num_particles > 1.0:
        for i in range(1, num_particles)[::-1]:
            qml.CNOT(wires=[0, i])
    qml.Hadamard(wires=0)


def circuit_second_half_imag(phi: np.ndarray, q_trial: Callable):
    """Construct the second half of the vacuum reference circuit (for imaginary expectation values)
    Args:
        Q (np.ndarray): orthonormalized walker state
        q_trial (function): quantum trial state
    """
    num_qubits, num_particles = phi.shape
    qml.adjoint(q_trial)()

    if num_particles > 1.0:
        for i in range(1, num_particles)[::-1]:
            qml.CNOT(wires=[0, i])

    qml.S(wires=0)
    qml.S(wires=0)
    qml.S(wires=0)
    qml.Hadamard(wires=0)


def amplitude_real(phi: np.ndarray, q_trial: Callable):
    """Construct the the vacuum reference circuit for measuring amplitude real part
    Args:
        phi (np.ndarray): orthonormalized walker state
        q_trial (function): quantum trial state
    """
    circuit_first_half(phi)
    circuit_second_half_real(phi, q_trial)


def amplitude_imag(phi: np.ndarray, q_trial: Callable):
    """Construct the the vacuum reference circuit for measuring amplitude imaginary part
    Args:
        phi (np.ndarray): orthonormalized walker state
        q_trial (function): quantum trial state
    """
    circuit_first_half(phi)
    circuit_second_half_imag(phi, q_trial)


def amplitude_estimate(phi: np.ndarray, q_trial: Callable, dev: str):
    """This function computes the amplitude between walker state and quantum trial state.
    Args:
        phi (np.ndarray): orthonormalized walker state
        q_trial (function): quantum trial state
        dev (str): 'lightning.qubit' for simulator
    Returns:
        amplitude: np.complex128
    """
    num_qubits, num_particles = phi.shape
    
    device = qml.device(dev, wires=num_qubits)
    @qml.qnode(device, interface=None, diff_method=None)
    def compute_real(phi, q_trial):
        amplitude_real(phi, q_trial)
        return qml.probs(range(num_qubits))

    probs_values = compute_real(phi, q_trial)
    real = probs_values[0] - probs_values[int(2**num_qubits / 2)]

    @qml.qnode(device, interface=None, diff_method=None)
    def compute_imag(phi, q_trial):
        amplitude_imag(phi, q_trial)
        return qml.probs(range(num_qubits))

    probs_values = compute_imag(phi, q_trial)
    imag = probs_values[0] - probs_values[int(2**num_qubits / 2)]

    return real + 1.0j * imag


def U_circuit(U: np.ndarray):
    """Construct circuit to perform unitary transformation U."""

    decomposition, diagonal = givens_decomposition_square(U)
    circuit_description = list(reversed(decomposition))

    for i in range(len(diagonal)):
        qml.RZ(np.angle(diagonal[i]), i)

    if circuit_description != []:
        prepare_slater_circuit(circuit_description)


def pauli_real(phi: np.ndarray, q_trial: Callable, U: np.ndarray, pauli: List[int]):
    """Construct the the vacuum reference circuit for measuring expectation value of a pauli real part
    Args:
        phi: orthonormalized walker state
        q_trial: quantum trial state
        U: unitary transformation to change the Pauli into Z basis
        pauli: list that stores the position of the Z gate, e.g., [0,1] represents 'ZZII'.
    """
    circuit_first_half(phi)

    U_circuit(U)
    for i in pauli:
        qml.PauliZ(wires=i)

    qml.adjoint(U_circuit)(U)
    circuit_second_half_real(phi, q_trial)

    
def pauli_imag(phi: np.ndarray, q_trial: Callable, U: np.ndarray, pauli: List[int]):
    """Construct the the vacuum reference circuit for measuring expectation value of a pauli imaginary part
    Args:
        Q: orthonormalized walker state
        V_T: quantum trial state
        U: unitary transformation to change the Pauli into Z basis
        pauli: list that stores the position of the Z gate, e.g., [0,1] represents 'ZZII'.
    """
    circuit_first_half(phi)

    U_circuit(U)
    for i in pauli:
        qml.PauliZ(wires=i)

    qml.adjoint(U_circuit)(U)
    circuit_second_half_imag(phi, q_trial)

    
def pauli_estimate(phi: np.ndarray, q_trial: Callable, U: np.ndarray, pauli: List[int], dev: str):    
    """This function returns the expectation value of $\\langle \\Psi_Q|pauli|\\phi_l\rangle$.
    Args:
        phi: np.ndarray; matrix representation of the walker state, not necessarily orthonormalized.
        q_trial: circuit unitary to prepare the quantum trial state
        U: eigenvector of Cholesky vectors, $L = U \\lambda U^{\\dagger}$
        pauli: list of 0 and 1 as the representation of a Pauli string, e.g., [0,1] represents 'ZZII'.
        dev: 'lightning.qubit' for simulator;

    Returns:
        expectation value
    """
    num_qubits, num_particles = phi.shape
    
    device = qml.device(dev, wires=num_qubits)
    @qml.qnode(device, interface=None, diff_method=None)
    def compute_real(phi, q_trial, U, pauli):
        pauli_real(phi, q_trial, U, pauli)
        return qml.probs(range(num_qubits))

    probs_values = compute_real(phi, q_trial, U, pauli)
    real = probs_values[0] - probs_values[int(2**num_qubits / 2)]

    @qml.qnode(device, interface=None, diff_method=None)
    def compute_imag(phi, q_trial, U, pauli):
        pauli_imag(phi, q_trial, U, pauli)
        return qml.probs(range(num_qubits))

    probs_values = compute_imag(phi, q_trial, U, pauli)
    imag = probs_values[0] - probs_values[int(2**num_qubits / 2)]

    return real + 1.0j * imag


def pauli_expect(initial_state: list, q_trial: Callable, U: np.ndarray, pauli: List[int], dev: str):
    '''This function computes the pauli expectation value $<\Psi_Q|U^+ v U|\Psi_Q>$
    Args:
        initial_state: Hartree-Fock state by default
        q_trial: quantum trial state
        U: eigenvector of Cholesky vectors, $L = U \\lambda U^{\\dagger}$
        pauli: list of 0 and 1 as the representation of a Pauli string, e.g., [0,1] represents 'ZZII'.
    Returns:
        expectation
    '''
    num_qubits = U.shape[1]
    device = qml.device(dev, wires=num_qubits)
    @qml.qnode(device, interface=None, diff_method=None)
    def compute_expectation(initial_state, q_trial, U, pauli):
        for i in initial_state:
            qml.PauliX(wires=i)
        q_trial()
        U_circuit(U)
        if len(pauli) == 1:
            return qml.expval(qml.PauliZ(pauli[0]))
        elif len(pauli) == 2:
            return qml.expval(qml.PauliZ(pauli[0]) @ qml.PauliZ(pauli[1]))
        else:
            raise Exception("Not implemented error.")
    
    expectation = compute_expectation(initial_state, q_trial, U, pauli)
    return expectation