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

from pydantic import Field, conint

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class SimulatorMetadata(BraketSchemaBase):
    """
    The simulator metadata result schema.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header.
            Users do not need to set this value. Only default is allowed.
        executionDuration (int): The number of milliseconds it took to execute
            the circuit on the simulator.

    Examples:
        >>> SimulatorMetadata(executionDuration=100)

    """

    _SIMULATOR_METADATA_HEADER = BraketSchemaHeader(
        name="braket.task_result.simulator_metadata", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_SIMULATOR_METADATA_HEADER, const=_SIMULATOR_METADATA_HEADER
    )
    executionDuration: conint(ge=0)
