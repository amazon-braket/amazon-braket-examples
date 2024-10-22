from unittest.mock import patch


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("../pennylane_results.json", __file__))
    mocker.set_start_query_result({"queryId": "TestId"})
    mocker.set_get_query_results_result(
        {
            "status": "Complete",
            "results": [
                [
                    {"field": "@message", "value": "iteration_number=0;cost=0;"},
                    {"field": "@timestamp", "value": "0"},
                ],
            ],
        }
    )
    default_job_results = {
        "braket_tasks_cost": 0.0,
    }
    mock_utils.mock_job_results(default_job_results)
    patch("cloudpickle.dumps", return_value="serialized").start()


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """
    )
