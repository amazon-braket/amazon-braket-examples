def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
        },
    )
    effects = [
            mock_utils.read_file(f"results/results_1_{i}.json", __file__)
            for i in range(7)]
    mocker.set_task_result_side_effect(effects)


def post_run(tb):
    pass
