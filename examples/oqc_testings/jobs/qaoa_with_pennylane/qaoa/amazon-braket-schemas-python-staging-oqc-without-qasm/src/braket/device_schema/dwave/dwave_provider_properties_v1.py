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

from typing import List

from pydantic import Field

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class DwaveProviderProperties(BraketSchemaBase):

    """

    This defines the properties specific to D-Wave device

    Attributes:
        qubits: the list of the qubits available in D-Wave
        qubitCount: number of qubits available in D-Wave
        topology: the connections between each qubits

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.dwave.dwave_provider_properties",
        ...        "version": "1",
        ...    },
        ...    "annealingOffsetStep": 1.45,
        ...    "annealingOffsetStepPhi0": 1.45,
        ...    "annealingOffsetRanges": [[1.45, 1.45], [1.45, 1.45]],
        ...    "annealingDurationRange": [1.45, 2.45, 3],
        ...    "couplers": [[1, 2, 3], [1, 2, 3]],
        ...    "defaultAnnealingDuration": 1,
        ...    "defaultProgrammingThermalizationDuration": 1,
        ...    "defaultReadoutThermalizationDuration": 1,
        ...    "extendedJRange": [1.1, 2.45, 3.45],
        ...    "hGainScheduleRange": [1.11, 2.56, 3.67],
        ...    "hRange": [1.4, 2.6, 3.66],
        ...    "jRange": [1.67, 2.666, 3.666],
        ...    "maximumAnnealingSchedulePoints": 1,
        ...    "maximumHGainSchedulePoints": 1,
        ...    "perQubitCouplingRange": [1.777, 2.567, 3.1201],
        ...    "programmingThermalizationDurationRange": [1, 2, 3],
        ...    "qubits": [1, 2, 3],
        ...    "qubitCount": 1,
        ...    "quotaConversionRate": 1.341234,
        ...    "readoutThermalizationDurationRange": [1, 2, 3],
        ...    "taskRunDurationRange": [1, 2, 3],
        ...    "topology": {},
        ... }
        >>> DwaveProviderProperties.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.dwave.dwave_provider_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    annealingOffsetStep: float
    annealingOffsetStepPhi0: float
    annealingOffsetRanges: List[List[float]]
    annealingDurationRange: List[float]
    couplers: List[List[int]]
    defaultAnnealingDuration: int
    defaultProgrammingThermalizationDuration: int
    defaultReadoutThermalizationDuration: int
    extendedJRange: List[float]
    hGainScheduleRange: List[float]
    hRange: List[float]
    jRange: List[float]
    maximumAnnealingSchedulePoints: int
    maximumHGainSchedulePoints: int
    perQubitCouplingRange: List[float]
    programmingThermalizationDurationRange: List[int]
    qubits: List[int]
    qubitCount: int
    quotaConversionRate: float
    readoutThermalizationDurationRange: List[int]
    taskRunDurationRange: List[int]
    topology: dict
