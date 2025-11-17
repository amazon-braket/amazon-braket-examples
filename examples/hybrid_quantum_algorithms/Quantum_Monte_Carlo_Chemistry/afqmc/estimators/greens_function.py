import numpy as np
import scipy.linalg


def gab(A, B):
    """This function computes the one-body Green's function
    G_pq = (V_{\phi} (U_{\psi}^{\dagger} V_{\phi})^{-1} U_{\psi}^{\dagger})_{qp}
    Args:
        psi, phi: np.ndarray
    Returns:
        G: one-body Green's function
    """
    O = np.dot(B.T, A.conj())
    GHalf = np.dot(scipy.linalg.inv(O), B.T)
    G = np.dot(A.conj(), GHalf)
    return G


def gab_mod(A, B):
    r"""One-particle Green's function.
    .. math::
        \langle \psi_A|c_i^{\dagger}c_j|\phi_B\rangle / \langle \psi_A|\phi_B\rangle
        = [B(A^{\dagger}B)^{-1}A^{\dagger}]_{ji}
        = [A* @ (B.T @ A*)^{-1} @ B.T]_{ij}
    where :math:`A,B` are the matrices representing the Slater determinants
    :math:`|\psi_{A,B}\rangle`.
    For example, usually A would represent (an element of) the trial wavefunction.
    .. warning::
        Assumes A and B are not orthogonal.
    Parameters
    ----------
    A : :class:`numpy.ndarray`
        Matrix representation of the bra used to construct G.
    B : :class:`numpy.ndarray`
        Matrix representation of the ket used to construct G.
    Returns
    -------
    GAB : :class:`numpy.ndarray`
        (One minus) the green's function.
    """
    O = np.dot(B.T, A.conj())
    GHalf = np.dot(scipy.linalg.inv(O), B.T)
    G = np.dot(A.conj(), GHalf)
    return (G, GHalf)


def gab_spin(A, B, na, nb):
    GA, GAH = gab_mod(A[:, :na], B[:, :na])
    if nb > 0:
        GB, GBH = gab_mod(A[:, na:], B[:, na:])
    return np.array([GA, GB]), [GAH, GBH]


def gab_mod_ovlp(A, B):
    r"""One-particle Green's function.
    This actually returns 1-G since it's more useful, i.e.,
    .. math::
        \langle \phi_A|c_i^{\dagger}c_j|\phi_B\rangle =
        [B(A^{\dagger}B)^{-1}A^{\dagger}]_{ji}
    where :math:`A,B` are the matrices representing the Slater determinants
    :math:`|\psi_{A,B}\rangle`.
    For example, usually A would represent (an element of) the trial wavefunction.
    .. warning::
        Assumes A and B are not orthogonal.
    Parameters
    ----------
    A : :class:`numpy.ndarray`
        Matrix representation of the bra used to construct G.
    B : :class:`numpy.ndarray`
        Matrix representation of the ket used to construct G.
    Returns
    -------
    GAB : :class:`numpy.ndarray`
        (One minus) the green's function.
    """
    inv_O = scipy.linalg.inv(np.dot(B.T, A.conj()))
    GHalf = np.dot(inv_O, B.T)
    G = np.dot(A.conj(), GHalf)
    return (G, GHalf, inv_O)