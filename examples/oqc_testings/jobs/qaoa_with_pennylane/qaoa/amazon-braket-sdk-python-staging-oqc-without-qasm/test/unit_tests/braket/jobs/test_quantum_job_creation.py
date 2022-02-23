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

import datetime
import tempfile
import time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from braket.aws import AwsSession
from braket.jobs.config import (
    CheckpointConfig,
    InstanceConfig,
    OutputDataConfig,
    S3DataSourceConfig,
    StoppingCondition,
)
from braket.jobs.quantum_job_creation import (
    _generate_default_job_name,
    _process_input_data,
    _process_local_source_module,
    _process_s3_source_module,
    _tar_and_upload_to_code_location,
    _validate_entry_point,
    prepare_quantum_job,
)


@pytest.fixture
def aws_session():
    _aws_session = Mock(spec=AwsSession)
    _aws_session.default_bucket.return_value = "default-bucket-name"
    _aws_session.get_default_jobs_role.return_value = "default-role-arn"
    return _aws_session


@pytest.fixture
def entry_point():
    return "test-source-dir.entry_point:func"


@pytest.fixture
def bucket():
    return "braket-region-id"


@pytest.fixture
def tags():
    return {"tag-key": "tag-value"}


@pytest.fixture(
    params=[
        None,
        "aws.location/amazon-braket-custom-jobs:tag.1.2.3",
        "other.uri/amazon-braket-custom-name:tag",
        "other.uri/custom-non-managed:tag",
        "other-custom-format.com",
    ]
)
def image_uri(request):
    return request.param


@pytest.fixture(params=["given_job_name", "default_job_name"])
def job_name(request):
    if request.param == "given_job_name":
        return "test-job-name"


@pytest.fixture
def s3_prefix(job_name):
    return f"{job_name}/non-default"


@pytest.fixture(params=["local_source", "s3_source"])
def source_module(request, bucket):
    if request.param == "local_source":
        return "test-source-module"
    elif request.param == "s3_source":
        return AwsSession.construct_s3_uri(bucket, "test-source-prefix", "source.tar.gz")


@pytest.fixture
def code_location(bucket, s3_prefix):
    return AwsSession.construct_s3_uri(bucket, s3_prefix, "script")


@pytest.fixture
def role_arn():
    return "arn:aws:iam::0000000000:role/AmazonBraketInternalSLR"


@pytest.fixture
def device():
    return "arn:aws:braket:::device/qpu/test/device-name"


@pytest.fixture
def hyperparameters():
    return {
        "param": "value",
        "other-param": 100,
    }


@pytest.fixture(params=["dict", "local"])
def input_data(request, bucket):
    if request.param == "dict":
        return {
            "s3_input": f"s3://{bucket}/data/prefix",
            "local_input": "local/prefix",
            "config_input": S3DataSourceConfig(f"s3://{bucket}/config/prefix"),
        }
    elif request.param == "local":
        return "local/prefix"


@pytest.fixture
def instance_config():
    return InstanceConfig(
        instanceType="ml.m5.large",
        volumeSizeInGb=1,
    )


@pytest.fixture
def stopping_condition():
    return StoppingCondition(
        maxRuntimeInSeconds=1200,
    )


@pytest.fixture
def output_data_config(bucket, s3_prefix):
    return OutputDataConfig(
        s3Path=AwsSession.construct_s3_uri(bucket, s3_prefix, "output"),
    )


@pytest.fixture
def checkpoint_config(bucket, s3_prefix):
    return CheckpointConfig(
        localPath="/opt/omega/checkpoints",
        s3Uri=AwsSession.construct_s3_uri(bucket, s3_prefix, "checkpoints"),
    )


@pytest.fixture
def generate_get_job_response():
    def _get_job_response(**kwargs):
        response = {
            "ResponseMetadata": {
                "RequestId": "d223b1a0-ee5c-4c75-afa7-3c29d5338b62",
                "HTTPStatusCode": 200,
            },
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
            "createdAt": datetime.datetime(2021, 6, 28, 21, 4, 51),
            "deviceConfig": {
                "device": "arn:aws:braket:::device/qpu/rigetti/Aspen-10",
            },
            "hyperParameters": {
                "foo": "bar",
            },
            "inputDataConfig": [
                {
                    "channelName": "training_input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://amazon-braket-jobs/job-path/input",
                        }
                    },
                }
            ],
            "instanceConfig": {
                "instanceType": "ml.m5.large",
                "volumeSizeInGb": 1,
            },
            "jobArn": "arn:aws:braket:us-west-2:875981177017:job/job-test-20210628140446",
            "jobName": "job-test-20210628140446",
            "outputDataConfig": {"s3Path": "s3://amazon-braket-jobs/job-path/data"},
            "roleArn": "arn:aws:iam::875981177017:role/AmazonBraketJobRole",
            "status": "RUNNING",
            "stoppingCondition": {"maxRuntimeInSeconds": 1200},
        }
        response.update(kwargs)

        return response

    return _get_job_response


