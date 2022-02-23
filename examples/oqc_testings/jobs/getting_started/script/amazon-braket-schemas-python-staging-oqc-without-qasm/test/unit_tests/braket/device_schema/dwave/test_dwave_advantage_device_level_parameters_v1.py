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
from jsonschema import validate
from pydantic import ValidationError

from braket.device_schema.dwave import (
    DwaveAdvantageDeviceLevelParameters,
    DwaveAdvantageDeviceParameters,
)
from braket.device_schema.dwave.dwave_provider_level_parameters_v1 import (
    DwaveProviderLevelParameters,
)


@pytest.mark.parametrize(
    "annealing_duration",
    (0.5, 1.5, 500, pytest.param(0, marks=pytest.mark.xfail(reason="positive int constraint"))),
)
@pytest.mark.parametrize(
    "max_results",
    (1, 20, pytest.param(0, marks=pytest.mark.xfail(reason="positive int constraint"))),
)
def test_valid(annealing_duration, max_results):
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.dwave.dwave_advantage_device_level_parameters",
            "version": "1",
        },
        "annealingOffsets": [3.67, 6.123],
        "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
        "annealingDuration": annealing_duration,
        "autoScale": None,
        "compensateFluxDrift": False,
        "fluxBiases": [1.1, 2.2, 3.3, 4.4],
        "initialState": [1, 3, 0, 1],
        "maxResults": max_results,
        "programmingThermalizationDuration": 625,
        "readoutThermalizationDuration": 256,
        "reduceIntersampleCorrelation": False,
        "reinitializeState": True,
        "resultFormat": "RAW",
        "spinReversalTransformCount": 100,
    }
    assert DwaveProviderLevelParameters.parse_raw_schema(json.dumps(input))


@pytest.mark.xfail(raises=ValidationError)
def test_invalid_attribute():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.dwave.dwave_advantage_device_level_parameters",
            "version": "1",
        },
        "annealingOffsets": 1,
    }
    # annealingOffsets should be List[int]
    DwaveProviderLevelParameters.parse_raw_schema(json.dumps(input))


# to demonstrate that validation ignore unkown fields
def test_invalid_attribute_name():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.dwave.dwave_advantage_device_level_parameters",
            "version": "1",
        },
        "fakeParameter": "fakeValue",
        "beta": 123.456,
    }
    # annealingOffsets should be List[int]
    device_level_params = DwaveAdvantageDeviceLevelParameters.parse_raw_schema(json.dumps(input))
    try:
        assert device_level_params.beta
        raise Exception("beta should not be parsed into the model")
    except AttributeError:
        pass
    device_parameters = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.dwave.dwave_advantage_device_parameters",
            "version": "1",
        },
        "deviceLevelParameters": input,
    }
    validate(device_parameters, DwaveAdvantageDeviceParameters.schema())
