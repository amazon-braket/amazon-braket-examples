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

import os
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from braket.jobs.local.local_job_container_setup import setup_container


@pytest.fixture
def aws_session():
    _aws_session = Mock()
    _aws_session.boto_session.get_credentials.return_value.access_key = "Test Access Key"
    _aws_session.boto_session.get_credentials.return_value.secret_key = "Test Secret Key"
    _aws_session.boto_session.get_credentials.return_value.token = None
    _aws_session.region = "Test Region"
    _aws_session.list_keys.side_effect = lambda bucket, prefix: [
        key
        for key in [
            "input-dir/",
            "input-dir/file-1.txt",
            "input-dir/file-2.txt",
        ]
        if key.startswith(prefix)
    ]
    return _aws_session


@pytest.fixture
def container():
    _container = Mock()
    return _container


@pytest.fixture
def creation_kwargs():
    return {
        "algorithmSpecification": {
            "scriptModeConfig": {
                "entryPoint": "my_file:start_here",
                "s3Uri": "s3://amazon-braket-jobs/job-path/my_file.py",
            }
        },
        "checkpointConfig": {
            "localPath": "/opt/omega/checkpoints",
            "s3Uri": "s3://amazon-braket-jobs/job-path/checkpoints",
        },
        "outputDataConfig": {"s3Path": "s3://test_bucket/test_location/"},
        "deviceConfig": {"device": "test device ARN"},
        "jobName": "Test-Job-Name",
        "roleArn": "arn:aws:iam::875981177017:role/AmazonBraketJobRole",
    }


@pytest.fixture
def compressed_script_mode_config():
    return {
        "scriptModeConfig": {
            "entryPoint": "my_file:start_here",
            "s3Uri": "s3://amazon-braket-jobs/job-path/my_archive.gzip",
            "compressionType": "gzip",
        }
    }


@pytest.fixture
def expected_envs():
    return {
        "AMZN_BRAKET_CHECKPOINT_DIR": "/opt/omega/checkpoints",
        "AMZN_BRAKET_DEVICE_ARN": "test device ARN",
        "AMZN_BRAKET_JOB_NAME": "Test-Job-Name",
        "AMZN_BRAKET_JOB_RESULTS_DIR": "/opt/braket/model",
        "AMZN_BRAKET_JOB_RESULTS_S3_PATH": "test_location/Test-Job-Name/output",
        "AMZN_BRAKET_OUT_S3_BUCKET": "test_bucket",
        "AMZN_BRAKET_SCRIPT_ENTRY_POINT": "my_file:start_here",
        "AMZN_BRAKET_SCRIPT_S3_URI": "s3://amazon-braket-jobs/job-path/my_file.py",
        "AMZN_BRAKET_TASK_RESULTS_S3_URI": "s3://test_bucket/jobs/Test-Job-Name/tasks",
        "AWS_ACCESS_KEY_ID": "Test Access Key",
        "AWS_DEFAULT_REGION": "Test Region",
        "AWS_SECRET_ACCESS_KEY": "Test Secret Key",
    }


@pytest.fixture
def input_data_config():
    return [
        # s3 prefix is a single file
        {
            "channelName": "single-file",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/input-dir/file-1.txt"}},
        },
        # s3 prefix is a directory no slash
        {
            "channelName": "directory-no-slash",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/input-dir"}},
        },
        # s3 prefix is a directory with slash
        {
            "channelName": "directory-slash",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/input-dir/"}},
        },
        # s3 prefix is a prefix for a directory
        {
            "channelName": "directory-prefix",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/input"}},
        },
        # s3 prefix is a prefix for multiple files
        {
            "channelName": "files-prefix",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/input-dir/file"}},
        },
    ]


def test_basic_setup(container, aws_session, creation_kwargs, expected_envs):
    aws_session.parse_s3_uri.return_value = ["test_bucket", "test_location"]
    envs = setup_container(container, aws_session, **creation_kwargs)
    assert envs == expected_envs
    container.makedir.assert_any_call("/opt/ml/model")
    container.makedir.assert_any_call(expected_envs["AMZN_BRAKET_CHECKPOINT_DIR"])
    assert container.makedir.call_count == 2


