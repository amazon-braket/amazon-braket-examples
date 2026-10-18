from pathlib import Path

import numpy as np
import pennylane as qml
import pytest


@pytest.mark.parametrize("broadcast", [False, True])
def test_compiled_matchgate_transforms_majoranas(monkeypatch, broadcast):
    example = Path(__file__).resolve().parents[2] / "examples/hybrid_quantum_algorithms"
    monkeypatch.syspath_prepend(str(example / "Quantum_Monte_Carlo_Chemistry"))
    from afqmc.utils.matchgate import (
        apply_gaussian_givens,
        apply_pauli_layer,
        compile_gaussian_givens,
    )

    orthogonal, _ = np.linalg.qr(np.random.default_rng(0).normal(size=(4, 4)))
    # Exercise both determinant signs, including the trailing Pauli layer.
    matrices = [orthogonal, orthogonal @ np.diag([-1, 1, 1, 1])]
    compiled = [compile_gaussian_givens(matrix) for matrix in matrices]
    schedule = compiled[0][0]

    def circuit(thetas, paulis):
        apply_gaussian_givens(thetas, schedule)
        apply_pauli_layer(paulis)

    circuit_matrix = qml.matrix(circuit, wire_order=[0, 1])
    if broadcast:
        thetas = np.stack([entry[1] for entry in compiled])
        paulis = np.stack([entry[2] for entry in compiled])
        unitaries = circuit_matrix(thetas, paulis)
    else:
        unitaries = [circuit_matrix(thetas, paulis) for _, thetas, paulis in compiled]

    majoranas = np.array(
        [
            qml.matrix(operator, wire_order=[0, 1])
            for operator in (qml.X(0), qml.Y(0), qml.Z(0) @ qml.X(1), qml.Z(0) @ qml.Y(1))
        ]
    )
    for matrix, unitary in zip(matrices, unitaries, strict=True):
        np.testing.assert_allclose(
            unitary.conj().T @ majoranas @ unitary,
            np.tensordot(matrix, majoranas, axes=1),
            rtol=0,
            atol=1e-12,
        )
