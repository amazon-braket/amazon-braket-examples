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

from braket.device_schema.rigetti.rigetti_device_capabilities_v1 import RigettiDeviceCapabilities


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.rigetti.rigetti_device_capabilities",
            "version": "1",
        },
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
            "braket.ir.jaqcd.program": {
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
        },
        "paradigm": {
            "braketSchemaHeader": {
                "name": "braket.device_schema.gate_model_qpu_paradigm_properties",
                "version": "1",
            },
            "qubitCount": 32,
            "nativeGateSet": ["ccnot", "cy"],
            "connectivity": {"fullyConnected": False, "connectivityGraph": {"1": ["2", "3"]}},
        },
        "deviceParameters": {},
    }
    return input


def test_valid(valid_input):
    result = RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))
    assert (
        result.braketSchemaHeader.name == "braket.device_schema.rigetti.rigetti_device_capabilities"
    )


@pytest.mark.xfail(raises=ValidationError)
def test__missing_schemaHeader(valid_input):
    valid_input.pop("braketSchemaHeader")
    RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_paradigm(valid_input):
    valid_input.pop("paradigm")
    RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_deviceParameters(valid_input):
    valid_input.pop("deviceParameters")
    RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_action(valid_input):
    valid_input.pop("action")
    RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_service(valid_input):
    valid_input.pop("service")
    RigettiDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))
