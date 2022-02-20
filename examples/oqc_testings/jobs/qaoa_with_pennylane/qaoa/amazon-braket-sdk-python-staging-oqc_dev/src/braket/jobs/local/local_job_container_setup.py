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
import tempfile
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Dict, Iterable

from braket.aws.aws_session import AwsSession
from braket.jobs.local.local_job_container import _LocalJobContainer


def setup_container(
    container: _LocalJobContainer, aws_session: AwsSession, **creation_kwargs
) -> Dict[str, str]:
    """Sets up a container with prerequisites for running a Braket Job. The prerequisites are
    based on the options the customer has chosen for the job. Similarly, any environment variables
    that are needed during runtime will be returned by this function.

    Args:
        container(_LocalJobContainer): The container that will run the braket job.
        aws_session (AwsSession): AwsSession for connecting to AWS Services.
        **creation_kwargs: Keyword arguments for the boto3 Amazon Braket `CreateJob` operation.

    Returns:
        (Dict[str, str]): A dictionary of environment variables that reflect Braket Jobs options
        requested by the customer.
    """
    logger = getLogger(__name__)
    _create_expected_paths(container, **creation_kwargs)
    run_environment_variables = {}
    run_environment_variables.update(_get_env_credentials(aws_session, logger))
    run_environment_variables.update(
        _get_env_script_mode_config(creation_kwargs["algorithmSpecification"]["scriptModeConfig"])
    )
    run_environment_variables.update(_get_env_default_vars(aws_session, **creation_kwargs))
    if _copy_hyperparameters(container, **creation_kwargs):
        run_environment_variables.update(_get_env_hyperparameters())
    if _copy_input_data_list(container, aws_session, **creation_kwargs):
        run_environment_variables.update(_get_env_input_data())
    return run_environment_variables


def _create_expected_paths(container: _LocalJobContainer, **creation_kwargs) -> None:
    """Creates the basic paths required for Braket Jobs to run.

    Args:
        container(_LocalJobContainer): The container that will run the braket job.
        **creation_kwargs: Keyword arguments for the boto3 Amazon Braket `CreateJob` operation.
    """
    container.makedir("/opt/ml/model")
    container.makedir(creation_kwargs["checkpointConfig"]["localPath"])


def _get_env_credentials(aws_session: AwsSession, logger: Logger) -> Dict[str, str]:
    """Gets the account credentials from boto so they can be added as environment variables to
    the running container.

    Args:
        aws_session (AwsSession): AwsSession for connecting to AWS Services.
        logger (Logger): Logger object with which to write logs. Default is `getLogger(__name__)`

    Returns:
        (Dict[str, str]): The set of key/value pairs that should be added as environment variables
        to the running container.
    """
    credentials = aws_session.boto_session.get_credentials()
    if credentials.token is None:
        logger.info("Using the long-lived AWS credentials found in session")
        return {
            "AWS_ACCESS_KEY_ID": str(credentials.access_key),
            "AWS_SECRET_ACCESS_KEY": str(credentials.secret_key),
        }
    logger.warning(
        "Using the short-lived AWS credentials found in session. They might expire while running."
    )
    return {
        "AWS_ACCESS_KEY_ID": str(credentials.access_key),
        "AWS_SECRET_ACCESS_KEY": str(credentials.secret_key),
        "AWS_SESSION_TOKEN": str(credentials.token),
    }


def _get_env_script_mode_config(script_mode_config: Dict[str, str]) -> Dict[str, str]:
    """Gets the environment variables related to the customer script mode config.

    Args:
        script_mode_config (Dict[str, str]): The values for scriptModeConfig in the boto3 input
        parameters for running a Braket Job.

    Returns:
        (Dict[str, str]): The set of key/value pairs that should be added as environment variables
        to the running container.
    """
    result = {
        "AMZN_BRAKET_SCRIPT_S3_URI": script_mode_config["s3Uri"],
        "AMZN_BRAKET_SCRIPT_ENTRY_POINT": script_mode_config["entryPoint"],
    }
    if "compressionType" in script_mode_config:
        result["AMZN_BRAKET_SCRIPT_COMPRESSION_TYPE"] = script_mode_config["compressionType"]
    return result


def _get_env_default_vars(aws_session: AwsSession, **creation_kwargs) -> Dict[str, str]:
    """This function gets the remaining 'simple' env variables, that don't require any
     additional logic to determine what they are or when they should be added as env variables.

    Returns:
        (Dict[str, str]): The set of key/value pairs that should be added as environment variables
        to the running container.
    """
    job_name = creation_kwargs["jobName"]
    bucket, location = AwsSession.parse_s3_uri(creation_kwargs["outputDataConfig"]["s3Path"])
    return {
        "AWS_DEFAULT_REGION": aws_session.region,
        "AMZN_BRAKET_JOB_NAME": job_name,
        "AMZN_BRAKET_DEVICE_ARN": creation_kwargs["deviceConfig"]["device"],
        "AMZN_BRAKET_JOB_RESULTS_DIR": "/opt/braket/model",
        "AMZN_BRAKET_CHECKPOINT_DIR": creation_kwargs["checkpointConfig"]["localPath"],
        "AMZN_BRAKET_OUT_S3_BUCKET": bucket,
        "AMZN_BRAKET_TASK_RESULTS_S3_URI": f"s3://{bucket}/jobs/{job_name}/tasks",
        "AMZN_BRAKET_JOB_RESULTS_S3_PATH": str(Path(location, job_name, "output").as_posix()),
    }


