import numpy as np
from braket.circuits import Circuit, circuit


def get_unitary(self):
    """
    Function to get the unitary matrix corresponding to an entire circuit.
    Acts on self and returns the corresponding unitary
    """
    num_qubits = int(
        max(self.qubits) + 1
    )  # Coincides with self.qubit_count when qubit indexing is contiguous.

    # Define the unitary matrix. Start with the identity matrix.
    # Reshape the unitary into a tensor with the right number of indices (given by num_qubits)
    unitary = np.reshape(np.eye(2 ** num_qubits, 2 ** num_qubits), [2] * 2 * num_qubits)

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
        unused_idxs = [idx for idx in range(2 * num_qubits) if idx not in targets]

        # The new order of indices is given by
        permutation = list(targets) + unused_idxs

        # Find the permutation that undoes this reordering
        inverse_permutation = np.argsort(permutation)

        # Relabel the qubits according to this inverse_permutation
        unitary = np.transpose(unitary, inverse_permutation)

    # Reshape to a 2^N x 2^N matrix (for N=num_qubits)and return
    unitary = np.reshape(unitary, (2 ** num_qubits, 2 ** num_qubits))
    return unitary


def adjoint(self):
    """Generates a circuit object corresponding to the adjoint of a given circuit, in which the order
    of gates is reversed, and each gate is the adjoint (i.e., conjugate transpose) of the original.
    """

    adjoint_circ = Circuit()

    # Loop through the instructions (gates) in the circuit:
    for instruction in self.instructions:
        # Save the operator name and target
        op_name = instruction.operator.name
        target = instruction.target
        angle = None
        # If the operator has an attribute called 'angle', save that too
        if hasattr(instruction.operator, "angle"):
            angle = instruction.operator.angle

        # To make use of native gates, we'll define the adjoint for each
        if op_name == "H":
            adjoint_gate = Circuit().h(target)
        elif op_name == "I":
            adjoint_gate = Circuit().i(target)
        elif op_name == "X":
            adjoint_gate = Circuit().x(target)
        elif op_name == "Y":
            adjoint_gate = Circuit().y(target)
        elif op_name == "Z":
            adjoint_gate = Circuit().z(target)
        elif op_name == "S":
            adjoint_gate = Circuit().si(target)
        elif op_name == "Si":
            adjoint_gate = Circuit().s(target)
        elif op_name == "T":
            adjoint_gate = Circuit().ti(target)
        elif op_name == "Ti":
            adjoint_gate = Circuit().t(target)
        elif op_name == "V":
            adjoint_gate = Circuit().vi(target)
        elif op_name == "Vi":
            adjoint_gate = Circuit().v(target)
        elif op_name == "Rx":
            adjoint_gate = Circuit().rx(target, -angle)
        elif op_name == "Ry":
            adjoint_gate = Circuit().ry(target, -angle)
        elif op_name == "Rz":
            adjoint_gate = Circuit().rz(target, -angle)
        elif op_name == "PhaseShift":
            adjoint_gate = Circuit().phaseshift(target, -angle)
        elif op_name == "CNot":
            adjoint_gate = Circuit().cnot(*target)
        elif op_name == "Swap":
            adjoint_gate = Circuit().swap(*target)
        elif op_name == "ISwap":
            adjoint_gate = Circuit().pswap(*target, -np.pi / 2)
        elif op_name == "PSwap":
            adjoint_gate = Circuit().pswap(*target, -angle)
        elif op_name == "XY":
            adjoint_gate = Circuit().xy(*target, -angle)
        elif op_name == "CPhaseShift":
            adjoint_gate = Circuit().cphaseshift(*target, -angle)
        elif op_name == "CPhaseShift00":
            adjoint_gate = Circuit().cphaseshift00(*target, -angle)
        elif op_name == "CPhaseShift01":
            adjoint_gate = Circuit().cphaseshift01(*target, -angle)
        elif op_name == "CPhaseShift10":
            adjoint_gate = Circuit().cphaseshift10(*target, -angle)
        elif op_name == "CY":
            adjoint_gate = Circuit().cy(*target)
        elif op_name == "CZ":
            adjoint_gate = Circuit().cz(*target)
        elif op_name == "XX":
            adjoint_gate = Circuit().xx(*target, -angle)
        elif op_name == "YY":
            adjoint_gate = Circuit().yy(*target, -angle)
        elif op_name == "ZZ":
            adjoint_gate = Circuit().zz(*target, -angle)
        elif op_name == "CCNot":
            adjoint_gate = Circuit().ccnot(*target)
        elif op_name == "CSwap":
            adjoint_gate = Circuit().cswap(*target)

        # If the gate is a custom unitary, we'll create a new custom unitary
        else:
            # Extract the transpose of the unitary matrix for the unitary gate
            adjoint_matrix = instruction.operator.to_matrix().T.conj()

            # Define a gate for which the unitary matrix is the adjoint found above.
            # Add an "H" to the display name.
            adjoint_gate = Circuit().unitary(
                matrix=adjoint_matrix,
                targets=instruction.target,
                display_name="".join(instruction.operator.ascii_symbols) + "H",
            )

        # Add the new gate to the adjoint circuit. Note the order of operations here:
        # (AB)^H = B^H A^H, where H is adjoint, thus we prepend new gates, rather than append.
        adjoint_circ = adjoint_gate.add(adjoint_circ)
    return adjoint_circ
