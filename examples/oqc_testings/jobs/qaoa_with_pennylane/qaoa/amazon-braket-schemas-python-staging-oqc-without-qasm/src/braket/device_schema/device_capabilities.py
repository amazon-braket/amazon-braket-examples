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

from typing import Dict, Union

from pydantic import BaseModel

from braket.device_schema.device_action_properties import DeviceActionProperties, DeviceActionType
from braket.device_schema.device_service_properties_v1 import DeviceServiceProperties


class DeviceCapabilities(BaseModel):
    """
    DeviceCapabilities are the properties specific to device, this schema defines what is common
    across all the devices

    Attributes:
        service (DeviceServiceProperties): properties which are common to the Braket service
        action (Dict[Union[DeviceActionType, str], DeviceActionProperties]): Map of the action
             to its properties
        deviceParameters (dict): The json schema of the deviceParameters for each device.
             For example, the deviceParameter for IonqDeviceCapabilities will be
            IonqDeviceParameters.json_schema()

    Examples:
        >>> import json
        >>> input_json = {
        ...    "service": {
        ...        "braketSchemaHeader": {
        ...            "name": "braket.device_schema.device_service_properties",
        ...            "version": "1",
        ...        },
        ...        "executionWindows": [
        ...            {
        ...                "executionDay": "Everyday",
        ...                "windowStartHour": "09:00",
        ...                "windowEndHour": "19:00",
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
        ...             "externalDocumentationUrl": "exter doc link",
        ...         },
        ...         "deviceLocation": "us-east-1",
        ...         "updatedAt": "2020-06-16T19:28:02.869136"
        ...    },
        ...    "action": {
        ...        "braket.ir.jaqcd.program": {
        ...            "actionType": "braket.ir.jaqcd.program",
        ...            "version": ["1"],
        ...        }
        ...    },
        ...    "deviceParameters": {#Schema of specific device parameter instance},
        ... }
        >>> DeviceCapabilities.parse_raw(json.dumps(input_json))
    """

    service: DeviceServiceProperties
    action: Dict[Union[DeviceActionType, str], DeviceActionProperties]
    deviceParameters: dict
