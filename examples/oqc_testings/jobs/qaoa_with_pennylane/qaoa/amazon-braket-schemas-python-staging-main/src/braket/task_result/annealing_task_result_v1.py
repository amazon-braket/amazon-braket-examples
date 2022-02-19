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

from typing import List, Optional

from pydantic import Field, conint, conlist

from braket.schema_common.schema_base import BraketSchemaBase, BraketSchemaHeader
from braket.task_result.additional_metadata import AdditionalMetadata
from braket.task_result.task_metadata_v1 import TaskMetadata


class AnnealingTaskResult(BraketSchemaBase):
    """
    The annealing task result schema.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        solutions (List[int]): Solutions of task result. Default is `None`.
        solutionCounts (List[int]): The number of times the solutions occurred.
            Default is `None`.
        values (List[float]): Output or energy of the solutions. Default is `None`.
        variableCount (int): The number of variables. Default is `None`.
        taskMetadata (TaskMetadata): The task metadata.
        additionalMetadata (AdditionalMetadata): Additional metadata of the task.

    """

    _ANNEALING_TASK_RESULT_HEADER = BraketSchemaHeader(
        name="braket.task_result.annealing_task_result", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_ANNEALING_TASK_RESULT_HEADER, const=_ANNEALING_TASK_RESULT_HEADER
    )
    solutions: Optional[List[conlist(conint(ge=-1, le=3), min_items=1)]]
    solutionCounts: Optional[List[conint(ge=0)]]
    values: Optional[List[float]]
    variableCount: Optional[conint(ge=0)]
    taskMetadata: TaskMetadata
    additionalMetadata: AdditionalMetadata
