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

import asyncio
from typing import Union

from braket.tasks import AnnealingQuantumTaskResult, GateModelQuantumTaskResult, QuantumTask


class LocalQuantumTask(QuantumTask):
    """A task containing the results of a local simulation.

    Since this class is instantiated with the results, cancel() and run_async() are unsupported.
    """

    def __init__(self, result: Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]):
        self._id = result.task_metadata.id
        self._result = result

    @property
    def id(self) -> str:
        return str(self._id)

    def cancel(self) -> None:
        raise NotImplementedError("Cannot cancel completed local task")

    def state(self) -> str:
        return "COMPLETED"

    def result(self) -> Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]:
        return self._result

    def async_result(self) -> asyncio.Task:
        # TODO: Allow for asynchronous simulation
        raise NotImplementedError("Asynchronous local simulation unsupported")

    def __repr__(self) -> str:
        return f"LocalQuantumTask('id':{self.id})"
