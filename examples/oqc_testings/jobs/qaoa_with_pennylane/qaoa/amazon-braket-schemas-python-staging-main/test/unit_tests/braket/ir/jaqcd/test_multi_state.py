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

import pytest
from pydantic import ValidationError

from braket.ir.jaqcd.shared_models import MultiState


@pytest.mark.xfail(raises=ValidationError)
def test_missing_states():
    MultiState()


@pytest.mark.xfail(raises=ValidationError)
def test_list_partial_non_str():
    MultiState(states=[20, "101"])


@pytest.mark.xfail(raises=ValidationError)
def test_list_partial_non_matching_regex():
    MultiState(states=["10202", "01"])


@pytest.mark.xfail(raises=ValidationError)
def test_empty_list():
    MultiState(states=[])


def test_list_matching_regex():
    states = ["1", "10101"]
    obj = MultiState(states=states)
    assert obj.states == states


def test_list_extra_params():
    MultiState(states=["01", "01101"], foo="bar")
