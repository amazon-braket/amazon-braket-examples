

def pre_run_inject_2(mock_utils):
    pass

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    res1 = mock_utils.read_file("ag_results.json", __file__)
    res2 = mock_utils.read_file("ag_results_2.json", __file__)
    res3 = mock_utils.read_file("ag_results_3.json", __file__)
    effects = []
    for i in range(3):
        effects.append(res1)
    for i in range(51):
        effects.append(res2)
    for i in range(20):
        effects.append(res3)
    mocker.set_task_result_side_effect(effects)


def post_run(tb):
    pass