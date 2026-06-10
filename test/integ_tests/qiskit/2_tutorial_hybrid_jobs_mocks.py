from importlib.machinery import SourceFileLoader
from pathlib import Path

helpers = SourceFileLoader(
    "qiskit_tutorial_mock_helpers",
    str(Path(__file__).with_name("_tutorial_mock_helpers.py")),
).load_module()


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    helpers.configure_qiskit_devices(mock_utils, mocker)
    mock_utils.mock_default_job_calls(mocker)
    helpers.write_plaintext_job_results(
        {
            "VQE": {
                "eigenvalue": -1.0,
                "optimal_parameters": [0.1, 0.2],
                "optimal_point": [0.1, 0.2],
                "optimal_value": -1.0,
            },
        },
    )


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """,
    )
