import tarfile
import os
import sys
import importlib.util
import time
import logging
from pathlib import Path
from unittest.mock import patch

import numpy as np
import braket.jobs.quantum_job_creation

from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

from braket.jobs.serialization import serialize_values


def function_with_retry(*args, **kwargs) -> None:
    index = kwargs.pop("index", 0)
    try:
        global saved_function
        return saved_function(*args, **kwargs)
    except (ModuleNotFoundError, AssertionError, ValueError):
        if index < 3:
            time.sleep(0.5)
            kwargs.update({"index": index + 1})
            function_with_retry(*args, **kwargs)
        else:
            raise ValueError(f"Entry point module was not found:")


def _validate_entry_point_extra(source_module_path: Path, entry_point: str) -> None:
    """
    Confirm that a valid entry point relative to source module is given.

    Args:
        source_module_path (Path): Path to source module.
        entry_point (str): Entry point relative to source module.
    """
    importable, _, _method = entry_point.partition(":")
    sys.path.append(str(source_module_path.parent))
    try:
        # second argument allows relative imports
        logging.basicConfig(level=logging.DEBUG)
        print("-----------------")
        print(importable)
        print(source_module_path)
        print(f"Sys path: {sys.path}")
        print(f"Parent dir contents: {os.listdir(source_module_path.parent)}")
        print(f"Dir contents: {os.listdir(source_module_path)}")
        print(f"Platform: {sys.platform}")
        module = importlib.util.find_spec(importable, source_module_path.stem)
        assert module is not None
        print(f"Cached: {module.cached}")
        print("-----------------")
    # if entry point is nested (ie contains '.'), parent modules are imported
    except (ModuleNotFoundError, AssertionError) as e:
        print("=================")
        print(f"Sys path: {sys.path}")
        print(f"Parent dir contents: {os.listdir(source_module_path.parent)}")
        print(f"Dir contents: {os.listdir(source_module_path)}")
        print("=================")
        raise ValueError(f"Entry point module was not found: {importable}")
    finally:
        sys.path.pop()

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
        patch("braket.jobs.quantum_job_creation._validate_entry_point").start()

    # global saved_function
    # saved_function = braket.jobs.quantum_job_creation.prepare_quantum_job
    # braket.aws.aws_quantum_job.prepare_quantum_job = function_with_retry
    # braket.jobs.quantum_job_creation._validate_entry_point = _validate_entry_point_extra


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """
    )
