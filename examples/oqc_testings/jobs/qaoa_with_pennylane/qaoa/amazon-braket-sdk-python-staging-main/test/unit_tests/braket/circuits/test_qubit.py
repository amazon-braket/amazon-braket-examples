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

import numpy as np
import pytest

from braket.circuits import Qubit


@pytest.fixture
def qubit():
    return Qubit(5)


@pytest.mark.xfail(raises=ValueError)
def test_index_lt_zero():
    Qubit(-1)


@pytest.mark.parametrize("qubit_arg", ("not a number", 0.5))
@pytest.mark.xfail(raises=TypeError)
def test_index_non_int(qubit_arg):
    Qubit(qubit_arg)


@pytest.mark.parametrize("qubit_index", (0, 5, np.int64(5)))
def test_index_gte_zero(qubit_index):
    Qubit(qubit_index)


def test_str(qubit):
    expected = "Qubit({})".format(int(qubit))
    assert str(qubit) == expected


def test_new_with_qubit():
    qubit = Qubit(0)
    qubit_new = Qubit.new(qubit)
    assert qubit_new == qubit
    assert qubit_new is qubit


def test_new_with_int():
    qubit = 0
    qubit_new = Qubit.new(qubit)
    assert qubit_new == qubit
    assert qubit_new is not qubit
