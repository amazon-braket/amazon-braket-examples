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

import re

import numpy as np
import pytest
from pydantic import BaseModel

from braket.circuits import AngledGate, Gate


@pytest.fixture
def angled_gate():
    return AngledGate(angle=0.15, qubit_count=1, ascii_symbols=["foo"])


def test_is_operator(angled_gate):
    assert isinstance(angled_gate, Gate)


@pytest.mark.xfail(raises=ValueError)
def test_angle_is_none():
    AngledGate(qubit_count=1, ascii_symbols=["foo"], angle=None)


def test_getters():
    qubit_count = 2
    ascii_symbols = ("foo", "bar")
    angle = 0.15
    gate = AngledGate(angle=angle, qubit_count=qubit_count, ascii_symbols=ascii_symbols)

    assert gate.qubit_count == qubit_count
    assert gate.ascii_symbols == ascii_symbols
    assert gate.angle == angle


@pytest.mark.xfail(raises=AttributeError)
def test_angle_setter(angled_gate):
    angled_gate.angle = 0.14


def test_equality(angled_gate):
    gate = AngledGate(angle=0.15, qubit_count=1, ascii_symbols=["bar"])
    other_gate = AngledGate(angle=0.3, qubit_count=1, ascii_symbols=["foo"])
    non_gate = "non gate"

    assert angled_gate == gate
    assert angled_gate is not gate
    assert angled_gate != other_gate
    assert angled_gate != non_gate


def test_np_float_angle_json():
    angled_gate = AngledGate(angle=np.float32(0.15), qubit_count=1, ascii_symbols=["foo"])
    angled_gate_json = BaseModel.construct(target=[0], angle=angled_gate.angle).json()
    match = re.match(r'\{"target": \[0], "angle": (\d*\.?\d*)}', angled_gate_json)
    angle_value = float(match.group(1))
    assert angle_value == angled_gate.angle
