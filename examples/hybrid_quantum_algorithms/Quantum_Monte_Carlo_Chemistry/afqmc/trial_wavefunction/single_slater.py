import copy
import numpy as np
from afqmc.estimators.greens_function import gab
from afqmc.utils.chemical_preparation import ChemicalProperties
from afqmc.estimators.local_energy import local_energy_generic_cholesky


class SingleSlater:
    def __init__(self, prop: ChemicalProperties, psi0: np.ndarray):
        '''This class defines the multi-Slater trial wavefunction using CI type expansions.
        Args:
            prop: ChemicalProperties dataclass
            psi0: the reference Slater determinant for expansion, usually the Hartree-Fock state
        '''
        self.name = "SingleSlater"
        
        self.spinbasis, self.nelec = psi0.shape
        if self.spinbasis != 2*prop.nbasis:
            raise Exception("The specified psi0 does not fit the dimension of the basis.")
           
        self.psi0 = psi0
        self.psia = self.psi0[::2, ::2]
        self.psib = self.psi0[1::2, 1::2]
        
        self.nup, self.ndown = prop.nup, prop.ndown
        self.nbasis = prop.nbasis
        self.h1e, self.eri = prop.h1e, prop.eri
        self.v_gamma, self.L_gamma = prop.v_gamma, prop.L_gamma
        self.nuclear_repulsion = prop.nuclear_repulsion
        self.Ga, self.Gb = gab(self.psia, self.psia), gab(self.psib, self.psib)
        self.G = [self.Ga, self.Gb]
        
        # define mean-field shift
        self.mf_shift = np.array([])
        for v in self.v_gamma:
            self.mf_shift = np.append(self.mf_shift, self.compute_trial_one_body(v))
            
        # define mean-field subtracted one-body term v_0.
        self.v_0 = copy.deepcopy(prop.h_chem)
        for i in range(len(self.v_gamma)):
            self.v_0 -= self.mf_shift[i] * self.v_gamma[i]
            
        
    def compute_trial_energy(self, prop):
        '''This function computes the energy expectation value of trial state
        \langle \Psi_T|H|\Psi_T\rangle / \langle \Psi_T|\Psi_T\rangle
        Args:
            prop: ChemicalProperties
        Returns
            E = local_energy_generic_cholesky(prop, self.G)
        '''
        return local_energy_generic_cholesky(prop, self.G)[2]
    
    
    def compute_trial_one_body(self, v):
        '''This function computes the expectation value of one-body operator v
        \langle \Psi_T|v|\Psi_T\rangle / \langle \Psi_T|\Psi_T\rangle
        '''
        # assuming the v is in spin-orbital basis
        value = np.einsum("ij,ij->", v[::2,::2], self.Ga)
        value += np.einsum("ij,ij->", v[1::2, 1::2], self.Gb)
        return value
    
    
    def compute_ovlp(self, walker):
        '''This function computes the overlap between MSD trial and a walker, using generalized Wick's theorem
        \langle \Psi_T|\phi \rangle = \langle \psi_0|\phi\rangle (c_0^* + \sum_i c_i^* 
        \langle \psi_0|\prod_{\mu} a_{p_{\mu}}^{\dagger} a_{t_{\mu}}|\phi\rangle / \langle \psi_0|\phi \rangle)
        ''' 
        return np.linalg.det(self.psi0.T.conj() @ walker)
    
    
    def compute_one_body_local(self, walker, v):
        '''This function computes the local one-body estimator using generalized Wick's theorem:
        \langle \Psi_T|v|\phi\rangle / \langle \Psi_T|\phi\rangle
        Args:
            walker:
            v: one-body operatpr v = v_pq a_p^+ a_q
        Returns:
        
        '''
        # first check dimentions
        if (walker.shape[0] != self.spinbasis) or (walker.shape[1] != self.nelec):
            raise Exception("The input walker state has a different number of basis or electrons.")
        
        if v.shape[0] == self.spinbasis:
            v_a, v_b = v[::2, ::2], v[1::2, 1::2]
        elif v.shape[0] == self.nbasis:   # h1e already in spatial orbital
            v_a, v_b = v, v
        
        # define the Greens and modified Green's function with input walker state
        Ga = gab(self.psia, walker[::2, ::2])
        Ga = np.array(Ga, dtype=np.complex128)
        Gb = gab(self.psib, walker[1::2, 1::2])
        Gb = np.array(Gb, dtype=np.complex128)
        
        value = np.einsum("ij,ij->", v_a, Ga)
        value += np.einsum("ij,ij->", v_b, Gb)
        return value
    
    
    def compute_local_energy(self, walker):
        Ga = gab(self.psia, walker[::2, ::2])
        Ga = np.array(Ga, dtype=np.complex128)
        Gb = gab(self.psib, walker[1::2, 1::2])
        Gb = np.array(Gb, dtype=np.complex128)
        G = [Ga, Gb]
        
        return local_energy_generic_cholesky(self, G)[2]
