# This class defines the quantum trial wavefunction where all relevant local quantities are
# computed from matchgate-shadow overlaps <\Psi_Q|\phi_l>. It runs no quantum circuit: the walker
# overlaps come from the shadows, while the (noiseless) reference energy E_shift and mean-field
# shift mf_shift are taken from the classical Hartree-Fock reference.

import copy
import numpy as np
from scipy.special import comb
from itertools import product
from afqmc.estimators.ci import get_hmatel, get_one_body_matel
from afqmc.estimators.greens_function import gab
from afqmc.estimators.local_energy import local_energy_generic_cholesky
from afqmc.utils.chemical_preparation import (R_basis_change, rotated_hamiltonian_preparation,
                                              ChemicalProperties, _general_basis_change)
from afqmc.utils.shadow import normalize_shadow, compact_to_signed_permutation, covariance_from_bits
from afqmc.utils.matchgate import ovlp_reconstruction


class QTrial:
    def __init__(self, prop: ChemicalProperties, shadow, comb_coeffs=None):
        '''This class defines the quantum trial wavefunction, evaluated from matchgate shadows.
        The walker overlaps come from the shadows; the reference energy E_shift and the mean-field
        shift mf_shift are computed from the classical Hartree-Fock reference (noiseless, no circuit).
        Args:
            prop: ChemicalProperties dataclass.
            shadow: matchgate shadow of the trial state -- the compact dict from
                afqmc.utils.shadow.shadow_from_json (a legacy (outcomes, Q_list) tuple is also
                accepted and normalized).
            comb_coeffs: optional channel-inversion coefficients for noisy shadows; if None they
                are computed for noiseless shadows.
        '''
        self.name = "QTrial"
        self.num_qubits = 2*prop.nbasis     # JW transformation is assumed
        self.num_particles = prop.nup + prop.ndown

        self.nup, self.ndown = prop.nup, prop.ndown
        self.nbasis = prop.nbasis
        self.h1e, self.eri = prop.h1e, prop.eri
        self.h_chem = copy.deepcopy(prop.h_chem)
        self.v_gamma, self.L_gamma = prop.v_gamma, prop.L_gamma
        self.nuclear_repulsion = prop.nuclear_repulsion

        # --- classical Hartree-Fock reference for the noiseless shift terms (no circuit, no shadow) ---
        # HF Slater determinant: the lowest N = nup + ndown spin orbitals of 2*nbasis are occupied.
        hf = np.eye(self.num_qubits, self.num_particles)
        Ga = gab(hf[::2, ::2],  hf[::2, ::2])        # spin-up HF one-particle density matrix
        Gb = gab(hf[1::2, 1::2], hf[1::2, 1::2])      # spin-down HF one-particle density matrix
        # mean-field shift  mf_shift = i <HF|L_gamma|HF>  (same contraction as the classical trial)
        self.mf_shift = np.array([
            1j * (np.einsum("ij,ij->", L[::2, ::2], Ga) + np.einsum("ij,ij->", L[1::2, 1::2], Gb))
            for L in self.L_gamma
        ])
        # reference energy  E_shift = <HF|H|HF>  (Hartree-Fock energy) for population control
        self.E_shift = np.real(local_energy_generic_cholesky(prop, [Ga, Gb])[2])

        # define mean-field subtracted one-body term v_0.
        self.v_0 = copy.deepcopy(prop.h_chem)
        for i in range(len(self.v_gamma)):
            self.v_0 -= self.mf_shift[i]*self.v_gamma[i]

        # define possible excitations of walker state (spin-conserving singles and doubles)
        self.single_excitations = [c for c in product(np.arange(self.num_particles, self.nbasis*2, 2), np.arange(0, self.num_particles, 2))]
        self.single_excitations += [c for c in product(np.arange(self.num_particles+1, self.nbasis*2, 2), np.arange(1, self.num_particles, 2))]

        self.double_excitations = []
        for i in range(len(self.single_excitations)):
            for j in range(i+1, len(self.single_excitations)):
                if self.single_excitations[j][0] != self.single_excitations[i][0] and self.single_excitations[j][1] != self.single_excitations[i][1]:
                    self.double_excitations.append((self.single_excitations[i] + self.single_excitations[j]))

        # process the shadow (compact dict, or a legacy (outcomes, Q_list) tuple)
        if shadow is None:
            raise Exception("shadow can not be None; QTrial is evaluated from matchgate shadows.")
        self.shadow = normalize_shadow(shadow)
        self.shadow_order = int(self.num_qubits - self.num_particles//2)
        if comb_coeffs is None:
            # noiseless shadows: comb_coeffs[k] = C(2n,2k)/C(n,k) is the degree-2k channel inverse
            self.comb_coeffs = np.array([
                comb(2*self.num_qubits, 2*k)/comb(self.num_qubits, k)
                for k in range(self.shadow_order + 1)
            ])
        else:
            if len(comb_coeffs) < (self.shadow_order+1):
                raise Exception("The length of the comb coeffs can not be smaller than dim")
            self.comb_coeffs = comb_coeffs[:self.shadow_order+1]

        # lazily-built cache of reconstructed covariances Q^T C_b Q (one per outcome), reused across
        # walkers/excitations; dropped on pickling (see __getstate__) so mp.Pool workers stay light.
        self._c_hats = None
        self._c_weights = None

    def _reconstructed_covariances(self):
        """Reconstructed covariances c_hats[i] = Q^T C_b Q for every measurement outcome, plus the
        shot-count weights. The dense signed permutation for each snapshot is rebuilt once and each
        outcome's covariance is reconstructed on the fly from the compact bitstrings.
        """
        dim = 2 * self.num_qubits
        perm, sign = self.shadow["perm"], self.shadow["sign"]
        bits, counts, snap_id = self.shadow["bits"], self.shadow["count"], self.shadow["snap_id"]
        q_dense = [compact_to_signed_permutation(perm[s], sign[s]).astype(np.complex128)
                   for s in range(perm.shape[0])]
        c_hats = np.empty((len(counts), dim, dim), dtype=np.complex128)
        for i in range(len(counts)):
            Qc = q_dense[snap_id[i]]
            c_hats[i] = Qc.T @ covariance_from_bits(bits[i]) @ Qc
        return c_hats, counts.astype(np.float64)

    def __getstate__(self):
        # Drop the (large, reconstructible) covariance cache before pickling so the object stays
        # compact when sent to multiprocessing workers; each worker rebuilds it lazily on first use.
        state = self.__dict__.copy()
        state["_c_hats"] = None
        state["_c_weights"] = None
        return state

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
    
    
    def compute_ovlp(self, walker):
        if self._c_hats is None:
            self._c_hats, self._c_weights = self._reconstructed_covariances()
        return ovlp_reconstruction(self._c_hats, self._c_weights, self.comb_coeffs, walker)
    
    
    def compute_one_body_local(self, walker, one_body_list, ovlp, ovlp_dict):
        r"""This function computes the expectation value of one-body operator between q trial state and walker 
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
            one_body_rotated = _general_basis_change(one_body[::2, ::2], R, (1, 0))

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
        r"""This function estimates the integral $\langle \Psi_Q|H|\phi_l\rangle$ with rotated basis.
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
        
        # Build (once) the overlaps with singly- and doubly-excited walker determinants. When a
        # populated ovlp_dict is passed in, reuse it instead of recomputing these overlaps.
        if not ovlp_dict:
            ovlp_dict = {(): ovlp}
            for key in self.single_excitations + self.double_excitations:
                # generate the excited Slater determinant in the rotated basis, rotate it back to
                # the canonical basis through R, and reconstruct its overlap from the shadows
                phi_exc_rot = self.generate_excited_slater(key)
                phi_exc = U_phi @ phi_exc_rot
                ovlp_dict[key] = self.compute_ovlp(phi_exc)

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