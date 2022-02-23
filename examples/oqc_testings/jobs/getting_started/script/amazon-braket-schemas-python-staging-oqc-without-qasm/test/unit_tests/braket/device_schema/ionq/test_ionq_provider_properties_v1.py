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

from braket.device_schema.ionq.ionq_provider_properties_v1 import IonqProviderProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.ionq.ionq_provider_properties",
            "version": "1",
        },
        "fidelity": {"1Q": {"mean": 0.99717}, "2Q": {"mean": 0.9696}, "spam": {"mean": 0.9961}},
        "timing": {
            "T1": 10000000000,
            "T2": 500000,
            "1Q": 1.1e-05,
            "2Q": 0.00021,
            "readout": 0.000175,
            "reset": 3.5e-05,
        },
    }
    return input


def test_valid(valid_input):
    result = IonqProviderProperties.parse_raw_schema(json.dumps(valid_input))
    assert result.braketSchemaHeader.name == "braket.device_schema.ionq.ionq_provider_properties"


@pytest.mark.xfail(raises=ValidationError)
def test__missing_schemaHeader(valid_input):
    valid_input.pop("braketSchemaHeader")
    IonqProviderProperties.parse_raw_schema(json.dumps(valid_input))


@pytest.mark.xfail(raises=ValidationError)
def test__missing_fidelity(valid_input):
    valid_input.pop("fidelity")
    IonqProviderProperties.parse_raw_schema(json.dumps(valid_input))
