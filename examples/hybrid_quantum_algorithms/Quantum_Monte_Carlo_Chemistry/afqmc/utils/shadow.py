import numpy as np

'''
This file contains functions to sample classical shadows for performing shadow tomography
'''

def calculate_classical_shadow(circuit_template, Q_list):
    """
    Collect matchgate shadows by running every random rotation through ONE broadcast circuit
    rather than one circuit per snapshot.

    Each Q is compiled classically into (schedule, angles, pauli_vector) by
    compile_gaussian_givens; the schedule (rotation topology) is identical for all Q of the
    same size, so only the angles and Pauli layer vary. Stacking those across all snapshots
    and passing them to a single fixed-topology QNode lets the simulator evaluate the whole
    batch in one vectorized call (and maps cleanly onto Braket program sets / concurrent
    execution on hardware).

    Results are stored in a compact "structure-of-arrays" format that keeps only the raw
    generators of each snapshot -- the measured bitstrings and the signed permutation matrices
    -- rather than the dense covariance/rotation matrices, which are reconstructed cheaply on
    the fly during post-processing. This keeps both the stored/serialized size and the
    multiprocessing pickling cost small (O(N_snap * n) integers instead of O(N_snap * n^2)
    complex numbers).
    Args:
        circuit_template (function): a Pennylane QNode taking (thetas, paulis) -- stacked
            rotation angles of shape (N_snap, n_rot) and Pauli vectors of shape (N_snap, 2n)
            -- and returning qp.counts() broadcast over the batch dimension.
        Q_list (list): random signed permutation matrices (dense); one snapshot per entry.
    Returns:
        shadow (dict): compact shadow with arrays
            "perm"    (N_snap, 2n) int16 : column of the +/-1 entry in each row of Q,
            "sign"    (N_snap, 2n) int8  : the +/-1 value,
            "bits"    (N_out,  n)  uint8 : measured bitstrings,
            "count"   (N_out,)     int32 : shot count for each outcome,
            "snap_id" (N_out,)     int32 : index of the snapshot each outcome belongs to.
    """
    # Imported here (not at module scope) to avoid a circular import: matchgate imports
    # construct_covariance from this module.
    from afqmc.utils.matchgate import compile_gaussian_givens

    n_snap = len(Q_list)
    dim = Q_list[0].shape[0]  # 2n Majorana / mode dimension
    n = dim // 2

    perm = np.zeros((n_snap, dim), dtype=np.int16)
    sign = np.zeros((n_snap, dim), dtype=np.int8)
    for s, Q in enumerate(Q_list):
        perm[s], sign[s] = signed_permutation_to_compact(Q)

    # Classically compile every snapshot, then run them all through one broadcast circuit.
    compiled = [compile_gaussian_givens(Q) for Q in Q_list]
    thetas = np.stack([angles for _, angles, _ in compiled])
    paulis = np.stack([pauli_vector for _, _, pauli_vector in compiled])
    counts_batch = circuit_template(thetas, paulis)

    bits, count, snap_id = [], [], []
    for s, counts in enumerate(counts_batch):
        for b_str, c in counts.items():
            bits.append([int(ch) for ch in b_str])
            count.append(int(c))
            snap_id.append(s)

    return {
        "perm": perm,
        "sign": sign,
        "bits": np.asarray(bits, dtype=np.uint8).reshape(-1, n),
        "count": np.asarray(count, dtype=np.int32),
        "snap_id": np.asarray(snap_id, dtype=np.int32),
    }


def construct_covariance(b_str: str):
    '''This function takes in computational basis state b as a string, and output its covariance matrix C,
    computed directly from Eqn.(12) from https://arxiv.org/abs/2207.13723
    Args:
        b_str (str): string of measurement output statistics, e.g., '0000'
    Returns:
        C (np.ndarray): covariance matrix
    '''
    # get the number of fermionic mode
    n = len(b_str)
    C = np.zeros((2*n, 2*n), dtype=np.complex128)
    for i in range(n):
        C[2*i, 2*i+1] = (-1)**int(b_str[i])
        C[2*i+1, 2*i] = -C[2*i, 2*i+1]
        
    return C.astype('complex128')


def covariance_from_bits(bits):
    '''Reconstruct the covariance matrix of a computational-basis state from its bitstring.
    Numeric counterpart of construct_covariance, used to rebuild C from the compact "bits" array.
    Args:
        bits (np.ndarray): 1D array of 0/1 occupations of length n.
    Returns:
        C (np.ndarray): 2n x 2n complex128 covariance matrix.
    '''
    n = len(bits)
    C = np.zeros((2 * n, 2 * n), dtype=np.complex128)
    for i in range(n):
        C[2 * i, 2 * i + 1] = (-1) ** int(bits[i])
        C[2 * i + 1, 2 * i] = -C[2 * i, 2 * i + 1]
    return C