@pytest.fixture(params=["fixtures", "defaults", "nones"])
def create_job_args(
    request,
    aws_session,
    entry_point,
    image_uri,
    source_module,
    job_name,
    code_location,
    role_arn,
    device,
    hyperparameters,
    input_data,
    instance_config,
    stopping_condition,
    output_data_config,
    checkpoint_config,
    tags,
):
    if request.param == "fixtures":
        return dict(
            (key, value)
            for key, value in {
                "device": device,
                "source_module": source_module,
                "entry_point": entry_point,
                "image_uri": image_uri,
                "job_name": job_name,
                "code_location": code_location,
                "role_arn": role_arn,
                "hyperparameters": hyperparameters,
                "input_data": input_data,
                "instance_config": instance_config,
                "stopping_condition": stopping_condition,
                "output_data_config": output_data_config,
                "checkpoint_config": checkpoint_config,
                "aws_session": aws_session,
                "tags": tags,
            }.items()
            if value is not None
        )
    elif request.param == "defaults":
        return {
            "device": device,
            "source_module": source_module,
            "entry_point": entry_point,
            "aws_session": aws_session,
        }
    elif request.param == "nones":
        return defaultdict(
            lambda: None,
            device=device,
            source_module=source_module,
            entry_point=entry_point,
            aws_session=aws_session,
        )


@patch("tarfile.TarFile.add")
@patch("importlib.util.find_spec")
@patch("braket.jobs.quantum_job_creation.Path")
@patch("time.time")
def test_create_job(
    mock_time,
    mock_path,
    mock_findspec,
    mock_tarfile,
    aws_session,
    source_module,
    create_job_args,
):
    mock_path.return_value.resolve.return_value.parent = "parent_dir"
    mock_path.return_value.resolve.return_value.stem = source_module
    mock_path.return_value.name = "file_name"
    mock_time.return_value = datetime.datetime.now().timestamp()
    expected_kwargs = _translate_creation_args(create_job_args)
    result_kwargs = prepare_quantum_job(**create_job_args)
    assert expected_kwargs == result_kwargs


def _translate_creation_args(create_job_args):
    aws_session = create_job_args["aws_session"]
    create_job_args = defaultdict(lambda: None, **create_job_args)
    image_uri = create_job_args["image_uri"]
    job_name = create_job_args["job_name"] or _generate_default_job_name(image_uri)
    default_bucket = aws_session.default_bucket()
    code_location = create_job_args["code_location"] or AwsSession.construct_s3_uri(
        default_bucket, "jobs", job_name, "script"
    )
    role_arn = create_job_args["role_arn"] or aws_session.get_default_jobs_role()
    device = create_job_args["device"]
    hyperparameters = create_job_args["hyperparameters"] or {}
    input_data = create_job_args["input_data"] or {}
    instance_config = create_job_args["instance_config"] or InstanceConfig()
    output_data_config = create_job_args["output_data_config"] or OutputDataConfig(
        s3Path=AwsSession.construct_s3_uri(default_bucket, "jobs", job_name, "data")
    )
    stopping_condition = create_job_args["stopping_condition"] or StoppingCondition()
    checkpoint_config = create_job_args["checkpoint_config"] or CheckpointConfig(
        s3Uri=AwsSession.construct_s3_uri(default_bucket, "jobs", job_name, "checkpoints")
    )
    entry_point = create_job_args["entry_point"]
    source_module = create_job_args["source_module"]
    if not AwsSession.is_s3_uri(source_module):
        entry_point = entry_point or Path(source_module).stem
    algorithm_specification = {
        "scriptModeConfig": {
            "entryPoint": entry_point,
            "s3Uri": f"{code_location}/source.tar.gz",
            "compressionType": "GZIP",
        }
    }
    if image_uri:
        algorithm_specification["containerImage"] = {"uri": image_uri}
    tags = create_job_args.get("tags", {})

    test_kwargs = {
        "jobName": job_name,
        "roleArn": role_arn,
        "algorithmSpecification": algorithm_specification,
        "inputDataConfig": _process_input_data(input_data, job_name, aws_session),
        "instanceConfig": asdict(instance_config),
        "outputDataConfig": asdict(output_data_config),
        "checkpointConfig": asdict(checkpoint_config),
        "deviceConfig": {"device": device},
        "hyperParameters": hyperparameters,
        "stoppingCondition": asdict(stopping_condition),
        "tags": tags,
    }

    return test_kwargs


