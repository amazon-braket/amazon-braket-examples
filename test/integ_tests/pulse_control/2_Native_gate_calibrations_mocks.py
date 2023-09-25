

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "providerName": "Rigetti",
        "deviceCapabilities" : mock_utils.read_file("rig_pulse_device_capabilities.json", __file__)
    })
    mocker.set_task_result_return(mock_utils.read_file("pulse_results.json", __file__))


def post_run(tb):
    pass