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
from __future__ import annotations

import importlib.util
import re
import sys
import tarfile
import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from braket.aws.aws_session import AwsSession
from braket.jobs.config import (
    CheckpointConfig,
    DeviceConfig,
    InstanceConfig,
    OutputDataConfig,
    S3DataSourceConfig,
    StoppingCondition,
)


def prepare_quantum_job(
    device: str,
    source_module: str,
    entry_point: str = None,
    image_uri: str = None,
    job_name: str = None,
    code_location: str = None,
    role_arn: str = None,
    hyperparameters: Dict[str, Any] = None,
    input_data: Union[str, Dict, S3DataSourceConfig] = None,
    instance_config: InstanceConfig = None,
    stopping_condition: StoppingCondition = None,
    output_data_config: OutputDataConfig = None,
    copy_checkpoints_from_job: str = None,
    checkpoint_config: CheckpointConfig = None,
    aws_session: AwsSession = None,
    tags: Dict[str, str] = None,
):
    """Creates a job by invoking the Braket CreateJob API.

    Args:
        device (str): ARN for the AWS device which is primarily
            accessed for the execution of this job.

        source_module (str): Path (absolute, relative or an S3 URI) to a python module to be
            tarred and uploaded. If `source_module` is an S3 URI, it must point to a
            tar.gz file. Otherwise, source_module may be a file or directory.

        entry_point (str): A str that specifies the entry point of the job, relative to
            the source module. The entry point must be in the format
            `importable.module` or `importable.module:callable`. For example,
            `source_module.submodule:start_here` indicates the `start_here` function
            contained in `source_module.submodule`. If source_module is an S3 URI,
            entry point must be given. Default: source_module's name

        image_uri (str): A str that specifies the ECR image to use for executing the job.
            `image_uris.retrieve_image()` function may be used for retrieving the ECR image URIs
            for the containers supported by Braket. Default = `<Braket base image_uri>`.

        job_name (str): A str that specifies the name with which the job is created.
            Default: f'{image_uri_type}-{timestamp}'.

        code_location (str): The S3 prefix URI where custom code will be uploaded.
            Default: f's3://{default_bucket_name}/jobs/{job_name}/script'.

        role_arn (str): A str providing the IAM role ARN used to execute the
            script. Default: IAM role returned by AwsSession's `get_default_jobs_role()`.

        hyperparameters (Dict[str, Any]): Hyperparameters accessible to the job.
            The hyperparameters are made accessible as a Dict[str, str] to the job.
            For convenience, this accepts other types for keys and values, but `str()`
            is called to convert them before being passed on. Default: None.

        input_data (Union[str, S3DataSourceConfig, dict]): Information about the training
            data. Dictionary maps channel names to local paths or S3 URIs. Contents found
            at any local paths will be uploaded to S3 at
            f's3://{default_bucket_name}/jobs/{job_name}/data/{channel_name}. If a local
            path, S3 URI, or S3DataSourceConfig is provided, it will be given a default
            channel name "input".
            Default: {}.

        instance_config (InstanceConfig): Configuration of the instances to be used
            to execute the job. Default: InstanceConfig(instanceType='ml.m5.large',
            instanceCount=1, volumeSizeInGB=30, volumeKmsKey=None).

        stopping_condition (StoppingCondition): The maximum length of time, in seconds,
            and the maximum number of tasks that a job can run before being forcefully stopped.
            Default: StoppingCondition(maxRuntimeInSeconds=5 * 24 * 60 * 60).

        output_data_config (OutputDataConfig): Specifies the location for the output of the job.
            Default: OutputDataConfig(s3Path=f's3://{default_bucket_name}/jobs/{job_name}/data',
            kmsKeyId=None).

        copy_checkpoints_from_job (str): A str that specifies the job ARN whose checkpoint you
            want to use in the current job. Specifying this value will copy over the checkpoint
            data from `use_checkpoints_from_job`'s checkpoint_config s3Uri to the current job's
            checkpoint_config s3Uri, making it available at checkpoint_config.localPath during
            the job execution. Default: None

        checkpoint_config (CheckpointConfig): Configuration that specifies the location where
            checkpoint data is stored.
            Default: CheckpointConfig(localPath='/opt/jobs/checkpoints',
            s3Uri=f's3://{default_bucket_name}/jobs/{job_name}/checkpoints').

        aws_session (AwsSession): AwsSession for connecting to AWS Services.
            Default: AwsSession()

        tags (Dict[str, str]): Dict specifying the key-value pairs for tagging this job.
            Default: {}.

    Returns:
        AwsQuantumJob: Job tracking the execution on Amazon Braket.

    Raises:
        ValueError: Raises ValueError if the parameters are not valid.
    """
    param_datatype_map = {
        "instance_config": (instance_config, InstanceConfig),
        "stopping_condition": (stopping_condition, StoppingCondition),
        "output_data_config": (output_data_config, OutputDataConfig),
        "checkpoint_config": (checkpoint_config, CheckpointConfig),
    }

    _validate_params(param_datatype_map)
    aws_session = aws_session or AwsSession()
    device_config = DeviceConfig(device)
    job_name = job_name or _generate_default_job_name(image_uri)
    role_arn = role_arn or aws_session.get_default_jobs_role()
    hyperparameters = hyperparameters or {}
    input_data = input_data or {}
    tags = tags or {}
    default_bucket = aws_session.default_bucket()
    input_data_list = _process_input_data(input_data, job_name, aws_session)
    instance_config = instance_config or InstanceConfig()
    stopping_condition = stopping_condition or StoppingCondition()
    output_data_config = output_data_config or OutputDataConfig()
    checkpoint_config = checkpoint_config or CheckpointConfig()
    code_location = code_location or AwsSession.construct_s3_uri(
        default_bucket,
        "jobs",
        job_name,
        "script",
    )
    if AwsSession.is_s3_uri(source_module):
        _process_s3_source_module(source_module, entry_point, aws_session, code_location)
    else:
        # if entry point is None, it will be set to default here
        entry_point = _process_local_source_module(
            source_module, entry_point, aws_session, code_location
        )
    algorithm_specification = {
        "scriptModeConfig": {
            "entryPoint": entry_point,
            "s3Uri": f"{code_location}/source.tar.gz",
            "compressionType": "GZIP",
        }
    }
    if image_uri:
        algorithm_specification["containerImage"] = {"uri": image_uri}
    if not output_data_config.s3Path:
        output_data_config.s3Path = AwsSession.construct_s3_uri(
            default_bucket,
            "jobs",
            job_name,
            "data",
        )
    if not checkpoint_config.s3Uri:
        checkpoint_config.s3Uri = AwsSession.construct_s3_uri(
            default_bucket,
            "jobs",
            job_name,
            "checkpoints",
        )
    if copy_checkpoints_from_job:
        checkpoints_to_copy = aws_session.get_job(copy_checkpoints_from_job)["checkpointConfig"][
            "s3Uri"
        ]
        aws_session.copy_s3_directory(checkpoints_to_copy, checkpoint_config.s3Uri)

    create_job_kwargs = {
        "jobName": job_name,
        "roleArn": role_arn,
        "algorithmSpecification": algorithm_specification,
        "inputDataConfig": input_data_list,
        "instanceConfig": asdict(instance_config),
        "outputDataConfig": asdict(output_data_config),
        "checkpointConfig": asdict(checkpoint_config),
        "deviceConfig": asdict(device_config),
        "hyperParameters": hyperparameters,
        "stoppingCondition": asdict(stopping_condition),
        "tags": tags,
    }

    return create_job_kwargs


