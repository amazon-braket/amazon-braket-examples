def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "providerName": "Rigetti",
            "deviceCapabilities": mock_utils.read_file("ankaa3_device_capabilities.json"),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        },
    )
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))

    boto_client = mocker._wrapper.boto_client
    boto_client.search_spending_limits.return_value = {"spendingLimits": []}
    boto_client.create_spending_limit.return_value = {
        "spendingLimitArn": "arn:aws:braket:us-west-1:000000:spending-limit/TestARN",
    }
    boto_client.update_spending_limit.return_value = {}
    boto_client.delete_spending_limit.return_value = {}


def post_run(tb):
    pass
