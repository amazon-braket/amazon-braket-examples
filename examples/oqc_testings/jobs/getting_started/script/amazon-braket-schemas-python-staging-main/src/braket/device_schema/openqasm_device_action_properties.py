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


class OpenQASMDeviceActionProperties(DeviceActionProperties):

    """
    Defines the schema for properties for the actions that can be supported by OpenQASM devices.

    Attributes:
        supportedOperations: Operations supported by the OpenQASM action.
        supportedResultTypes: Result types that are supported by the OpenQASM action.
        supportPhysicalQubits: Whether the device supports the ability to run circuits
            with the exact qubits chosen, without any rewiring downstream.
        supportedPragmas: List of pragmas supported (not ignored) in the OpenQASM action.
        forbiddenPragmas: List of pragmas that will raise an error when sent to the device.
        forbiddenArrayOperations: Forbidden operations on arrays.
        requiresAllQubitsMeasurement: Whether measurements have to be made on all qubits in the
            OpenQASM action.
        requiresContiguousQubitIndices: Whether used qubit indices of qubit arrays
            are required to be contiguous.

    Examples:
        >>> import json
        >>> input_json = {
        ...    "actionType": "braket.ir.openqasm.program",
        ...    "version": ["1"],
        ...    "supportedOperations": ["x", "y"],
        ...    "supportedResultTypes": [{
        ...         "name": "resultType1",
        ...         "observables": ["observable1"],
        ...         "minShots": 0,
        ...         "maxShots": 4,
        ...     }],
        ...    "supportPhysicalQubits": True
        ...    "supportedPragmas": ["braket_bit_flip_noise"],
        ...    "forbiddenPragmas": ["braket_kraus_operator"],
        ...    "forbiddenArrayOperations": ["concatenation", "range", "slicing"],
        ...    "requiresAllQubitsMeasurement": False
        ...    "requiresContiguousQubitIndices": False
        ... }
        >>> OpenQASMDeviceActionProperties.parse_raw(json.dumps(input_json))

    """

    actionType: constr(regex=r"^braket\.ir\.openqasm\.program$")
    supportedOperations: List[str]
    supportedPragmas: Optional[List[str]] = []
    forbiddenPragmas: Optional[List[str]] = []
    maximumQubitArrays: Optional[int] = None  # None indicates no limit
    maximumClassicalArrays: Optional[int] = None  # None indicates no limit
    forbiddenArrayOperations: Optional[List[str]] = []
    requiresAllQubitsMeasurement: Optional[bool] = False
    supportPhysicalQubits: Optional[bool] = False
    requiresContiguousQubitIndices: Optional[bool] = False
    disabledQubitRewiringSupported: Optional[bool] = False
    supportedResultTypes: Optional[List[ResultType]]
