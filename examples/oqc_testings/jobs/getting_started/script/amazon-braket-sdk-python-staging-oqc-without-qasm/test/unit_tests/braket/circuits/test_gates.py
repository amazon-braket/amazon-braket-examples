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

import braket.ir.jaqcd as ir
from braket.circuits import Circuit, Gate, Instruction, QubitSet
from braket.ir.jaqcd.shared_models import (
    Angle,
    DoubleControl,
    DoubleTarget,
    MultiTarget,
    SingleControl,
    SingleTarget,
    TwoDimensionalMatrix,
)

testdata = [
    (Gate.H, "h", ir.H, [SingleTarget], {}),
    (Gate.I, "i", ir.I, [SingleTarget], {}),
    (Gate.X, "x", ir.X, [SingleTarget], {}),
    (Gate.Y, "y", ir.Y, [SingleTarget], {}),
    (Gate.Z, "z", ir.Z, [SingleTarget], {}),
    (Gate.S, "s", ir.S, [SingleTarget], {}),
    (Gate.Si, "si", ir.Si, [SingleTarget], {}),
    (Gate.T, "t", ir.T, [SingleTarget], {}),
    (Gate.Ti, "ti", ir.Ti, [SingleTarget], {}),
    (Gate.V, "v", ir.V, [SingleTarget], {}),
    (Gate.Vi, "vi", ir.Vi, [SingleTarget], {}),
    (Gate.Rx, "rx", ir.Rx, [SingleTarget, Angle], {}),
    (Gate.Ry, "ry", ir.Ry, [SingleTarget, Angle], {}),
    (Gate.Rz, "rz", ir.Rz, [SingleTarget, Angle], {}),
    (Gate.CNot, "cnot", ir.CNot, [SingleTarget, SingleControl], {}),
    (Gate.CV, "cv", ir.CV, [SingleTarget, SingleControl], {}),
    (Gate.CCNot, "ccnot", ir.CCNot, [SingleTarget, DoubleControl], {}),
    (Gate.Swap, "swap", ir.Swap, [DoubleTarget], {}),
    (Gate.CSwap, "cswap", ir.CSwap, [SingleControl, DoubleTarget], {}),
    (Gate.ISwap, "iswap", ir.ISwap, [DoubleTarget], {}),
    (Gate.PSwap, "pswap", ir.PSwap, [DoubleTarget, Angle], {}),
    (Gate.XY, "xy", ir.XY, [DoubleTarget, Angle], {}),
    (Gate.PhaseShift, "phaseshift", ir.PhaseShift, [SingleTarget, Angle], {}),
    (Gate.CPhaseShift, "cphaseshift", ir.CPhaseShift, [SingleControl, SingleTarget, Angle], {}),
    (
        Gate.CPhaseShift00,
        "cphaseshift00",
        ir.CPhaseShift00,
        [SingleControl, SingleTarget, Angle],
        {},
    ),
    (
        Gate.CPhaseShift01,
        "cphaseshift01",
        ir.CPhaseShift01,
        [SingleControl, SingleTarget, Angle],
        {},
    ),
    (
        Gate.CPhaseShift10,
        "cphaseshift10",
        ir.CPhaseShift10,
        [SingleControl, SingleTarget, Angle],
        {},
    ),
    (Gate.CY, "cy", ir.CY, [SingleTarget, SingleControl], {}),
    (Gate.CZ, "cz", ir.CZ, [SingleTarget, SingleControl], {}),
    (Gate.ECR, "ecr", ir.ECR, [DoubleTarget], {}),
    (Gate.XX, "xx", ir.XX, [DoubleTarget, Angle], {}),
    (Gate.YY, "yy", ir.YY, [DoubleTarget, Angle], {}),
    (Gate.ZZ, "zz", ir.ZZ, [DoubleTarget, Angle], {}),
    (
        Gate.Unitary,
        "unitary",
        ir.Unitary,
        [TwoDimensionalMatrix, MultiTarget],
        {"input_type": complex},
    ),
    (
        Gate.Unitary,
        "unitary",
        ir.Unitary,
        [TwoDimensionalMatrix, MultiTarget],
        {"input_type": float},
    ),
    (
        Gate.Unitary,
        "unitary",
        ir.Unitary,
        [TwoDimensionalMatrix, MultiTarget],
        {"input_type": int},
    ),
]


