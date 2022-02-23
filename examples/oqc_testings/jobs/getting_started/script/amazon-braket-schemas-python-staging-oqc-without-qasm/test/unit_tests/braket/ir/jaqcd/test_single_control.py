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

from braket.ir.jaqcd.shared_models import SingleControl


@pytest.mark.xfail(raises=ValidationError)
def test_missing_control():
    SingleControl()


@pytest.mark.xfail(raises=ValidationError)
def test_non_int():
    SingleControl(control="foo")


@pytest.mark.xfail(raises=ValidationError)
def test_int_lt_zero():
    SingleControl(control=-1)


def test_int_gte_zero():
    for control in (0, 1):
        obj = SingleControl(control=control)
        assert obj.control == control


def test_int_extra_params():
    SingleControl(control=0, foo="bar")


@pytest.mark.xfail(raises=ValidationError)
def test_list():
    SingleControl(control=[0])
