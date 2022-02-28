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
from braket.circuits import Circuit, Instruction, Noise, QubitSet
from braket.ir.jaqcd.shared_models import (
    DampingProbability,
    DampingSingleProbability,
    DoubleControl,
    DoubleTarget,
    MultiProbability,
    MultiTarget,
    SingleControl,
    SingleProbability,
    SingleProbability_34,
    SingleProbability_1516,
    SingleTarget,
    TripleProbability,
    TwoDimensionalMatrixList,
)

testdata = [
    (Noise.BitFlip, "bit_flip", ir.BitFlip, [SingleTarget, SingleProbability], {}),
    (Noise.PhaseFlip, "phase_flip", ir.PhaseFlip, [SingleTarget, SingleProbability], {}),
    (Noise.Depolarizing, "depolarizing", ir.Depolarizing, [SingleTarget, SingleProbability_34], {}),
    (
        Noise.AmplitudeDamping,
        "amplitude_damping",
        ir.AmplitudeDamping,
        [SingleTarget, DampingProbability],
        {},
    ),
    (
        Noise.GeneralizedAmplitudeDamping,
        "generalized_amplitude_damping",
        ir.GeneralizedAmplitudeDamping,
        [SingleTarget, DampingProbability, DampingSingleProbability],
        {},
    ),
    (
        Noise.PhaseDamping,
        "phase_damping",
        ir.PhaseDamping,
        [SingleTarget, DampingProbability],
        {},
    ),
    (
        Noise.TwoQubitDepolarizing,
        "two_qubit_depolarizing",
        ir.TwoQubitDepolarizing,
        [DoubleTarget, SingleProbability_1516],
        {},
    ),
    (
        Noise.TwoQubitDephasing,
        "two_qubit_dephasing",
        ir.TwoQubitDephasing,
        [DoubleTarget, SingleProbability_34],
        {},
    ),
    (
        Noise.TwoQubitPauliChannel,
        "two_qubit_pauli_channel",
        ir.MultiQubitPauliChannel,
        [DoubleTarget, MultiProbability],
        {},
    ),
    (
        Noise.PauliChannel,
        "pauli_channel",
        ir.PauliChannel,
        [SingleTarget, TripleProbability],
        {},
    ),
    (
        Noise.Kraus,
        "kraus",
        ir.Kraus,
        [TwoDimensionalMatrixList, MultiTarget],
        {"input_type": complex},
    ),
    (
        Noise.Kraus,
        "kraus",
        ir.Kraus,
        [TwoDimensionalMatrixList, MultiTarget],
        {"input_type": float},
    ),
    (
        Noise.Kraus,
        "kraus",
        ir.Kraus,
        [TwoDimensionalMatrixList, MultiTarget],
        {"input_type": int},
    ),
]


invalid_kraus_matrices = [
    ([np.array([[1]])]),
    ([np.array([1])]),
    ([np.array([0, 1, 2])]),
    ([np.array([[0, 1], [1, 2], [3, 4]])]),
    ([np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])]),
    ([np.array([[0, 1], [1, 1]])]),
    ([np.array([[1, 0], [0, 1]]), np.array([[0, 1], [1, 0]])]),
    ([np.array([[1, 0], [0, 1]]) * np.sqrt(0.5), np.eye(4) * np.sqrt(0.5)]),
    ([np.eye(8)]),
    ([np.eye(2), np.eye(2), np.eye(2), np.eye(2), np.eye(2)]),
]


def single_target_valid_input(**kwargs):
    return {"target": 2}


def double_target_valid_ir_input(**kwargs):
    return {"targets": [2, 3]}


def double_target_valid_input(**kwargs):
    return {"target1": 2, "target2": 3}


def single_probability_valid_input(**kwargs):
    return {"probability": 0.1234}


def single_probability_34_valid_input(**kwargs):
    return {"probability": 0.1234}


def single_probability_1516_valid_input(**kwargs):
    return {"probability": 0.1234}


def damping_single_probability_valid_input(**kwargs):
    return {"probability": 0.1234}


def damping_probability_valid_input(**kwargs):
    return {"gamma": 0.1234}


def triple_probability_valid_input(**kwargs):
    return {"probX": 0.1234, "probY": 0.1324, "probZ": 0.1423}


def single_control_valid_input(**kwargs):
    return {"control": 0}


def double_control_valid_ir_input(**kwargs):
    return {"controls": [0, 1]}


def double_control_valid_input(**kwargs):
    return {"control1": 0, "control2": 1}


def multi_target_valid_input(**kwargs):
    return {"targets": [5]}


def two_dimensional_matrix_list_valid_ir_input(**kwargs):
    return {"matrices": [[[[0, 0], [1, 0]], [[1, 0], [0, 0]]]]}


def two_dimensional_matrix_list_valid_input(**kwargs):
    input_type = kwargs.get("input_type")
    return {
        "matrices": [np.array([[input_type(0), input_type(1)], [input_type(1), input_type(0)]])]
    }


def multi_probability_valid_input(**kwargs):
    return {"probabilities": {"XX": 0.1}}


def multi_probability_invalid_input(**kwargs):
    return {"probabilities": {"XX": 1.1}}


valid_ir_switcher = {
    "SingleTarget": single_target_valid_input,
    "DoubleTarget": double_target_valid_ir_input,
    "SingleProbability": single_probability_valid_input,
    "SingleProbability_34": single_probability_34_valid_input,
    "SingleProbability_1516": single_probability_1516_valid_input,
    "DampingProbability": damping_probability_valid_input,
    "DampingSingleProbability": damping_single_probability_valid_input,
    "TripleProbability": triple_probability_valid_input,
    "MultiProbability": multi_probability_valid_input,
    "SingleControl": single_control_valid_input,
    "DoubleControl": double_control_valid_ir_input,
    "MultiTarget": multi_target_valid_input,
    "TwoDimensionalMatrixList": two_dimensional_matrix_list_valid_ir_input,
}


