#!/usr/bin/env

import copy
import multiprocessing as mp
import os

import numpy as np
from openfermion.circuits.low_rank import low_rank_two_body_decomposition
from scipy.linalg import det, expm, qr
from tqdm import tqdm

CUTOFF = 1e-14


def reortho(A):
    """Reorthogonalise a MxN matrix A.
    Performs a QR decomposition of A. Note that for consistency elsewhere we
    want to preserve detR > 0 which is not guaranteed. We thus factor the signs
    of the diagonal of R into Q.

    Args:
        A (np.ndarray): MxN matrix.

    Returns:
        Q (np.ndarray): Orthogonal matrix. A = QR.
        detR (float): Determinant of upper triangular matrix (R) from QR decomposition.
    """
    (Q, R) = qr(A, mode="economic")
    signs = np.diag(np.sign(np.diag(R)))
    Q = Q.dot(signs)
    detR = det(signs.dot(R))
    return (Q, detR)


def G_pq(psi: np.ndarray, phi: np.ndarray):
    """This function coomputes the one-body Green's function

    Args:
        psi, phi: np.ndarray

    Returns:
        G: one-body Green's function
    """
    overlap_inverse = np.linalg.inv(psi.transpose() @ phi)
    G = phi @ overlap_inverse @ psi.transpose()
    return G


def local_energy(h1e, eri, G, enuc):
    r"""Calculate local for generic two-body hamiltonian.
    This uses the full (spatial) form for the two-electron integrals.

    Args:
        h1e (np.ndarray): one-body term
        eri (np.ndarray): two-body term
        G (np.ndarray): Walker's "green's function"

    Returns:
        T + V + enuc (float): kinetic, potential energies and nuclear repulsion energy.
    """
    e1 = np.einsum("ij,ij->", h1e, G[0]) + np.einsum("ij,ij->", h1e, G[1])

    euu = 0.5 * (
        np.einsum("ijkl,il,jk->", eri, G[0], G[0]) - np.einsum("ijkl,ik,jl->", eri, G[0], G[0])
    )
    edd = 0.5 * (
        np.einsum("ijkl,il,jk->", eri, G[1], G[1]) - np.einsum("ijkl,ik,jl->", eri, G[1], G[1])
    )
    eud = 0.5 * np.einsum("ijkl,il,jk->", eri, G[0], G[1])
    edu = 0.5 * np.einsum("ijkl,il,jk->", eri, G[1], G[0])
    e2 = euu + edd + eud + edu

    return e1 + e2 + enuc


def chemistry_preparation(mol, hf, trial):
    """
    This function returns one- and two-electron integrals from PySCF.

    Args:
        mol (pyscf.gto.mole.Mole): PySCF molecular structure
        hf (pyscf.scf.hf.RHF): PySCF non-relativistic RHF
        trial (np.ndarray): trial wavefunction

    Returns:
        v_0: one-body term stored as np.ndarray, with mean-field subtraction
        h_chem: one-body term stored as np.ndarray, without mean-field subtraction
        v_gamma: 1.j*L_gamma
        L_gamma: Cholesky vector decomposed from two-body terms
        mf_shift: mean-field shift
        nuclear_repulsion: nuclear repulsion constant
    """

    h1e = mol.intor("int1e_kin") + mol.intor("int1e_nuc")
    h2e = mol.intor("int2e")
    scf_c = hf.mo_coeff
    nuclear_repulsion = mol.energy_nuc()

    # Get the one and two electron integral in the Hatree Fock basis
    h1e = scf_c.T @ h1e @ scf_c

    # For the modified physics notation adapted to quantum computing convention.
    for _ in range(4):
        h2e = np.tensordot(h2e, scf_c, axes=1).transpose(3, 0, 1, 2)
    eri = h2e.transpose(0, 2, 3, 1)

    lamb, g, one_body_correction, residue = low_rank_two_body_decomposition(eri, spin_basis=False)
    v_0 = np.kron(h1e, np.eye(2)) + 0.5 * one_body_correction
    h_chem = copy.deepcopy(v_0)
    num_spin_orbitals = int(h_chem.shape[0])

    L_gamma = []
    v_gamma = []
    for i in range(len(lamb)):
        L_gamma.append(np.sqrt(lamb[i]) * g[i])
        v_gamma.append(1.0j * np.sqrt(lamb[i]) * g[i])

    trial_up = trial[::2, ::2]
    trial_down = trial[1::2, 1::2]
    G = [G_pq(trial_up, trial_up), G_pq(trial_down, trial_down)]

    # compute mean-field shift as an imaginary value
    mf_shift = np.array([])
    for i in v_gamma:
        value = np.einsum("ij,ij->", i[::2, ::2], G[0])
        value += np.einsum("ij,ij->", i[1::2, 1::2], G[1])
        mf_shift = np.append(mf_shift, value)

    # Note that we neglect the prime symbol for simplicity.
    for i in range(len(v_gamma)):
        v_0 -= mf_shift[i] * v_gamma[i]

    lambda_l = []
    U_l = []
    for i in L_gamma:
        if np.count_nonzero(np.round(i - np.diag(np.diagonal(i)), 7)) != 0:
            eigval, eigvec = np.linalg.eigh(i)
            lambda_l.append(eigval)
            U_l.append(eigvec)
        else:
            lambda_l.append(np.diagonal(i))
            U_l.append(np.eye(num_spin_orbitals))

    return h1e, eri, nuclear_repulsion, v_0, h_chem, v_gamma, L_gamma, mf_shift, lambda_l, U_l


