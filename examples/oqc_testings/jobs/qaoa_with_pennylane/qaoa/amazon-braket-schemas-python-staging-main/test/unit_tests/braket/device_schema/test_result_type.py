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

from braket.device_schema.result_type import ResultType


@pytest.fixture(scope="module")
def valid_input():
    input = {"name": "resultType1", "observables": ["observable1"], "minShots": 2, "maxShots": 4}
    return input


def test_valid(valid_input):
    result = ResultType.parse_raw(json.dumps(valid_input))
    assert result.name == "resultType1"
    assert result.observables == ["observable1"]
    assert result.minShots == 2
    assert result.maxShots == 4


@pytest.mark.xfail(raises=ValidationError)
def test_missing_name(valid_input):
    valid_input.pop("name")
    ResultType.parse_raw(json.dumps(valid_input))