def test_compressed_script_mode(
    container, aws_session, creation_kwargs, expected_envs, compressed_script_mode_config
):
    creation_kwargs["algorithmSpecification"] = compressed_script_mode_config
    expected_envs["AMZN_BRAKET_SCRIPT_S3_URI"] = "s3://amazon-braket-jobs/job-path/my_archive.gzip"
    expected_envs["AMZN_BRAKET_SCRIPT_COMPRESSION_TYPE"] = "gzip"
    aws_session.parse_s3_uri.return_value = ["test_bucket", "test_location"]
    envs = setup_container(container, aws_session, **creation_kwargs)
    assert envs == expected_envs
    container.makedir.assert_any_call("/opt/ml/model")
    container.makedir.assert_any_call(expected_envs["AMZN_BRAKET_CHECKPOINT_DIR"])
    assert container.makedir.call_count == 2


@patch("json.dump")
@patch("tempfile.TemporaryDirectory")
def test_hyperparameters(tempfile, json, container, aws_session, creation_kwargs, expected_envs):
    with patch("builtins.open", mock_open()):
        tempfile.return_value.__enter__.return_value = "temporaryDir"
        creation_kwargs["hyperParameters"] = {"test": "hyper"}
        expected_envs["AMZN_BRAKET_HP_FILE"] = "/opt/braket/input/config/hyperparameters.json"
        aws_session.parse_s3_uri.return_value = ["test_bucket", "test_location"]
        envs = setup_container(container, aws_session, **creation_kwargs)
        assert envs == expected_envs
        container.makedir.assert_any_call("/opt/ml/model")
        container.makedir.assert_any_call(expected_envs["AMZN_BRAKET_CHECKPOINT_DIR"])
        assert container.makedir.call_count == 2
        container.copy_to.assert_called_with(
            os.path.join("temporaryDir", "hyperparameters.json"),
            "/opt/ml/input/config/hyperparameters.json",
        )


def test_input(container, aws_session, creation_kwargs, input_data_config):
    creation_kwargs.update({"inputDataConfig": input_data_config})
    setup_container(container, aws_session, **creation_kwargs)
    download_locations = [call[0][1] for call in aws_session.download_from_s3.call_args_list]
    expected_downloads = [
        Path("single-file", "file-1.txt"),
        Path("directory-no-slash", "file-1.txt"),
        Path("directory-no-slash", "file-2.txt"),
        Path("directory-slash", "file-1.txt"),
        Path("directory-slash", "file-2.txt"),
        Path("directory-prefix", "input-dir", "file-1.txt"),
        Path("directory-prefix", "input-dir", "file-2.txt"),
        Path("files-prefix", "file-1.txt"),
        Path("files-prefix", "file-2.txt"),
    ]

    for download, expected_download in zip(download_locations, expected_downloads):
        assert download.endswith(str(expected_download))


def test_duplicate_input(container, aws_session, creation_kwargs, input_data_config):
    input_data_config.append(
        {
            # this is a duplicate channel
            "channelName": "single-file",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/irrelevant"}},
        }
    )
    creation_kwargs.update({"inputDataConfig": input_data_config})
    dupes_not_allowed = "Duplicate channel names not allowed for input data: single-file"
    with pytest.raises(ValueError, match=dupes_not_allowed):
        setup_container(container, aws_session, **creation_kwargs)


def test_no_data_input(container, aws_session, creation_kwargs, input_data_config):
    input_data_config.append(
        {
            # this channel won't match any data
            "channelName": "no-data",
            "dataSource": {"s3DataSource": {"s3Uri": "s3://input_bucket/irrelevant"}},
        }
    )
    creation_kwargs.update({"inputDataConfig": input_data_config})
    no_data_found = "No data found for channel 'no-data'"
    with pytest.raises(RuntimeError, match=no_data_found):
        setup_container(container, aws_session, **creation_kwargs)


def test_temporary_credentials(container, aws_session, creation_kwargs, expected_envs):
    aws_session.boto_session.get_credentials.return_value.token = "Test Token"
    expected_envs["AWS_SESSION_TOKEN"] = "Test Token"
    aws_session.parse_s3_uri.return_value = ["test_bucket", "test_location"]
    envs = setup_container(container, aws_session, **creation_kwargs)
    assert envs == expected_envs
    container.makedir.assert_any_call("/opt/ml/model")
    container.makedir.assert_any_call(expected_envs["AMZN_BRAKET_CHECKPOINT_DIR"])
    assert container.makedir.call_count == 2
