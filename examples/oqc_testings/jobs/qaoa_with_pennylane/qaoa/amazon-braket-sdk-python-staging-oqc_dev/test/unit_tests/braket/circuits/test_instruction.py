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

from braket.circuits import Gate, Instruction, Qubit, QubitSet


@pytest.fixture
def instr():
    return Instruction(Gate.H(), 0)


@pytest.fixture
def cnot():
    return Instruction(Gate.CNot(), [0, 1])


@pytest.mark.xfail(raises=ValueError)
def test_empty_operator():
    Instruction(None, target=0)


@pytest.mark.xfail(raises=ValueError)
def test_non_matching_qubit_set_and_qubit_count():
    Instruction(Gate.CNot(), target=[0, 0])


def test_init_with_qubits():
    target = QubitSet([0, 1])
    instr = Instruction(Gate.CNot(), target)
    assert instr.target == target


def test_init_with_qubit():
    target = Qubit(0)
    instr = Instruction(Gate.H(), target)
    assert instr.target == QubitSet(0)


def test_init_with_int():
    target = 0
    instr = Instruction(Gate.H(), target)
    assert instr.target == QubitSet(0)


def test_init_with_sequence():
    target = [0, Qubit(1)]
    instr = Instruction(Gate.CNot(), target)
    assert instr.target == QubitSet([0, 1])


def test_getters():
    target = [0, 1]
    operator = Gate.CNot()
    instr = Instruction(operator, target)

    assert instr.operator == operator
    assert instr.target == QubitSet([0, 1])


@pytest.mark.xfail(raises=AttributeError)
def test_operator_setter(instr):
    instr.operator = Gate.H()


@pytest.mark.xfail(raises=AttributeError)
def test_target_setter(instr):
    instr.target = QubitSet(0)


def test_str(instr):
    expected = "Instruction('operator': {}, 'target': {})".format(instr.operator, instr.target)
    assert str(instr) == expected


def test_equality():
    instr_1 = Instruction(Gate.H(), 0)
    instr_2 = Instruction(Gate.H(), 0)
    other_instr = Instruction(Gate.CNot(), [0, 1])
    non_instr = "non instruction"

    assert instr_1 == instr_2
    assert instr_1 is not instr_2
    assert instr_1 != other_instr
    assert instr_1 != non_instr


def test_to_ir():
    expected_target = QubitSet([0, 1])
    expected_ir = "foo bar value"

    class FooGate(Gate):
        def __init__(self):
            super().__init__(qubit_count=2, ascii_symbols=["foo", "bar"])

        def to_ir(self, target):
            assert target == expected_target
            return expected_ir

    instr = Instruction(FooGate(), expected_target)
    assert instr.to_ir() == expected_ir


def test_copy_creates_new_object(instr):
    copy = instr.copy()
    assert copy == instr
    assert copy is not instr


def test_copy_with_mapping(cnot):
    target_mapping = {0: 10, 1: 11}
    expected = Instruction(Gate.CNot(), [10, 11])
    assert cnot.copy(target_mapping=target_mapping) == expected


def test_copy_with_target(cnot):
    target = [10, 11]
    expected = Instruction(Gate.CNot(), target)
    assert cnot.copy(target=target) == expected


@pytest.mark.xfail(raises=TypeError)
def test_copy_with_target_and_mapping(instr):
    instr.copy(target=[10], target_mapping={0: 10})
