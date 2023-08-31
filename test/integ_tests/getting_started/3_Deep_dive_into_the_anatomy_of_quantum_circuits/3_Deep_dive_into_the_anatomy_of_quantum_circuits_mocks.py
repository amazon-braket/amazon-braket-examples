import os


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_cancel_quantum_task_result({
        "cancellationStatus": "CANCELLING",
    })


def post_run(tb):
    log_file = tb.ref("log_file")
    os.remove(log_file)
