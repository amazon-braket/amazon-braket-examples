

def pre_run(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "deviceCapabilities" : mock_utils.load_json("photonics_device_capabilities.json", __file__)
    })


def post_run(tb):
    pass