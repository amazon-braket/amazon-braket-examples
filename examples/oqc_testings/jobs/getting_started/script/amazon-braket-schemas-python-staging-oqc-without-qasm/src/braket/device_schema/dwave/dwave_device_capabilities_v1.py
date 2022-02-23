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

from braket.device_schema.device_capabilities import DeviceCapabilities
from braket.device_schema.dwave.dwave_provider_properties_v1 import DwaveProviderProperties
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class DwaveDeviceCapabilities(DeviceCapabilities, BraketSchemaBase):

    """
    These are the capabilities specific to D-Wave device

    Attributes:
        provider: Properties specific to D-Wave provider

    Examples:
        >>> import json
        >>> input_json = ...{
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.dwave.dwave_device_capabilities",
        ...        "version": "1",
        ...    },
        ...    "provider": {
        ...        "braketSchemaHeader": {
        ...            "name": "braket.device_schema.dwave.dwave_provider_properties",
        ...            "version": "1",
        ...        },
        ...        "annealingOffsetStep": 1.45,
        ...        "annealingOffsetStepPhi0": 1.45,
        ...        "annealingOffsetRanges": [[1.45, 1.45], [1.45, 1.45]],
        ...        "annealingDurationRange": [1.45, 2.45, 3],
        ...        "couplers": [[1, 2, 3], [1, 2, 3]],
        ...        "defaultAnnealingDuration": 1,
        ...        "defaultProgrammingThermalizationDuration": 1,
        ...        "defaultReadoutThermalizationDuration": 1,
        ...        "extendedJRange": [1, 2, 3],
        ...        "hGainScheduleRange": [1, 2, 3],
        ...        "hRange": [1, 2, 3],
        ...        "jRange": [1, 2, 3],
        ...        "maximumAnnealingSchedulePoints": 1,
        ...        "maximumHGainSchedulePoints": 1,
        ...        "perQubitCouplingRange": [1, 2, 3],
        ...        "programmingThermalizationDurationRange": [1, 2, 3],
        ...        "qubits": [1, 2, 3],
        ...        "qubitCount": 1,
        ...        "quotaConversionRate": 1,
        ...        "readoutThermalizationDurationRange": [1, 2, 3],
        ...        "taskRunDurationRange": [1, 2, 3],
        ...        "topology": {},
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
        ...        "braket.ir.annealing.problem": {
        ...            "actionType": "braket.ir.annealing.problem",
        ...            "version": ["1"],
        ...        }
        ...    },
        ...    "deviceParameters": {DwaveDeviceParameters.schema_json()},
        ... }
        >>> DwaveDeviceCapabilities.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.dwave.dwave_device_capabilities", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    provider: DwaveProviderProperties
