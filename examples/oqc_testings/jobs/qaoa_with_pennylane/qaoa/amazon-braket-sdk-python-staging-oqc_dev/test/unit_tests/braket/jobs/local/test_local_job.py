# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from unittest.mock import Mock, mock_open, patch

import pytest

from braket.jobs.local.local_job import LocalQuantumJob


@pytest.fixture
def aws_session():
    _aws_session = Mock()
    return _aws_session


@pytest.fixture
def job_results():
    return {"dataFormat": "plaintext", "dataDictionary": {"some_results": {"excellent": "here"}}}


@pytest.fixture
def run_log():
    test_log = (
        "This is a multi-line log.\n"
        "This is the next line.\n"
        "Metrics - timestamp=1633027264.5406773; Cost=-4.034; iteration_number=0;\n"
        "Metrics - timestamp=1633027288.6284382; Cost=-3.957; iteration_number=1;\n"
    )
    return test_log


@pytest.fixture
def test_envs():
    return {"Test": "Env"}


@pytest.mark.parametrize(
    "creation_kwargs",
    [
        (
            {
                "jobName": "Test-Job-Name",
                "algorithmSpecification": {"containerImage": {"uri": "file://test-URI"}},
                "checkpointConfig": {"localPath": "test/local/path/"},
            }
        ),
        (
            {
                "jobName": "Test-Job-Name",
                "algorithmSpecification": {"containerImage": {"uri": "file://test-URI"}},
                "checkpointConfig": {},
            }
        ),
        (
            {
                "jobName": "Test-Job-Name",
                "algorithmSpecification": {"containerImage": {"uri": "file://test-URI"}},
            }
        ),
        (
            {
                "jobName": "Test-Job-Name",
                "algorithmSpecification": {},
            }
        ),
    ],
)
@patch("braket.jobs.local.local_job.prepare_quantum_job")
@patch("braket.jobs.local.local_job.retrieve_image")
@patch("braket.jobs.local.local_job.setup_container")
@patch("braket.jobs.local.local_job._LocalJobContainer")
@patch("os.path.isdir")
def test_create(
    mock_dir,
    mock_container,
    mock_setup,
    mock_retrieve_image,
    mock_prepare_job,
    aws_session,
    creation_kwargs,
    job_results,
    run_log,
    test_envs,
):
    with patch("builtins.open", mock_open()) as file_open:
        mock_dir.return_value = False
        mock_prepare_job.return_value = creation_kwargs

        mock_container_open = mock_container.return_value.__enter__.return_value
        mock_container_open.run_log = run_log
        file_read = file_open()
        file_read.read.return_value = json.dumps(job_results)
        mock_setup.return_value = test_envs

        job = LocalQuantumJob.create(
            device=Mock(),
            source_module=Mock(),
            entry_point=Mock(),
            image_uri=Mock(),
            job_name=Mock(),
            code_location=Mock(),
            role_arn=Mock(),
            hyperparameters=Mock(),
            input_data=Mock(),
            output_data_config=Mock(),
            checkpoint_config=Mock(),
            aws_session=aws_session,
        )
        assert job.name == "Test-Job-Name"
        assert job.arn == "local:job/Test-Job-Name"
        assert job.state() == "COMPLETED"
        assert job.run_log == run_log
        assert job.metadata() is None
        assert job.cancel() is None
        assert job.download_result() is None
        assert job.logs() is None
        assert job.result() == job_results["dataDictionary"]
        assert job.metrics() == {
            "Cost": [-4.034, -3.957],
            "iteration_number": [0.0, 1.0],
            "timestamp": [1633027264.5406773, 1633027288.6284382],
        }
        mock_setup.assert_called_with(mock_container_open, aws_session, **creation_kwargs)
        mock_container_open.run_local_job.assert_called_with(test_envs)


def test_create_invalid_arg():
    unexpected_kwarg = "create\\(\\) got an unexpected keyword argument 'wait_until_complete'"
    with pytest.raises(TypeError, match=unexpected_kwarg):
        LocalQuantumJob.create(
            device="device",
            source_module="source",
            wait_until_complete=True,
        )


@patch("os.path.isdir")
def test_read_runlog_file(mock_dir):
    mock_dir.return_value = True
    with patch("builtins.open", mock_open()) as file_open:
        file_read = file_open()
        file_read.read.return_value = "Test Log"
        job = LocalQuantumJob("local:job/Fake-Job")
        assert job.run_log == "Test Log"


@patch("braket.jobs.local.local_job.prepare_quantum_job")
@patch("os.path.isdir")
def test_create_existing_job(mock_dir, mock_prepare_job, aws_session):
    mock_dir.return_value = True
    mock_prepare_job.return_value = {
        "jobName": "Test-Job-Name",
        "algorithmSpecification": {"containerImage": {"uri": "file://test-URI"}},
        "checkpointConfig": {"localPath": "test/local/path/"},
    }
    dir_already_exists = (
        "A local directory called Test-Job-Name already exists. Please use a different job name."
    )
    with pytest.raises(ValueError, match=dir_already_exists):
        LocalQuantumJob.create(
            device=Mock(),
            source_module=Mock(),
            entry_point=Mock(),
            image_uri=Mock(),
            job_name=Mock(),
            code_location=Mock(),
            role_arn=Mock(),
            hyperparameters=Mock(),
            input_data=Mock(),
            output_data_config=Mock(),
            checkpoint_config=Mock(),
            aws_session=aws_session,
        )


def test_invalid_arn():
    invalid_arn = "Arn Invalid-Arn is not a valid local job arn"
    with pytest.raises(ValueError, match=invalid_arn):
        LocalQuantumJob("Invalid-Arn")


def test_missing_job_dir():
    missing_dir = "Unable to find local job results for Missing-Dir"
    with pytest.raises(ValueError, match=missing_dir):
        LocalQuantumJob("local:job/Missing-Dir")


@patch("os.path.isdir")
def test_missing_runlog_file(mock_dir):
    mock_dir.return_value = True
    job = LocalQuantumJob("local:job/Fake-Dir")
    no_file = "Unable to find logs in the local job directory Fake-Dir."
    with pytest.raises(ValueError, match=no_file):
        job.run_log


@patch("os.path.isdir")
def test_missing_results_file(mock_dir):
    mock_dir.return_value = True
    job = LocalQuantumJob("local:job/Fake-Dir")
    no_results = "Unable to find results in the local job directory Fake-Dir."
    with pytest.raises(ValueError, match=no_results):
        job.result()
