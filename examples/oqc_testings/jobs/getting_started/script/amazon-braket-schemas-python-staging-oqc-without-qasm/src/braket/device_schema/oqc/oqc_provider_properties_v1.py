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

from typing import Dict, List, TypeVar, Union

from pydantic import Field

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader

# TODO: Replace the calibration data with actual values we receive from the device.


GateFidelityType = TypeVar("GateFidelityType", bound=Dict[str, Union[str, float]])
OneQubitType = TypeVar("OneQubitType", bound=Union[float, List[GateFidelityType]])
TwoQubitType = TypeVar("TwoQubitType", bound=Dict[str, Union[float, Dict[str, int]]])

QubitType = TypeVar("QubitType", bound=Dict[str, Union[OneQubitType, TwoQubitType]])


class OqcProviderProperties(BraketSchemaBase):
    """
    This defines the properties common to all the OQC devices.

    Attributes:
        properties (Dict[str, Dict[str, Union[int, List[int]]]]): Basic specifications for
            the device, such as gate fidelities and coherence times.

    Examples:
        >>> import json
        >>> input_json = {
        ... "braketSchemaHeader": {
        ...     "name": "braket.device_schema.oqc.oqc_provider_properties",
        ...     "version": "1",
        ... },
        ... "properties": {
        ...     "one_qubit": {
        ...         "0": {
        ...             "T1": 12.2,
        ...             "T2": 13.5,
        ...             "fRO": 0.99,
        ...             "fRB": 0.98,
        ...             "native-gate-fidelities": [
        ...                 {"native-gate": "rz", "CLf": 0.99},
        ...                 {"native-gate": "sx", "CLf": 0.99},
        ...                 {"native-gate": "x", "CLf": 0.99},
        ...             ],
        ...             "EPE": 0.001,
        ...         },
        ...     },
        ...     "two_qubit": {
        ...         "0-1": {
        ...             "coupling": {"control_qubit": 0, "target_qubit": 1},
        ...             "CLf": 0.99,
        ...             "ECR_f": 0.99,
        ...         },
        ...     },
        ... },
        ... }
        >>> OqcProviderProperties.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.oqc.oqc_provider_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    properties: Dict[str, Dict[str, QubitType]]
