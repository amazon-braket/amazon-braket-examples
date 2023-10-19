import tarfile
from unittest.mock import patch

from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

from braket.jobs.serialization import serialize_values


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("../pennylane_results.json", __file__))
    mocker.set_start_query_result({
        "queryId": "TestId"
    })
    mocker.set_get_query_results_result({
        "status": "Complete",
        "results": [
            [
                {"field": "@message", "value": "iteration_number=0;cost=0;"},
                {"field": "@timestamp", "value": "0"},
            ],
        ]
    })
    default_job_results = {
        'braket_tasks_cost': 0.0,
    }
    with open("results.json", "w") as f:
        serialized_data = serialize_values(default_job_results, PersistedJobDataFormat.PICKLED_V4)
        persisted_data = PersistedJobData(
            dataDictionary=serialized_data,
            dataFormat=PersistedJobDataFormat.PICKLED_V4,
        )
        f.write(persisted_data.json())
    with tarfile.open("model.tar.gz", "w:gz") as tar:
        tar.add("results.json")
    patch('cloudpickle.dumps', return_value='serialized').start()


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """
    )
