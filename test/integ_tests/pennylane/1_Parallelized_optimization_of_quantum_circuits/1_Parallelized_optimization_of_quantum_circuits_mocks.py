def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("1_pennylane_results.json", __file__))
    mocker.set_get_device_result(
        {
            "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            "deviceCapabilities": mock_utils.read_file("1_pennylane_capabilities.json", __file__),
            "deviceName": "SV1",
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queuePriority": "Normal", "queueSize": "0"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queuePriority": "Priority", "queueSize": "0"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
            "deviceStatus": "ONLINE",
            "deviceType": "SIMULATOR",
            "providerName": "Amazon Braket",
        },
    )


def post_run(tb):
    pass
