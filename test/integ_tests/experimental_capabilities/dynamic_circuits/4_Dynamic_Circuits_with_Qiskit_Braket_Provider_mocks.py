def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": mock_utils.read_file(
                "garnet_device_capabilities_without_programset.json",
                __file__,
            ),
        },
    )
    files = [
        "results/results_4_0.json",
        "results/results_4_1.json",
        "results/results_4_2.json",
        "results/results_4_3.json",
        "results/results_4_4.json",
    ]
    mocker.set_task_result_side_effect(
        [mock_utils.read_file(file, __file__) for file in files]
    )


def post_run(tb):
    pass
