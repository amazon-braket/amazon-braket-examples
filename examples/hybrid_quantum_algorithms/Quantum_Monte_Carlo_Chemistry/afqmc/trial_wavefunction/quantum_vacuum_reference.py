import copy
import numpy as np
import pennylane as qml
from typing import List
from afqmc.utils.chemical_preparation import ChemicalProperties
from afqmc.utils.quantum import amplitude_estimate, pauli_expect, pauli_estimate


class QTrial:
    def __init__(self, prop: ChemicalProperties, initial_state: List, ansatz_circuit, dev="lightning.qubit"):
        '''This class defines the quantum trial wavefunction.
        Args:
            prop: ChemicalProperties dataclass
            initial_state: the initial occupied orbitals as a list
            ansatz_circuit: pennylane circuit
            dev: only support for simulators, e.g., 'lightning.qubit';
        '''
        self.name = "QTrial"
        self.num_qubits = 2*prop.nbasis # JW transformation is assumed
        self.num_particles = prop.nup + prop.ndown
        self.initial_state = initial_state
        self.q_trial = ansatz_circuit
        self.dev = dev
        
        self.nup, self.ndown = prop.nup, prop.ndown
        self.nbasis = prop.nbasis
        self.h1e, self.eri = prop.h1e, prop.eri
        self.h_chem = copy.deepcopy(prop.h_chem)
        self.v_gamma, self.L_gamma = prop.v_gamma, prop.L_gamma
        self.nuclear_repulsion = prop.nuclear_repulsion
        self.lambda_l, self.U_l = prop.lambda_l, prop.U_l
        
        # define mean-field shift
        self.mf_shift = 1.j*self.compute_trial_one_body(self.L_gamma)
        
        # define mean-field subtracted one-body term v_0.
        self.v_0 = copy.deepcopy(prop.h_chem)
        for i in range(len(self.v_gamma)):
            self.v_0 -= self.mf_shift[i]*self.v_gamma[i]
        
            
    def compute_trial_energy(self, hamiltonian):
        """This function estimates the integral $\langle \Psi_Q|H|\Psi_Q\rangle$.
        Args:
            hamiltonian: hamiltonian class from pennylane, nuclear repulsion energy included; 
        Returns:
            energy: np.complex128
        """
        device = qml.device(self.dev, wires=self.num_qubits)
        @qml.qnode(device, interface=None, diff_method=None)
        def compute_hamiltonian_expectation(initial_state, q_trial, hamiltonian):
            for i in initial_state:
                qml.PauliX(wires=i)
            q_trial()
            return qml.expval(hamiltonian)
        
        energy = compute_hamiltonian_expectation(self.initial_state, self.q_trial, hamiltonian)
        return energy
    
    
    def compute_trial_one_body(self, one_body_list):
        '''This function computes the expectation value of one-body operator of quantum trial state
        <\Psi_Q|v|\Psi_Q>
        Args:
            one_body_list: a list of real-symmetric or hermitian one-body operators
        Returns:
            expectation: np.array
        '''
        num_qubits = self.num_qubits
        
        Id = np.identity(num_qubits)
        expectation = np.array([])
        pauli_dict = {i: pauli_expect(self.initial_state, self.q_trial, Id, [i], self.dev) for i in range(num_qubits)}
        
        for one_body in one_body_list:
            value = 0.0 + 0.0j
            # check if the one-body term is already diagonal or not
            if np.count_nonzero(np.round(one_body - np.diag(np.diagonal(one_body)), 7)) != 0:
                lamb, U = np.linalg.eigh(one_body)
                pauli_dict_2 = {i: pauli_expect(self.initial_state, self.q_trial, U, [i], self.dev) for i in range(num_qubits)}
                for i in range(num_qubits):
                    expectation_value = 0.5 * (1.0 - pauli_dict_2.get(i))
                    value += lamb[i] * expectation_value
            else:
                for i in range(num_qubits):
                    expectation_value = 0.5 * (1.0 - pauli_dict.get(i))
                    value += one_body[i, i] * expectation_value
            expectation = np.append(expectation, value)
            
        return expectation


    def compute_ovlp(self, walker):
        return amplitude_estimate(walker, self.q_trial, self.dev)
    
    
    def compute_one_body_local(self, walker, one_body_list, ovlp):
        """This function computes the expectation value of one-body operator between q trial state and walker 
        <\Psi_Q|v|\phi> / <\Psi_Q|\phi>
        Args:
            walker: walker Slater determinant
            one_body_list: a list of real-symmetric or hermitian one-body operators
            ovlp: amplitude between walker and the quantum trial state
        Returns:
            expectation: np.array
        """
        num_qubits, num_particles = walker.shape
        Id = np.identity(num_qubits)
        expectation = np.array([])
        pauli_dict = {i: pauli_estimate(walker, self.q_trial, Id, [i], self.dev) for i in range(num_qubits)}

        for one_body in one_body_list:
            value = 0.0 + 0.0j
            # check if the one-body term is already diagonal or not
            if np.count_nonzero(np.round(one_body - np.diag(np.diagonal(one_body)), 7)) != 0:
                lamb, U = np.linalg.eigh(one_body)
                pauli_dict_2 = {i: pauli_estimate(walker, self.q_trial, U, [i], self.dev) for i in range(num_qubits)}
                for i in range(num_qubits):
                    expectation_value = 0.5 * (ovlp - pauli_dict_2.get(i))
                    value += lamb[i] * expectation_value
            else:
                for i in range(num_qubits):
                    expectation_value = 0.5 * (ovlp - pauli_dict.get(i))
                    value += one_body[i, i] * expectation_value
            expectation = np.append(expectation, (value / ovlp))
        return expectation
        
        
    def compute_local_energy(self, walker, ovlp):
        """This function estimates the integral $\langle \Psi_Q|H|\phi_l\rangle$ with vacuum reference circuit.
        Args:
            walker: np.ndarray; matrix representation of the walker state, not necessarily orthonormalized.
            ovlp: amplitude between walker and the quantum trial state
        Returns:
            energy: np.complex128
        """
        energy = 0.0 + 0.j
        num_qubits, num_particles = walker.shape
        one_body = self.h_chem
        
        # For diagonal operators where additional rotations U is not necessary
        Id = np.identity(num_qubits)
        pauli_dict = {}
        for i in range(num_qubits):
            pauli_dict[i] = pauli_estimate(walker, self.q_trial, Id, [i], self.dev)
            for j in range(i+1, num_qubits):
                pauli_dict[(i, j)] = pauli_estimate(walker, self.q_trial, Id, [i, j], self.dev)
        
        # check if the one-body term is already diagonal or not
        if np.count_nonzero(np.round(one_body - np.diag(np.diagonal(one_body)), 7)) != 0:
            lamb, U = np.linalg.eigh(one_body)
            pauli_dict_2 = {i: pauli_estimate(walker, self.q_trial, U, [i], self.dev) for i in range(num_qubits)}
            for i in range(num_qubits):
                expectation_value = 0.5 * (ovlp - pauli_dict_2.get(i))
                energy += lamb[i] * expectation_value
        else:
            for i in range(num_qubits):
                expectation_value = 0.5 * (ovlp - pauli_dict.get(i))
                energy += one_body[i, i] * expectation_value
        
        # Cholesky decomposed two-body term
        for lamb, U in zip(self.lambda_l, self.U_l):
            # define a dictionary to store all the expectation values
            if np.count_nonzero(np.round(U - np.diag(np.diagonal(U)), 7)) == 0:
                pauli_dict_2 = pauli_dict
            else:
                pauli_dict_2 = {}
                for i in range(num_qubits):
                    pauli_dict_2[i] = pauli_estimate(walker, self.q_trial, U, [i], self.dev)
                    for j in range(i, num_qubits):
                        pauli_dict_2[(i, j)] = pauli_estimate(walker, self.q_trial, U, [i, j], self.dev)
                        
            for i in range(num_qubits):
                for j in range(i, num_qubits):
                    if i == j:
                        expectation_value = 0.5 * (ovlp - pauli_dict_2.get(i))
                    else:
                        expectation_value = 0.5 * (
                            ovlp - pauli_dict_2.get(i) - pauli_dict_2.get(j) + pauli_dict_2.get((i, j))
                        )
                    energy += 0.5 * lamb[i] * lamb[j] * expectation_value
        return energy