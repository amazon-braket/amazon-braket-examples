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

import uuid

import numpy as np
import pytest

from braket.task_result import TaskMetadata
from braket.tasks import GateModelQuantumTaskResult
from braket.tasks.local_quantum_task import LocalQuantumTask

RESULT = GateModelQuantumTaskResult(
    task_metadata=TaskMetadata(**{"id": str(uuid.uuid4()), "deviceId": "default", "shots": 100}),
    additional_metadata=None,
    measurements=np.array([[0, 1], [1, 0]]),
    measured_qubits=[0, 1],
    result_types=None,
    values=None,
)

TASK = LocalQuantumTask(RESULT)


def test_id():
    # Task ID is valid UUID
    uuid.UUID(TASK.id)


def test_state():
    assert TASK.state() == "COMPLETED"


def test_result():
    assert RESULT.task_metadata.id == TASK.id
    assert TASK.result() == RESULT


@pytest.mark.xfail(raises=NotImplementedError)
def test_cancel():
    TASK.cancel()


@pytest.mark.xfail(raises=NotImplementedError)
def test_async():
    TASK.async_result()


def test_str():
    expected = "LocalQuantumTask('id':{})".format(TASK.id)
    assert str(TASK) == expected
