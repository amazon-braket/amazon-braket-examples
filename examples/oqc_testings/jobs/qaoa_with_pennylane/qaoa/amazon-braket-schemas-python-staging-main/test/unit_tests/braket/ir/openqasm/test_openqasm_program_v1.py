# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
# # or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import pytest
from pydantic import ValidationError

from braket.ir.openqasm.program_v1 import Program as OpenQASMProgram


@pytest.mark.xfail(raises=ValidationError)
def test_missing_source_property():
    OpenQASMProgram()


def test_arbitrary_openqasm_program():
    obj = OpenQASMProgram(source="this is a string.")
    assert obj.braketSchemaHeader.name == "braket.ir.openqasm.program"
    assert obj.source == "this is a string."


def test_parse_obj():
    obj = OpenQASMProgram(source="this is a string.")
    assert obj == OpenQASMProgram.parse_obj(obj.dict())


def test_parse_raw():
    obj = OpenQASMProgram(source="this is a string.")
    assert obj == OpenQASMProgram.parse_raw(obj.json())