@patch("time.time")
def test_generate_default_job_name(mock_time, image_uri):
    job_type_mapping = {
        None: "-default",
        "aws.location/amazon-braket-custom-jobs:tag.1.2.3": "-custom",
        "other.uri/amazon-braket-custom-name:tag": "-custom-name",
        "other.uri/custom-non-managed:tag": "",
        "other-custom-format.com": "",
    }
    job_type = job_type_mapping[image_uri]
    mock_time.return_value = datetime.datetime.now().timestamp()
    assert _generate_default_job_name(image_uri) == f"braket-job{job_type}-{time.time() * 1000:.0f}"


@pytest.mark.parametrize(
    "source_module",
    (
        "s3://bucket/source_module.tar.gz",
        "s3://bucket/SOURCE_MODULE.TAR.GZ",
    ),
)
def test_process_s3_source_module(source_module, aws_session):
    _process_s3_source_module(source_module, "entry_point", aws_session, "code_location")
    aws_session.copy_s3_object.assert_called_with(source_module, "code_location/source.tar.gz")


def test_process_s3_source_module_not_tar_gz(aws_session):
    must_be_tar_gz = (
        "If source_module is an S3 URI, it must point to a tar.gz file. "
        "Not a valid S3 URI for parameter `source_module`: s3://bucket/source_module"
    )
    with pytest.raises(ValueError, match=must_be_tar_gz):
        _process_s3_source_module(
            "s3://bucket/source_module", "entry_point", aws_session, "code_location"
        )


def test_process_s3_source_module_no_entry_point(aws_session):
    entry_point_required = "If source_module is an S3 URI, entry_point must be provided."
    with pytest.raises(ValueError, match=entry_point_required):
        _process_s3_source_module("s3://bucket/source_module", None, aws_session, "code_location")


@patch("braket.jobs.quantum_job_creation._tar_and_upload_to_code_location")
@patch("braket.jobs.quantum_job_creation._validate_entry_point")
def test_process_local_source_module(validate_mock, tar_and_upload_mock, aws_session):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module = Path(temp_dir, "source_module")
        source_module.touch()

        _process_local_source_module(
            str(source_module), "entry_point", aws_session, "code_location"
        )

        source_module_abs_path = Path(temp_dir, "source_module").resolve()
        validate_mock.assert_called_with(source_module_abs_path, "entry_point")
        tar_and_upload_mock.assert_called_with(source_module_abs_path, aws_session, "code_location")


def test_process_local_source_module_not_found(aws_session):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module = str(Path(temp_dir, "source_module").as_posix())
        source_module_not_found = f"Source module not found: {source_module}"
        with pytest.raises(ValueError, match=source_module_not_found):
            _process_local_source_module(source_module, "entry_point", aws_session, "code_location")


def test_validate_entry_point_default_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module.py")
        source_module_path.touch()
        # import source_module
        _validate_entry_point(source_module_path, "source_module")
        # from source_module import func
        _validate_entry_point(source_module_path, "source_module:func")
        # import .
        _validate_entry_point(source_module_path, ".")
        # from . import func
        _validate_entry_point(source_module_path, ".:func")


def test_validate_entry_point_default_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module")
        source_module_path.mkdir()
        # import source_module
        _validate_entry_point(source_module_path, "source_module")
        # from source_module import func
        _validate_entry_point(source_module_path, "source_module:func")
        # import .
        _validate_entry_point(source_module_path, ".")
        # from . import func
        _validate_entry_point(source_module_path, ".:func")


def test_validate_entry_point_submodule_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module")
        source_module_path.mkdir()
        Path(source_module_path, "submodule.py").touch()
        # from source_module import submodule
        _validate_entry_point(source_module_path, "source_module.submodule")
        # from source_module.submodule import func
        _validate_entry_point(source_module_path, "source_module.submodule:func")
        # from . import submodule
        _validate_entry_point(source_module_path, ".submodule")
        # from .submodule import func
        _validate_entry_point(source_module_path, ".submodule:func")


def test_validate_entry_point_submodule_init():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module")
        source_module_path.mkdir()
        Path(source_module_path, "submodule.py").touch()
        with open(str(Path(source_module_path, "__init__.py")), "w") as f:
            f.write("from . import submodule as renamed")
        # from source_module import renamed
        _validate_entry_point(source_module_path, "source_module:renamed")
        # from . import renamed
        _validate_entry_point(source_module_path, ".:renamed")


