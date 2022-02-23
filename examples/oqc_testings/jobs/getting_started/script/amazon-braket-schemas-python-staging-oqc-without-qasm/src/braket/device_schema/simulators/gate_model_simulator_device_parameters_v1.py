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

from braket.device_schema.gate_model_parameters_v1 import GateModelParameters
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class GateModelSimulatorDeviceParameters(BraketSchemaBase):
    """
    This defines the parameters common to all the gatemodel devices.

    Attributes:
        paradigmParameters: Parameters that are common to gatemodel paradigm

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.simulators.gate_model_simulator_device_parameters",
        ...        "version": "1",
        ...    },
        ...    "paradigmParameters": {"braketSchemaHeader": {
        ...        "name": "braket.device_schema.gate_model_parameters",
        ...        "version": "1",
        ...    },"qubitCount": 1},
        ... }
        >>> GateModelSimulatorDeviceParameters.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.simulators.gate_model_simulator_device_parameters", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    paradigmParameters: GateModelParameters