def random_signed_permutation(size):
    '''Generating size 2n signed permutation matrix Q, from Borel group B(2n).
       This will save matchgate circuit depth compared to Orthogonal group.
    '''
    Q = np.zeros((size, size))
    permutation = np.random.permutation(size)
    sign = np.random.randint(2, size=size)

    for i in range(size):
        Q[permutation[i], i] = (-1)**sign[i]
    return Q


def signed_permutation_to_compact(Q):
    '''Compress a dense signed permutation matrix Q to (perm, sign) arrays.
    Q has exactly one nonzero (+/-1) per column; perm[i] is the row of that entry in column i.
    Args:
        Q (np.ndarray): dense signed permutation matrix.
    Returns:
        (perm, sign): int16 array of row indices and int8 array of +/-1 values.
    '''
    dim = Q.shape[0]
    perm = np.zeros(dim, dtype=np.int16)
    sign = np.zeros(dim, dtype=np.int8)
    for i in range(dim):
        rows = np.nonzero(Q[:, i])[0]
        r = int(rows[0])
        perm[i] = r
        sign[i] = int(np.sign(np.real(Q[r, i])))
    return perm, sign


def compact_to_signed_permutation(perm, sign):
    '''Rebuild a dense signed permutation matrix from (perm, sign). Inverse of
    signed_permutation_to_compact.
    '''
    dim = len(perm)
    Q = np.zeros((dim, dim))
    for i in range(dim):
        Q[int(perm[i]), i] = sign[i]
    return Q


def shadow_from_json(output, Q_save):
    '''Convert the on-disk shadow JSON ({output, Q_save}) into the compact in-memory dict, without
    materializing any dense covariance/rotation matrices.
    Args:
        output: list (per snapshot) of {bitstring: count} dicts.
        Q_save: list (per snapshot) of signed, 1-indexed permutation vectors.
    Returns:
        shadow (dict): arrays perm/sign (N_snap, 2n) int; bits (N_out, n) uint8; count/snap_id (N_out,) int.
    '''
    q_save = np.asarray(Q_save)                       # (N_snap, 2n), signed 1-indexed
    perm = (np.abs(q_save) - 1).astype(np.int16)
    sign = np.sign(q_save).astype(np.int8)
    n = q_save.shape[1] // 2                           # number of qubits (fermionic modes)

    bits, count, snap_id = [], [], []
    for s, counts in enumerate(output):
        for b_str, c in counts.items():
            bits.append([int(ch) for ch in b_str])
            count.append(int(c))
            snap_id.append(s)

    return {
        "perm": perm,
        "sign": sign,
        "bits": np.asarray(bits, dtype=np.uint8).reshape(-1, n),
        "count": np.asarray(count, dtype=np.int32),
        "snap_id": np.asarray(snap_id, dtype=np.int32),
    }


def normalize_shadow(shadow):
    '''Return a shadow in the compact dict format, accepting either that dict or the legacy
    (outcomes, Q_list) tuple so that previously saved shadows still load.
    Args:
        shadow: compact dict (returned as-is) or legacy (outcomes, Q_list) tuple.
    Returns:
        shadow (dict): compact shadow dict (see calculate_classical_shadow).
    '''
    if isinstance(shadow, dict):
        return shadow

    outcomes, Q_list = shadow
    n_snap = len(Q_list)
    dim = Q_list[0].shape[0]
    n = dim // 2
    perm = np.zeros((n_snap, dim), dtype=np.int16)
    sign = np.zeros((n_snap, dim), dtype=np.int8)
    bits, count, snap_id = [], [], []
    for s, (Q, b_list) in enumerate(zip(Q_list, outcomes)):
        perm[s], sign[s] = signed_permutation_to_compact(Q)
        for C_b, c in b_list:
            # invert construct_covariance: C[2i, 2i+1] = (-1)^{b_i}
            bits.append([0 if np.real(C_b[2 * i, 2 * i + 1]) > 0 else 1 for i in range(n)])
            count.append(int(c))
            snap_id.append(s)
    return {
        "perm": perm,
        "sign": sign,
        "bits": np.asarray(bits, dtype=np.uint8).reshape(-1, n),
        "count": np.asarray(count, dtype=np.int32),
        "snap_id": np.asarray(snap_id, dtype=np.int32),
    }

