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

from typing import Dict, Optional, Union

from pydantic import Field

from braket.device_schema.device_action_properties import DeviceActionType
from braket.device_schema.device_capabilities import DeviceCapabilities
from braket.device_schema.gate_model_qpu_paradigm_properties_v1 import (
    GateModelQpuParadigmProperties,
)
from braket.device_schema.jaqcd_device_action_properties import JaqcdDeviceActionProperties
from braket.device_schema.openqasm_device_action_properties import OpenQASMDeviceActionProperties
from braket.device_schema.oqc.oqc_provider_properties_v1 import OqcProviderProperties
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader

# TODO: Update the device and topology details when we have information from the provider


class OqcDeviceCapabilities(BraketSchemaBase, DeviceCapabilities):
    """
    This defines the capabilities of an OQC device.

    Attributes:
        action(Dict[Union[DeviceActionType, str],
            Union[OpenQASMDeviceActionProperties, JaqcdDeviceActionProperties]]): Actions that an
            OQC device can support
        paradigm(GateModelQpuParadigmProperties): Paradigm properties
        provider(Optional[OqcProviderProperties]): OQC provider specific properties

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.oqc.oqc_device_capabilities",
        ...        "version": "1",
        ...    },
        ...    "service": {
        ...        "braketSchemaHeader": {
        ...            "name": "braket.device_schema.device_service_properties",
        ...            "version": "1",
        ...        },
        ...        "executionWindows": [
        ...            {
        ...                "executionDay": "Everyday",
        ...                "windowStartHour": "09:00",
        ...                "windowEndHour": "10:00",
        ...            }
        ...        ],
        ...        "shotsRange": [1, 10],
        ...        "deviceCost": {
        ...             "price": 0.25,
        ...             "unit": "minute"
        ...         },
        ...         "deviceDocumentation": {
        ...             "imageUrl": "image_url",
        ...             "summary": "Summary on the device",
        ...             "externalDocumentationUrl": "external doc link",
        ...         },
        ...         "deviceLocation": "eu-west-2",
        ...         "updatedAt": "2020-06-16T19:28:02.869136"
        ...    },
        ...    "action": {
        ...        "braket.ir.jaqcd.program": {
        ...            "actionType": "braket.ir.jaqcd.program",
        ...            "version": ["1"],
        ...            "supportedOperations": ["x", "y"],
        ...            "supportedResultTypes": [{
        ...                 "name": "resultType1",
        ...                 "observables": ["observable1"],
        ...                 "minShots": 0,
        ...                 "maxShots": 4,
        ...             }],
        ...        }
        ...    },
        ...    "paradigm": {
        ...        "braketSchemaHeader": {
        ...            "name": "braket.device_schema.gate_model_qpu_paradigm_properties",
        ...            "version": "1",
        ...        },
        ...        "qubitCount": 11,
        ...        "nativeGateSet": ["ccnot", "cy"],
        ...        "connectivity": {
        ...            "fullyConnected": False,
        ...            "connectivityGraph": {"1": ["2", "3"]},
        ...        },
        ...    },
        ...    "deviceParameters": {OqcDeviceParameters.schema_json()},
        ... }
        >>> OqcDeviceCapabilities.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.oqc.oqc_device_capabilities", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    action: Dict[
        Union[DeviceActionType, str],
        Union[OpenQASMDeviceActionProperties, JaqcdDeviceActionProperties],
    ]
    paradigm: GateModelQpuParadigmProperties
    provider: Optional[OqcProviderProperties]
