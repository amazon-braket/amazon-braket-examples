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

import functools

import numpy as np
import pytest

from braket.circuits.quantum_operator_helpers import (
    get_pauli_eigenvalues,
    is_cptp,
    is_hermitian,
    is_square_matrix,
    is_unitary,
    verify_quantum_operator_matrix_dimensions,
)

valid_unitary_hermitian_matrix = np.array([[0, 1], [1, 0]])

valid_CPTP_matrices = [
    np.array([[0, 1], [1, 0]]) / np.sqrt(2),
    np.array([[0, 1], [1, 0]]) / np.sqrt(2),
]

invalid_dimension_matrices = [
    (np.array([[1]])),
    (np.array([1])),
    (np.array([0, 1, 2])),
    (np.array([[0, 1], [1, 2], [3, 4]])),
    (np.array([[0, 1, 2], [2, 3]], dtype=object)),
    (np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])),
]

invalid_unitary_matrices_false = [(np.array([[0, 1], [1, 1]])), (np.array([[1, 2], [3, 4]]))]

invalid_hermitian_matrices_false = [(np.array([[1, 0], [0, 1j]])), (np.array([[1, 2], [3, 4]]))]

invalid_CPTP_matrices_false = [np.array([[1, 0], [0, 1]]), np.array([[0, 1], [1, 0]])]

invalid_matrix_type_error = np.array([[0, 1], ["a", 0]])

z_matrix = np.array([[1, 0], [0, -1]])


def test_verify_quantum_operator_matrix_dimensions():
    assert verify_quantum_operator_matrix_dimensions(valid_unitary_hermitian_matrix) is None


def test_is_unitary_true():
    assert is_unitary(valid_unitary_hermitian_matrix)


def test_is_hermitian_true():
    assert is_hermitian(valid_unitary_hermitian_matrix)


def test_is_cptp_true():
    assert is_cptp(valid_CPTP_matrices)


def test_is_square_matrix():
    assert is_square_matrix(valid_unitary_hermitian_matrix)


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("matrix", invalid_dimension_matrices)
def test_verify_quantum_operator_matrix_dimensions_value_error(matrix):
    verify_quantum_operator_matrix_dimensions(matrix)


@pytest.mark.parametrize("matrix", invalid_unitary_matrices_false)
def test_is_unitary_false(matrix):
    assert not is_unitary(matrix)


@pytest.mark.parametrize("matrix", invalid_hermitian_matrices_false)
def test_is_hermitian_false(matrix):
    assert not is_hermitian(matrix)


def test_is_cptp_false():
    assert not is_cptp(invalid_CPTP_matrices_false)


@pytest.mark.xfail(raises=Exception)
def test_is_hermitian_exception():
    is_hermitian(invalid_matrix_type_error)


@pytest.mark.xfail(raises=Exception)
def test_is_unitary_exception():
    is_unitary(invalid_matrix_type_error)


@pytest.mark.xfail(raises=Exception)
def test_is_cptp_exception():
    is_cptp([invalid_matrix_type_error])


def test_get_pauli_eigenvalues_correct_eigenvalues_one_qubit():
    """Test the get_pauli_eigenvalues function for one qubit"""
    assert np.array_equal(get_pauli_eigenvalues(1), np.diag(z_matrix))


def test_get_pauli_eigenvalues_correct_eigenvalues_two_qubits():
    """Test the get_pauli_eigenvalues function for two qubits"""
    assert np.array_equal(get_pauli_eigenvalues(2), np.diag(np.kron(z_matrix, z_matrix)))


def test_get_pauli_eigenvalues_correct_eigenvalues_three_qubits():
    """Test the get_pauli_eigenvalues function for three qubits"""
    assert np.array_equal(
        get_pauli_eigenvalues(3),
        np.diag(np.kron(z_matrix, np.kron(z_matrix, z_matrix))),
    )


@pytest.mark.parametrize("depth", list(range(1, 6)))
def test_get_pauli_eigenvalues_cache_usage(depth):
    """Test that the right number of cachings have been executed after clearing the cache"""
    get_pauli_eigenvalues.cache_clear()
    get_pauli_eigenvalues(depth)
    assert functools._CacheInfo(depth - 1, depth, 128, depth) == get_pauli_eigenvalues.cache_info()


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("num_qubits", [1, 2])
def test_get_pauli_eigenvalues_immutable(num_qubits):
    get_pauli_eigenvalues(num_qubits)[0] = 100