invalid_unitary_matrices = [
    (np.array([[1]])),
    (np.array([1])),
    (np.array([0, 1, 2])),
    (np.array([[0, 1], [1, 2], [3, 4]])),
    (np.array([[0, 1, 2], [2, 3]], dtype=object)),
    (np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])),
    (np.array([[0, 1], [1, 1]])),
]


def single_target_valid_input(**kwargs):
    return {"target": 2}


def double_target_valid_ir_input(**kwargs):
    return {"targets": [2, 3]}


def double_target_valid_input(**kwargs):
    return {"target1": 2, "target2": 3}


def angle_valid_input(**kwargs):
    return {"angle": 0.123}


def single_control_valid_input(**kwargs):
    return {"control": 0}


def double_control_valid_ir_input(**kwargs):
    return {"controls": [0, 1]}


def double_control_valid_input(**kwargs):
    return {"control1": 0, "control2": 1}


def multi_target_valid_input(**kwargs):
    return {"targets": [5]}


def two_dimensional_matrix_valid_ir_input(**kwargs):
    return {"matrix": [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]}


def two_dimensional_matrix_valid_input(**kwargs):
    input_type = kwargs.get("input_type")
    return {"matrix": np.array([[input_type(0), input_type(1)], [input_type(1), input_type(0)]])}


valid_ir_switcher = {
    "SingleTarget": single_target_valid_input,
    "DoubleTarget": double_target_valid_ir_input,
    "Angle": angle_valid_input,
    "SingleControl": single_control_valid_input,
    "DoubleControl": double_control_valid_ir_input,
    "MultiTarget": multi_target_valid_input,
    "TwoDimensionalMatrix": two_dimensional_matrix_valid_ir_input,
}


valid_subroutine_switcher = dict(
    valid_ir_switcher,
    **{
        "TwoDimensionalMatrix": two_dimensional_matrix_valid_input,
        "DoubleTarget": double_target_valid_input,
        "DoubleControl": double_control_valid_input,
    }
)


def create_valid_ir_input(irsubclasses):
    input = {}
    for subclass in irsubclasses:
        input.update(valid_ir_switcher.get(subclass.__name__, lambda: "Invalid subclass")())
    return input


def create_valid_subroutine_input(irsubclasses, **kwargs):
    input = {}
    for subclass in irsubclasses:
        input.update(
            valid_subroutine_switcher.get(subclass.__name__, lambda: "Invalid subclass")(**kwargs)
        )
    return input


def create_valid_target_input(irsubclasses):
    input = {}
    qubit_set = []
    # based on the concept that control goes first in target input
    for subclass in irsubclasses:
        if subclass == SingleTarget:
            qubit_set.extend(list(single_target_valid_input().values()))
        elif subclass == DoubleTarget:
            qubit_set.extend(list(double_target_valid_ir_input().values()))
        elif subclass == MultiTarget:
            qubit_set.extend(list(multi_target_valid_input().values()))
        elif subclass == SingleControl:
            qubit_set = list(single_control_valid_input().values()) + qubit_set
        elif subclass == DoubleControl:
            qubit_set = list(double_control_valid_ir_input().values()) + qubit_set
        elif subclass == Angle or subclass == TwoDimensionalMatrix:
            pass
        else:
            raise ValueError("Invalid subclass")
    input["target"] = QubitSet(qubit_set)
    return input


def create_valid_gate_class_input(irsubclasses, **kwargs):
    input = {}
    if Angle in irsubclasses:
        input.update(angle_valid_input())
    if TwoDimensionalMatrix in irsubclasses:
        input.update(two_dimensional_matrix_valid_input(**kwargs))
    return input


