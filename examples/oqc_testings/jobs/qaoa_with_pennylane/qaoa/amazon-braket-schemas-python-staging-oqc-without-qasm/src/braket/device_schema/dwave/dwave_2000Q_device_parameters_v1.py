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

from pydantic import Field

from braket.device_schema.dwave.dwave_2000Q_device_level_parameters_v1 import (
    Dwave2000QDeviceLevelParameters,
)
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class Dwave2000QDeviceParameters(BraketSchemaBase):
    """
    This is the description of the D-Wave parameters

    Attributes:
        deviceLevelParameters: Parameters that are specific to this D-Wave device.
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.dwave.dwave_2000Q_device_parameters", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    deviceLevelParameters: Dwave2000QDeviceLevelParameters
