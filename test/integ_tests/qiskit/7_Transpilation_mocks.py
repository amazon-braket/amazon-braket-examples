from unittest.mock import patch

from qiskit_braket_provider import BraketAwsBackend


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    # IQM Emerald uses the same schema as Garnet (IQM device)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceName": "Emerald",
            "deviceStatus": "ONLINE",
            "providerName": "IQM",
            "deviceCapabilities": mock_utils.read_file(
                "garnet_device_capabilities_without_programset.json", __file__
            ),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        }
    )
    mocker.set_create_quantum_task_result(
        {"quantumTaskArn": "arn:aws:braket:eu-north-1:000000:quantum-task/TestARN"}
    )
    mocker.set_get_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:eu-north-1:000000:quantum-task/TestARN",
            "status": "COMPLETED",
            "outputS3Bucket": "Test Bucket",
            "outputS3Directory": "Test Directory",
            "shots": 1000,
            "deviceArn": "arn:aws:braket:eu-north-1::device/qpu/iqm/Emerald",
            "queueInfo": {
                "queue": "QUANTUM_TASKS_QUEUE",
                "position": "2",
                "queuePriority": "Normal",
            },
            "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
        }
    )
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))

    patch.object(
        BraketAwsBackend,
        "qubit_labels",
        property(
            lambda self: (
                tuple(sorted(self._device.topology_graph.nodes))
                if self._device.topology_graph
                else None
            )
        ),
        create=True,
    ).start()


def post_run(tb):
    pass
