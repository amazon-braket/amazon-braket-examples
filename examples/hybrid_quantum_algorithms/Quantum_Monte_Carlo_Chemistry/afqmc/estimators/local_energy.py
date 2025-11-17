import numpy as np

def local_energy_generic(h1e: np.ndarray, eri: np.ndarray, nuclear_repulsion: int, G):
    r"""Calculate local for generic two-body hamiltonian.
    This uses the full (spatial) form for the two-electron integrals stored in modified physicist's notation.
    Args:
        h1e: np.ndarray
        eri: np.ndarray
        nuclear_repulsion: int
        G (np.ndarray): Walker's "green's function"
    Returns:
        T + V + enuc (float): kinetic, potential energies and nuclear repulsion energy.
    """
    e1 = np.einsum("ij,ij->", h1e, G[0]) + np.einsum("ij,ij->", h1e, G[1])

    euu = 0.5 * (np.einsum("ijkl,il,jk->", eri, G[0], G[0]) - np.einsum("ijkl,ik,jl->", eri, G[0], G[0]))
    edd = 0.5 * (np.einsum("ijkl,il,jk->", eri, G[1], G[1]) - np.einsum("ijkl,ik,jl->", eri, G[1], G[1]))
    eud = 0.5 * np.einsum("ijkl,il,jk->", eri, G[0], G[1])
    edu = 0.5 * np.einsum("ijkl,il,jk->", eri, G[1], G[0])
    e2 = euu + edd + eud + edu
    
    return e1, e2, e1+e2+nuclear_repulsion


def local_energy_generic_cholesky(trial, G):
    r"""Calculate local for generic two-body hamiltonian. This uses the cholesky decomposed two-electron integrals.
    E = H_0 + \sum_ij h_ij G_ij + 1/2*\sum_{\gamma} \sum_{pqrs} L^{\gamma}_{pr} L^{\gamma}_{qs} (G_pr G_qs - G_ps G_qr)
    Parameters
    ----------
    trial or prop should be both fit
    G: [Ga, Gb], list of `numpy.ndarray`, Walker's "green's function" in spin up and down sector
    
    Returns
    -------
    (E, T, V): tuple
        Total , one and two-body energies.
    """
    # Element wise multiplication.
    e1b = np.sum(trial.h1e*G[0]) + np.sum(trial.h1e*G[1])
    nbasis = trial.nbasis
    nchol = len(trial.L_gamma)
    
    # since RHF, the spin-up and spin-down component will be identical
    chol_vecs = [i[::2,::2] for i in trial.L_gamma]
    chol_vecs = np.array(chol_vecs).reshape((-1, nbasis**2)).T
    Ga, Gb = G[0], G[1]
    
    # compute \sum_pr L^{\gamma}_{pr} G_pr
    if np.isrealobj(chol_vecs):
        Xa = chol_vecs.T.dot(Ga.real.ravel()) + 1.0j*chol_vecs.T.dot(Ga.imag.ravel())
        Xb = chol_vecs.T.dot(Gb.real.ravel()) + 1.0j*chol_vecs.T.dot(Gb.imag.ravel())
    else:
        Xa = chol_vecs.T.dot(Ga.ravel())
        Xb = chol_vecs.T.dot(Gb.ravel())
        
    ecoul = np.dot(Xa, Xa)
    ecoul += np.dot(Xb, Xb)
    ecoul += 2*np.dot(Xa, Xb)
    
    T = np.zeros((nbasis, nbasis), dtype=np.complex128)
    
    GaT = Ga.T.copy()
    GbT = Gb.T.copy()
    
    exx = 0.0j  # we will iterate over cholesky index to update Ex energy for alpha and beta
    if np.isrealobj(chol_vecs):
        for x in range(nchol):
            # compute \sum_p G_{sp} L^{\gamma}_{pr}
            Lmn = chol_vecs[:, x].reshape((nbasis, nbasis))
            T[:, :].real = GaT.real.dot(Lmn)
            T[:, :].imag = GaT.imag.dot(Lmn)
            # compute \sum_rs T_{sr} T_{rs}
            
            exx += np.trace(T.dot(T))
            T[:, :].real = GbT.real.dot(Lmn)
            T[:, :].imag = GbT.imag.dot(Lmn)
            exx += np.trace(T.dot(T))
    else:
        for x in range(nchol):
            Lmn = chol_vecs[:, x].reshape((nbasis, nbasis))
            T[:, :] = GaT.dot(Lmn)
            exx += np.trace(T.dot(T))
            T[:, :] = GbT.dot(Lmn)
            exx += np.trace(T.dot(T))
            
    e2b = 0.5*(ecoul - exx)
    return e1b, e2b, e1b+e2b+trial.nuclear_repulsion