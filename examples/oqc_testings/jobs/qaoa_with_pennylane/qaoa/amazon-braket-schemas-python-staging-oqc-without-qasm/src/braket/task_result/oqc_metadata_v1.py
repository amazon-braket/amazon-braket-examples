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
# language governing permissions and limitations under the License

from pydantic import Field, constr

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class OqcMetadata(BraketSchemaBase):
    """
    The Oqc metadata result schema.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header.
            Users do not need to set this value. Only default is allowed.
        executedProgram (str): The program executed on the QPU.

    Examples:
        >>> OqcMetadata(executedProgram="DECLARE ro BIT[2];")
    """

    _OQC_METADATA_HEADER = BraketSchemaHeader(name="braket.task_result.oqc_metadata", version="1")
    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_OQC_METADATA_HEADER, const=_OQC_METADATA_HEADER
    )

    executedProgram: constr(min_length=2)
