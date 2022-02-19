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

from enum import Enum
from typing import List, Union

from pydantic import BaseModel


class DeviceActionType(str, Enum):
    """
    These are the actions supported by Braket.
    """

    OPENQASM = "braket.ir.openqasm.program"
    JAQCD = "braket.ir.jaqcd.program"
    ANNEALING = "braket.ir.annealing.problem"


class DeviceActionProperties(BaseModel):
    """
    This class defines the actions that can be performed by a device

    Attributes:
        version (List[str]): List of versions for the actions the device supports
        actionType (Union[DeviceActionType, str]): Enum for the action type.
             Type of the action to be performed.

    Examples:
        >>> import json
        >>> input_json = {
        ...     "actionType": "braket.ir.jaqcd.program",
        ...     "version": ["1"],
        ... }
        >>> DeviceActionProperties.parse_raw(json.dumps(input_json))
    """

    version: List[str]
    actionType: Union[DeviceActionType, str]
