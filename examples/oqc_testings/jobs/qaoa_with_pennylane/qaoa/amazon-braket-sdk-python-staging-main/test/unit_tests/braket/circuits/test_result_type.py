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

from braket.circuits import Observable, ObservableResultType, ResultType


@pytest.fixture
def result_type():
    return ResultType(ascii_symbols=["foo"])


@pytest.fixture
def prob():
    return ResultType.Probability([0, 1])


@pytest.fixture
def sv():
    return ResultType.StateVector()


@pytest.mark.xfail(raises=ValueError)
def test_none_ascii():
    ResultType(ascii_symbols=None)


def test_name(result_type):
    expected = result_type.__class__.__name__
    assert result_type.name == expected


def test_ascii_symbol():
    ascii_symbols = ["foo"]
    result_type = ResultType(ascii_symbols=ascii_symbols)
    assert result_type.ascii_symbols == ascii_symbols


def test_equality_statevector():
    result1 = ResultType.StateVector()
    result2 = ResultType.StateVector()
    result3 = ResultType.Probability([1])
    result4 = "hi"
    assert result1 == result2
    assert result1 != result3
    assert result1 != result4


def test_equality_densitymatrix():
    result1 = ResultType.DensityMatrix()
    result2 = ResultType.DensityMatrix()
    result3 = ResultType.StateVector()
    result4 = "foo"
    assert result1 == result2
    assert result1 != result3
    assert result1 != result4


@pytest.mark.xfail(raises=AttributeError)
def test_ascii_symbol_setter(result_type):
    result_type.ascii_symbols = ["bar"]


@pytest.mark.xfail(raises=AttributeError)
def test_name_setter(result_type):
    result_type.name = "hi"


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_ir_not_implemented_by_default(result_type):
    result_type.to_ir(None)


def test_register_result():
    class _FooResultType(ResultType):
        def __init__(self):
            super().__init__(ascii_symbols=["foo"])

    ResultType.register_result_type(_FooResultType)
    assert ResultType._FooResultType().name == _FooResultType().name


def test_copy_creates_new_object(prob):
    copy = prob.copy()
    assert copy == prob
    assert copy is not prob


def test_copy_with_mapping_target(sv):
    target_mapping = {0: 10, 1: 11}
    expected = ResultType.StateVector()
    assert sv.copy(target_mapping=target_mapping) == expected


def test_copy_with_mapping_target_hasattr(prob):
    target_mapping = {0: 10, 1: 11}
    expected = ResultType.Probability([10, 11])
    assert prob.copy(target_mapping=target_mapping) == expected


def test_copy_with_target_hasattr(prob):
    target = [10, 11]
    expected = ResultType.Probability(target)
    assert prob.copy(target=target) == expected


def test_copy_with_target(sv):
    target = [10, 11]
    expected = ResultType.StateVector()
    assert sv.copy(target=target) == expected


@pytest.mark.xfail(raises=TypeError)
def test_copy_with_target_and_mapping(prob):
    prob.copy(target=[10], target_mapping={0: 10})


# ObservableResultType


@pytest.mark.xfail(raises=ValueError)
def test_expectation_init_value_error_target():
    ObservableResultType(
        ascii_symbols=["Obs", "Obs"], observable=Observable.X() @ Observable.Y(), target=[]
    )


@pytest.mark.xfail(raises=ValueError)
def test_expectation_init_value_error_ascii_symbols():
    ObservableResultType(
        ascii_symbols=["Obs"], observable=Observable.X() @ Observable.Y(), target=[1, 2]
    )


@pytest.mark.xfail(raises=ValueError)
def test_obs_rt_init_value_error_qubit_count():
    ObservableResultType(ascii_symbols=["Obs"], observable=Observable.X(), target=[0, 1])


def test_obs_rt_equality():
    a1 = ObservableResultType(ascii_symbols=["Obs"], observable=Observable.X(), target=0)
    a2 = ObservableResultType(ascii_symbols=["Obs"], observable=Observable.X(), target=0)
    a3 = ObservableResultType(ascii_symbols=["Obs"], observable=Observable.X(), target=1)
    a4 = "hi"
    assert a1 == a2
    assert a1 != a3
    assert a1 != a4
    assert ResultType.Variance(observable=Observable.Y(), target=0) != ResultType.Expectation(
        observable=Observable.Y(), target=0
    )


def test_obs_rt_repr():
    a1 = ObservableResultType(ascii_symbols=["Obs"], observable=Observable.X(), target=0)
    assert (
        str(a1)
        == "ObservableResultType(observable=X('qubit_count': 1), target=QubitSet([Qubit(0)]))"
    )
