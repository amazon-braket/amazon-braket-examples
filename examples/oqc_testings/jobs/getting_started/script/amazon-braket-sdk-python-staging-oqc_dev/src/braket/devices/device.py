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

from abc import ABC, abstractmethod
from typing import Optional, Union

from braket.annealing.problem import Problem
from braket.circuits import Circuit
from braket.tasks.quantum_task import QuantumTask


class Device(ABC):
    """An abstraction over quantum devices that includes quantum computers and simulators."""

    def __init__(self, name: str, status: str):
        """
        Args:
            name (str): Name of quantum device
            status (str): Status of quantum device
        """
        self._name = name
        self._status = status

    @abstractmethod
    def run(
        self, task_specification: Union[Circuit, Problem], shots: Optional[int], *args, **kwargs
    ) -> QuantumTask:
        """Run a quantum task specification on this quantum device. A task can be a circuit
        or an annealing problem.

        Args:
            task_specification (Union[Circuit, Problem]):  Specification of a task
                to run on device.

            shots (int): The number of times to run the task on the device. Default is `None`.

        Returns:
            QuantumTask: The QuantumTask tracking task execution on this device
        """

    @property
    def name(self) -> str:
        """Return the name of this Device.

        Returns:
            str: The name of this Device
        """
        return self._name

    @property
    def status(self) -> str:
        """Return the status of this Device.

        Returns:
            str: The status of this Device
        """
        return self._status