def PropagateWalker(x, v_0, v_gamma, mf_shift, dtau, trial, walker, G):
    r"""This function updates the walker from imaginary time propagation.

    Args:
        x: auxiliary fields
        v_0: modified one-body term from reordering the two-body operator + mean-field subtraction.
        v_gamma: Cholesky vectors stored in list (L, num_spin_orbitals, num_spin_orbitals), without mf_shift
        mf_shift: mean-field shift \Bar{v}_{\gamma} stored in np.array format
        dtau: imaginary time step size
        trial: trial state as np.ndarray, e.g., for h2 HartreeFock state, it is np.array([[1,0], [0,1], [0,0], [0,0]])
        walker: walker state as np.ndarray, others are the same as trial
        G: one-body Green's function

    Returns:
        new_walker: new walker for next time step
    """
    num_spin_orbitals, num_electrons = trial.shape
    num_fields = len(v_gamma)

    v_expectation = np.array([])
    for i in v_gamma:
        value = np.einsum("ij,ij->", i[::2, ::2], G[0])
        value += np.einsum("ij,ij->", i[1::2, 1::2], G[1])
        v_expectation = np.append(v_expectation, value)

    xbar = -np.sqrt(dtau) * (v_expectation - mf_shift)
    # Sampling the auxiliary fields
    xshifted = x - xbar

    # Define the B operator B(x - \bar{x})
    exp_v0 = expm(-dtau / 2 * v_0)

    V = np.zeros((num_spin_orbitals, num_spin_orbitals), dtype=np.complex128)
    for i in range(num_fields):
        V += np.sqrt(dtau) * xshifted[i] * v_gamma[i]
    exp_V = expm(V)

    # Note that v_gamma doesn't include the mf_shift, there is an additional term coming from
    # -(x - xbar)*mf_shift, this term is also a complex value.
    # cmf = -np.sqrt(dtau)*np.dot(xshifted, mf_shift)
    # prefactor = np.exp(-dtau*(H_0 - E_0) + cmf)
    B = exp_v0 @ exp_V @ exp_v0

    # Find the new walker state
    new_walker, _ = reortho(B @ walker)

    return new_walker


