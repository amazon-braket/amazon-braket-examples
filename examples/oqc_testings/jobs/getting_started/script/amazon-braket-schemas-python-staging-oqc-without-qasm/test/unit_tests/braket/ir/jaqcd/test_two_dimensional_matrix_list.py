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

from braket.ir.jaqcd.shared_models import TwoDimensionalMatrixList


@pytest.mark.xfail(raises=ValidationError)
def test_missing_targets():
    TwoDimensionalMatrixList()


@pytest.mark.xfail(raises=ValidationError)
def test_list_partial_non_int():
    TwoDimensionalMatrixList(matrices=[[0, "foo"]])


@pytest.mark.xfail(raises=ValidationError)
def test_empty_nested_list():
    TwoDimensionalMatrixList(matrices=[[]])


@pytest.mark.xfail(raises=ValidationError)
def test_element_list_size_gt_two():
    TwoDimensionalMatrixList(matrices=[[[0, 1, 2]]])


@pytest.mark.xfail(raises=ValidationError)
def test_empty_list():
    TwoDimensionalMatrixList(matrices=[])


@pytest.mark.xfail(raises=ValidationError)
def test_single_matrix():
    TwoDimensionalMatrixList(
        matrices=[[[1, 0], [0, 0]], [[0, 0], [1, 0]], [[0, 0], [1, 0]], [[1, 0], [0, 0]]]
    )


def test_list_gte_zero():
    matrices = [[[[1, 0], [0, 0]], [[0, 0], [1, 0]]], [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]]
    obj = TwoDimensionalMatrixList(matrices=matrices)
    assert obj.matrices == matrices


def test_list_extra_params():
    TwoDimensionalMatrixList(
        matrices=[[[[1, 0], [0, 0]], [[0, 0], [1, 0]]], [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]],
        foo="bar",
    )
