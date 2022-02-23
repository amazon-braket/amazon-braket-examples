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

import pytest

from braket.circuits import Qubit, QubitSet


@pytest.fixture
def qubits():
    return QubitSet([0, Qubit(1)])


def test_qubit_set_is_ordered_set():
    qubits = QubitSet([1, 2, 3, 1, 2, 3])
    assert qubits == QubitSet([1, 2, 3])


def test_default_input():
    assert QubitSet() == QubitSet([])


def test_with_single():
    assert QubitSet(0) == tuple([Qubit(0)])


def test_with_iterable():
    assert QubitSet([0, 1]) == tuple([Qubit(0), Qubit(1)])


def test_with_nested_iterable():
    assert QubitSet([0, 1, [2, 3]]) == tuple([Qubit(0), Qubit(1), Qubit(2), Qubit(3)])


def test_with_qubit_set():
    qubits = QubitSet([0, 1])
    assert QubitSet([qubits, [2, 3]]) == tuple([Qubit(0), Qubit(1), Qubit(2), Qubit(3)])


def test_flattening_does_not_recurse_infinitely():
    with pytest.raises(TypeError):  # str instead of expected int
        QubitSet("kaboom")


def test_map_creates_new_object(qubits):
    mapped_qubits = qubits.map({})
    assert mapped_qubits == qubits
    assert mapped_qubits is not qubits


def test_map_happy_case():
    mapping = {Qubit(0): Qubit(11), Qubit(1): Qubit(5)}
    qubits = QubitSet([0, 1])
    mapped_qubits = qubits.map(mapping)

    assert mapped_qubits == QubitSet([11, 5])


def test_hash(qubits):
    assert hash(qubits) == hash(tuple(qubits))