def _generate_default_job_name(image_uri: Optional[str]) -> str:
    """
    Generate default job name using the image uri and a timestamp
    Args:
        image_uri (str, optional): URI for the image container.

    Returns:
        str: Job name.
    """
    if not image_uri:
        job_type = "-default"
    else:
        job_type_match = re.search("/amazon-braket-(.*)-jobs:", image_uri) or re.search(
            "/amazon-braket-([^:/]*)", image_uri
        )
        job_type = f"-{job_type_match.groups()[0]}" if job_type_match else ""

    return f"braket-job{job_type}-{time.time() * 1000:.0f}"


def _process_s3_source_module(
    source_module: str, entry_point: str, aws_session: AwsSession, code_location: str
) -> None:
    """
    Check that the source module is an S3 URI of the correct type and that entry point is
    provided.

    Args:
        source_module (str): S3 URI pointing to the tarred source module.
        entry_point (str): Entry point for the job.
        aws_session (AwsSession): AwsSession to copy source module to code location.
        code_location (str): S3 URI pointing to the location where the code will be
            copied to.
    """
    if entry_point is None:
        raise ValueError("If source_module is an S3 URI, entry_point must be provided.")
    if not source_module.lower().endswith(".tar.gz"):
        raise ValueError(
            "If source_module is an S3 URI, it must point to a tar.gz file. "
            f"Not a valid S3 URI for parameter `source_module`: {source_module}"
        )
    aws_session.copy_s3_object(source_module, f"{code_location}/source.tar.gz")


