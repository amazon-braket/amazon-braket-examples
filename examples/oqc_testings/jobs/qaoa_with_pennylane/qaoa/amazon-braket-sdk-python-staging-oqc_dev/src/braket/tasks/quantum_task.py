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
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

from braket.tasks.annealing_quantum_task_result import AnnealingQuantumTaskResult
from braket.tasks.gate_model_quantum_task_result import GateModelQuantumTaskResult


class QuantumTask(ABC):
    """An abstraction over a quantum task on a quantum device."""

    @property
    @abstractmethod
    def id(self) -> str:
        """str: The task ID."""

    @abstractmethod
    def cancel(self) -> None:
        """Cancel the quantum task."""

    @abstractmethod
    def state(self) -> str:
        """str: State of the quantum task"""

    @abstractmethod
    def result(self) -> Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]:
        """
        Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]: Get the quantum task result.
        Call async_result if you want the result in an asynchronous way.
        """

    @abstractmethod
    def async_result(self) -> asyncio.Task:
        """asyncio.Task: Get the quantum task result asynchronously."""

    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        """
        Get task metadata.

        Args:
            use_cached_value (bool, optional): If True, uses the value retrieved from the previous
                request.

        Returns:
            Dict[str, Any]: The metadata regarding the task. If `use_cached_value` is True,
            then the value retrieved from the most recent request is used.
        """
