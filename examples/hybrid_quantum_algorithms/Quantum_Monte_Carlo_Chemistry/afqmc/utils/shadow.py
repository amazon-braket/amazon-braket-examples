import random
import numpy as np
import pennylane as qml


'''
This file contains functions to sample classical shadows for performing shadow tomography
'''

def calculate_classical_shadow(circuit_template, Q_list):
    """
    Given a circuit template, creates a collection of snapshots consisting of a bit string and the corresponding
    unitary operation. 
    *Note that although this function could fit for a real QPU on Braket, it's recommended for simulator use only.
    Args:
        circuit_template (function): a Pennylane QNode.
        shadow_size (int): number of snapshots in the shadow.
        num_qubits (int): number of qubits in the circuit.
    Returns:
        outcomes: measurement statistics, written as a list of lists containing sublists, with the first element
                  being the covariance matrix C, and the second element is the number of shots;
        Q_list: random orthogonal
    """
    shadow_size = len(Q_list)
    output = []
    for ns in range(shadow_size):
        output.append(circuit_template(Q_list[ns]))
        
    # the data structure might be changed for better efficiency during postprocessing
    outcomes = []
    for i in output:
        shadow_outcome = []
        for j in list(i.keys()):
            shadow_outcome.append([construct_covariance(j), i.get(j)])
        outcomes.append(shadow_outcome)
        
    return outcomes


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

