import os
from itertools import cycle
from unittest import mock


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_quantum_task_side_effect(
        cycle(
            [
                {
                    "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
                    "status": "QUEUED",
                    "outputS3Bucket": "Test Bucket",
                    "outputS3Directory": "Test Directory",
                    "shots": 10,
                    "deviceArn": "Test Device Arn",
                    "queueInfo": {
                        "queue": "QUANTUM_TASKS_QUEUE",
                        "position": "2",
                        "queuePriority": "Normal",
                    },
                    "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
                },
                {
                    "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
                    "status": "RUNNING",
                    "outputS3Bucket": "Test Bucket",
                    "outputS3Directory": "Test Directory",
                    "shots": 10,
                    "deviceArn": "Test Device Arn",
                    "queueInfo": {
                        "queue": "QUANTUM_TASKS_QUEUE",
                        "position": "2",
                        "queuePriority": "Normal",
                    },
                    "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
                },
                mock.DEFAULT,
            ]
        )
    )
    mocker.set_cancel_quantum_task_result(
        {
            "cancellationStatus": "CANCELLING",
        },
    )


def post_run(tb):
    log_file = tb.ref("log_file")
    os.remove(log_file)
