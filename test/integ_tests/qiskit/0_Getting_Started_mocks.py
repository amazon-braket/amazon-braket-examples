from qiskit import user_config


def pre_run_inject(mock_utils):
    qiskit_config = user_config.get_config()
    if qiskit_config:
        user_config.set_config("circuit_drawer", "text")

    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_search_result([
        {
            "devices": [
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "SV1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Test Provider"
                },
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "dm1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Test Provider"
                },
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "TN1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Test Provider"
                },
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "Aspen-M-3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "Test Provider"
                }
            ]
        }
    ])


def post_run(tb):
    pass