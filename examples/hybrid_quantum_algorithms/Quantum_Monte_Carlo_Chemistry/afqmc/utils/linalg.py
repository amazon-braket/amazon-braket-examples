import numpy as np
from numba import njit, guvectorize
from scipy.linalg import det, qr

def reortho(A: np.ndarray):
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

"""
Next we define the function to calculate matrix pfaffian

"""

@guvectorize(
    ['void(complex128[:,:], complex128[:])'],
    '(n,n)->()',
)
def pfaffian_LTL(A, out):
    n, m = A.shape
    A = A.copy()
    
    pfaffian_val = 1.0
    for k in range(0, n - 1, 2):
        # First, find the largest entry in A[k+1:,k] and
        # permute it to A[k+1,k]
        kp = k + 1 + np.abs(A[k + 1 :, k]).argmax()
        
        # Check if we need to pivot
        if kp != k + 1:
            # interchange rows k+1 and kp
            temp = A[k + 1, k:].copy()
            A[k + 1, k:] = A[kp, k:]
            A[kp, k:] = temp
            
            # Then interchange columns k+1 and kp
            temp = A[k:, k + 1].copy()
            A[k:, k + 1] = A[k:, kp]
            A[k:, kp] = temp
            
            # every interchange corresponds to a "-" in det(P)
            pfaffian_val *= -1
        
        # Now form the Gauss vector
        #if A[k + 1, k] != 0.0:
        if abs(A[k + 1, k]) > 1E-8:
            tau = A[k, k + 2 :].copy()

            # tau = tau / A[k, k + 1] # not supported, replaced by for-loop
            for i in range(len(tau)):
                tau[i] = tau[i] / A[k, k + 1]

            pfaffian_val *= A[k, k + 1]

            if k + 2 < n:
                # Update the matrix block A(k+2:,k+2)
                # A[k + 2 :, k + 2 :] = A[k + 2 :, k + 2 :] + np.outer(
                #     tau, A[k + 2 :, k + 1]
                # ) # not supported, replaced by for-loops
                vector1 = tau
                vector2 = A[k + 2 :, k + 1]
                for i in range(len(vector1)):
                    for j in range(len(vector2)):
                        row = k+2+i
                        col = k+2+j
                        A[row][col] = A[row][col] + vector1[i] * vector2[j]
                
                # A[k + 2 :, k + 2 :] = A[k + 2 :, k + 2 :] - np.outer(
                #     A[k + 2 :, k + 1], tau
                # ) # not supported, replaced by for-loops
                vector1 = A[k + 2 :, k + 1]
                vector2 = tau
                for i in range(len(vector1)):
                    for j in range(len(vector2)):
                        row = k+2+i
                        col = k+2+j
                        A[row][col] = A[row][col] - vector1[i] * vector2[j]
        else:
            out[0] = 0.0
            return None
            
    out[0] = pfaffian_val
    
    
"""
Next we define functions for polyfit compatible with Numba
"""
@njit("complex128[:,:](complex128[:], int64)")
def _coeff_mat(x, deg):
    mat_ = np.zeros(shape=(x.shape[0], deg+1), dtype=np.complex128)
    const = np.ones_like(x, dtype=np.complex128)
    mat_[:, 0] = const
    mat_[:, 1] = x
    if deg > 1:
        for n in range(2, deg + 1):
            mat_[:, n] = x**n
    return mat_

@njit("complex128[:](complex128[:,:], complex128[:])")
def _fit_x(a, b):
    # linalg solves ax = b
    det_ = np.linalg.lstsq(a, b)[0]
    return det_

@njit("complex128[:](complex128[:], complex128[:], int64)")
def fit_poly(x, y, deg):
    a = _coeff_mat(x, deg)
    p = _fit_x(a, y)
    # The order renders p[0] being the coefficient of lowest order
    return p