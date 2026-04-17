def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "providerName": "Rigetti",
            "deviceCapabilities": mock_utils.read_file("rigetti_device_capabilities.json"),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        },
    )
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))
    mocker.set_search_result(
        [
            {
                "devices": [
                    {
                        "deviceArn": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                        "deviceName": "Cepheus-1-108Q",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "Rigetti",
                    },
                ],
            },
        ],
    )


def post_run(tb):
    pass
