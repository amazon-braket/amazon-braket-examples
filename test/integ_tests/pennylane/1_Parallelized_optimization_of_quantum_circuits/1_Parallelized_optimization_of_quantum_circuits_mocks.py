

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("1_pennylane_results.json", __file__))


def post_run(tb):
    pass