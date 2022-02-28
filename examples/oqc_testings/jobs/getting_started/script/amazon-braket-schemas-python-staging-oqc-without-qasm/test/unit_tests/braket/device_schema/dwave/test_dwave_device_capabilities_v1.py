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

from braket.device_schema.dwave import DwaveDeviceCapabilities


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.dwave.dwave_device_capabilities",
            "version": "1",
        },
        "provider": {
            "braketSchemaHeader": {
                "name": "braket.device_schema.dwave.dwave_provider_properties",
                "version": "1",
            },
            "annealingOffsetStep": 1.45,
            "annealingOffsetStepPhi0": 1.45,
            "annealingOffsetRanges": [[1.45, 1.45], [1.45, 1.45]],
            "annealingDurationRange": [1.45, 2.45, 3],
            "couplers": [[1, 2, 3], [1, 2, 3]],
            "defaultAnnealingDuration": 1,
            "defaultProgrammingThermalizationDuration": 1,
            "defaultReadoutThermalizationDuration": 1,
            "extendedJRange": [1, 2, 3],
            "hGainScheduleRange": [1, 2, 3],
            "hRange": [1, 2, 3],
            "jRange": [1, 2, 3],
            "maximumAnnealingSchedulePoints": 1,
            "maximumHGainSchedulePoints": 1,
            "perQubitCouplingRange": [1, 2, 3],
            "programmingThermalizationDurationRange": [1, 2, 3],
            "qubits": [1, 2, 3],
            "qubitCount": 1,
            "quotaConversionRate": 1,
            "readoutThermalizationDurationRange": [1, 2, 3],
            "taskRunDurationRange": [1, 2, 3],
            "topology": {},
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
            "braket.ir.annealing.problem": {
                "actionType": "braket.ir.annealing.problem",
                "version": ["1"],
            }
        },
        "paradigm": {
            "braketSchemaHeader": {
                "name": "braket.device_schema.device_paradigm_properties",
                "version": "1",
            }
        },
        "deviceParameters": {
            "braketSchemaHeader": {
                "name": "braket.device_schema.dwave.dwave_device_parameters",
                "version": "1",
            },
            "providerLevelParameters": {
                "braketSchemaHeader": {
                    "name": "braket.device_schema.dwave.dwave_provider_level_parameters",
                    "version": "1",
                }
            },
        },
    }
    return input


def test_valid(valid_input):
    result = DwaveDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))
    assert result.provider.qubitCount == 1


@pytest.mark.xfail(raises=ValidationError)
def test__missing_schemaHeader(valid_input):
    valid_input.pop("braketSchemaHeader")
    DwaveDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test_missing_qubitCount(valid_input):
    valid_input.pop("provider")
    DwaveDeviceCapabilities.parse_raw_schema(json.dumps(valid_input))
