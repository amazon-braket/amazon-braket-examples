from unittest.mock import patch

import numpy as np


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_task_result_return(mock_utils.read_file("../pennylane_results.json", __file__))
    default_job_results = {
        "params": np.array([0.32900000000000007, 2.5835999999999997]),
        "costs": np.array(
            [
                0.974,
                0.958,
                0.932,
                0.936,
                0.894,
                0.838,
                0.794,
                0.73,
                0.7,
                0.544,
                0.426,
                0.284,
                0.156,
                0.056,
                -0.124,
                -0.24,
                -0.374,
                -0.558,
                -0.69,
                -0.748,
            ],
        ),
        "braket_tasks_cost": 0.375,
    }
    mock_utils.mock_job_results(default_job_results)
    patch("cloudpickle.dumps", return_value="serialized").start()


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """,
    )
