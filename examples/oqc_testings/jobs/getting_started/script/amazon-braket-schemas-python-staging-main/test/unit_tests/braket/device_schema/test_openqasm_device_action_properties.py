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

import json

import pytest
from pydantic import ValidationError

from braket.device_schema.openqasm_device_action_properties import OpenQASMDeviceActionProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "actionType": "braket.ir.openqasm.program",
        "version": ["1"],
        "supportedOperations": ["x", "y"],
        "supportedResultTypes": [
            {"name": "resultType1", "observables": ["observable1"], "minShots": 2, "maxShots": 4}
        ],
        "supportPhysicalQubits": True,
        "supportedPragmas": ["braket_bit_flip_noise"],
        "forbiddenPragmas": ["braket_kraus_operator"],
        "forbiddenArrayOperations": ["concatenation", "range", "slicing"],
        "requiresAllQubitsMeasurement": False,
        "requiresContiguousQubitIndices": False,
    }
    return input


def test_valid(valid_input):
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.actionType == "braket.ir.openqasm.program"
    assert result.supportedOperations == ["x", "y"]
    assert result.supportedResultTypes == [
        {"name": "resultType1", "observables": ["observable1"], "minShots": 2, "maxShots": 4}
    ]
    assert result.supportPhysicalQubits is True
    assert result.supportedPragmas == ["braket_bit_flip_noise"]
    assert result.forbiddenPragmas == ["braket_kraus_operator"]
    assert result.forbiddenArrayOperations == ["concatenation", "range", "slicing"]
    assert result.requiresAllQubitsMeasurement is False
    assert result.requiresContiguousQubitIndices is False


def test_default_supported_result_types(valid_input):
    valid_input.pop("supportedResultTypes")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.supportedResultTypes is None


def test_default_supports_physical_qubits(valid_input):
    valid_input.pop("supportPhysicalQubits")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.supportPhysicalQubits is False


def test_default_supported_pragmas(valid_input):
    valid_input.pop("supportedPragmas")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.supportedPragmas == []


def test_default_forbidden_pragmas(valid_input):
    valid_input.pop("forbiddenPragmas")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.forbiddenPragmas == []


def test_default_forbidden_array_operations(valid_input):
    valid_input.pop("forbiddenArrayOperations")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.forbiddenArrayOperations == []


def test_default_requires_all_qubits_measurement(valid_input):
    valid_input.pop("requiresAllQubitsMeasurement")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.requiresAllQubitsMeasurement is False


def test_default_requires_contiguous_qubit_indices(valid_input):
    valid_input.pop("requiresContiguousQubitIndices")
    result = OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.requiresContiguousQubitIndices is False


@pytest.mark.xfail(raises=ValidationError)
def test_missing_action_type(valid_input):
    valid_input.pop("actionType")
    OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_invalid_supported_operations(valid_input):
    valid_input.pop("supportedOperations")
    OpenQASMDeviceActionProperties.parse_raw(json.dumps(valid_input))
