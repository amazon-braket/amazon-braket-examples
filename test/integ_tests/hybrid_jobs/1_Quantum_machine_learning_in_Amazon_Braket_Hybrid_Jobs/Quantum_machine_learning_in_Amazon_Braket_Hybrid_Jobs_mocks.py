import tarfile
import sys
import importlib.util
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import braket.jobs.quantum_job_creation

from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

from braket.jobs.serialization import serialize_values


def validate_entry_point_with_retry(source_module_path: Path, entry_point: str, index = 0) -> None:
    try:
        global saved_function
        saved_function(source_module_path, entry_point)
    except (ModuleNotFoundError, AssertionError, ValueError):
        if index < 3:
            time.sleep(0.5)
            validate_entry_point_with_retry(source_module_path, entry_point, index + 1)
        else:
            raise ValueError(f"Entry point module was not found:")


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
    global saved_function
    saved_function = braket.jobs.quantum_job_creation._validate_entry_point
    braket.jobs.quantum_job_creation._validate_entry_point = validate_entry_point_with_retry


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """
    )
