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

import braket.ir.jaqcd as ir
from braket.circuits import compiler_directives
from braket.circuits.compiler_directive import CompilerDirective

testdata = [
    (compiler_directives.StartVerbatimBox, ir.StartVerbatimBox),
    (compiler_directives.EndVerbatimBox, ir.EndVerbatimBox),
]


@pytest.mark.parametrize("testclass,irclass", testdata)
def test_to_ir(testclass, irclass):
    assert testclass().to_ir() == irclass()


@pytest.mark.parametrize("testclass,irclass", testdata)
def test_equality(testclass, irclass):
    op1 = testclass()
    op2 = testclass()
    assert op1 == op2
    assert op1 is not op2
    assert op1 != CompilerDirective(ascii_symbols=["foo"])
    assert op1 != "not a directive"
