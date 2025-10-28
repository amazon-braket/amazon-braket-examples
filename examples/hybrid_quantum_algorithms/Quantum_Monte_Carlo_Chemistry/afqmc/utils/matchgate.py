import copy, os, itertools, math
import numpy as np
import pennylane as qml
from numba import jit, njit
from scipy.special import comb
from scipy.linalg import det, expm, qr
from typing import cast, Iterable, Sequence, Callable, List, Tuple
from openfermion.linalg.givens_rotations import (
    givens_rotate,
    givens_matrix_elements,
    givens_decomposition_square,
    fermionic_gaussian_decomposition,
)
from afqmc.utils.shadow import construct_covariance
from afqmc.utils.linalg import reortho, pfaffian_LTL, fit_poly

'''
This file contains functions to compute overlap integrals from matchgate shadows
'''
def ovlp_reconstruction(b_lists, Q_list, comb_coeffs, phi_state, num_fit=8):
    """Reconstruct overlap approximation as an average over all shadows.
    Args:
        b_lists:
        Q_list:
        comb_coeffs:
        phi_state (np.ndarray): walker state
        num_fit:
    Returns:
        ovlp (np.complex128): overlap integral reconstructed from matchgate shadows.
    """
    num_qubits, num_particles = phi_state.shape
    dim = int(num_qubits - num_particles//2)
    prefactor = 1.j**(num_particles//2) / (2**(num_qubits - num_particles//2))
    
    # create necessary quantities for postprocessing
    C_0 = construct_covariance('0'*num_qubits)
    W = construct_W(num_qubits, num_particles)
    Q_tilde = construct_Q_tilde(phi_state)
    
    M1 = np.delete(C_0, [2*i for i in range(num_particles)], 0)
    M1 = np.delete(M1, [2*i for i in range(num_particles)], 1)
    
    # first create all the M1, M2s from b_lists and Q_list
    M2s = []
    for b_list, Q in zip(b_lists, Q_list):
        Q = Q.astype('complex128')
        for b_state in b_list:
            COMP = ma_mul(Q, Q_tilde, W, b_state[0])
            M2s.append(COMP)
            
    M2s = np.stack(M2s, axis=0)
    M2s = np.delete(M2s, [2*i for i in range(num_particles)], 1)
    M2s = np.delete(M2s, [2*i for i in range(num_particles)], 2)
    
    # next create all matrices necessary to interpolate and stack them
    z_list = np.linspace(0., 1., num_fit)
    M = m_pf_generator(M1, M2s, z_list)
    
    # then perform the vectorized pfaffian calculations
    pfaffian_list = pfaffian_LTL(M)
    
    b_flattened = [i for j in b_lists for i in j]
    z_list = z_list.astype('complex128')
    
    # generate the coeffs by fitting the data
    ovlp_list = np.zeros(len(b_flattened), dtype=np.complex128)
    denom_list = np.zeros(len(b_flattened))
    for i, b_state in enumerate(b_flattened):
        pf_coeffs = fit_poly(z_list, pfaffian_list[i*num_fit:(i+1)*num_fit], deg=dim)
        ovlp_list[i] = pf_coeffs @ comb_coeffs
        denom_list[i] = b_state[1]
    
    ovlp_mean = np.average(ovlp_list, weights=denom_list, axis=0)
    return 2 * prefactor * ovlp_mean



def ovlp_reconstruction_robust(b_lists, Q_list, comb_coeffs, comb_coeffs_robust, phi_state, num_fit=8):
    """Reconstruct overlap approximation as an average over all shadows.
    Args:
        shadow (tuple): A shadow tuple obtained from `calculate_classical_shadow`.
        phi_state (np.ndarray): walker state
        comb_coeffs:
        num_fit:
    Returns:
        ovlp (np.complex128): overlap integral reconstructed from matchgate shadows.
    """
    num_qubits, num_particles = phi_state.shape
    dim = int(num_qubits - num_particles//2)
    prefactor = 1.j**(num_particles//2) / (2**(num_qubits - num_particles//2))
    
    # create necessary quantities for postprocessing
    C_0 = construct_covariance('0'*num_qubits)
    W = construct_W(num_qubits, num_particles)
    Q_tilde = construct_Q_tilde(phi_state)
    
    M1 = np.delete(C_0, [2*i for i in range(num_particles)], 0)
    M1 = np.delete(M1, [2*i for i in range(num_particles)], 1)
    
    # first create all the M1, M2s from b_lists and Q_list
    M2s = []
    for b_list, Q in zip(b_lists, Q_list):
        Q = Q.astype('complex128')
        for b_state in b_list:
            COMP = ma_mul(Q, Q_tilde, W, b_state[0])
            M2s.append(COMP)
            
    M2s = np.stack(M2s, axis=0)
    M2s = np.delete(M2s, [2*i for i in range(num_particles)], 1)
    M2s = np.delete(M2s, [2*i for i in range(num_particles)], 2)
    
    # next create all matrices necessary to interpolate and stack them
    z_list = np.linspace(0., 1., num_fit)
    M = m_pf_generator(M1, M2s, z_list)
    
    # then perform the vectorized pfaffian calculations, len should be 20*\sum_{shadow} outcome
    pfaffian_list = pfaffian_LTL(M)
    
    b_flattened = [i for j in b_lists for i in j]
    z_list = z_list.astype('complex128')
    
    # generate the coeffs by fitting the data
    ovlp_list = np.zeros(len(b_flattened), dtype=np.complex128)
    ovlp_robust_list = np.zeros(len(b_flattened), dtype=np.complex128)
    denom_list = np.zeros(len(b_flattened))
    for i, b_state in enumerate(b_flattened):
        pf_coeffs = fit_poly(z_list, pfaffian_list[i*num_fit:(i+1)*num_fit], deg=dim)
        ovlp_list[i] = pf_coeffs @ comb_coeffs
        ovlp_robust_list[i] = pf_coeffs @ comb_coeffs_robust
        denom_list[i] = b_state[1]
    
    ovlp_mean = np.average(ovlp_list, weights=denom_list, axis=0)
    ovlp_robust_mean = np.average(ovlp_robust_list, weights=denom_list, axis=0)
    return 2*prefactor*ovlp_mean, 2*prefactor*ovlp_robust_mean

    
"""
Next we define a series of help functions for post-processing the matchgate shadows
"""

def construct_Q_tilde(phi_state):
    '''This function constructs the \tilde{Q} matrix according to Eqn.(15) from https://arxiv.org/abs/2207.13723.
    Args:
        phi_state (np.ndarray)
    Returns:
        Q_tilde (np.ndarray)
    '''
    num_qubits, num_particles = phi_state.shape
    
    # construct a unitary matrix V from phi
    complement = np.random.rand(num_qubits, num_qubits-num_particles)
    V, _ = reortho(np.hstack((phi_state, complement)))
    
    Q_tilde = np.zeros((2*num_qubits, 2*num_qubits), dtype=np.complex128)
    for i in range(num_qubits):
        for j in range(num_qubits):
            Q_tilde[2*i, 2*j] = np.real(V[i,j])
            Q_tilde[2*i+1, 2*j+1] = np.real(V[i,j])
            Q_tilde[2*i, 2*j+1] = -np.imag(V[i,j])
            Q_tilde[2*i+1, 2*j] = np.imag(V[i,j])
            
    return Q_tilde


def construct_W(nmode, nelec):
    '''This function constructs the W matrix according to Eqn.(42) from https://arxiv.org/abs/2207.13723
    Args:
        nmode: number of fermionic modes
        nelec: number of electrons
    Returns:
        W: np.ndarray
    '''
    W = np.zeros((2*nmode, 2*nmode), dtype=np.complex128)
    for i in range(nelec):
        W[2*i,2*i] = 1/np.sqrt(2)
        W[2*i+1,2*i] = 1/np.sqrt(2)
        W[2*i,2*i+1] = -1.j/np.sqrt(2)
        W[2*i+1,2*i+1] = 1.j/np.sqrt(2)
    for i in range(nelec, nmode):
        W[2*i,2*i] = 1
        W[2*i+1,2*i+1] = 1
        
    return W


@jit(nopython=True)
def m_pf_generator(M1, M2s, z_list):
    M = np.zeros((len(M2s)*len(z_list), M1.shape[0], M1.shape[1]), dtype=np.complex128)
    for i, M2 in enumerate(M2s):
        for j, z in enumerate(z_list):
            M[i*len(z_list)+j,:,:] = M1 + z*M2
    return M


@jit('complex128[:,:](complex128[:,:], complex128[:,:], complex128[:,:], complex128[:,:])', nopython=True)
def ma_mul(Q, Q_tilde, W, b_cov):
    COMP = W.conj() @ Q_tilde.T @ Q.T @ b_cov @ Q @ Q_tilde @ W.conj().T
    return COMP

"""
The code here allows for compiling Cirq circuits of general fermionic
Gaussian unitaries, using their O(2n)-matrix representation.
Adapted from OpenFermion's optimal_givens_decomposition to the context of
general Gaussian transformations. Assumes Jordan-Wigner mapping; specifically,
for p \in {0, ..., n-1},
\gamma_{2p} = a_p + a_p^\dagger = X_p \prod_{q < p} Z_q,
\gamma_{2p+1} = -i(a_p - a_p^\dagger) = Y_p \prod_{q < p} Z_q.
The routine here simplifies the general fermionic Gaussian unitary
construction of Phys. Rev. Appl. 9, 044036 (2018), namely by implementing any
O(2n) transformation, rather than requiring additional circuitry on top of
the state-preparation algorithm.

Note from OpenFermion:
A routine for constructing a circuit to exactly implement a unitary generated by
one-body rotations through the optimal Givens rotation network.  Construction
of this circuit can be found in Optica Vol. 3, Issue 12, pp. 1460-1465 (2016).
This Givens network improves upon the parallel Givens network for implementing
basis rotations in Phys. Rev. Lett. 120, 110501 (2018).
"""

class GivensTranspositionError(Exception):
    pass

class GivensMatrixError(Exception):
    pass      


def gaussian_givens_decomposition(orthogonal_matrix: np.ndarray):
    r"""
    Implement a circuit that provides the unitary that is generated by
    quadratic fermion generators
    .. math::
        U(Q) = exp(-(1/4) [log(Q)]_{j,k} \gamma_j \gamma_k).
    This can be used for implementing an exact fermionic Gaussian unitary from
    any orthogonal 2n x 2n matrix Q.
    Args:
        qubits: Sequence of qubits to apply the operations over.  The qubits
                should be ordered in linear physical order.
        orthogonal_matrix: 2n x 2n orthogonal matrix which defines the linear
                           transformation,
    .. math::
        U(Q)^\dagger \gamma_j U(Q) = \sum_{k=0}^{2n-1} Q_{j,k} \gamma_k.
    """
    N = orthogonal_matrix.shape[0]
    assert N % 2 == 0
    
    current_matrix = np.copy(orthogonal_matrix)
    right_rotations = []
    left_rotations = []
    for i in range(1, N):
        if i % 2 == 1:
            for j in range(0, i):
                # eliminate U[N - j, i - j] by mixing U[N - j, i - j],
                # U[N - j, i - j - 1] by right multiplication
                # of a givens rotation matrix in column [i - j, i - j + 1]
                gmat = givens_matrix_elements(current_matrix[N - j - 1,
                                                             i - j - 1],
                                              current_matrix[N - j - 1,
                                                             i - j - 1 + 1],
                                              which='left')
                right_rotations.append((gmat.T, (i - j - 1, i - j)))
                givens_rotate(current_matrix,
                              gmat.conj(),
                              i - j - 1,
                              i - j,
                              which='col')
        else:
            for j in range(1, i + 1):
                # elimination of U[N + j - i, j] by mixing U[N + j - i, j] and
                # U[N + j - i - 1, j] by left multiplication
                # of a givens rotation that rotates row space
                # [N + j - i - 1, N + j - i
                gmat = givens_matrix_elements(current_matrix[N + j - i - 1 - 1,
                                                             j - 1],
                                              current_matrix[N + j - i - 1,
                                                             j - 1],
                                              which='right')
                left_rotations.append((gmat, (N + j - i - 2, N + j - i - 1)))
                givens_rotate(current_matrix,
                              gmat,
                              N + j - i - 2,
                              N + j - i - 1,
                              which='row')

    new_left_rotations = []
    for (left_gmat, (i, j)) in reversed(left_rotations):
        phase_matrix = np.diag([current_matrix[i, i], current_matrix[j, j]])
        matrix_to_decompose = left_gmat.conj().T.dot(phase_matrix)
        new_givens_matrix = givens_matrix_elements(matrix_to_decompose[1, 0],
                                                   matrix_to_decompose[1, 1],
                                                   which='left')
        new_phase_matrix = matrix_to_decompose.dot(new_givens_matrix.T)

        # check if T_{m,n}^{-1}D  = D T.
        # coverage: ignore
        if not np.allclose(new_phase_matrix.dot(new_givens_matrix.conj()),
                           matrix_to_decompose):
            raise GivensTranspositionError("Failed to shift the phase matrix "
                                           "from right to left")
        # coverage: ignore

        current_matrix[i, i], current_matrix[j, j] = (new_phase_matrix[0, 0],
                                                      new_phase_matrix[1, 1])
        new_left_rotations.append((new_givens_matrix.conj(), (i, j)))

    phases = np.diag(current_matrix)
    rotations = []
    ordered_rotations = []
    for (gmat, (i, j)) in list(reversed(new_left_rotations)) + list(
            map(lambda x: (x[0].conj().T, x[1]), reversed(right_rotations))):
        ordered_rotations.append((gmat, (i, j)))
        
        theta = np.arcsin(np.real(gmat[1, 0]))
        rotations.append((i, j, -theta))     # change into Kianna's convention
    
    for op in reversed(rotations):
        i, j, theta = cast(Tuple[int, int, float], op)
        if not np.isclose(theta, 0.0):
            if i % 2 == 0:
                qml.RZ(theta, wires=i//2)
            else:
                p = (i - 1) // 2
                qml.IsingXX(theta, wires=[p, p+1])
    
    # final layer of Pauli gates to implement phases, which must be \pm 1 since
    # orthogonal matrices are real
    # we use the F_2n/stabilizer representation of Pauli operators here
    final_pauli_gate = np.zeros(N)
    n = N // 2
    for p in range(n):
        if np.isclose(phases[2*p], phases[2*p + 1]):
            if np.isclose(phases[2*p], -1.0):
                final_pauli_gate[p + n] += 1
        else:
            final_pauli_gate[p] += 1
            if np.isclose(phases[2*p], 1.0):
                for q in range(p + 1, n):
                    final_pauli_gate[q + n] += 1
            else:
                for q in range(p, n):
                    final_pauli_gate[q + n] += 1
    
    for p in range(n):
        if final_pauli_gate[p] % 2 == 0 and final_pauli_gate[p + n] % 2 == 1:
            qml.PauliZ(wires=p)
        elif final_pauli_gate[p] % 2 == 1 and final_pauli_gate[p + n] % 2 == 0:
            qml.PauliX(wires=p)
        elif final_pauli_gate[p] % 2 == 1 and final_pauli_gate[p + n] % 2 == 1:
            qml.PauliY(wires=p)