def pre_run_inject(mock_utils):
    mock_utils.prefer_text_circuit_drawer()

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
            "deviceQueueInfo": mock_utils.EMPTY_QUEUE_INFO,
        }
    )
    mocker.set_search_result(
        [
            {
                "devices": [
                    mock_utils.device_summary(
                        "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
                        "Aria 1",
                        "QPU",
                        "IonQ",
                    ),
                    mock_utils.device_summary(
                        "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-2",
                        "Aria 2",
                        "QPU",
                        "IonQ",
                    ),
                    mock_utils.device_summary(
                        "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
                        "SV1",
                        "SIMULATOR",
                        "Amazon",
                    ),
                    mock_utils.device_summary(
                        "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
                        "dm1",
                        "SIMULATOR",
                        "Amazon",
                    ),
                ],
            }
        ]
    )


def post_run(tb):
    pass
