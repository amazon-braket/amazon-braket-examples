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

from braket.ir.jaqcd.shared_models import TripleProbability


@pytest.mark.xfail(raises=ValidationError)
def test_missing_probability():
    TripleProbability()


@pytest.mark.xfail(raises=ValidationError)
def test_non_float():
    TripleProbability(probX="foo", probY=0, probZ=0)


@pytest.mark.xfail(raises=ValidationError)
def test_nan_float():
    TripleProbability(probX=float("nan"), probY=0, probZ=0)


@pytest.mark.xfail(raises=ValidationError)
def test_inf_float():
    TripleProbability(probX=float("inf"), probY=0, probZ=0)


@pytest.mark.xfail(raises=ValidationError)
def test_negative_inf_float():
    TripleProbability(probX=float("-inf"), probY=0, probZ=0)


@pytest.mark.xfail(raises=ValidationError)
def test_negative_float():
    TripleProbability(probX=float(-1.5), probY=0, probZ=0)


@pytest.mark.xfail(raises=ValidationError)
def test_greater_than_one_float():
    TripleProbability(probX=float(2.1), probY=0, probZ=0)


@pytest.mark.xfail(raises=ValueError)
def test_too_large_probability():
    TripleProbability(probX=float(0.6), probY=float(0.4), probZ=float(0.1))


def test_float():
    probX = 0.15
    probY = 0.2
    probZ = 0.25
    obj = TripleProbability(probX=probX, probY=probY, probZ=probZ)
    assert obj.probX == probX
    assert obj.probY == probY
    assert obj.probZ == probZ


def test_extra_params():
    TripleProbability(probX=0, probY=0, probZ=0, foo="bar")
