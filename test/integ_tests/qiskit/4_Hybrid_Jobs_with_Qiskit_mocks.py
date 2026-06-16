import os
import subprocess
import tarfile
from unittest import mock

default_job_results = ""


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mock_utils.mock_default_job_calls(mocker)
    mocker.set_create_job_result(
        {"jobArn": f"arn:aws:braket:{mocker.region_name}:000000:job/testJob"},
    )
    mocker.set_log_streams_result({"logStreams": []})
    mocker.set_get_query_results_result(
        {
            "status": "Complete",
            "results": [
                [
                    {"field": "@message", "value": "iteration_number=0;expval=-1.0;"},
                    {"field": "@timestamp", "value": "0"},
                ],
            ],
        },
    )
    mocker.set_start_query_result({"queryId": "TestId"})

    global default_job_results
    default_job_results = mock_utils.read_file("vqe_job_results.json", __file__)
    with open("results.json", "w") as f:
        f.write(default_job_results)
    with tarfile.open("model.tar.gz", "w:gz") as tar:
        tar.add("results.json")
    subprocess.check_output = subprocess_check_output

    os.environ["AMZN_BRAKET_DEVICE_ARN"] = (
        f"arn:aws:braket:{mocker.region_name}::device/quantum-simulator/amazon/sv1"
    )


def post_run(tb):
    tb.inject(
        """
        import os
        if os.path.exists("model.tar.gz"):
            os.remove("model.tar.gz")
        if os.path.exists("results.json"):
            os.remove("results.json")
        """,
    )


def subprocess_check_output(*args, **kwargs):
    cmd = args[0]
    if cmd[0] == "docker" and cmd[1] == "cp" and len(cmd) > 3 and cmd[3].startswith("braket-job"):
        local_job_name = cmd[3]
        os.makedirs(local_job_name, exist_ok=True)
        with open(os.path.join(local_job_name, "results.json"), "w") as f:
            f.write(default_job_results)
    return mock.Mock()
