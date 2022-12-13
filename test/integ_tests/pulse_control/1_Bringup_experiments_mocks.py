

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "deviceCapabilities" : mock_utils.read_file("rig_pulse_device_capabilities.json", __file__)
    })
    res1 = mock_utils.read_file("1_1_pulse_results.json", __file__)
    res2 = mock_utils.read_file("1_2_pulse_results.json", __file__)
    res3 = mock_utils.read_file("1_3_pulse_results.json", __file__)
    effects = []
    for i in range(60):
        effects.append(res1)
        effects.append(res2)
        effects.append(res3)
    mocker.set_task_result_side_effect(effects)


def post_run(tb):
    pass