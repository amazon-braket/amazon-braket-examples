from itertools import cycle


def pre_run_inject(mock_utils):
    mock_utils.prefer_text_circuit_drawer()
    mocker = mock_utils.Mocker()

    # Cycle through: Cepheus-1-108Q (Rigetti), Garnet (IQM), Forte Enterprise 1 (IonQ), Forte Enterprise 1 again (for task runs)
    cepheus_caps = {
        "deviceType": "QPU",
        "deviceName": "Cepheus-1-108Q",
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
        "deviceName": "Forte Enterprise 1",
        "deviceStatus": "ONLINE",
        "providerName": "IonQ",
        "deviceCapabilities": mock_utils.read_file(
            "ionq_forte_enterprise_device_capabilities.json"
        ),
        "deviceQueueInfo": mock_utils.EMPTY_QUEUE_INFO,
    }

    # get_device is called for: Cepheus-1-108Q, Garnet, Forte Enterprise 1, then task operations reuse Forte Enterprise 1
    mocker._wrapper.boto_client.get_device.side_effect = cycle(
        [cepheus_caps, garnet_caps, aria_caps]
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
            "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-Enterprise-1",
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
                        "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                        "Cepheus-1-108Q",
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
                        "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-Enterprise-1",
                        "Forte Enterprise 1",
                        "QPU",
                        "IonQ",
                    ),
                ]
            }
        ]
    )


def post_run(tb):
    pass