def test_validate_entry_point_source_module_not_found():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module")
        source_module_path.mkdir()
        Path(source_module_path, "submodule.py").touch()

        # catches ModuleNotFoundError
        module_not_found = "Entry point module was not found: fake_source_module.submodule"
        with pytest.raises(ValueError, match=module_not_found):
            _validate_entry_point(source_module_path, "fake_source_module.submodule")

        # catches AssertionError for module is not None
        submodule_not_found = "Entry point module was not found: source_module.fake_submodule"
        with pytest.raises(ValueError, match=submodule_not_found):
            _validate_entry_point(source_module_path, "source_module.fake_submodule")


@patch("tarfile.TarFile.add")
def test_tar_and_upload_to_code_location(mock_tar_add, aws_session):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_module_path = Path(temp_dir, "source_module")
        source_module_path.mkdir()
        _tar_and_upload_to_code_location(source_module_path, aws_session, "code_location")
        mock_tar_add.assert_called_with(source_module_path, arcname="source_module")
        local, s3 = aws_session.upload_to_s3.call_args_list[0][0]
        assert local.endswith("source.tar.gz")
        assert s3 == "code_location/source.tar.gz"


@patch("braket.jobs.quantum_job_creation._process_local_source_module")
@patch("braket.jobs.quantum_job_creation._validate_entry_point")
@patch("braket.jobs.quantum_job_creation._validate_params")
def test_copy_checkpoints(
    mock_validate_input,
    mock_validate_entry_point,
    mock_process_local_source,
    aws_session,
    entry_point,
    device,
    checkpoint_config,
    generate_get_job_response,
):
    other_checkpoint_uri = "s3://amazon-braket-jobs/job-path/checkpoints"
    aws_session.get_job.return_value = generate_get_job_response(
        checkpointConfig={
            "s3Uri": other_checkpoint_uri,
        }
    )
    prepare_quantum_job(
        device=device,
        source_module="source_module",
        entry_point=entry_point,
        copy_checkpoints_from_job="other-job-arn",
        checkpoint_config=checkpoint_config,
        aws_session=aws_session,
    )
    aws_session.copy_s3_directory.assert_called_with(other_checkpoint_uri, checkpoint_config.s3Uri)


def test_invalid_input_parameters(entry_point, aws_session):
    error_message = (
        "'instance_config' should be of '<class 'braket.jobs.config.InstanceConfig'>' "
        "but user provided <class 'int'>."
    )
    with pytest.raises(ValueError, match=error_message):
        prepare_quantum_job(
            aws_session=aws_session,
            entry_point=entry_point,
            device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            source_module="alpha_test_job",
            hyperparameters={
                "param-1": "first parameter",
                "param-2": "second param",
            },
            instance_config=2,
        )


@pytest.mark.parametrize(
    "input_data, input_data_configs",
    (
        (
            "local/prefix",
            [
                {
                    "channelName": "input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://default-bucket-name/jobs/job-name/data/input/prefix",
                        },
                    },
                }
            ],
        ),
        (
            "s3://my-bucket/my/prefix-",
            [
                {
                    "channelName": "input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://my-bucket/my/prefix-",
                        },
                    },
                }
            ],
        ),
        (
            S3DataSourceConfig(
                "s3://my-bucket/my/manifest.json",
                content_type="text/csv",
            ),
            [
                {
                    "channelName": "input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://my-bucket/my/manifest.json",
                        },
                    },
                    "contentType": "text/csv",
                }
            ],
        ),
        (
            {
                "local-input": "local/prefix",
                "s3-input": "s3://my-bucket/my/prefix-",
                "config-input": S3DataSourceConfig(
                    "s3://my-bucket/my/manifest.json",
                ),
            },
            [
                {
                    "channelName": "local-input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://default-bucket-name/jobs/job-name/"
                            "data/local-input/prefix",
                        },
                    },
                },
                {
                    "channelName": "s3-input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://my-bucket/my/prefix-",
                        },
                    },
                },
                {
                    "channelName": "config-input",
                    "dataSource": {
                        "s3DataSource": {
                            "s3Uri": "s3://my-bucket/my/manifest.json",
                        },
                    },
                },
            ],
        ),
    ),
)
def test_process_input_data(aws_session, input_data, input_data_configs):
    job_name = "job-name"
    assert _process_input_data(input_data, job_name, aws_session) == input_data_configs
