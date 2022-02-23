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

from braket.ir.jaqcd.shared_models import Angle


@pytest.mark.xfail(raises=ValidationError)
def test_missing_angle():
    Angle()


@pytest.mark.xfail(raises=ValidationError)
def test_non_float():
    Angle(angle="foo")


@pytest.mark.xfail(raises=ValidationError)
def test_nan_float():
    Angle(angle=float("nan"))


@pytest.mark.xfail(raises=ValidationError)
def test_inf_float():
    Angle(angle=float("inf"))


@pytest.mark.xfail(raises=ValidationError)
def test_negative_inf_float():
    Angle(angle=float("-inf"))


def test_float():
    angle = 0.15
    obj = Angle(angle=angle)
    assert obj.angle == angle


def test_extra_params():
    Angle(angle=0, foo="bar")
