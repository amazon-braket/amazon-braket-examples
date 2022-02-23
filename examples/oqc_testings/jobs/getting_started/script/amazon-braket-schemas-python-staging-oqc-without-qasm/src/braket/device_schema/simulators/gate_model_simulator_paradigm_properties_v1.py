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

from pydantic import Field, conint

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class GateModelSimulatorParadigmProperties(BraketSchemaBase):

    """
    This class defines the properties that are specific to simulator device

    Attributes:
        qubitCount: number of qubits simulator device contains

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name":
        ...             "braket.device_schema.simulators.gate_model_simulator_paradigm_properties",
        ...        "version": "1",
        ...    },
        ...    "qubitCount": 32
        ... }
        >>> GateModelSimulatorParadigmProperties.parse_raw_schema(json.dumps(input_json))

    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.simulators.gate_model_simulator_paradigm_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    qubitCount: conint(ge=0)
