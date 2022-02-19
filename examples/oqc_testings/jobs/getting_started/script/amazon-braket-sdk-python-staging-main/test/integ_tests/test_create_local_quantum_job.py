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
import os
import re
import tempfile
from pathlib import Path

import pytest

from braket.jobs.local import LocalQuantumJob


def test_completed_local_job(aws_session, capsys):
    """Asserts the job is completed with the respective files and folders for logs,
    results and checkpoints. Validate the results are what we expect. Also,
    assert that logs contains all the necessary steps for setup and running
    the job is displayed to the user.
    """
    absolute_source_module = str(Path("test/integ_tests/job_test_script.py").resolve())
    current_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        job = LocalQuantumJob.create(
            "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            source_module=absolute_source_module,
            entry_point="job_test_script:start_here",
            hyperparameters={"test_case": "completed"},
            aws_session=aws_session,
        )

        job_name = job.name
        pattern = f"^local:job/{job_name}$"
        re.match(pattern=pattern, string=job.arn)

        assert job.state() == "COMPLETED"
        assert Path(job_name).is_dir()

        # Check results match the expectations.
        assert Path(f"{job_name}/results.json").exists()
        assert job.result() == {"converged": True, "energy": -0.2}

        # Validate checkpoint files and data
        assert Path(f"{job_name}/checkpoints/{job_name}.json").exists()
        assert Path(f"{job_name}/checkpoints/{job_name}_plain_data.json").exists()

        for file_name, expected_data in [
            (
                f"{job_name}/checkpoints/{job_name}_plain_data.json",
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
                f"{job_name}/checkpoints/{job_name}.json",
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
            with open(file_name, "r") as f:
                assert json.loads(f.read()) == expected_data

        # Capture logs
        assert Path(f"{job_name}/log.txt").exists()
        job.logs()
        log_data, errors = capsys.readouterr()

        logs_to_validate = [
            "Beginning Setup",
            "Running Code As Process",
            "Test job started!!!!!",
            "Test job completed!!!!!",
            "Code Run Finished",
        ]

        for data in logs_to_validate:
            assert data in log_data

        os.chdir(current_dir)


def test_failed_local_job(aws_session, capsys):
    """Asserts the job is failed with the output, checkpoints not created in bucket
    and only logs are populated. Validate the calling result function raises
    the ValueError. Also, check if the logs displays the required error message.
    """
    absolute_source_module = str(Path("test/integ_tests/job_test_script.py").resolve())
    current_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        job = LocalQuantumJob.create(
            "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            source_module=absolute_source_module,
            entry_point="job_test_script:start_here",
            hyperparameters={"test_case": "failed"},
            aws_session=aws_session,
        )

        job_name = job.name
        pattern = f"^local:job/{job_name}$"
        re.match(pattern=pattern, string=job.arn)

        assert Path(job_name).is_dir()

        # Check no files are populated in checkpoints folder.
        assert not any(Path(f"{job_name}/checkpoints").iterdir())

        # Check results match the expectations.
        error_message = f"Unable to find results in the local job directory {job_name}."
        with pytest.raises(ValueError, match=error_message):
            job.result()

        assert Path(f"{job_name}/log.txt").exists()
        job.logs()
        log_data, errors = capsys.readouterr()

        logs_to_validate = [
            "Beginning Setup",
            "Running Code As Process",
            "Test job started!!!!!",
            "Code Run Finished",
        ]

        for data in logs_to_validate:
            assert data in log_data

        os.chdir(current_dir)
