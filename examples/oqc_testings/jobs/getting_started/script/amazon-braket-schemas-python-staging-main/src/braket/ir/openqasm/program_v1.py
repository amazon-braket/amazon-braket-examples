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

from pydantic import Field

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class Program(BraketSchemaBase):
    """
    Root object of the OpenQASM IR.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        source (str): OpenQASM source program.

    Examples:
        >>> OpenQASMProgram(source='OPENQASM3.0; cx $0, $1')
    """

    _PROGRAM_HEADER = BraketSchemaHeader(name="braket.ir.openqasm.program", version="1")
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    source: str
