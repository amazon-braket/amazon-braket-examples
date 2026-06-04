from itertools import cycle

from qiskit import user_config


def pre_run_inject(mock_utils):
    qiskit_config = user_config.get_config()
    if qiskit_config:
        user_config.set_config("circuit_drawer", "text")
    mocker = mock_utils.Mocker()

    # Cycle through: Ankaa-3 (Rigetti), Garnet (IQM), Aria 1 (IonQ), Aria 1 again (for task runs)
    ankaa_caps = {
        "deviceType": "QPU",
        "deviceName": "Ankaa-3",
        "deviceStatus": "ONLINE",
        "providerName": "Rigetti",
        "deviceCapabilities": mock_utils.read_file("rigetti_device_capabilities.json"),
        "deviceQueueInfo": [
            {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
            {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
            {"queue": "JOBS_QUEUE", "queueSize": "0"},
        ],
    }
    garnet_caps = {
        "deviceType": "QPU",
        "deviceName": "Garnet",
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
    aria_caps = {
        "deviceType": "QPU",
        "deviceName": "Aria 1",
        "deviceStatus": "ONLINE",
        "providerName": "IonQ",
        "deviceCapabilities": mock_utils.read_file("ionq_forte_enterprise_device_capabilities.json"),
        "deviceQueueInfo": [
            {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
            {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
            {"queue": "JOBS_QUEUE", "queueSize": "0"},
        ],
    }

    # get_device is called for: Ankaa-3, Garnet, Aria 1, then task operations reuse Aria 1
    mocker._wrapper.boto_client.get_device.side_effect = cycle(
        [ankaa_caps, garnet_caps, aria_caps]
    )

    mocker.set_create_quantum_task_result(
        {"quantumTaskArn": "arn:aws:braket:us-east-1:000000:quantum-task/TestARN"}
    )
    mocker.set_get_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:us-east-1:000000:quantum-task/TestARN",
            "status": "COMPLETED",
            "outputS3Bucket": "Test Bucket",
            "outputS3Directory": "Test Directory",
            "shots": 10,
            "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
            "queueInfo": {
                "queue": "QUANTUM_TASKS_QUEUE",
                "position": "2",
                "queuePriority": "Normal",
            },
            "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
        }
    )
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))
    mocker.set_search_result(
        [
            {
                "devices": [
                    {
                        "deviceArn": "arn:aws:braket:us-west-2::device/qpu/rigetti/Ankaa-3",
                        "deviceName": "Ankaa-3",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "Rigetti",
                    },
                    {
                        "deviceArn": "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
                        "deviceName": "Garnet",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "IQM",
                    },
                    {
                        "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
                        "deviceName": "Aria 1",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "IonQ",
                    },
                ]
            }
        ]
    )


def post_run(tb):
    pass
