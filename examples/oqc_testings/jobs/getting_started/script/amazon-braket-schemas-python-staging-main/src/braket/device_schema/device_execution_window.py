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

from datetime import time
from enum import Enum
from typing import Union

from pydantic import BaseModel


class ExecutionDay(str, Enum):
    """
    Enums for the execution days.

    Attributes:
        EVERYDAY: It tells us that the device can execute on all the days
        WEEKDAYS: It tells us that the device can execute only on the weekdays
        WEEKENDS: It tells us that the device can execute only on the weekends
        MONDAY: It tells us that the device can execute only on the monday
        TUESDAY: It tells us that the device can execute only on the tuesday
        WEDNESDAY: It tells us that the device can execute only on the wednesday
        THURSDAY: It tells us that the device can execute only on the thursday
        FRIDAY: It tells us that the device can execute only on the friday
        SATURDAY: It tells us that the device can execute only on the saturday
        SUNDAY: It tells us that the device can execute only on the sunday
    """

    EVERYDAY = "Everyday"
    WEEKDAYS = "Weekdays"
    WEEKENDS = "Weekend"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class DeviceExecutionWindow(BaseModel):

    """
    This class defines when a device can execute a given task.

    Attributes:
        executionDay (Union[ExecutionDay, str]): Days of the execution window
        windowStartHour (time): UTC 24-hour format of the time when the execution window starts
        windowEndHour (time): UTC 24-hour format of the time when the execution window ends

    Examples:
        >>> import json
        >>> input_json = {
        ...    "executionDay": "Everyday",
        ...    "windowStartHour": "09:00",
        ...    "windowEndHour": "19:00",
        ... }
        >>> DeviceExecutionWindow.parse_raw(json.dumps(input_json))

    """

    executionDay: Union[ExecutionDay, str]
    windowStartHour: time
    windowEndHour: time
