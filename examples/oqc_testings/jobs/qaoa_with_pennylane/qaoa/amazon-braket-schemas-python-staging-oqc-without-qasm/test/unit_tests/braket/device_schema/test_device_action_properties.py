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

from braket.device_schema.device_action_properties import DeviceActionProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "actionType": "braket.ir.jaqcd.program",
        "version": ["1"],
    }
    return input


def test_valid(valid_input):
    result = DeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.actionType == "braket.ir.jaqcd.program"


def test_valid_str_invalid_enum(valid_input):
    valid_input["actionType"] = "blah"
    result = DeviceActionProperties.parse_raw(json.dumps(valid_input))
    assert result.actionType == "blah"


@pytest.mark.xfail(raises=ValidationError)
def test__missing_actionType(valid_input):
    valid_input.pop("actionType")
    DeviceActionProperties.parse_raw(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test__missing_version(valid_input):
    valid_input.pop("version")
    DeviceActionProperties.parse_raw(json.dumps(valid_input))
