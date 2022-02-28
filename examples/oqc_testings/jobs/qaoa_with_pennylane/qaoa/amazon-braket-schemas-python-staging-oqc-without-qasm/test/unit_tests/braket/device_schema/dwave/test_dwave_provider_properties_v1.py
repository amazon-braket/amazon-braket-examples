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

from braket.device_schema.dwave.dwave_provider_properties_v1 import DwaveProviderProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
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
        "extendedJRange": [1.1, 2.45, 3.45],
        "hGainScheduleRange": [1.11, 2.56, 3.67],
        "hRange": [1.4, 2.6, 3.66],
        "jRange": [1.67, 2.666, 3.666],
        "maximumAnnealingSchedulePoints": 1,
        "maximumHGainSchedulePoints": 1,
        "perQubitCouplingRange": [1.777, 2.567, 3.1201],
        "programmingThermalizationDurationRange": [1, 2, 3],
        "qubits": [1, 2, 3],
        "qubitCount": 1,
        "quotaConversionRate": 1.341234,
        "readoutThermalizationDurationRange": [1, 2, 3],
        "taskRunDurationRange": [1, 2, 3],
        "topology": {},
    }
    return input


def test_valid(valid_input):
    result = DwaveProviderProperties.parse_raw_schema(json.dumps(valid_input))
    assert result.qubitCount == 1


@pytest.mark.xfail(raises=ValidationError)
def test__missing_schemaHeader(valid_input):
    valid_input.pop("braketSchemaHeader")
    DwaveProviderProperties.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test__missing_qubitCount(valid_input):
    valid_input.pop("qubitCount")
    DwaveProviderProperties.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test__invalid_qubitcount(valid_input):
    valid_input["qubitCount"] = "string"
    DwaveProviderProperties.parse_raw_schema(json.dumps(valid_input))
