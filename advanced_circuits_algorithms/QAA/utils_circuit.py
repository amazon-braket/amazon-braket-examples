import numpy as np
from braket.circuits import Circuit, circuit

def get_unitary(self):
    """
    Funtion to get the unitary matrix corresponding to an entire circuit.
    Acts on self and returns the corresponding unitary
    """
    num_qubits = self.qubit_count
    
    # Define the unitary matrix. Start with the identity matrix.
    # Reshape the unitary into a tensor with the right number of indices (given by num_qubits)
    unitary = np.reshape(np.eye(2**num_qubits, 2**num_qubits), [2] * 2 * num_qubits)
    
    # Iterate over the moments in the circuit
    for key in self.moments:
        
        # Get the matrix corresponding to the gate
        matrix = self.moments[key].operator.to_matrix()
        # Get the target indices for the gate
        targets = self.moments[key].target

        # Reshape the gate matrix
        gate_matrix = np.reshape(matrix, [2] * len(targets) * 2)
        
        # Construct a tuple specifying the axes along which we contract (i.e., which qubits the gate acts on)
        axes = (
            np.arange(len(targets), 2 * len(targets)),
            targets,
        )
        
        # Apply the gate by contracting the existing unitary with the new gate
        unitary = np.tensordot(gate_matrix, unitary, axes=axes)

        # tensordot causes the axes contracted to end up in the first positions.
        # We'll need to invert this permutation to put the indices in the correct place
        
        # Find the indices that are not used
        unused_idxs = [idx for idx in range(2*num_qubits) if idx not in targets]
        
        # The new order of indices is given by 
        permutation = list(targets) + unused_idxs
        
        # Find the permutation that undoes this reordering
        inverse_permutation = np.argsort(permutation)
        
        # Relabel the qubits according to this inverse_permutation
        unitary = np.transpose(unitary, inverse_permutation)

    # Reshape to a 2^N x 2^N matrix (for N=num_qubits)and return
    unitary = np.reshape(unitary, (2**num_qubits, 2**num_qubits))
    return unitary

def adjoint(self):
    """Generates a circuit object corresponding to the adjoint of a given circuit, in which the order
    of gates is reversed, and each gate is the adjoint (i.e., conjugate transpose) of the original.
    """

    adjoint_circ = Circuit()
    
    # Loop through the instructions (gates) in the circuit:
    for instruction in self.instructions:           
        # Extract the transpose of the unitary matrix for each circuit element in the original circuit
        adjoint_matrix = instruction.operator.to_matrix().T.conj()
        
        # Add a gate to the start of the new circuit for which the unitary matrix is the adjoint found above.
        # Add an "H" to the display name. Note the order of operations here:
        # (AB)^H = B^H A^H, where H is adjoint, thus we prepend new gates, rather than append.
        adjoint_gate = Circuit().unitary(matrix=adjoint_matrix, targets=instruction.target, display_name="".join(instruction.operator.ascii_symbols)+"H")
        adjoint_circ = adjoint_gate.add(adjoint_circ)
    return adjoint_circ