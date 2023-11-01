import sys
from unittest.mock import patch

import numpy as np


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_log_streams_result({
        "logStreams": []
    })
    mocker.set_start_query_result({
        "queryId": "TestId"
    })
    mocker.set_get_query_results_result({
        "status": "Complete",
        "results": [
            [
                {"field": "@message", "value": "iteration_number=0;loss=0;"},
                {"field": "@timestamp", "value": "0"}
            ],
        ]
    })
    default_job_results = {
        'params': np.array(
            [
                0.77996265, 0.52813787, 0.61299074, -0.09124156, 0.17680213,
                -0.02222335, 0.91524364, -0.31786518, 0.64940861, 0.62663773,
                0.87611417, -0.0715285, -0.00379581, 1.04400452, 0.20672916,
                0.94888017, 0.55607485, 1.03805133, 1.08456977, -0.75108754,
                1.13637642, 0.72634854, 0.93536659, 0.17868376, 0.79434158,
                0.05315669, 0.81228023, -0.62405866, 0.10342629, -0.8736394
            ]
        ),
        'task summary': {},
        'estimated cost': 0.0,
    }
    mock_utils.mock_job_results(default_job_results)
    # not explicitly stopped as notebooks are run in new kernels
    patch('cloudpickle.dumps', return_value='serialized').start()
    if sys.platform == "linux":
        # we skip validation of this function in linux because of a bug where Ubuntu will sometimes
        # fail to load up the hybrid jobs entry point. I did a few days of investigation on this,
        # but it is only reproducible in our notebook tests, in GitHub actions, when hybrid jobs
        # use decorators in a loop. This is a work-around until we find the root cause, but
        # it doesn't seem reasonable to keep investigating this until we find easier repro steps.
        patch("braket.jobs.quantum_job_creation._validate_entry_point").start()


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        os.remove("data.npy")
        os.remove("final_params.npy")
        """
    )
