import os
import pennylane as qp
import numpy as np
from afqmc.utils.matchgate import (
    apply_gaussian_givens,
    apply_pauli_layer,
    compile_gaussian_givens,
    givens_schedule,
)

num_qubits = 4

def run(shadow_size: int, shots: int, device: qp.device):
    print("Perform shadow tomography")
    seed = int(os.environ.get("SEED", 1234))
    rng = np.random.default_rng(seed)

    # The rotation schedule depends only on the number of qubits, not on Q. Computing
    # it once is what lets every snapshot share one circuit.
    schedule = givens_schedule(num_qubits)

    @qp.qnode(device, shots=shots)
    def hydrogen_shadow_circuit(thetas, paulis):
        """One fixed circuit, for a single snapshot or a batch of them.

        thetas are (28,) or (batch, 28); paulis are (8,) or (batch, 8).
        """
        qp.Hadamard(wires=0)
        qp.CNOT(wires=[0, 1])
        qp.DoubleExcitation(0.12, wires=[0, 1, 2, 3])
        apply_gaussian_givens(thetas, schedule)
        apply_pauli_layer(paulis)
        return qp.counts()

    q_list = []
    q_save = []
    for _ in range(shadow_size):
        q, signed_per = random_signed_permutation(2 * num_qubits, rng)
        q_save.append(signed_per.tolist())
        q_list.append(q)
    print("The random signed matrices are successfully generated.")

    compiled = [compile_gaussian_givens(q) for q in q_list]
    thetas = np.stack([angles for _, angles, _ in compiled])
    paulis = np.stack([pauli_vector for _, _, pauli_vector in compiled])

    print(f"Execute {shadow_size} quantum tasks at {shots} each on {device}...")
    counts_batch = hydrogen_shadow_circuit(thetas, paulis)
    output = [{bits: int(count) for bits, count in counts.items()} for counts in counts_batch]

    print('All the measurements are completed.')

    return output, q_save


def random_signed_permutation(size, rng):
    """Generating size 2n signed permutation matrix Q, from Borel group B(2n).
    This will save matchgate circuit depth compared to Orthogonal group;

    Draws from an explicit Generator rather than numpy's global state, so the run is
    reproducible from SEED alone.
    """
    q = np.zeros((size, size))
    permutation = rng.permutation(size)
    save = np.array([i+1 for i in permutation])
    sign = rng.integers(2, size=size)

    for i in range(size):
        q[permutation[i], i] = (-1)**sign[i]
        save[i] *= (-1)**sign[i]
    return q, save