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

import json
from unittest.mock import Mock

from braket.aws import AwsQuantumTaskBatch

DWAVE_ARN = "arn:aws:braket:::device/qpu/d-wave/Advantage_system1"
RIGETTI_ARN = "arn:aws:braket:::device/qpu/rigetti/Aspen-10"
IONQ_ARN = "arn:aws:braket:::device/qpu/ionq/ionQdevice"
SV1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
TN1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"

RIGETTI_REGION = "us-west-1"


class MockS3:
    MOCK_TASK_METADATA = {
        "braketSchemaHeader": {"name": "braket.task_result.task_metadata", "version": "1"},
        "id": "task_arn",
        "shots": 100,
        "deviceId": "default",
    }

    MOCK_S3_RESULT_GATE_MODEL = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.gate_model_task_result",
                "version": "1",
            },
            "measurements": [[0, 0], [0, 0], [0, 0], [1, 1]],
            "measuredQubits": [0, 1],
            "taskMetadata": MOCK_TASK_METADATA,
            "additionalMetadata": {
                "action": {
                    "braketSchemaHeader": {"name": "braket.ir.jaqcd.program", "version": "1"},
                    "instructions": [{"control": 0, "target": 1, "type": "cnot"}],
                },
            },
        }
    )

    MOCK_S3_RESULT_GATE_MODEL_WITH_RESULT_TYPES = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.gate_model_task_result",
                "version": "1",
            },
            "measurements": [[0, 0], [0, 0], [0, 0], [1, 1]],
            "measuredQubits": [0, 1],
            "resultTypes": [
                {
                    "type": {"observable": ["h", "x"], "targets": [0, 1], "type": "expectation"},
                    "value": 0.7071067811865474,
                },
                {
                    "type": {"states": ["01", "10", "00", "11"], "type": "amplitude"},
                    "value": {
                        "01": [0.0, 0.0],
                        "10": [0.0, 0.0],
                        "00": [0.7071067811865475, 0.0],
                        "11": [0.7071067811865475, 0.0],
                    },
                },
            ],
            "taskMetadata": MOCK_TASK_METADATA,
            "additionalMetadata": {
                "action": {
                    "braketSchemaHeader": {"name": "braket.ir.jaqcd.program", "version": "1"},
                    "instructions": [{"control": 0, "target": 1, "type": "cnot"}],
                },
            },
        }
    )

    MOCK_S3_RESULT_ANNEALING = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.annealing_task_result",
                "version": "1",
            },
            "solutions": [[-1, -1, -1, -1], [1, -1, 1, 1], [1, -1, -1, 1]],
            "solutionCounts": [3, 2, 4],
            "values": [0.0, 1.0, 2.0],
            "variableCount": 4,
            "taskMetadata": {
                "id": "task_arn",
                "shots": 100,
                "deviceId": DWAVE_ARN,
            },
            "additionalMetadata": {
                "action": {
                    "type": "ISING",
                    "linear": {"0": 0.3333, "1": -0.333, "4": -0.333, "5": 0.333},
                    "quadratic": {"0,4": 0.667, "0,5": -1.0, "1,4": 0.667, "1,5": 0.667},
                },
                "dwaveMetadata": {
                    "activeVariables": [0],
                    "timing": {
                        "qpuSamplingTime": 100,
                        "qpuAnnealTimePerSample": 20,
                        "qpuAccessTime": 10917,
                        "qpuAccessOverheadTime": 3382,
                        "qpuReadoutTimePerSample": 274,
                        "qpuProgrammingTime": 9342,
                        "qpuDelayTimePerSample": 21,
                        "postProcessingOverheadTime": 117,
                        "totalPostProcessingTime": 117,
                        "totalRealTime": 10917,
                        "runTimeChip": 1575,
                        "annealTimePerRun": 20,
                        "readoutTimePerRun": 274,
                    },
                },
            },
        }
    )


