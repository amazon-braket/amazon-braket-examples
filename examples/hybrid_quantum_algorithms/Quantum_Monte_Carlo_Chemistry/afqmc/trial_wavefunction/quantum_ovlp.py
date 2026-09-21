# This class defines the quantum trial wavefunction where all relevant local quantities are
# computed from matchgate-shadow overlaps <\Psi_Q|\phi_l>

import copy
import numpy as np
from scipy.special import comb
from itertools import product, combinations
from afqmc.estimators.ci import get_hmatel, get_one_body_matel
from afqmc.utils.chemical_preparation import (
    R_basis_change,
    rotated_hamiltonian_preparation,
    ChemicalProperties,
    _general_basis_change,
)
from afqmc.utils.matchgate import ovlp_reconstruction
from afqmc.utils.shadow import normalize_shadow, compact_to_signed_permutation, covariance_from_bits

# Maps a^dag_P a_Q = (1/4) sum_{a,b} c[a,b] gamma_{2P+a} gamma_{2Q+b} (Jordan-Wigner, Majorana form).
_C_MATRIX = np.array([[1.0, -1.0j], [1.0j, 1.0]], dtype=np.complex128)


def _reduce_majorana(indices):
    """Reduce a product of Majorana operators gamma_{i1} gamma_{i2} ... to a canonical form.

    Repeatedly applies the anticommutation relations: swapping two distinct adjacent operators
    flips the sign, and gamma_i^2 = 1 removes an adjacent equal pair. The result is a sorted
    tuple of distinct indices together with the accumulated overall sign (+/-1).
    Args:
        indices: iterable of Majorana indices.
    Returns:
        (sign, reduced): sign in {1, -1}; reduced is a tuple of sorted distinct indices.
    """
    arr = list(indices)
    sign = 1
    changed = True
    while changed:
        changed = False
        j = 0
        while j < len(arr) - 1:
            if arr[j] == arr[j + 1]:
                del arr[j + 1]
                del arr[j]
                changed = True
                j = max(j - 1, 0)
            elif arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                sign = -sign
                changed = True
                j += 1
            else:
                j += 1
    return sign, tuple(arr)


