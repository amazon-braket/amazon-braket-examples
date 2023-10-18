import tarfile
from unittest.mock import patch

import numpy as np
from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

from braket.jobs.serialization import serialize_values


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("../pennylane_results.json", __file__))
    mocker.set_create_job_result(
        {
            "jobArn": f"arn:aws:braket:{mocker.region_name}:000000:job/testJob"
        }
    )
    default_job_results = {
        'params': np.array([0.32900000000000007, 2.5835999999999997]),
        'costs': np.array([
            0.974, 0.958, 0.932, 0.936, 0.894, 0.838, 0.794, 0.73,
            0.7, 0.544, 0.426, 0.284, 0.156, 0.056, -0.124, -0.24,
            -0.374, -0.558, -0.69, -0.748
        ]),
        'braket_tasks_cost': 0.375,
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