valid_subroutine_switcher = dict(
    valid_ir_switcher,
    **{
        "TwoDimensionalMatrixList": two_dimensional_matrix_list_valid_input,
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
        elif any(
            subclass == i
            for i in [
                SingleProbability,
                SingleProbability_34,
                SingleProbability_1516,
                DampingSingleProbability,
                DampingProbability,
                TripleProbability,
                TwoDimensionalMatrixList,
                MultiProbability,
            ]
        ):
            pass
        else:
            raise ValueError("Invalid subclass")
    input["target"] = QubitSet(qubit_set)
    return input


def create_valid_noise_class_input(irsubclasses, **kwargs):
    input = {}
    if SingleProbability in irsubclasses:
        input.update(single_probability_valid_input())
    if SingleProbability_34 in irsubclasses:
        input.update(single_probability_34_valid_input())
    if SingleProbability_1516 in irsubclasses:
        input.update(single_probability_1516_valid_input())
    if DampingSingleProbability in irsubclasses:
        input.update(damping_single_probability_valid_input())
    if DampingProbability in irsubclasses:
        input.update(damping_probability_valid_input())
    if TripleProbability in irsubclasses:
        input.update(triple_probability_valid_input())
    if MultiProbability in irsubclasses:
        input.update(multi_probability_valid_input())
    if TwoDimensionalMatrixList in irsubclasses:
        input.update(two_dimensional_matrix_list_valid_input(**kwargs))
    return input


def create_valid_instruction_input(testclass, irsubclasses, **kwargs):
    input = create_valid_target_input(irsubclasses)
    input["operator"] = testclass(**create_valid_noise_class_input(irsubclasses, **kwargs))
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
        elif any(
            subclass == i
            for i in [
                SingleProbability,
                SingleProbability_34,
                SingleProbability_1516,
                DampingSingleProbability,
                DampingProbability,
                TripleProbability,
                MultiProbability,
                TwoDimensionalMatrixList,
            ]
        ):
            pass
        else:
            raise ValueError("Invalid subclass")
    return qubit_count


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_ir_noise_level(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    expected = irclass(**create_valid_ir_input(irsubclasses))
    actual = testclass(**create_valid_noise_class_input(irsubclasses, **kwargs)).to_ir(
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
def test_noise_subroutine(testclass, subroutine_name, irclass, irsubclasses, kwargs):
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
                    operator=testclass(**create_valid_noise_class_input(irsubclasses, **kwargs)),
                    target=target,
                )
            )
        subroutine = getattr(Circuit(), subroutine_name)
        subroutine_input = {"target": multi_targets}
        if SingleProbability in irsubclasses:
            subroutine_input.update(single_probability_valid_input())
        if SingleProbability_34 in irsubclasses:
            subroutine_input.update(single_probability_34_valid_input())
        if SingleProbability_1516 in irsubclasses:
            subroutine_input.update(single_probability_1516_valid_input())
        if DampingSingleProbability in irsubclasses:
            subroutine_input.update(damping_single_probability_valid_input())
        if DampingProbability in irsubclasses:
            subroutine_input.update(damping_probability_valid_input())
        if TripleProbability in irsubclasses:
            subroutine_input.update(triple_probability_valid_input())
        if MultiProbability in irsubclasses:
            subroutine_input.update(multi_probability_valid_input())

        circuit1 = subroutine(**subroutine_input)
        circuit2 = Circuit(instruction_list)
        assert circuit1 == circuit2


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_noise_to_matrix(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    noise1 = testclass(**create_valid_noise_class_input(irsubclasses, **kwargs))
    noise2 = testclass(**create_valid_noise_class_input(irsubclasses, **kwargs))
    assert all(isinstance(matrix, np.ndarray) for matrix in noise1.to_matrix())
    assert all(np.allclose(m1, m2) for m1, m2 in zip(noise1.to_matrix(), noise2.to_matrix()))


@pytest.mark.parametrize("testclass,subroutine_name,irclass,irsubclasses,kwargs", testdata)
def test_fixed_qubit_count(testclass, subroutine_name, irclass, irsubclasses, kwargs):
    fixed_qubit_count = testclass.fixed_qubit_count()
    if fixed_qubit_count is not NotImplemented:
        noise = testclass(**create_valid_noise_class_input(irsubclasses, **kwargs))
        assert noise.qubit_count == fixed_qubit_count


# Additional Unitary noise tests


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("matrices", invalid_kraus_matrices)
def test_kraus_invalid_matrix(matrices):
    Noise.Kraus(matrices=matrices)


@pytest.mark.xfail(raises=ValueError)
def test_kraus_matrix_target_size_mismatch():
    Circuit().kraus(
        matrices=[np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])], targets=[0]
    )


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize(
    "probs",
    [
        {"X": -0.1},
        {"XY": 1.1},
        {"TX": 0.1},
        {"X": 0.5, "Y": 0.6},
        {"X": 0.1, "YY": 0.2},
        {"II": 0.9, "XX": 0.1},
    ],
)
def test_invalid_values_pauli_channel_two_qubit(probs):
    Noise.TwoQubitPauliChannel(probs)


@pytest.mark.parametrize(
    "probs",
    [
        {"XY": 0.1},
        {"XX": 0.1, "ZZ": 0.2},
    ],
)
def test_valid_values_pauli_channel_two_qubit(probs):
    noise = Noise.TwoQubitPauliChannel(probs)
    assert len(noise.to_matrix()) == 16
