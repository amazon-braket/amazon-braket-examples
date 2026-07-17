import re
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
                    {"field": "@message", "value": "iteration_number=0;energies=0;"},
                    {"field": "@timestamp", "value": "0"},
                ],
            ],
        },
    )
    default_job_results = {"energies": -1.5, "braket_tasks_cost": 0.0}
    mock_utils.mock_job_results(default_job_results)
    patch("cloudpickle.dumps", return_value="serialized").start()


def modify_cells(cells):
    # The only meaningful compute here is the final shot-based VQE run on
    # braket.local.qubit (5000 shots + parameter-shift gradients, ~18s of ~30s);
    # the analytic lightning run is ~0s and the @hybrid_job run is mocked. The
    # integ test only checks cells execute without error, so fewer iterations and
    # shots is safe and leaves the published notebook untouched.
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell["source"]
        src = re.sub(r"iterations = 7\b", "iterations = 3", src)
        src = re.sub(r"shots=5000\b", "shots=500", src)
        cell["source"] = src


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """,
    )
