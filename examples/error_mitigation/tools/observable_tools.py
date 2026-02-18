import networkx as nx
import numpy as np

from braket.circuits.observables import Hermitian, I, Sum, TensorProduct, X, Y, Z

_PAULI_OBSERVABLES = {"X": X, "Y": Y, "Z": Z, "I":I}

PAULI_PHASE_PRODUCT = {
    "X":{"Y":+1j,"Z":-1j},
    "Y":{"X":-1j,"Z":+1j},
    "Z":{"X":+1j,"Y":-1j}
}

PAULI_PRODUCT = {
    "X":{"Y":"Z","Z":"Y"},
    "Y":{"X":"Z","Z":"X"},
    "Z":{"X":"Y","Y":"X"}
}


def matrix_to_pauli(obs : Hermitian | np.ndarray, tol : float = 1e-12) -> list[tuple[complex,str]]:
    """Decompose a Hermitian observable or matrix into a sum of Pauli terms.
    
    Args:
        obs (Hermitian) : a Hermitian observable
        tol (float) : numerical tolerance 
    """
    match obs:
        case Hermitian():
            matrix = np.copy(obs._matrix)
        case np.ndarray():
            matrix = obs
    n_qubits = round(np.log2(matrix.shape[0]))
    dim = matrix.shape[0]
    terms = []
    nonzero_rows, nonzero_cols = np.nonzero(np.abs(matrix) > tol)        
    # Group by XOR pattern
    xor_groups = set()
    for r, c in zip(nonzero_rows, nonzero_cols):
        xor_pattern = r ^ c
        if xor_pattern not in xor_groups:
            xor_groups.add(xor_pattern)
    terms = None
    while len(xor_groups)>0:    
        # Process largest XOR group, no;
        key = xor_groups.pop() 
        x_pauli = "".join(["I" if i=="0" else "X" for i in "{:0{}b}".format(key, n_qubits)])
        diag = [matrix[c, c ^ key] for c in range(dim)]
        for c in range(dim):
            matrix[c,c ^ key] = 0
        pauli_coeffs = _coeff_to_pauli(
            _fast_walsh_hadamard(diag),
                               num_qubits=n_qubits,
                               threshold=tol)
        for c, p in pauli_coeffs:
            pauli,phase = _pauli_mul(p, x_pauli)
            if terms is None:
                terms = [(c * phase, pauli)]
            else:
                terms.append((c * phase, pauli))
    return terms

def _fast_walsh_hadamard(diag_entries):
    """Fast Walsh-Hadamard transform on diagonal entries."""
    v = np.array(diag_entries, dtype=complex)
    n = len(v)
    h = 1
    while h < n:
        for i in range(0, n, h * 2):
            for j in range(i, i + h):
                x = v[j]
                y = v[j + h]
                v[j] = x + y
                v[j + h] = x - y
        h *= 2
    return v / len(v)

def _pauli_mul(a : str,b : str):
    """ perform pauli multiplication """
    return "".join([
        "I" if ai==bi 
        else ai if bi=="I" 
        else bi if ai=="I"
        else PAULI_PRODUCT[ai][bi] for ai,bi in zip(a,b)
        ]), np.prod([
            1 if ai==bi or ai=="I" or bi=="I"
            else PAULI_PHASE_PRODUCT[ai][bi] for ai,bi in zip(a,b)])

def _coeff_to_pauli(entries : list, 
                   num_qubits : int, 
                   threshold = 1e-12,
                   ):
    paulis = []
    for n,c in enumerate(entries):
        if abs(c)>threshold:
            paulis.append((c,"".join(
                ["I" if k=="0" else "Z" for k in "{:0{}b}".format(n,num_qubits)]
            )))
    return paulis


def pauli_from_observable( 
        observable: TensorProduct | I | X | Y | Z,
        nq: int | None = None,
        ) -> tuple[complex, str]:
    """Create Pauli from Braket Observable.

    Args:
        observable: Braket observable (single Pauli or tensor product).
        nq: Total number of qubits. If None, inferred from observable.

    Returns:
        tuple: coefficient and str representation

    Example:
        >>> obs = 0.5 * (X(0) @ Y(1))
        >>> ps = pauli_from_observable(obs)
    """
    has_targets = len(observable.targets) > 0
    if nq is None:
        nq = (max(observable.targets) + 1 if has_targets
                else getattr(observable, "__len__", [0].__len__)())
    if nq == 1:
        return (observable.coefficient,observable.ascii_symbols[0])
    pstr = ["I"] * nq
    if hasattr(observable, "factors"):
        for i, term in enumerate(observable.factors):
            qubit = int(term.targets) if has_targets else i
            pstr[qubit] = term.ascii_symbols[0]
    else:
        pstr[int(observable.targets[0])] = observable.ascii_symbols[0]
    return  (observable.coefficient,"".join(pstr))

def qubit_wise_commuting(p1: str | tuple, p2: str | tuple) -> bool:
    """Check if two Pauli strings are qubit-wise commuting. """
    if isinstance(p1,tuple):
        p1, p2 = p1[1], p2[1]
    return all(a == 'I' or b == 'I' or a == b for a, b in zip(p1, p2))

def group_signature(paulis: list[str]) -> str:
    """Create signature string for a group of qubit-wise commuting Paulis."""
    if isinstance(paulis[0], tuple):
        paulis = [p[1] for p in paulis]
    signature = ['I'] * len(paulis[0])
    for pauli in paulis:
        for i, p in enumerate(pauli):
            if p != 'I':
                if signature[i] == 'I':
                    signature[i] = p
                elif signature[i] != p:
                    raise ValueError(f"Conflicting Paulis at position {i}: {signature[i]} vs {p}")
    return ''.join(signature)

def pauli_grouping(paulis: list[str] | list[tuple[float, str]]) -> tuple[list[str], list[list[str]]]:
    """Group Pauli strings by qubit-wise commutation.
    
    Returns:
        signatures: List of group signature strings
        groups: List of lists, each containing Pauli strings in that group
    """
    # Build anticommutation graph
    G = nx.Graph()
    G.add_nodes_from(range(len(paulis)))
    
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not qubit_wise_commuting(paulis[i], paulis[j]):
                G.add_edge(i, j)
    
    # Greedy coloring
    coloring = nx.greedy_color(G, strategy='largest_first')
    
    # Group by color
    color_groups = {}
    for node, color in coloring.items():
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append(paulis[node])
    
    # Create signatures and groups
    signatures = []
    groups = []
    for group in color_groups.values():
        signatures.append(group_signature(group))
        groups.append(group)
    
    return signatures, groups

def tensor_from_string(
        pstr : str,
        include_trivial: bool = False) -> TensorProduct:
        """Returns the observable corresponding to the unsigned part of the Pauli string.

        For example, for a Pauli string -XYZ, the corresponding observable is X ⊗ Y ⊗ Z.

        Args:
            include_trivial (bool): Whether to include explicit identity factors in the observable.
                Default: False.

        Returns:
            TensorProduct: The tensor product of the unsigned factors in the Pauli string.
        """
        return TensorProduct(
            [_PAULI_OBSERVABLES[p](n) for n,p in enumerate(pstr) if p != "I" or include_trivial])
