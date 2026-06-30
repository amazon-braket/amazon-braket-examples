def pre_run_inject(mock_utils):
    mock_utils.prefer_text_circuit_drawer()

    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "SIMULATOR",
            "deviceName": "SV1",
            "deviceStatus": "ONLINE",
            "providerName": "Amazon",
            "deviceCapabilities": mock_utils.read_file("rigetti_device_capabilities.json"),
        },
    )
    mocker.set_search_result(
        [
            {
                "devices": [
                    {
                        "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                        "deviceName": "SV1",
                        "deviceType": "SIMULATOR",
                        "deviceStatus": "ONLINE",
                        "providerName": "Test Provider",
                    },
                    {
                        "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                        "deviceName": "dm1",
                        "deviceType": "SIMULATOR",
                        "deviceStatus": "ONLINE",
                        "providerName": "Test Provider",
                    },
                    {
                        "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                        "deviceName": "Cepheus-1-108Q",
                        "deviceType": "QPU",
                        "deviceStatus": "ONLINE",
                        "providerName": "Test Provider",
                    },
                ],
            },
        ],
    )


def post_run(tb):
    pass