def ImagTimePropagator(
    v_0: np.ndarray,
    v_gamma: list,
    mf_shift: np.ndarray,
    dtau: float,
    trial: np.ndarray,
    walker: np.ndarray,
    weight: float,
    h1e,
    eri,
    enuc,
    E_shift: float,
):
    r"""This function defines the imaginary propagation process and will return new walker state and new weight.

    Args:
        v_0: modified one-body term from reordering the two-body operator + mean-field subtraction.
        v_gamma: Cholesky vectors stored in list (L, num_spin_orbitals, num_spin_orbitals), without mf_shift
        mf_shift: mean-field shift \Bar{v}_{\gamma} stored in np.array format
        dtau: imaginary time step size
        trial: trial state as np.ndarray, e.g., for h2 HartreeFock state, it is np.array([[1,0], [0,1], [0,0], [0,0]])
        walker: walker state as np.ndarray, others are the same as trial
        weight: weight associated with the specific walker
        h1e, eri: one- and two-electron integral stored in spatial orbitals basis
        enuc: nuclear repulsion energy
        E_shift: reference energy, usually taken as the HF energy.

    Returns:
        E_loc: local energy
        new_weight: new weight for next time step
        new_walker: new walker for next time step

    """
    seed = np.random.seed(int.from_bytes(os.urandom(4), byteorder="little"))

    # First compute the bias force using the expectation value of L operators
    num_spin_orbitals, num_electrons = trial.shape
    num_fields = len(v_gamma)

    # compute the overlap integral
    ovlp = np.linalg.det(trial.transpose().conj() @ walker)

    trial_up = trial[::2, ::2]
    trial_down = trial[1::2, 1::2]
    walker_up = walker[::2, ::2]
    walker_down = walker[1::2, 1::2]
    G = [G_pq(trial_up, walker_up), G_pq(trial_down, walker_down)]
    E_loc = local_energy(h1e, eri, G, enuc)

    # sampling the auxiliary fields
    x = np.random.normal(0.0, 1.0, size=num_fields)
    # update the walker
    new_walker = PropagateWalker(x, v_0, v_gamma, mf_shift, dtau, trial, walker, G)

    # Define the I operator and find new weight
    new_ovlp = np.linalg.det(trial.transpose().conj() @ new_walker)
    arg = np.angle(new_ovlp / ovlp)
    new_weight = weight * np.exp(-dtau * (np.real(E_loc) - E_shift)) * np.max([0.0, np.cos(arg)])

    return E_loc, new_walker, new_weight


def ImagTimePropagatorWrapper(args):
    """
    Wrapper function for multiprocessing
    """
    return ImagTimePropagator(*args)


def cAFQMC(
    num_walkers,
    num_steps,
    v_0,
    v_gamma,
    mf_shift,
    dtau,
    trial,
    h1e,
    eri,
    enuc,
    Ehf,
    max_pool,
    progress_bar=True,
):
    r"""
    Args:
        num_walkers:
        num_steps: number of steps for imaginary time evolution
        v_0: modified one-body term from reordering the two-body operator + mean-field subtraction.
        v_gamma: Cholesky vectors stored in list (L, num_spin_orbitals, num_spin_orbitals), without mf_shift
        mf_shift: mean-field shift \Bar{v}_{\gamma} stored in np.array format
        dtau: imaginary time step size
        trial: trial state as np.ndarray, e.g., for h2 HartreeFock state, it is np.array([[1,0], [0,1], [0,0], [0,0]])
        h1e, eri: one- and two-electron integral stored in spatial orbitals basis
        enuc: nuclear repulsion energy
        E_shift: reference energy, usually taken as the HF energy
        max_pool: number of cores to parallelize the calculations
        progress_bar: bool
    Returns:
        total_time: list that stores the time series of the evolution
        E_list: list that stores the computed energy
    """
    E_list = []
    E_shift = Ehf  # set energy shift E_0 as HF energy from earlier
    total_time = np.linspace(dtau, int(dtau * num_steps), num=num_steps)
    walkers = [trial] * num_walkers
    weights = [1.0] * num_walkers

    for _ in tqdm(range(num_steps + 1), disable=not progress_bar):
        inputs = [
            (v_0, v_gamma, mf_shift, dtau, trial, walker, weight, h1e, eri, enuc, E_shift)
            for walker, weight in zip(walkers, weights)
        ]

        weight_list, walker_list, energy_list = run_classical_qmc(max_pool, inputs)

        E = np.real(np.average(energy_list, weights=weights))
        E_list.append(E)
        E_shift = E

        walkers = walker_list  # update the walkers
        weights = weight_list  # update the weights

    return total_time, E_list


def run_classical_qmc(max_pool, inputs):
    with mp.Pool(max_pool) as pool:
        results = list(pool.map(ImagTimePropagatorWrapper, inputs))

    weight_list = []
    walker_list = []
    energy_list = []
    for (E_loc, new_walker, new_weight) in results:
        energy_list.append(E_loc)
        # for computational stability, we neglect the weights that are too small.
        if new_weight > CUTOFF:
            weight_list.append(new_weight)
            walker_list.append(new_walker)
    return weight_list, walker_list, energy_list
