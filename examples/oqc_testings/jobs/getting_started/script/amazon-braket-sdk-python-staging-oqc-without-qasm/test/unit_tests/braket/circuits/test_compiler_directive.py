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

from braket.circuits import Operator
from braket.circuits.compiler_directive import CompilerDirective


@pytest.fixture
def ascii_symbols():
    return ["foo"]


@pytest.fixture
def compiler_directive(ascii_symbols):
    return CompilerDirective(ascii_symbols=ascii_symbols)


def test_is_operator(compiler_directive):
    assert isinstance(compiler_directive, Operator)


def test_ascii_symbols(compiler_directive, ascii_symbols):
    assert compiler_directive.ascii_symbols == tuple(ascii_symbols)


@pytest.mark.xfail(raises=ValueError)
def test_none_ascii():
    CompilerDirective(ascii_symbols=None)


def test_name(compiler_directive):
    expected = compiler_directive.__class__.__name__
    assert compiler_directive.name == expected


@pytest.mark.xfail(raises=NotImplementedError)
def test_to_ir_not_implemented_by_default(compiler_directive):
    compiler_directive.to_ir(None)


def test_str(compiler_directive):
    assert str(compiler_directive) == compiler_directive.name
