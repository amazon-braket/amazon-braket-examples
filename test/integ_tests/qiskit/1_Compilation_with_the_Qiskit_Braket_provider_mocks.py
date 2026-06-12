def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceType": "QPU",
        "deviceName": "Garnet",
        "deviceStatus": "ONLINE",
        "providerName": "IQM",
        "deviceCapabilities": mock_utils.read_file(
            "garnet_device_capabilities_without_programset.json", __file__
        ),
    })
    mocker.set_task_result_return(mock_utils.read_file("result_compiled.json", __file__))
    mock_utils.patch_braket_qubit_labels()


def post_run(tb):
    pass
