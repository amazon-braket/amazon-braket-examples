import os

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_utils.mock_program_set_calls(
        mocker, base_path=os.path.join(current_dir, "results", "result_4")
    )
    
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": mock_utils.read_file(
                "garnet_device_capabilities_with_programset.json",
                __file__,
            ),
        },
    )


def post_run(tb):
    pass
