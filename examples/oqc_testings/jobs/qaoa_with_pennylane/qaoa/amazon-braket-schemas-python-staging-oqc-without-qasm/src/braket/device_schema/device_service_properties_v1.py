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

from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from braket.device_schema.device_execution_window import DeviceExecutionWindow
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class DeviceCost(BaseModel):

    """
    This class provides the details on the cost of a device.

    Attributes:
        price (float): Price of the device in terms of US dollars
        unit (str): unit for charging the price, eg: minute, hour, task [price per task]

    Examples:
        >>> import json
        >>> input_json = {
        ...     "price": 0.25,
        ...     "unit": "minute"
        ... }
        >>> DeviceCost.parse_raw(json.dumps(input_json))
    """

    price: float
    unit: str


class DeviceDocumentation(BaseModel):
    """
    This class provides the device documentations like image,
    summary of it and external documentation.

    Attributes:
        imageUrl (Optional[str]): URL for the image of the device
        summary (Optional[str]): brief description on the device
        externalDocumentationUrl (Optional[str]): external documentation URL

    Examples:
        >>> import json
        >>> input_json = {
        ...     "imageUrl": "image_url",
        ...     "summary": "Summary on the device",
        ...     "externalDocumentationUrl": "exter doc link",
        ... }
        >>> DeviceDocumentation.parse_raw(json.dumps(input_json))
    """

    imageUrl: Optional[str]
    summary: Optional[str]
    externalDocumentationUrl: Optional[str]


class DeviceServiceProperties(BraketSchemaBase):
    """
    This class defines the common service properties for each device.

    Attributes:
        executionWindows (List[DeviceExecutionWindow]): List of the execution windows,
            it tells us which days the device can execute a task.
        shotsRange (Tuple[int, int]): range of the shots for a given device.
        deviceCost (Optional[DeviceCost]): cost of the device to run the quantum circuits
        deviceDocumentation (Optional[DeviceDocumentation]): provides device specific
            details like image, summary etc.
        deviceLocation (Optional[str]): location fo the device
        updatedAt (Optional[datetime]): time when the device properties are last updated.

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.device_service_properties",
        ...        "version": "1",
        ...    },
        ...    "executionWindows": [
        ...        {
        ...            "executionDay": "Everyday",
        ...            "windowStartHour": "09:00",
        ...            "windowEndHour": "09:55",
        ...        }
        ...    ],
        ...    "shotsRange": [1,10],
        ...    "deviceCost": {
        ...        "price": 0.25,
        ...        "unit": "minute"
        ...    },
        ...    "deviceDocumentation": {
        ...        "imageUrl": "image_url",
        ...        "summary": "Summary on the device",
        ...        "externalDocumentationUrl": "exter doc link",
        ...    },
        ...    "deviceLocation": "us-east-1",
        ...    "updatedAt": "2020-06-16T19:28:02.869136"
        ... }
        >>> DeviceServiceProperties.parse_raw_schema(json.dumps(input_json))

    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.device_service_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    executionWindows: List[DeviceExecutionWindow]
    shotsRange: Tuple[int, int]
    deviceCost: Optional[DeviceCost]
    deviceDocumentation: Optional[DeviceDocumentation]
    deviceLocation: Optional[str]
    updatedAt: Optional[datetime]