def run_and_assert(
    aws_quantum_task_mock,
    device,
    default_s3_folder,
    default_shots,
    default_poll_timeout,
    default_poll_interval,
    circuit,
    s3_destination_folder,  # Treated as positional arg
    shots,  # Treated as positional arg
    poll_timeout_seconds,  # Treated as positional arg
    poll_interval_seconds,  # Treated as positional arg
    extra_args,
    extra_kwargs,
):
    task_mock = Mock()
    aws_quantum_task_mock.return_value = task_mock

    run_args = []
    if s3_destination_folder is not None:
        run_args.append(s3_destination_folder)
    if shots is not None:
        run_args.append(shots)
    if poll_timeout_seconds is not None:
        run_args.append(poll_timeout_seconds)
    if poll_interval_seconds is not None:
        run_args.append(poll_interval_seconds)
    run_args += extra_args if extra_args else []
    run_kwargs = extra_kwargs or {}

    task = device.run(circuit, *run_args, **run_kwargs)
    assert task == task_mock

    create_args, create_kwargs = _create_task_args_and_kwargs(
        default_s3_folder,
        default_shots,
        default_poll_timeout,
        default_poll_interval,
        s3_destination_folder,
        shots,
        poll_timeout_seconds,
        poll_interval_seconds,
        extra_args,
        extra_kwargs,
    )

    aws_quantum_task_mock.assert_called_with(
        device._aws_session, device.arn, circuit, *create_args, **create_kwargs
    )


def run_batch_and_assert(
    aws_quantum_task_mock,
    aws_session_mock,
    device,
    default_s3_folder,
    default_shots,
    default_poll_timeout,
    default_poll_interval,
    circuits,
    s3_destination_folder,
    shots,
    max_parallel,
    max_connections,
    poll_timeout_seconds,
    poll_interval_seconds,
    extra_args,
    extra_kwargs,
):
    task_mock = Mock()
    task_mock.state.return_value = "COMPLETED"
    aws_quantum_task_mock.return_value = task_mock
    new_session_mock = Mock()
    aws_session_mock.return_value = new_session_mock

    run_args = []
    if s3_destination_folder is not None:
        run_args.append(s3_destination_folder)
    if shots is not None:
        run_args.append(shots)
    if max_parallel is not None:
        run_args.append(max_parallel)
    if max_connections is not None:
        run_args.append(max_connections)
    if poll_timeout_seconds is not None:
        run_args.append(poll_timeout_seconds)
    if poll_interval_seconds is not None:
        run_args.append(poll_interval_seconds)
    run_args += extra_args if extra_args else []
    run_kwargs = extra_kwargs or {}

    batch = device.run_batch(circuits, *run_args, **run_kwargs)
    assert batch.tasks == [task_mock for _ in range(len(circuits))]

    create_args, create_kwargs = _create_task_args_and_kwargs(
        default_s3_folder,
        default_shots,
        default_poll_timeout,
        default_poll_interval,
        s3_destination_folder,
        shots,
        poll_timeout_seconds,
        poll_interval_seconds,
        extra_args,
        extra_kwargs,
    )

    max_pool_connections = max_connections or AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT

    # aws_session_mock.call_args.kwargs syntax is newer than Python 3.7
    assert aws_session_mock.call_args[1]["config"].max_pool_connections == max_pool_connections
    aws_quantum_task_mock.assert_called_with(
        new_session_mock, device.arn, circuits[0], *create_args, **create_kwargs
    )


def _create_task_args_and_kwargs(
    default_s3_folder,
    default_shots,
    default_poll_timeout,
    default_poll_interval,
    s3_folder,
    shots,
    poll_timeout_seconds,
    poll_interval_seconds,
    extra_args,
    extra_kwargs,
):
    create_args = [
        s3_folder if s3_folder is not None else default_s3_folder,
        shots if shots is not None else default_shots,
    ]
    create_args += extra_args if extra_args else []
    create_kwargs = extra_kwargs or {}
    create_kwargs.update(
        {
            "poll_timeout_seconds": poll_timeout_seconds
            if poll_timeout_seconds is not None
            else default_poll_timeout,
            "poll_interval_seconds": poll_interval_seconds
            if poll_interval_seconds is not None
            else default_poll_interval,
        }
    )
    return create_args, create_kwargs
