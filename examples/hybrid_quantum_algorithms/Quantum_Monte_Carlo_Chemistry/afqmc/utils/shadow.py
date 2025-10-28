import copy, os, itertools, random, math
import numpy as np
import pennylane as qml
from numba import jit, njit, guvectorize
from scipy.linalg import det, expm, qr
from typing import cast, Iterable, Sequence, Callable, List, Tuple

'''
This file contains functions to sample classical shadows for performing shadow tomography;
Only matchgate shadow is supported for the moment.
'''

def calculate_classical_shadow(circuit_template, shadow_size, num_qubits):
    """
    Given a circuit template, creates a collection of snapshots consisting of a bit string and the corresponding
    unitary operation.
    Args:
        circuit_template (function): A Pennylane QNode.
        shadow_size (int): The number of snapshots in the shadow.
        num_qubits (int): The number of qubits in the circuit.
    Returns:
        outcomes: measurement statistics, written as a list of lists containing sublists, with the first element
                  being the covariance matrix C, and the second element is the number of shots;
        Q_list: random orthogonal
    """
    # sample random orthogonal matrix from M_n here, it would be straight-forward to generalize;
    Q_list = []
    for _ in range(shadow_size):
        Q_list.append(random_signed_permutation(2*num_qubits))
    
    output = []
    for ns in range(shadow_size):
        # for each snapshot, add a random Clifford circuit
        output.append(circuit_template(Q_list[ns]))
        
    # the data structure has to be changed for better efficiency during postprocessing
    outcomes = []
    for i in output:
        shadow_outcome = []
        for j in list(i.keys()):
            shadow_outcome.append([construct_covariance(j), i.get(j)])
        outcomes.append(shadow_outcome)
        
    return outcomes, Q_list


def construct_covariance(b_str: str):
    '''This function takes in computational basis state b as a string, and output its covariance matrix C,
    computed directly from Eqn.(12) from https://arxiv.org/abs/2207.13723
    Args:
        b_str (str): string of measurement output statistics, e.g., '0000'
    Returns:
        C (np.ndarray): covariance matrix
    '''
    # get the number of fermionic mode
    n = len(b_str)
    C = np.zeros((2*n, 2*n), dtype=np.complex128)
    for i in range(n):
        C[2*i, 2*i+1] = (-1)**int(b_str[i])
        C[2*i+1, 2*i] = -C[2*i, 2*i+1]
        
    return C.astype('complex128')


def random_signed_permutation(size):
    '''Generating size 2n signed permutation matrix Q, from Borel group B(2n).
       This will save matchgate circuit depth compared to Orthogonal group.
    '''
    Q = np.zeros((size, size))
    permutation = np.random.permutation(size)
    sign = np.random.randint(2, size=size)
    
    for i in range(size):
        Q[permutation[i], i] = (-1)**sign[i]
    return Q

