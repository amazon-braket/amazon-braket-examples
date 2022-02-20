# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import math

import numpy as np
import pytest

from braket.circuits import Gate, Observable
from braket.circuits.observables import observable_from_ir
from braket.circuits.quantum_operator_helpers import get_pauli_eigenvalues

testdata = [
    (Observable.I(), Gate.I(), ["i"], (), np.array([1, 1])),
    (Observable.X(), Gate.X(), ["x"], tuple([Gate.H()]), get_pauli_eigenvalues(1)),
    (
        Observable.Y(),
        Gate.Y(),
        ["y"],
        tuple([Gate.Z(), Gate.S(), Gate.H()]),
        get_pauli_eigenvalues(1),
    ),
    (Observable.Z(), Gate.Z(), ["z"], (), get_pauli_eigenvalues(1)),
    (Observable.H(), Gate.H(), ["h"], tuple([Gate.Ry(-math.pi / 4)]), get_pauli_eigenvalues(1)),
]

invalid_hermitian_matrices = [
    (np.array([[1]])),
    (np.array([1])),
    (np.array([0, 1, 2])),
    (np.array([[0, 1], [1, 2], [3, 4]])),
    (np.array([[0, 1, 2], [2, 3]], dtype=object)),
    (np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])),
    (Gate.T().to_matrix()),
]


@pytest.mark.parametrize(
    "testobject,gateobject,expected_ir,basis_rotation_gates,eigenvalues", testdata
)
def test_to_ir(testobject, gateobject, expected_ir, basis_rotation_gates, eigenvalues):
    expected = expected_ir
    actual = testobject.to_ir()
    assert actual == expected


@pytest.mark.parametrize(
    "testobject,gateobject,expected_ir,basis_rotation_gates,eigenvalues", testdata
)
def test_gate_equality(testobject, gateobject, expected_ir, basis_rotation_gates, eigenvalues):
    assert testobject.qubit_count == gateobject.qubit_count
    assert testobject.ascii_symbols == gateobject.ascii_symbols
    assert testobject.matrix_equivalence(gateobject)
    assert testobject.basis_rotation_gates == basis_rotation_gates
    assert np.allclose(testobject.eigenvalues, eigenvalues)


@pytest.mark.parametrize(
    "testobject,gateobject,expected_ir,basis_rotation_gates,eigenvalues", testdata
)
def test_basis_rotation_gates(
    testobject, gateobject, expected_ir, basis_rotation_gates, eigenvalues
):
    assert testobject.basis_rotation_gates == basis_rotation_gates


@pytest.mark.parametrize(
    "testobject,gateobject,expected_ir,basis_rotation_gates,eigenvalues", testdata
)
def test_eigenvalues(testobject, gateobject, expected_ir, basis_rotation_gates, eigenvalues):
    compare_eigenvalues(testobject, eigenvalues)


@pytest.mark.parametrize(
    "testobject,gateobject,expected_ir,basis_rotation_gates,eigenvalues", testdata
)
def test_observable_from_ir(testobject, gateobject, expected_ir, basis_rotation_gates, eigenvalues):
    assert testobject == observable_from_ir(expected_ir)


# Hermitian


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("matrix", invalid_hermitian_matrices)
def test_hermitian_invalid_matrix(matrix):
    Observable.Hermitian(matrix=matrix)


def test_hermitian_equality():
    matrix = Observable.H().to_matrix()
    a1 = Observable.Hermitian(matrix=matrix)
    a2 = Observable.Hermitian(matrix=matrix)
    a3 = Observable.Hermitian(matrix=Observable.I().to_matrix())
    a4 = "hi"
    assert a1 == a2
    assert a1 != a3
    assert a1 != a4


def test_hermitian_to_ir():
    matrix = Observable.I().to_matrix()
    obs = Observable.Hermitian(matrix=matrix)
    assert obs.to_ir() == [[[[1, 0], [0, 0]], [[0, 0], [1, 0]]]]


@pytest.mark.parametrize(
    "matrix,eigenvalues",
    [
        (np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([1, 1])),
        (np.array([[0, -1j], [1j, 0]]), np.array([-1.0, 1.0])),
        (np.array([[1, 1 - 1j], [1 + 1j, -1]]), np.array([-np.sqrt(3), np.sqrt(3)])),
    ],
)
def test_hermitian_eigenvalues(matrix, eigenvalues):
    compare_eigenvalues(Observable.Hermitian(matrix=matrix), eigenvalues)


def test_flattened_tensor_product():
    observable_one = Observable.Z() @ Observable.Y()
    observable_two = Observable.X() @ Observable.H()
    actual = Observable.TensorProduct([observable_one, observable_two])
    expected = Observable.TensorProduct(
        [Observable.Z(), Observable.Y(), Observable.X(), Observable.H()]
    )
    assert expected == actual


