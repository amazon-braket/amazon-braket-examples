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

import numpy as np
import pytest

from braket.circuits import Operator, QuantumOperator


class _DummyQuantumOperator(QuantumOperator):
    @staticmethod
    def fixed_qubit_count():
        return 2


@pytest.fixture
def ascii_symbols():
    return ["foo"]


@pytest.fixture
def quantum_operator(ascii_symbols):
    return QuantumOperator(qubit_count=1, ascii_symbols=ascii_symbols)


def test_is_operator(quantum_operator):
    assert isinstance(quantum_operator, Operator)


def test_ascii_symbols(quantum_operator, ascii_symbols):
    assert quantum_operator.ascii_symbols == tuple(ascii_symbols)


def test_fixed_qubit_count_implemented():
    operator = _DummyQuantumOperator(qubit_count=None, ascii_symbols=["foo", "bar"])
    assert operator.qubit_count == _DummyQuantumOperator.fixed_qubit_count()


@pytest.mark.xfail(raises=ValueError)
def test_qubit_count_fixed_qubit_count_unequal():
    _DummyQuantumOperator(qubit_count=1, ascii_symbols=["foo", "bar"])


@pytest.mark.xfail(raises=TypeError)
def test_qubit_count_not_int():
    QuantumOperator(qubit_count="hello", ascii_symbols=[])


@pytest.mark.xfail(raises=ValueError)
def test_qubit_count_lt_one():
    QuantumOperator(qubit_count=0, ascii_symbols=[])


@pytest.mark.xfail(raises=ValueError)
def test_none_ascii():
    QuantumOperator(qubit_count=1, ascii_symbols=None)


@pytest.mark.xfail(raises=ValueError)
def test_mismatch_length_ascii():
    QuantumOperator(qubit_count=1, ascii_symbols=["foo", "bar"])


def test_name(quantum_operator):
    expected = quantum_operator.__class__.__name__
    assert quantum_operator.name == expected


def test_getters():
    qubit_count = 2
    ascii_symbols = ("foo", "bar")
    quantum_operator = QuantumOperator(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

    assert quantum_operator.qubit_count == qubit_count
    assert quantum_operator.ascii_symbols == ascii_symbols


@pytest.mark.xfail(raises=AttributeError)
def test_qubit_count_setter(quantum_operator):
    quantum_operator.qubit_count = 10


@pytest.mark.xfail(raises=AttributeError)
def test_ascii_symbols_setter(quantum_operator):
    quantum_operator.ascii_symbols = ["foo", "bar"]


@pytest.mark.xfail(raises=AttributeError)
def test_name_setter(quantum_operator):
    quantum_operator.name = "hi"


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_ir_not_implemented_by_default(quantum_operator):
    quantum_operator.to_ir(None)


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_matrix_not_implemented_by_default(quantum_operator):
    quantum_operator.to_matrix(None)


def test_matrix_equivalence():
    class _Foo1(QuantumOperator):
        def __init__(self):
            super().__init__(qubit_count=1, ascii_symbols=["foo"])

        def to_matrix(self):
            return np.array([[1.0, 0.0], [0.0, 1.0j]])

    class _Foo2(QuantumOperator):
        def __init__(self):
            super().__init__(qubit_count=1, ascii_symbols=["foo"])

        def to_matrix(self):
            return np.array([[1.0, 0.0], [1.0, 0.0]])

    quantum_operator1 = _Foo1()
    quantum_operator2 = _Foo1()
    quantum_operator3 = _Foo2()
    assert quantum_operator1.matrix_equivalence(quantum_operator2)
    assert not quantum_operator1.matrix_equivalence(quantum_operator3)


def test_matrix_equivalence_non_quantum_operator():
    quantum_operator1 = QuantumOperator(qubit_count=1, ascii_symbols=["foo"])
    assert not quantum_operator1.matrix_equivalence(1)


def test_str(quantum_operator):
    expected = "{}('qubit_count': {})".format(quantum_operator.name, quantum_operator.qubit_count)
    assert str(quantum_operator) == expected
