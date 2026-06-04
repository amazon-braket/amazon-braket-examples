from qiskit import user_config


def pre_run_inject(mock_utils):
    qiskit_config = user_config.get_config()
    if qiskit_config:
        user_config.set_config("circuit_drawer", "text")

    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceName": "Aria 1",
            "deviceStatus": "ONLINE",
            "providerName": "IonQ",
            "deviceCapabilities": mock_utils.read_file(
                "ionq_forte_enterprise_device_capabilities.json"
            ),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        }
    )
    mocker.set_search_result(
        [
            {
                "devices": [
                    {
                        "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
                        "deviceName": "Aria 1",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "IonQ",
                    },
                    {
                        "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-2",
                        "deviceName": "Aria 2",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "IonQ",
                    },
                    {
                        "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
                        "deviceName": "SV1",
                        "deviceType": "SIMULATOR",
                        "deviceStatus": "ONLINE",
                        "providerName": "Amazon",
                    },
                    {
                        "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
                        "deviceName": "dm1",
                        "deviceType": "SIMULATOR",
                        "deviceStatus": "ONLINE",
                        "providerName": "Amazon",
                    },
                ],
            }
        ]
    )


def post_run(tb):
    pass