@pytest.mark.parametrize(
    "matrix,basis_rotation_matrix",
    [
        (
            np.array([[0.0, 1.0], [1.0, 0.0]]),
            np.array([[-0.70710678, 0.70710678], [0.70710678, 0.70710678]]).conj().T,
        ),
        (
            np.array([[0, -1j], [1j, 0]]),
            np.array(
                [[-0.70710678 + 0.0j, -0.70710678 + 0.0j], [0.0 + 0.70710678j, 0.0 - 0.70710678j]]
            )
            .conj()
            .T,
        ),
        (
            np.array([[1, 1 - 1j], [1 + 1j, -1]]),
            np.array(
                [
                    [-0.45970084 - 0.0j, 0.62796303 - 0.62796303j],
                    [-0.88807383 - 0.0j, -0.32505758 + 0.32505758j],
                ]
            ),
        ),
    ],
)
def test_hermitian_basis_rotation_gates(matrix, basis_rotation_matrix):
    expected_unitary = Gate.Unitary(matrix=basis_rotation_matrix)
    actual_rotation_gates = Observable.Hermitian(matrix=matrix).basis_rotation_gates
    assert actual_rotation_gates == tuple([expected_unitary])
    assert expected_unitary.matrix_equivalence(actual_rotation_gates[0])


@pytest.mark.xfail(raises=ValueError)
def test_observable_from_ir_hermitian_value_error():
    ir_observable = [[[[1.0, 0], [0, 1]], [[0.0, 1], [1, 0]]]]
    observable_from_ir(ir_observable)


def test_observable_from_ir_hermitian():
    ir_observable = [[[[1, 0], [0, 0]], [[0, 0], [1, 0]]]]
    actual_observable = observable_from_ir(ir_observable)
    assert actual_observable == Observable.Hermitian(matrix=np.array([[1.0, 0.0], [0.0, 1.0]]))


def test_hermitian_str():
    assert (
        str(Observable.Hermitian(matrix=np.array([[1.0, 0.0], [0.0, 1.0]])))
        == "Hermitian('qubit_count': 1, 'matrix': [[1.+0.j 0.+0.j], [0.+0.j 1.+0.j]])"
    )


# TensorProduct


def test_tensor_product_to_ir():
    t = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    assert t.to_ir() == ["z", "i", "x"]
    assert t.qubit_count == 3
    assert t.ascii_symbols == tuple(["Z@I@X"] * 3)


def test_tensor_product_matmul_tensor():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    t2 = Observable.TensorProduct(
        [Observable.Hermitian(matrix=Observable.I().to_matrix()), Observable.Y()]
    )
    t3 = t1 @ t2
    assert t3.to_ir() == ["z", "i", "x", [[[1.0, 0], [0, 0]], [[0, 0], [1.0, 0]]], "y"]
    assert t3.qubit_count == 5
    assert t3.ascii_symbols == tuple(["Z@I@X@Hermitian@Y"] * 5)


def test_tensor_product_matmul_observable():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    o1 = Observable.I()
    t = t1 @ o1
    assert t.to_ir() == ["z", "i", "x", "i"]
    assert t.qubit_count == 4
    assert t.ascii_symbols == tuple(["Z@I@X@I"] * 4)


@pytest.mark.xfail(raises=ValueError)
def test_tensor_product_eigenvalue_index_out_of_bounds():
    obs = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    obs.eigenvalue(8)


@pytest.mark.xfail(raises=ValueError)
def test_tensor_product_value_error():
    Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()]) @ "a"


def test_tensor_product_rmatmul_observable():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    o1 = Observable.I()
    t = o1 @ t1
    assert t.to_ir() == ["i", "z", "i", "x"]
    assert t.qubit_count == 4
    assert t.ascii_symbols == tuple(["I@Z@I@X"] * 4)


@pytest.mark.parametrize(
    "observable,eigenvalues",
    [
        (Observable.X() @ Observable.Y(), np.array([1, -1, -1, 1])),
        (Observable.X() @ Observable.Y() @ Observable.Z(), np.array([1, -1, -1, 1, -1, 1, 1, -1])),
        (Observable.X() @ Observable.Y() @ Observable.I(), np.array([1, 1, -1, -1, -1, -1, 1, 1])),
        (
            Observable.X()
            @ Observable.Hermitian(
                np.array([[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            )
            @ Observable.Y(),
            np.array([-1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, 1, -1, 1]),
        ),
    ],
)
def test_tensor_product_eigenvalues(observable, eigenvalues):
    compare_eigenvalues(observable, eigenvalues)
    # Test caching
    observable._factors = ()
    compare_eigenvalues(observable, eigenvalues)


@pytest.mark.parametrize(
    "observable,basis_rotation_gates",
    [
        (Observable.X() @ Observable.Y(), tuple([Gate.H(), Gate.Z(), Gate.S(), Gate.H()])),
        (
            Observable.X() @ Observable.Y() @ Observable.Z(),
            tuple([Gate.H(), Gate.Z(), Gate.S(), Gate.H()]),
        ),
        (
            Observable.X() @ Observable.Y() @ Observable.I(),
            tuple([Gate.H(), Gate.Z(), Gate.S(), Gate.H()]),
        ),
        (Observable.X() @ Observable.H(), tuple([Gate.H(), Gate.Ry(-np.pi / 4)])),
    ],
)
def test_tensor_product_basis_rotation_gates(observable, basis_rotation_gates):
    assert observable.basis_rotation_gates == basis_rotation_gates


def test_observable_from_ir_tensor_product():
    expected_observable = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    actual_observable = observable_from_ir(["z", "i", "x"])
    assert expected_observable == actual_observable


@pytest.mark.xfail(raises=ValueError)
def test_observable_from_ir_tensor_product_value_error():
    observable_from_ir(["z", "i", "foo"])


def compare_eigenvalues(observable, expected):
    assert np.allclose(observable.eigenvalues, expected)
    assert np.allclose(
        np.array([observable.eigenvalue(i) for i in range(2**observable.qubit_count)]),
        expected,
    )