class QTrial:
    def __init__(self, prop: ChemicalProperties, shadow, comb_coeffs=None):
        '''This class defines the quantum trial wavefunction, evaluated entirely from matchgate
        shadows (no quantum circuit is run by this class).
        Args:
            prop: ChemicalProperties dataclass.
            shadow: matchgate shadow of the trial state -- either the compact dict from
                calculate_classical_shadow or the legacy (outcomes, Q_list) tuple.
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
        self.lambda_l, self.U_l = prop.lambda_l, prop.U_l

        # process the shadow (accept the compact dict or the legacy (outcomes, Q_list) tuple)
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

        # lazily-built cache of the reconstructed covariances Q^T C_b Q (one per measurement
        # outcome). These are walker-independent, so they are computed once (on first overlap
        # evaluation) and reused for every walker/excitation. The cache is dropped on pickling
        # (see __getstate__), so it never re-bloats the object sent to multiprocessing workers.
        self._c_hats = None
        self._c_weights = None

        # degree-2 Majorana correlators G[mu,nu] = <Psi_Q|gamma_mu gamma_nu|Psi_Q>, from the shadows;
        # reused for the mean-field shift, the one-body local terms, and the trial energy.
        self.G = self._compute_degree2_correlators()

        # define mean-field shift (from shadows, no circuit)
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

    def _reconstructed_covariances(self):
        """Reconstructed covariances c_hats[i] = Q^T C_b Q for every measurement outcome, and the
        shot-count weights. The dense signed permutation for each snapshot is rebuilt once and each
        outcome's covariance is reconstructed on the fly from the compact bitstrings.
        Returns:
            (c_hats, weights): c_hats is (N_out, 2*num_qubits, 2*num_qubits) complex; weights float.
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

    def _compute_degree2_correlators(self):
        """Degree-2 Majorana correlators G[mu,nu] = <Psi_Q|gamma_mu gamma_nu|Psi_Q> from the shadows.
        The 2x2 Pfaffian is linear, so the shot-weighted mean of the reconstructed covariances
        Q^T C_b Q suffices (no need to keep all per-snapshot matrices in memory). Diagonal set to 0.
        """
        dim = 2 * self.num_qubits
        perm, sign = self.shadow["perm"], self.shadow["sign"]
        bits, counts, snap_id = self.shadow["bits"], self.shadow["count"], self.shadow["snap_id"]
        q_dense = [compact_to_signed_permutation(perm[s], sign[s]).astype(np.complex128)
                   for s in range(perm.shape[0])]
        weights = counts.astype(np.float64)
        c_bar = np.zeros((dim, dim), dtype=np.complex128)
        for i in range(len(counts)):
            Qc = q_dense[snap_id[i]]
            c_bar += weights[i] * (Qc.T @ covariance_from_bits(bits[i]) @ Qc)
        c_bar /= weights.sum()
        G = (-1j) * self.comb_coeffs[1] * c_bar
        np.fill_diagonal(G, 0.0)
        return G

    def _one_body_expectation(self, matrix):
        """<Psi_Q|O|Psi_Q> for a one-body operator O = sum_{PQ} matrix_{PQ} a^dag_P a_Q, from the
        degree-2 correlators. With B = (1/4) kron(matrix, c_matrix), O = sum_{mu,nu} B_{mu,nu}
        gamma_mu gamma_nu; the mu=nu (identity) part is captured by <gamma_mu gamma_mu> = 1.
        """
        g_full = self.G.copy()
        np.fill_diagonal(g_full, 1.0)
        b = 0.25 * np.kron(matrix, _C_MATRIX)
        return np.sum(b * g_full)

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
    
    
    def compute_trial_energy_shadow(self):
        r"""Estimate the quantum trial energy $\langle\Psi_Q|H|\Psi_Q\rangle$ (including nuclear
        repulsion) purely from the matchgate shadows, without any additional quantum circuit.

        The electronic Hamiltonian is a degree-4 polynomial in the $2m$ Majorana operators
        ($m$ = number of spin orbitals = ``self.num_qubits``). Using the AFQMC decomposition
        already stored on ``prop``,
            $H = E_{nuc} + \sum_{PQ}[h\_chem]_{PQ}a_P^\dagger a_Q + \tfrac12\sum_\gamma \hat L_\gamma^2$,
            $\hat L_\gamma = \sum_{PQ}[L_\gamma]_{PQ}a_P^\dagger a_Q$,
        each expectation reduces to Majorana correlators $\langle\gamma_S\rangle$ that the
        matchgate shadow estimates unbiasedly (valid for the non-Gaussian $\Psi_Q$).

        Per-snapshot degree-$2k$ estimator ($|S|=2k$, $S$ ordered):
            $\langle\gamma_S\rangle = i^{-k}\,\text{comb\_coeffs}[k]\,
             \langle \mathrm{Pf}[(Q^\top C_b Q)_{S,S}]\rangle_{\text{snapshots}}$,
        where the average is weighted by shot counts, matching ``ovlp_reconstruction``.

        Returns:
            energy (float): total trial energy (electronic + nuclear repulsion) as a real float.
        """
        if len(self.comb_coeffs) < 3:
            raise Exception(
                "Shadow order too small for a two-body (degree-4) energy estimate; "
                "need comb_coeffs of length >= 3."
            )

        dim = 2 * self.num_qubits  # number of Majorana operators

        # --- per-snapshot reconstructed covariances Chat = Q^T C_b Q, with shot weights ---
        # (needed for the nonlinear degree-4 Pfaffians; degree-2 reuses the cached self.G)
        c_hats, weights = self._reconstructed_covariances()
        wsum = weights.sum()

        G = self.G  # degree-2 correlators, precomputed in __init__

        # --- degree-4 correlators: <gamma_a gamma_b gamma_c gamma_d> for sorted distinct (a,b,c,d) ---
        # Pf is nonlinear, so we Pfaffian each snapshot then average (cannot use the mean covariance).
        four_corr = {}
        for s in combinations(range(dim), 4):
            idx = np.asarray(s)
            blk = c_hats[:, idx[:, None], idx[None, :]]  # (num_snapshots, 4, 4)
            pf = (blk[:, 0, 1] * blk[:, 2, 3]
                  - blk[:, 0, 2] * blk[:, 1, 3]
                  + blk[:, 0, 3] * blk[:, 1, 2])
            four_corr[s] = (-1.0) * self.comb_coeffs[2] * np.dot(weights, pf) / wsum

        def majorana_corr(indices):
            """<gamma_{i1} gamma_{i2} ...> for arbitrary indices, via anticommutation + gamma^2=1."""
            sgn, red = _reduce_majorana(indices)
            if len(red) == 0:
                return sgn * 1.0
            if len(red) == 2:
                return sgn * G[red[0], red[1]]
            return sgn * four_corr[red]

        # one-body term: <Psi_Q|h_chem|Psi_Q>
        energy = self._one_body_expectation(self.h_chem)

        # two-body term: (1/2) sum_gamma <L_gamma^2>. Precompute the degree-4 tensor once
        # (T[mu,nu,rho,sigma] = <gamma_mu gamma_nu gamma_rho gamma_sigma>) and contract per gamma.
        t_tensor = np.zeros((dim, dim, dim, dim), dtype=np.complex128)
        for mu in range(dim):
            for nu in range(dim):
                for rho in range(dim):
                    for sigma in range(dim):
                        t_tensor[mu, nu, rho, sigma] = majorana_corr((mu, nu, rho, sigma))

        for l_gamma in self.L_gamma:
            b = 0.25 * np.kron(l_gamma, _C_MATRIX)
            energy += 0.5 * np.einsum("mn,rs,mnrs->", b, b, t_tensor, optimize=True)

        # the trial energy is physically real
        return float(np.real(energy + self.nuclear_repulsion))


    def compute_trial_one_body(self, one_body_list):
        r'''Expectation value <\Psi_Q|v|\Psi_Q> of each one-body operator v, from the matchgate
        shadows (degree-2 Majorana correlators) -- no quantum circuit.
        Args:
            one_body_list: a list of hermitian one-body operators in the spin-orbital basis.
        Returns:
            expectation (np.ndarray): one (real) entry per operator.
        '''
        return np.array([np.real(self._one_body_expectation(v)) for v in one_body_list])


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