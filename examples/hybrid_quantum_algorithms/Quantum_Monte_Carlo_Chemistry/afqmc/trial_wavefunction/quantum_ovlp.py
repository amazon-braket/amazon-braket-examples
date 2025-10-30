# This class defines the quantum trial wavefunction where all the relevant local quantities 
# are computed from overlaps <\Psi_Q|\phi_l>

import copy
import numpy as np
import pennylane as qml
from scipy.special import comb
from typing import List
from itertools import product
from openfermion.ops import general_basis_change
from afqmc.estimators.ci import get_hmatel, get_one_body_matel
from afqmc.utils.chemical_preparation import R_basis_change, rotated_hamiltonian_preparation, ChemicalProperties
from afqmc.utils.quantum import amplitude_estimate, pauli_expect
from afqmc.utils.matchgate import ovlp_reconstruction


class QTrial:
    def __init__(self, prop: ChemicalProperties, initial_state: List, ansatz_circuit, dev="lightning.qubit",
                 ifshadow=False, shadow=None, comb_coeffs=[]):
        '''This class defines the quantum trial wavefunction.
        Args:
            prop: ChemicalProperties dataclass
            initial_state: the initial occupied orbitals as a list
            ansatz_circuit: pennylane circuit
            dev: only support for simulators, e.g., 'lightning.qubit';
            ifshadow (bool): Use shadow tomography or not;
            shadow: format being (outcomes, Q_list), where 'outcomes' contains the measurement statistics;
                    and 'Q_list' contains the random signed permutation matrix being sampled.
        '''
        self.name = "QTrial"
        self.num_qubits = 2*prop.nbasis     # JW transformation is assumed
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
        
        # define possible excitations of walker state, this may be moved to walker class in the future
        # create single excitation list
        self.single_excitations = [c for c in product(np.arange(self.num_particles, self.nbasis*2, 2), np.arange(0, self.num_particles, 2))]
        self.single_excitations += [c for c in product(np.arange(self.num_particles+1, self.nbasis*2, 2), np.arange(1, self.num_particles, 2))]
        
        self.double_excitations = []
        for i in range(len(self.single_excitations)):
            for j in range(i+1, len(self.single_excitations)):
                if self.single_excitations[j][0] != self.single_excitations[i][0] and self.single_excitations[j][1] != self.single_excitations[i][1]:
                    self.double_excitations.append((self.single_excitations[i] + self.single_excitations[j]))
            
        
        # processing the shadow-related quantities
        self.ifshadow = ifshadow
        if self.ifshadow:
            if shadow == None:
                raise Exception("shadow can not be None or empty if shadow tomography is used.")
            else:
                self.b_lists, self.Q_list = shadow
                self.shadow_order = int(self.num_qubits - self.num_particles//2)
        
        if self.ifshadow:
            if comb_coeffs == []:
                # we treat it as noiseless shadows
                self.comb_coeffs = np.array([])
                for k in range(self.shadow_order + 1):
                    self.comb_coeffs = np.append(
                        self.comb_coeffs,
                        [comb(2*self.num_qubits, 2*k)/comb(self.num_qubits,k)]
                    )
            else:
                if len(comb_coeffs) < (self.shadow_order+1):
                    raise Exception("The length of the comb coeffs can not be smaller than dim")
                self.comb_coeffs = comb_coeffs[:self.shadow_order+1]
    
    
    def generate_excited_slater(self, excitation: tuple):
        """This function assumes the number of spin_up and spin_down electrons are the same."""
        
        # first we define the Hartree-Fock state:
        shape = (self.num_qubits, self.num_particles)
        hf = np.zeros((shape[0], shape[1]))
        for i in range(shape[1]):
            hf[i, i] = 1
            
        # generate excited slater determinant:
        excited_slater = copy.deepcopy(hf)
        for i in range(len(excitation)//2): # the length of excitation list has to be even
            for j in range(shape[1]):
                if excited_slater[excitation[2*i+1], j] == 1:
                    excited_slater[excitation[2*i+1], j] = 0
                    excited_slater[excitation[2*i], j] = 1
                    break
                
        return excited_slater
    
    
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
        pauli_dict = {i: pauli_expect(self.initial_state, self.q_trial,
                                      Id, [i], self.dev) for i in range(num_qubits)}
        
        for one_body in one_body_list:
            value = 0.0 + 0.0j
            # check if the one-body term is already diagonal or not
            if np.count_nonzero(np.round(one_body - np.diag(np.diagonal(one_body)), 7)) != 0:
                lamb, U = np.linalg.eigh(one_body)
                pauli_dict_2 = {i: pauli_expect(self.initial_state, self.q_trial,
                                                U, [i], self.dev) for i in range(num_qubits)}
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
        if self.ifshadow:
            return ovlp_reconstruction(self.b_lists, self.Q_list, self.comb_coeffs, walker)
        else:
            return amplitude_estimate(walker, self.q_trial, self.dev)
    
    
    def compute_one_body_local(self, walker, one_body_list, ovlp, ovlp_dict):
        """This function computes the expectation value of one-body operator between q trial state and walker 
        <\Psi_Q|v|\phi> / <\Psi_Q|\phi>; The idea is to rewrite the general Slater determinant into a linear
        combination after the operation of number operators, where the rows and columns of that orbital are
        cleaned up.
        Args:
            walker: walker Slater determinant
            one_body_list: a list of real-symmetric or hermitian one-body operators
            ovlp: amplitude between walker and the quantum trial state
        Returns:
            expectation: np.array
        """
        num_qubits, num_particles = walker.shape
        R = R_basis_change(walker)
        expectation = np.array([])
        
        for one_body in one_body_list:
            one_body_rotated = general_basis_change(one_body[::2, ::2], R, (1, 0))
            
            # define the Hartree-Fock Slater
            dj = np.arange(num_particles)
            value = ovlp * get_one_body_matel(one_body_rotated, dj, dj)
            
            # loop over the possible single excitations
            for key in self.single_excitations:
                di = copy.deepcopy(dj)
                for index in range(self.num_particles):
                    if di[index] == key[1]:
                        di[index] = key[0]
                value += ovlp_dict.get(key) * get_one_body_matel(one_body_rotated, di, dj)
            
            expectation = np.append(expectation, (value / ovlp))
        return expectation
    
    
    def compute_local_energy(self, walker, ovlp, ovlp_dict=None):
        """This function estimates the integral $\langle \Psi_Q|H|\phi_l\rangle$ with rotated basis.
        Args:
            walker: np.ndarray; matrix representation of the walker state, not necessarily orthonormalized.
            ovlp: amplitude between walker and the quantum trial state
            ovlp_dict
        Returns:
            energy: np.complex128
        """
        energy = 0. + 0.j
        num_qubits, num_particles = walker.shape
        R = R_basis_change(walker)
        U_phi = np.kron(R, np.eye(2))
        h1e_rot, eri_rot = rotated_hamiltonian_preparation(self.h1e, self.eri, walker)
        
        # here we create a dictionary to save the ovlp needed for diagonal one-body terms;
        if not ovlp_dict:
            ovlp_dict = {(): ovlp}
            # loop over the possible single excitations and save them
            for key in self.single_excitations:
                # generate excited Slater determinant in the rotated basis
                phi_exc_rot = self.generate_excited_slater(key)
                
                # rotate it back to canonical basis through R
                phi_exc = U_phi @ phi_exc_rot
                phi_exc_ovlp = self.compute_ovlp(phi_exc)
                ovlp_dict.update({key: phi_exc_ovlp})
        
        # compute the overlap with double excitation Slaters
        for key in self.double_excitations:
            # generate excited Slater determinant in the rotated basis
            phi_exc_rot = self.generate_excited_slater(key)
            
            # rotate it back to canonical basis through R
            phi_exc = U_phi @ phi_exc_rot
            phi_exc_ovlp = self.compute_ovlp(phi_exc)
            ovlp_dict.update({key: phi_exc_ovlp})
        
        dj = np.arange(num_particles)
        energy += ovlp * get_hmatel(h1e_rot, eri_rot, dj, dj)[0]
        
        for key in self.single_excitations:
            di = copy.deepcopy(dj)
            for index in range(self.num_particles):
                if di[index] == key[1]:
                    di[index] = key[0]
            energy += ovlp_dict.get(key) * get_hmatel(h1e_rot, eri_rot, di, dj)[0]
        
        for key in self.double_excitations:
            di = copy.deepcopy(dj)
            for index in range(self.num_particles):
                if di[index] == key[1]:
                    di[index] = key[0]
                elif di[index] == key[3]:
                    di[index] = key[2]
                    
            energy += ovlp_dict.get(key) * get_hmatel(h1e_rot, eri_rot, di, dj)[0]
        
        return energy, ovlp_dict