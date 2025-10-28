import copy, os
import numpy as np
from itertools import product
from typing import List, Tuple
from dataclasses import dataclass
from pyscf.scf.hf import RHF
from pyscf.scf.uhf import UHF
from pyscf.gto.mole import Mole
from pyscf import fci, gto, scf, mcscf, ao2mo
from scipy.linalg import null_space
from openfermion.circuits.low_rank import low_rank_two_body_decomposition
from openfermion.ops import general_basis_change
from afqmc.utils.linalg import reortho

@dataclass
class ChemicalProperties:
    nbasis: int # number of basis functions
    nup: int # number of spin up electrons
    ndown: int # number of spin down electrons
    h1e: np.ndarray  # one-body term
    eri: np.ndarray  # two-body term
    nuclear_repulsion: float  # nuclear repulsion energy or core energy for active space calculations
    h_chem: np.ndarray  # one-body term stored as np.ndarray, without mean-field subtraction
    v_gamma: List[np.ndarray]  # 1j * L_gamma
    L_gamma: List[np.ndarray]  # Cholesky vector decomposed from two-body terms
    lambda_l: List[np.ndarray]  # eigenvalues of Cholesky vectors
    U_l: List[np.ndarray]  # eigenvectors of Cholesky vectors        
        
        
def chemistry_preparation(mol: Mole, hf: RHF, active_orbitals=None, nel=None):
    """
    This function returns necessary operators and vectors for classical AFQMC calculations from PySCF.

    Args:
        mol (pyscf.gto.mole.Mole): PySCF molecular structure
        hf (pyscf.scf.hf.RHF): PySCF non-relativistic RHF
        trial (np.ndarray): trial wavefunction, currently only the hartree-fock state has been implemented
        active_orbitals: list of (1-based) active orbitals; default None
        nel: tuple of (alpha, beta) electrons in the active space; default None
    Returns:
        v_0: one-body term stored as np.ndarray, with mean-field subtraction
        h_chem: one-body term stored as np.ndarray, without mean-field subtraction
        v_gamma: 1.j*L_gamma
        L_gamma: Cholesky vector decomposed from two-body terms
        mf_shift: mean-field shift
        nuclear_repulsion: nuclear repulsion constant
    """
    if active_orbitals == None:
        nbasis = mol.nao_nr()
        nup, ndown = mol.nelectron//2, mol.nelectron//2   # assuming the number of spin-up and down eles being the same
        h1e = mol.intor("int1e_kin") + mol.intor("int1e_nuc")
        h2e = mol.intor("int2e")
        scf_c = hf.mo_coeff
        nuclear_repulsion = mol.energy_nuc()

        # Get the one and two electron integral in the Hatree Fock basis
        h1e = scf_c.T @ h1e @ scf_c

        # For the modified physics notation adapted to quantum computing convention.
        for _ in range(4):
            h2e = np.tensordot(h2e, scf_c, axes=1).transpose(3, 0, 1, 2)
        eri = h2e.transpose(0,2,3,1)
    else:
        nbasis = len(active_orbitals)
        cas = mcscf.CASCI(hf, len(active_orbitals), nel)
        mo = cas.sort_mo(active_orbitals)
        cas.kernel(mo)

        h1e, nuclear_repulsion = cas.h1e_for_cas()
        h2e = cas.get_h2cas()
        h2e = ao2mo.addons.restore(symmetry=1, eri=h2e, norb=len(active_orbitals))
        eri = h2e.transpose(0,2,3,1)
        nup, ndown = nel[0], nel[1]

    lamb, g, one_body_correction, residue = low_rank_two_body_decomposition(eri, spin_basis=False)
    h_chem = np.kron(h1e, np.eye(2)) + 0.5 * one_body_correction
    num_spin_orbitals = int(h_chem.shape[0])
    
    # for a general molecule, add additional low rank decomposition to diagonalize the h_chem;
    # for h2, h_chem is already diagonal
    
    L_gamma = []
    v_gamma = []
    for i in range(len(lamb)):
        L_gamma.append(np.sqrt(lamb[i])*g[i])
        v_gamma.append(1.j*np.sqrt(lamb[i])*g[i])
        
    lambda_l = []
    U_l = []
    for i in L_gamma:
        if np.count_nonzero(np.round(i - np.diag(np.diagonal(i)), 7)) != 0:
            eigval, eigvec = np.linalg.eigh(np.round(i, 8))
            lambda_l.append(eigval)
            U_l.append(eigvec)
        else:
            lambda_l.append(np.diagonal(i))
            U_l.append(np.eye(num_spin_orbitals))
            
    return ChemicalProperties(
        nbasis, nup, ndown, h1e, eri, nuclear_repulsion, h_chem, v_gamma, L_gamma, lambda_l, U_l
    )


        
def rotated_hamiltonian_preparation(h1e, eri, phi: np.ndarray):
    """This function returns the rotated Hamiltonian for local energy evaluation.
       We assume a RHF starting point for this function.
    Args:
        h1e (np.ndarray): one-body term in spatial orbital basis
        eri (np.ndarray): two-body term written in modified physicist's notation
        phi (np.ndarray): walker wavefunction
    """
    # define the unitary rotation matrix from walker wavefunction
    R = R_basis_change(phi)
    
    h1e_rotated = general_basis_change(h1e, R, (1, 0))
    eri_rotated = general_basis_change(eri, R, (1, 1, 0, 0))
    return h1e_rotated, eri_rotated

        
def R_basis_change(phi):
    """This only applies to hydrogen molecule for the moment
    """
    num_qubits, num_electrons = phi.shape
    R = np.zeros((num_qubits//2, num_qubits//2), dtype=np.complex128)
    R[:, :num_electrons//2] = phi[::2, ::2]
    R[:, num_electrons//2:] = null_space(phi[::2, ::2].T)
    
    V, _ = reortho(R)
    return V