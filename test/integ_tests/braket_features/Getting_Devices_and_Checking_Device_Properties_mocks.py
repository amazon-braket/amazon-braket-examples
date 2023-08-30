def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mocker.set_get_device_result({
        "deviceType": "QPU",
        "deviceCapabilities": mock_utils.read_file("default_capabilities.json")
    })
    mocker.set_search_result([
        {
            "devices": [
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "Test Device",
                    "deviceType": "ONLINE",
                    "deviceStatus": "AVAILABLE",
                    "providerName": "Test Provider"
                }
            ]
        }
    ])


def post_run(tb):
    pass
