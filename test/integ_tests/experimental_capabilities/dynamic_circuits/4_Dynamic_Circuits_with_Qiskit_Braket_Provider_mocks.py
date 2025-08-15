import json


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    capabilities = json.loads(
        mocker._wrapper.boto_client.get_device.return_value["deviceCapabilities"]
    )
    capabilities["action"]["braket.ir.openqasm.program"]["supportedOperations"].remove("kraus")
    mocker._wrapper.boto_client.get_device.return_value["deviceCapabilities"] = json.dumps(
        capabilities
    )


def post_run(tb):
    pass
