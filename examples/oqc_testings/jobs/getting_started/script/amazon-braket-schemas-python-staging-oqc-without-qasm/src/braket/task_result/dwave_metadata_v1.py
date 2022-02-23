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
# language governing permissions and limitations under the License

from typing import Optional

from pydantic import BaseModel, Field, conint, conlist

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class DwaveTiming(BaseModel):
    """
    The D-Wave timing metadata result schema.

    The times represented are in microseconds.

    Examples:
        >>> DwaveTiming(qpuSamplingTime=1575, qpuAnnealTimePerSample=20)
    """

    qpuSamplingTime: Optional[conint(ge=0)]
    qpuAnnealTimePerSample: Optional[conint(ge=0)]
    qpuAccessTime: Optional[conint(ge=0)]
    qpuAccessOverheadTime: Optional[conint(ge=0)]
    qpuReadoutTimePerSample: Optional[conint(ge=0)]
    qpuProgrammingTime: Optional[conint(ge=0)]
    qpuDelayTimePerSample: Optional[conint(ge=0)]
    postProcessingOverheadTime: Optional[conint(ge=0)]
    totalPostProcessingTime: Optional[conint(ge=0)]
    totalRealTime: Optional[conint(ge=0)]
    runTimeChip: Optional[conint(ge=0)]
    annealTimePerRun: Optional[conint(ge=0)]
    readoutTimePerRun: Optional[conint(ge=0)]


class DwaveMetadata(BraketSchemaBase):
    """
    The D-Wave metadata result schema.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        activeVariables (List[int]): The active variables of the task on D-Wave
        timing (DwaveTiming): Additional timing metadata of the task on D-Wave

    Examples:
        >>> timing = DwaveTiming(qpuSamplingTime=1575, qpuAnnealTimePerSample=20)
        >>> DwaveMetadata(activeVariables=[0, 3, 4], timing=timing)
    """

    _DWAVE_METADATA_HEADER = BraketSchemaHeader(
        name="braket.task_result.dwave_metadata", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_DWAVE_METADATA_HEADER, const=_DWAVE_METADATA_HEADER
    )
    activeVariables: conlist(conint(ge=0))
    timing: DwaveTiming
