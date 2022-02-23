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

from braket.device_schema.jaqcd_device_action_properties import JaqcdDeviceActionProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "actionType": "braket.ir.jaqcd.program",
        "version": ["1"],
        "supportedOperations": ["x", "y"],
        "supportedResultTypes": [
            {"name": "resultType1", "observables": ["observable1"], "minShots": 2, "maxShots": 4}
        ],
        "disabledQubitRewiringSupported": True,
    }
    return input


def test_valid(valid_input):
    result = JaqcdDeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.actionType == "braket.ir.jaqcd.program"
    assert result.supportedOperations == ["x", "y"]
    assert result.supportedResultTypes == [
        {"name": "resultType1", "observables": ["observable1"], "minShots": 2, "maxShots": 4}
    ]
    assert result.disabledQubitRewiringSupported


def test_no_qubit_rewiring_unsupported():
    result = JaqcdDeviceActionProperties.parse_raw(
        json.dumps(
            {
                "actionType": "braket.ir.jaqcd.program",
                "version": ["1"],
                "supportedOperations": ["x", "y"],
                "supportedResultTypes": [
                    {
                        "name": "resultType1",
                        "observables": ["observable1"],
                        "minShots": 2,
                        "maxShots": 4,
                    }
                ],
                "disabledQubitRewiringSupported": False,
            }
        )
    )
    assert result.disabledQubitRewiringSupported is False


def test_no_qubit_rewiring_unspecified():
    result = JaqcdDeviceActionProperties.parse_raw(
        json.dumps(
            {
                "actionType": "braket.ir.jaqcd.program",
                "version": ["1"],
                "supportedOperations": ["x", "y"],
                "supportedResultTypes": [
                    {
                        "name": "resultType1",
                        "observables": ["observable1"],
                        "minShots": 2,
                        "maxShots": 4,
                    }
                ],
            }
        )
    )
    assert result.disabledQubitRewiringSupported is None


@pytest.mark.xfail(raises=ValidationError)
def test_missing_action_type(valid_input):
    valid_input.pop("actionType")
    JaqcdDeviceActionProperties.parse_raw(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_invalid_supported_operations(valid_input):
    valid_input.pop("supportedOperations")
    JaqcdDeviceActionProperties.parse_raw(json.dumps(valid_input))