def _process_local_source_module(
    source_module: str, entry_point: str, aws_session: AwsSession, code_location: str
) -> str:
    """
    Check that entry point is valid with respect to source module, or provide a default
    value if entry point is not given. Tar and upload source module to code location in S3.
    Args:
        source_module (str): Local path pointing to the source module.
        entry_point (str): Entry point relative to the source module.
        aws_session (AwsSession): AwsSession for uploading tarred source module.
        code_location (str): S3 URI pointing to the location where the code will
            be uploaded to.

    Returns:
        str: Entry point.
    """
    try:
        # raises FileNotFoundError if not found
        abs_path_source_module = Path(source_module).resolve(strict=True)
    except FileNotFoundError:
        raise ValueError(f"Source module not found: {source_module}")

    entry_point = entry_point or abs_path_source_module.stem
    _validate_entry_point(abs_path_source_module, entry_point)
    _tar_and_upload_to_code_location(abs_path_source_module, aws_session, code_location)
    return entry_point


def _validate_entry_point(source_module_path: Path, entry_point: str) -> None:
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
        module = importlib.util.find_spec(importable, source_module_path.stem)
        assert module is not None
    # if entry point is nested (ie contains '.'), parent modules are imported
    except (ModuleNotFoundError, AssertionError):
        raise ValueError(f"Entry point module was not found: {importable}")
    finally:
        sys.path.pop()


def _tar_and_upload_to_code_location(
    source_module_path: Path, aws_session: AwsSession, code_location: str
) -> None:
    """
    Tar and upload source module to code location.

    Args:
        source_module_path (Path): Path to source module.
        aws_session (AwsSession): AwsSession for uploading source module.
        code_location (str): S3 URI pointing to the location where the tarred
            source module will be uploaded to.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(f"{temp_dir}/source.tar.gz", "w:gz", dereference=True) as tar:
            tar.add(source_module_path, arcname=source_module_path.name)
        aws_session.upload_to_s3(f"{temp_dir}/source.tar.gz", f"{code_location}/source.tar.gz")


def _validate_params(dict_arr: Dict[str, Tuple[any, any]]) -> None:
    """
    Validate that config parameters are of the right type.

    Args:
        dict_arr (Dict[str, Tuple[any, any]]): dict mapping parameter names to
            a tuple containing the provided value and expected type.
    """
    for parameter_name, value_tuple in dict_arr.items():
        user_input, expected_datatype = value_tuple

        if user_input and not isinstance(user_input, expected_datatype):
            raise ValueError(
                f"'{parameter_name}' should be of '{expected_datatype}' "
                f"but user provided {type(user_input)}."
            )


def _process_input_data(
    input_data: Union[str, Dict, S3DataSourceConfig], job_name: str, aws_session: AwsSession
) -> List[Dict[str, Any]]:
    """
    Convert input data into a list of dicts compatible with the Braket API.
    Args:
        input_data (Union[str, Dict, S3DataSourceConfig]): Either a channel definition or a
            dictionary mapping channel names to channel definitions, where a channel definition
            can be an S3DataSourceConfig or a str corresponding to a local prefix or S3 prefix.
        job_name (str): Job name.
        aws_session (AwsSession): AwsSession for possibly uploading local data.

    Returns:
        List[Dict[str, Any]]: A list of channel configs.
    """
    if not isinstance(input_data, dict):
        input_data = {"input": input_data}
    for channel_name, data in input_data.items():
        if not isinstance(data, S3DataSourceConfig):
            input_data[channel_name] = _process_channel(data, job_name, aws_session, channel_name)
    return _convert_input_to_config(input_data)


def _process_channel(
    location: str, job_name: str, aws_session: AwsSession, channel_name: str
) -> S3DataSourceConfig:
    """
    Convert a location to an S3DataSourceConfig, uploading local data to S3, if necessary.
    Args:
        location (str): Local prefix or S3 prefix.
        job_name (str): Job name.
        aws_session (AwsSession): AwsSession to be used for uploading local data.
        channel_name (str): Name of the channel.

    Returns:
        S3DataSourceConfig: S3DataSourceConfig for the channel.
    """
    if AwsSession.is_s3_uri(location):
        return S3DataSourceConfig(location)
    else:
        # local prefix "path/to/prefix" will be mapped to
        # s3://bucket/jobs/job-name/data/input/prefix
        location_name = Path(location).name
        s3_prefix = AwsSession.construct_s3_uri(
            aws_session.default_bucket(), "jobs", job_name, "data", channel_name, location_name
        )
        aws_session.upload_local_data(location, s3_prefix)
        return S3DataSourceConfig(s3_prefix)


def _convert_input_to_config(input_data: Dict[str, S3DataSourceConfig]) -> List[Dict[str, Any]]:
    """
    Convert a dictionary mapping channel names to S3DataSourceConfigs into a list of channel
    configs compatible with the Braket API.

    Args:
        input_data (Dict[str, S3DataSourceConfig]): A dictionary mapping channel names to
            S3DataSourceConfig objects.

    Returns:
        List[Dict[str, Any]]: A list of channel configs.
    """
    return [
        {
            "channelName": channel_name,
            **data_config.config,
        }
        for channel_name, data_config in input_data.items()
    ]
