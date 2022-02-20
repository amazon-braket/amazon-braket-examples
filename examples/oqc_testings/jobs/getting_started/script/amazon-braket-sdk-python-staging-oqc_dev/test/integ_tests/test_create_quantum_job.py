# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json
import os.path
import re
import tempfile
from pathlib import Path

from braket.aws.aws_quantum_job import AwsQuantumJob


def test_failed_quantum_job(aws_session, capsys):
    """Asserts the job is failed with the output, checkpoints,
    tasks not created in bucket and only input is uploaded to s3. Validate the
    results/download results have the response raising RuntimeError. Also,
    check if the logs displays the Assertion Error.
    """

    job = AwsQuantumJob.create(
        "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
        source_module="test/integ_tests/job_test_script.py",
        entry_point="job_test_script:start_here",
        aws_session=aws_session,
        wait_until_complete=True,
        hyperparameters={"test_case": "failed"},
    )

    job_name = job.name
    pattern = f"^arn:aws:braket:{aws_session.region}:\\d12:job/{job_name}$"
    re.match(pattern=pattern, string=job.arn)

    # Check job is in failed state.
    assert job.state() == "FAILED"

    # Check whether the respective folder with files are created for script,
    # output, tasks and checkpoints.
    keys = aws_session.list_keys(
        bucket=f"amazon-braket-{aws_session.region}-{aws_session.account_id}",
        prefix=f"jobs/{job_name}",
    )
    assert keys == [f"jobs/{job_name}/script/source.tar.gz"]

    # no results saved
    assert job.result() == {}

    job.logs()
    log_data, errors = capsys.readouterr()
    assert errors == ""
    logs_to_validate = [
        "Invoking script with the following command:",
        "/usr/local/bin/python3.7 braket_container.py",
        "Running Code As Process",
        "Test job started!!!!!",
        "AssertionError",
        "Code Run Finished",
        '"user_entry_point": "braket_container.py"',
    ]

    for data in logs_to_validate:
        assert data in log_data

    assert job.metadata()["failureReason"] == (
        "AlgorithmError: Job at job_test_script:start_here exited with exit code: 1"
    )


def test_completed_quantum_job(aws_session, capsys):
    """Asserts the job is completed with the output, checkpoints, tasks and
    script folder created in S3 for respective job. Validate the results are
    downloaded and results are what we expect. Also, assert that logs contains all the
    necessary steps for setup and running the job and is displayed to the user.
    """

    job = AwsQuantumJob.create(
        "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
        source_module="test/integ_tests/job_test_script.py",
        entry_point="job_test_script:start_here",
        wait_until_complete=True,
        aws_session=aws_session,
        hyperparameters={"test_case": "completed"},
    )

    job_name = job.name
    pattern = f"^arn:aws:braket:{aws_session.region}:\\d12:job/{job_name}$"
    re.match(pattern=pattern, string=job.arn)

    # check job is in completed state.
    assert job.state() == "COMPLETED"

    # Check whether the respective folder with files are created for script,
    # output, tasks and checkpoints.
    s3_bucket = f"amazon-braket-{aws_session.region}-{aws_session.account_id}"
    keys = aws_session.list_keys(
        bucket=s3_bucket,
        prefix=f"jobs/{job_name}",
    )
    for expected_key in [
        f"jobs/{job_name}/script/source.tar.gz",
        f"jobs/{job_name}/data/output/model.tar.gz",
        f"jobs/{job_name}/tasks/[^/]*/results.json",
        f"jobs/{job_name}/checkpoints/{job_name}_plain_data.json",
        f"jobs/{job_name}/checkpoints/{job_name}.json",
    ]:
        assert any(re.match(expected_key, key) for key in keys)

    # Check if checkpoint is uploaded in requested format.
    for s3_key, expected_data in [
        (
            f"jobs/{job_name}/checkpoints/{job_name}_plain_data.json",
            {
                "braketSchemaHeader": {
                    "name": "braket.jobs_data.persisted_job_data",
                    "version": "1",
                },
                "dataDictionary": {"some_data": "abc"},
                "dataFormat": "plaintext",
            },
        ),
        (
            f"jobs/{job_name}/checkpoints/{job_name}.json",
            {
                "braketSchemaHeader": {
                    "name": "braket.jobs_data.persisted_job_data",
                    "version": "1",
                },
                "dataDictionary": {"some_data": "gASVBwAAAAAAAACMA2FiY5Qu\n"},
                "dataFormat": "pickled_v4",
            },
        ),
    ]:
        assert (
            json.loads(
                aws_session.retrieve_s3_object_body(s3_bucket=s3_bucket, s3_object_key=s3_key)
            )
            == expected_data
        )

    # Check downloaded results exists in the file system after the call.
    downloaded_result = f"{job_name}/{AwsQuantumJob.RESULTS_FILENAME}"
    current_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        job.download_result()
        assert (
            Path(AwsQuantumJob.RESULTS_TAR_FILENAME).exists() and Path(downloaded_result).exists()
        )

        # Check results match the expectations.
        assert job.result() == {"converged": True, "energy": -0.2}
        os.chdir(current_dir)

    # Check the logs and validate it contains required output.
    job.logs(wait=True)
    log_data, errors = capsys.readouterr()
    assert errors == ""
    logs_to_validate = [
        "Invoking script with the following command:",
        "/usr/local/bin/python3.7 braket_container.py",
        "Running Code As Process",
        "Test job started!!!!!",
        "Test job completed!!!!!",
        "Code Run Finished",
        '"user_entry_point": "braket_container.py"',
        "Reporting training SUCCESS",
    ]

    for data in logs_to_validate:
        assert data in log_data
