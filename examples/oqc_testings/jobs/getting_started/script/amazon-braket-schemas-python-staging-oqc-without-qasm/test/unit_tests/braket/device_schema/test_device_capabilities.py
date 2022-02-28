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

from braket.device_schema.device_capabilities import DeviceCapabilities


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "service": {
            "braketSchemaHeader": {
                "name": "braket.device_schema.device_service_properties",
                "version": "1",
            },
            "executionWindows": [
                {"executionDay": "Everyday", "windowStartHour": "11:00", "windowEndHour": "12:00"}
            ],
            "shotsRange": [1, 10],
            "deviceCost": {"price": 0.25, "unit": "minute"},
            "deviceDocumentation": {
                "imageUrl": "image_url",
                "summary": "Summary on the device",
                "externalDocumentationUrl": "exter doc link",
            },
            "deviceLocation": "us-east-1",
            "updatedAt": "2020-06-16T19:28:02.869136",
        },
        "action": {
            "braket.ir.jaqcd.program": {"actionType": "braket.ir.jaqcd.program", "version": ["1"]}
        },
        "deviceParameters": {},
    }
    return input


def test_valid(valid_input):
    assert DeviceCapabilities.parse_raw(json.dumps(valid_input))


def test_valid_action_str(valid_input):
    action = valid_input["action"]
    action["blah"] = action["braket.ir.jaqcd.program"]
    action.pop("braket.ir.jaqcd.program")
    assert DeviceCapabilities.parse_raw(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_action(valid_input):
    valid_input.pop("action")
    DeviceCapabilities.parse_raw(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_service(valid_input):
    valid_input.pop("service")
    DeviceCapabilities.parse_raw(json.dumps(valid_input))
