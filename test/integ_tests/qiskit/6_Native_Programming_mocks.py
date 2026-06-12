from itertools import cycle


def pre_run_inject(mock_utils):
    mock_utils.prefer_text_circuit_drawer()
    mocker = mock_utils.Mocker()

    # Cycle through: Ankaa-3 (Rigetti), Garnet (IQM), Aria 1 (IonQ), Aria 1 again (for task runs)
    ankaa_caps = {
        "deviceType": "QPU",
        "deviceName": "Ankaa-3",
        "deviceStatus": "ONLINE",
        "providerName": "Rigetti",
        "deviceCapabilities": mock_utils.read_file("rigetti_device_capabilities.json"),
        "deviceQueueInfo": mock_utils.EMPTY_QUEUE_INFO,
    }
    garnet_caps = {
        "deviceType": "QPU",
        "deviceName": "Garnet",
        "deviceStatus": "ONLINE",
        "providerName": "IQM",
        "deviceCapabilities": mock_utils.read_file(
            "garnet_device_capabilities_without_programset.json", __file__
        ),
        "deviceQueueInfo": mock_utils.EMPTY_QUEUE_INFO,
    }
    aria_caps = {
        "deviceType": "QPU",
        "deviceName": "Aria 1",
        "deviceStatus": "ONLINE",
        "providerName": "IonQ",
        "deviceCapabilities": mock_utils.read_file("ionq_forte_enterprise_device_capabilities.json"),
        "deviceQueueInfo": mock_utils.EMPTY_QUEUE_INFO,
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
                    mock_utils.device_summary(
                        "arn:aws:braket:us-west-2::device/qpu/rigetti/Ankaa-3",
                        "Ankaa-3",
                        "QPU",
                        "Rigetti",
                    ),
                    mock_utils.device_summary(
                        "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
                        "Garnet",
                        "QPU",
                        "IQM",
                    ),
                    mock_utils.device_summary(
                        "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
                        "Aria 1",
                        "QPU",
                        "IonQ",
                    ),
                ]
            }
        ]
    )


def post_run(tb):
    pass