def create_valid_instruction_input(testclass, irsubclasses, **kwargs):
    input = create_valid_target_input(irsubclasses)
    input["operator"] = testclass(**create_valid_gate_class_input(irsubclasses, **kwargs))
    return input


def calculate_qubit_count(irsubclasses):
    qubit_count = 0
    for subclass in irsubclasses:
        if subclass == SingleTarget:
            qubit_count += 1
        elif subclass == DoubleTarget:
            qubit_count += 2
        elif subclass == SingleControl:
            qubit_count += 1
        elif subclass == DoubleControl:
            qubit_count += 2
        elif subclass == MultiTarget:
            qubit_count += 3
        elif subclass == Angle or subclass == TwoDimensionalMatrix:
            pass
        else:
            raise ValueError("Invalid subclass")
    return qubit_count


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_ir_gate_level(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    expected = irclass(**create_valid_ir_input(irsubclasses))
    actual = testclass(**create_valid_gate_class_input(irsubclasses, **kwargs)).to_ir(
        **create_valid_target_input(irsubclasses)
    )
    assert actual == expected


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_ir_instruction_level(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    expected = irclass(**create_valid_ir_input(irsubclasses))
    instruction = Instruction(**create_valid_instruction_input(testclass, irsubclasses, **kwargs))
    actual = instruction.to_ir()
    assert actual == expected


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_gate_subroutine(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    qubit_count = calculate_qubit_count(irsubclasses)
    subroutine = getattr(Circuit(), subroutine_name)
    assert subroutine(**create_valid_subroutine_input(irsubclasses, **kwargs)) == Circuit(
        Instruction(**create_valid_instruction_input(testclass, irsubclasses, **kwargs))
    )
    if qubit_count == 1:
        multi_targets = [0, 1, 2]
        instruction_list = []
        for target in multi_targets:
            instruction_list.append(
                Instruction(
                    operator=testclass(**create_valid_gate_class_input(irsubclasses, **kwargs)),
                    target=target,
                )
            )
        subroutine = getattr(Circuit(), subroutine_name)
        subroutine_input = {"target": multi_targets}
        if Angle in irsubclasses:
            subroutine_input.update(angle_valid_input())
        assert subroutine(**subroutine_input) == Circuit(instruction_list)


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_gate_to_matrix(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    gate1 = testclass(**create_valid_gate_class_input(irsubclasses, **kwargs))
    gate2 = testclass(**create_valid_gate_class_input(irsubclasses, **kwargs))
    assert isinstance(gate1.to_matrix(), np.ndarray)
    assert gate1.matrix_equivalence(gate2)


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_fixed_qubit_count(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    fixed_qubit_count = testclass.fixed_qubit_count()
    if fixed_qubit_count is not NotImplemented:
        gate = testclass(**create_valid_gate_class_input(irsubclasses, **kwargs))
        assert gate.qubit_count == fixed_qubit_count


# Additional Unitary gate tests


def test_equality():
    u1 = Gate.Unitary(np.array([[0 + 0j, 1 + 0j], [1 + 0j, 0 + 0j]]))
    u2 = Gate.Unitary(np.array([[0, 1], [1, 0]], dtype=np.float32), display_name=["u2"])
    other_gate = Gate.Unitary(np.array([[1, 0], [0, 1]]))
    non_gate = "non gate"

    assert u1 == u2
    assert u1 is not u2
    assert u1 != other_gate
    assert u1 != non_gate


def test_large_unitary():
    matrix = np.eye(16, dtype=np.float32)
    # Permute rows of matrix
    matrix[[*range(16)]] = matrix[[(i + 1) % 16 for i in range(16)]]
    unitary = Gate.Unitary(matrix)
    assert unitary.qubit_count == 4


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("matrix", invalid_unitary_matrices)
def test_unitary_invalid_matrix(matrix):
    Gate.Unitary(matrix=matrix)


@pytest.mark.xfail(raises=ValueError)
def test_unitary_matrix_target_size_mismatch():
    Circuit().unitary(
        matrix=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]), targets=[0]
    )
