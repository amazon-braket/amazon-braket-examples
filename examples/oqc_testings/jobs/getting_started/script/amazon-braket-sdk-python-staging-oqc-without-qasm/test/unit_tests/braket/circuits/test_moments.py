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

from collections import OrderedDict

import pytest

from braket.circuits import Gate, Instruction, Moments, MomentsKey, QubitSet


def cnot(q1, q2):
    return Instruction(Gate.CNot(), [q1, q2])


def h(q):
    return Instruction(Gate.H(), q)


@pytest.fixture
def moments():
    return Moments([h(0), h(0)])


def test_add():
    moments = Moments()
    moments.add([h(0)])
    moments.add([h(0)])

    expected = OrderedDict()
    expected[MomentsKey(0, QubitSet(0), "gate", 0)] = h(0)
    expected[MomentsKey(1, QubitSet(0), "gate", 0)] = h(0)
    assert OrderedDict(moments) == expected


def test_default_constructor():
    moments = Moments()
    assert OrderedDict(moments) == OrderedDict()
    assert moments.depth == 0
    assert moments.qubits == QubitSet()


def test_constructor_with_instructions():
    moments = Moments([h(0), h(1)])
    expected = Moments()
    expected.add([h(0)])
    expected.add([h(1)])
    assert moments == expected


def test_depth():
    moments = Moments([h(0), h(1)])
    assert moments.depth == 1

    moments.add([cnot(0, 2), h(3)])
    assert moments.depth == 2


@pytest.mark.xfail(raises=AttributeError)
def test_depth_setter(moments):
    moments.depth = 5


def test_overlaping_qubits():
    moments = Moments([h(0), h(0)])
    assert moments.depth == 2

    moments.add([cnot(0, 3), h(1)])
    assert moments.depth == 3

    moments.add([cnot(2, 4)])
    assert moments.depth == 3


def test_qubits():
    moments = Moments([h(0), h(10), h(5)])
    expected = QubitSet([0, 10, 5])
    assert moments.qubits == expected
    assert moments.qubit_count == len(expected)


@pytest.mark.xfail(raises=AttributeError)
def test_qubits_setter(moments):
    moments.qubits = QubitSet(1)


@pytest.mark.xfail(raises=AttributeError)
def test_qubit_count_setter(moments):
    moments.qubit_count = 1


def test_time_slices():
    moments = Moments([h(0), h(1), cnot(0, 1)])
    expected = {0: [h(0), h(1)], 1: [cnot(0, 1)]}
    assert moments.time_slices() == expected


def test_keys():
    moments = Moments([h(0), h(0), h(1)])
    expected = [
        MomentsKey(0, QubitSet(0), "gate", 0),
        MomentsKey(1, QubitSet(0), "gate", 0),
        MomentsKey(0, QubitSet(1), "gate", 0),
    ]
    assert list(moments.keys()) == expected


def test_items():
    moments = Moments([h(0), h(0), h(1)])
    expected = [
        (MomentsKey(0, QubitSet(0), "gate", 0), h(0)),
        (MomentsKey(1, QubitSet(0), "gate", 0), h(0)),
        (MomentsKey(0, QubitSet(1), "gate", 0), h(1)),
    ]
    assert list(moments.items()) == expected


def test_values():
    moments = Moments([h(0), h(0), h(1)])
    expected = [h(0), h(0), h(1)]
    assert list(moments.values()) == expected


def test_get():
    moments = Moments([h(0)])
    unknown_key = MomentsKey(100, QubitSet(100), "gate", 0)
    assert moments.get(MomentsKey(0, QubitSet(0), "gate", 0)) == h(0)
    assert moments.get(unknown_key) is None
    assert moments.get(unknown_key, h(0)) == h(0)


def test_getitem():
    moments = Moments([h(0)])
    assert moments[MomentsKey(0, QubitSet(0), "gate", 0)] == h(0)


def test_iter(moments):
    assert [key for key in moments] == list(moments.keys())


def test_len():
    moments = Moments([h(0), h(0)])
    assert len(moments) == 2


def test_contains():
    moments = Moments([h(0), h(0)])
    assert MomentsKey(0, QubitSet(0), "gate", 0) in moments
    assert MomentsKey(0, QubitSet(100), "gate", 0) not in moments


def test_equals():
    moments_1 = Moments([h(0)])
    moments_2 = Moments([h(0)])
    other_moments = Moments([h(1)])
    non_moments = "non moments"

    assert moments_1 == moments_2
    assert moments_1 is not moments_2
    assert moments_1 != other_moments
    assert moments_1 != non_moments


def test_repr(moments):
    assert repr(moments) == repr(OrderedDict(moments))


def test_str(moments):
    assert str(moments) == str(OrderedDict(moments))
