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

from typing import List, Optional

from pydantic import constr

from braket.device_schema.device_action_properties import DeviceActionProperties
from braket.device_schema.result_type import ResultType


class JaqcdDeviceActionProperties(DeviceActionProperties):

    """
    Defines the schema for properties for the actions that can be supported by JAQCD devices.

    Attributes:
        supportedOperations: Operations supported by the JAQCD action.
        supportedResultTypes: Result types that are supported by the JAQCD action.
        disabledQubitRewiringSupported: Whether the device supports the ability to run
            circuits with the exact qubits chosen, without any rewiring downstream.


    Examples:
        >>> import json
        >>> input_json = {
        ...    "actionType": "braket.ir.jaqcd.program",
        ...    "version": ["1"],
        ...    "supportedOperations": ["x", "y"],
        ...    "supportedResultTypes": [{
        ...         "name": "resultType1",
        ...         "observables": ["observable1"],
        ...         "minShots": 0,
        ...         "maxShots": 4,
        ...     }],
        ...    "disabledQubitRewiringSupported": True
        ... }
        >>> JaqcdDeviceActionProperties.parse_raw(json.dumps(input_json))

    """

    actionType: constr(regex=r"^braket\.ir\.jaqcd\.program$")
    supportedOperations: List[str]
    supportedResultTypes: Optional[List[ResultType]]
    disabledQubitRewiringSupported: Optional[bool] = None