def _get_env_hyperparameters() -> Dict[str, str]:
    """Gets the env variable for hyperparameters. This should only be added if the customer has
    provided hyperpameters to the job.

    Returns:
        (Dict[str, str]): The set of key/value pairs that should be added as environment variables
        to the running container.
    """
    return {
        "AMZN_BRAKET_HP_FILE": "/opt/braket/input/config/hyperparameters.json",
    }


def _get_env_input_data() -> Dict[str, str]:
    """Gets the env variable for input data. This should only be added if the customer has
    provided input data to the job.

    Returns:
        (Dict[str, str]): The set of key/value pairs that should be added as environment variables
        to the running container.
    """
    return {
        "AMZN_BRAKET_INPUT_DIR": "/opt/braket/input/data",
    }


def _copy_hyperparameters(container: _LocalJobContainer, **creation_kwargs) -> bool:
    """If hyperpameters are present, this function will store them as a JSON object in the
     container in the appropriate location on disk.

    Args:
        container(_LocalJobContainer): The container to save hyperparameters to.
        **creation_kwargs: Keyword arguments for the boto3 Amazon Braket `CreateJob` operation.

    Returns:
        (bool): True if any hyperparameters were copied to the container.
    """
    if "hyperParameters" not in creation_kwargs:
        return False
    hyperparameters = creation_kwargs["hyperParameters"]
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir, "hyperparameters.json")
        with open(file_path, "w") as write_file:
            json.dump(hyperparameters, write_file)
        container.copy_to(str(file_path), "/opt/ml/input/config/hyperparameters.json")
    return True


def _download_input_data(
    aws_session: AwsSession,
    download_dir: str,
    input_data: Dict[str, Any],
) -> None:
    """Downloads input data for a job.

    Args:
        aws_session (AwsSession): AwsSession for connecting to AWS Services.
        download_dir (str): The directory path to download to.
        input_data (Dict[str, Any]): One of the input data in the boto3 input parameters for
            running a Braket Job.
    """
    # If s3 prefix is the full name of a directory and all keys are inside
    # that directory, the contents of said directory will be copied into a
    # directory with the same name as the channel. This behavior is the same
    # whether or not s3 prefix ends with a "/". Moreover, if s3 prefix ends
    # with a "/", this is certainly the behavior to expect, since it can only
    # match a directory.
    # If s3 prefix matches any files exactly, or matches as a prefix of any
    # files or directories, then all files and directories matching s3 prefix
    # will be copied into a directory with the same name as the channel.
    channel_name = input_data["channelName"]
    s3_uri_prefix = input_data["dataSource"]["s3DataSource"]["s3Uri"]
    bucket, prefix = AwsSession.parse_s3_uri(s3_uri_prefix)
    s3_keys = aws_session.list_keys(bucket, prefix)
    top_level = prefix if _is_dir(prefix, s3_keys) else str(Path(prefix).parent)
    found_item = False
    try:
        Path(download_dir, channel_name).mkdir()
    except FileExistsError:
        raise ValueError(f"Duplicate channel names not allowed for input data: {channel_name}")
    for s3_key in s3_keys:
        relative_key = Path(s3_key).relative_to(top_level)
        download_path = Path(download_dir, channel_name, relative_key)
        if not s3_key.endswith("/"):
            download_path.parent.mkdir(parents=True, exist_ok=True)
            aws_session.download_from_s3(
                AwsSession.construct_s3_uri(bucket, s3_key), str(download_path)
            )
            found_item = True
    if not found_item:
        raise RuntimeError(f"No data found for channel '{channel_name}'")


def _is_dir(prefix: str, keys: Iterable[str]) -> bool:
    """determine whether the prefix refers to a directory"""
    if prefix.endswith("/"):
        return True
    return all(key.startswith(f"{prefix}/") for key in keys)


def _copy_input_data_list(
    container: _LocalJobContainer, aws_session: AwsSession, **creation_kwargs
) -> bool:
    """If the input data list is not empty, this function will download the input files and
    store them in the container.

    Args:
        container(_LocalJobContainer): The container to save input data to.
        aws_session (AwsSession): AwsSession for connecting to AWS Services.
        **creation_kwargs: Keyword arguments for the boto3 Amazon Braket `CreateJob` operation.

    Returns:
        (bool): True if any input data was copied to the container.
    """
    if "inputDataConfig" not in creation_kwargs:
        return False

    input_data_list = creation_kwargs["inputDataConfig"]
    with tempfile.TemporaryDirectory() as temp_dir:
        for input_data in input_data_list:
            _download_input_data(aws_session, temp_dir, input_data)
        container.copy_to(temp_dir, "/opt/ml/input/data/")
    return bool(input_data_list)
