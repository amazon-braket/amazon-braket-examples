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

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, confloat, conint, conlist, constr

from braket.ir.jaqcd.program_v1 import Results
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader
from braket.task_result.additional_metadata import AdditionalMetadata
from braket.task_result.task_metadata_v1 import TaskMetadata


class ResultTypeValue(BaseModel):
    """
    Requested result type and value of gate model task result.

    Attributes:
         type (Union[Expectation, Sample, StateVector, Variance, Probability, Amplitude]): The
            requested result type
         value (Union[List, float, Dict]): The value of the requested result
    """

    type: Union[Results]
    value: Union[List, float, Dict]


class GateModelTaskResult(BraketSchemaBase):
    """
    The gate model task result schema

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        measurements (List[List[int]]: List of lists, where each list represents a shot
            and each index of the list represents a qubit. Default is `None`.
        measurementProbabilities (Dict[str, float]): A dictionary of probabilistic results.
            Key is the measurements in a big endian binary string.
            Value is the probability the measurement occurred.
            Default is `None`.
        measuredQubits (List[int]): The indices of the measured qubits.
            Indicates which qubits are in `measurements`. Default is `None`.
        resultTypes (List[ResultTypeValue]): Requested result types and their values.
            Default is `None`.
        taskMetadata (TaskMetadata): The task metadata
        additionalMetadata (AdditionalMetadata): Additional metadata of the task
    """

    _GATE_MODEL_TASK_RESULT_HEADER = BraketSchemaHeader(
        name="braket.task_result.gate_model_task_result", version="1"
    )

    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_GATE_MODEL_TASK_RESULT_HEADER, const=_GATE_MODEL_TASK_RESULT_HEADER
    )
    measurements: Optional[conlist(conlist(conint(ge=0, le=1), min_items=1), min_items=1)]
    measurementProbabilities: Optional[
        Dict[constr(regex="^[01]+$", min_length=1), confloat(ge=0, le=1)]
    ]
    resultTypes: Optional[List[ResultTypeValue]]
    measuredQubits: Optional[conlist(conint(ge=0), min_items=1)]
    taskMetadata: TaskMetadata
    additionalMetadata: AdditionalMetadata
