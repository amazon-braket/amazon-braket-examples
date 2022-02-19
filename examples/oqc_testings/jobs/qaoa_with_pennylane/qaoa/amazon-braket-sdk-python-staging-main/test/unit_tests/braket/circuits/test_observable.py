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

from braket.circuits import Observable, QuantumOperator, StandardObservable


@pytest.fixture
def observable():
    return Observable(qubit_count=1, ascii_symbols=["foo"])


@pytest.fixture
def standard_observable():
    return StandardObservable(ascii_symbols=["foo"])


def test_is_operator(observable):
    assert isinstance(observable, QuantumOperator)


@pytest.mark.xfail(raises=ValueError)
def test_qubit_count_lt_one():
    Observable(qubit_count=0, ascii_symbols=[])


@pytest.mark.xfail(raises=ValueError)
def test_none_ascii():
    Observable(qubit_count=1, ascii_symbols=None)


@pytest.mark.xfail(raises=ValueError)
def test_mismatch_length_ascii():
    Observable(qubit_count=1, ascii_symbols=["foo", "bar"])


def test_name(observable):
    expected = observable.__class__.__name__
    assert observable.name == expected


def test_getters():
    qubit_count = 2
    ascii_symbols = ("foo", "bar")
    observable = Observable(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

    assert observable.qubit_count == qubit_count
    assert observable.ascii_symbols == ascii_symbols


@pytest.mark.xfail(raises=AttributeError)
def test_qubit_count_setter(observable):
    observable.qubit_count = 10


@pytest.mark.xfail(raises=AttributeError)
def test_ascii_symbols_setter(observable):
    observable.ascii_symbols = ["foo", "bar"]


@pytest.mark.xfail(raises=AttributeError)
def test_name_setter(observable):
    observable.name = "hi"


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_ir_not_implemented_by_default(observable):
    observable.to_ir()


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_matrix_not_implemented_by_default(observable):
    observable.to_matrix(None)


@pytest.mark.xfail(raises=NotImplementedError)
def test_basis_rotation_gates_not_implemented_by_default(observable):
    observable.basis_rotation_gates


@pytest.mark.xfail(raises=NotImplementedError)
def test_eigenvalues_not_implemented_by_default(observable):
    observable.eigenvalues


@pytest.mark.xfail(raises=NotImplementedError)
def test_eigenvalue_not_implemented_by_default(observable):
    observable.eigenvalue(0)


def test_str(observable):
    expected = "{}('qubit_count': {})".format(observable.name, observable.qubit_count)
    assert str(observable) == expected


def test_register_observable():
    class _FooObservable(Observable):
        def __init__(self):
            super().__init__(qubit_count=1, ascii_symbols=["foo"])

    Observable.register_observable(_FooObservable)
    assert Observable._FooObservable().name == _FooObservable().name


def test_matmul_observable():
    o1 = Observable.I()
    o2 = Observable.Z()
    o3 = o1 @ o2
    assert isinstance(o3, Observable.TensorProduct)
    assert o3.qubit_count == 2
    assert o3.to_ir() == ["i", "z"]
    assert o3.ascii_symbols == ("I@Z", "I@Z")


@pytest.mark.xfail(raises=ValueError)
def test_matmul_non_observable():
    Observable.I() @ "a"


def test_observable_equality():
    o1 = Observable.I()
    o2 = Observable.I()
    o3 = Observable.Z()
    o4 = "a"
    assert o1 == o2
    assert o1 != o3
    assert o1 != o4


def test_standard_observable_subclass_of_observable(standard_observable):
    assert isinstance(standard_observable, Observable)


def test_standard_observable_eigenvalues(standard_observable):
    assert np.allclose(standard_observable.eigenvalues, np.array([1, -1]))
