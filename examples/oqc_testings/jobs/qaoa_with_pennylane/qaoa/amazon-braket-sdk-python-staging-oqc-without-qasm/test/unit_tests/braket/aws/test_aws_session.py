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
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber

import braket._schemas as braket_schemas
import braket._sdk as braket_sdk
from braket.aws import AwsSession

TEST_S3_OBJ_CONTENTS = {
    "TaskMetadata": {
        "Id": "blah",
    }
}


@pytest.fixture
def boto_session():
    _boto_session = Mock()
    _boto_session.region_name = "us-west-2"
    return _boto_session


@pytest.fixture
def braket_client():
    _braket_client = Mock()
    _braket_client.meta.region_name = "us-west-2"
    return _braket_client


@pytest.fixture
def aws_session(boto_session, braket_client, account_id):
    _aws_session = AwsSession(boto_session=boto_session, braket_client=braket_client)

    _aws_session._sts = Mock()
    _aws_session._sts.get_caller_identity.return_value = {
        "Account": account_id,
    }

    _aws_session._s3 = Mock()
    return _aws_session


@pytest.fixture
def aws_explicit_session():
    _boto_session = Mock()
    _boto_session.region_name = "us-test-1"

    creds = Mock()
    creds.access_key = "access key"
    creds.secret_key = "secret key"
    creds.token = "token"
    creds.method = "explicit"
    _boto_session.get_credentials.return_value = creds

    _aws_session = Mock()
    _aws_session.boto_session = _boto_session
    _aws_session._default_bucket = "amazon-braket-us-test-1-00000000"
    _aws_session.default_bucket.return_value = _aws_session._default_bucket
    _aws_session._custom_default_bucket = False
    _aws_session.account_id = "00000000"
    _aws_session.region = "us-test-1"
    return _aws_session


@pytest.fixture
def account_id():
    return "000000000"


@pytest.fixture
def job_role_name():
    return "AmazonBraketJobsExecutionRole-134534514345"


@pytest.fixture
def job_role_arn(job_role_name):
    return f"arn:aws:iam::0000000000:role/{job_role_name}"


@pytest.fixture
def get_job_response():
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
        "instanceConfig": {
            "instanceCount": 1,
            "instanceType": "ml.m5.large",
            "volumeSizeInGb": 1,
        },
        "jobArn": "arn:aws:braket:us-west-2:875981177017:job/job-test-20210628140446",
        "jobName": "job-test-20210628140446",
        "outputDataConfig": {"s3Path": "s3://amazon-braket-jobs/job-path/output"},
        "roleArn": "arn:aws:iam::875981177017:role/AmazonBraketJobRole",
        "status": "RUNNING",
    }


@pytest.fixture
def resource_not_found_response():
    return {
        "Error": {
            "Code": "ResourceNotFoundException",
            "Message": "unit-test-error",
        }
    }


@pytest.fixture
def throttling_response():
    return {
        "Error": {
            "Code": "ThrottlingException",
            "Message": "unit-test-error",
        }
    }


def test_initializes_boto_client_if_required(boto_session):
    AwsSession(boto_session=boto_session)
    boto_session.client.assert_any_call("braket", config=None)


def test_user_supplied_braket_client():
    boto_session = Mock()
    boto_session.region_name = "foobar"
    braket_client = Mock()
    braket_client.meta.region_name = "foobar"
    aws_session = AwsSession(boto_session=boto_session, braket_client=braket_client)
    assert aws_session.braket_client == braket_client


def test_config(boto_session):
    config = Mock()
    AwsSession(boto_session=boto_session, config=config)
    boto_session.client.assert_any_call("braket", config=config)


def test_region():
    boto_region = "boto-region"
    braket_region = "braket-region"

    boto_session = Mock()
    boto_session.region_name = boto_region
    braket_client = Mock()
    braket_client.meta.region_name = braket_region

    assert (
        AwsSession(
            boto_session=boto_session,
        ).region
        == boto_region
    )

    assert (
        AwsSession(
            braket_client=braket_client,
        ).region
        == braket_region
    )

    regions_must_match = (
        "Boto Session region and Braket Client region must match and currently "
        "they do not: Boto Session region is 'boto-region', but "
        "Braket Client region is 'braket-region'."
    )
    with pytest.raises(ValueError, match=regions_must_match):
        AwsSession(
            boto_session=boto_session,
            braket_client=braket_client,
        )


def test_iam(aws_session):
    aws_session._iam = Mock()
    assert aws_session.iam_client
    aws_session.boto_session.client.assert_not_called()
    aws_session._iam = None
    assert aws_session.iam_client
    aws_session.boto_session.client.assert_called_with("iam", region_name="us-west-2")


def test_s3(aws_session):
    assert aws_session.s3_client
    aws_session.boto_session.client.assert_not_called()
    aws_session._s3 = None
    assert aws_session.s3_client
    aws_session.boto_session.client.assert_called_with("s3", region_name="us-west-2")


def test_sts(aws_session):
    assert aws_session.sts_client
    aws_session.boto_session.client.assert_not_called()
    aws_session._sts = None
    assert aws_session.sts_client
    aws_session.boto_session.client.assert_called_with("sts", region_name="us-west-2")


def test_logs(aws_session):
    aws_session._logs = Mock()
    assert aws_session.logs_client
    aws_session.boto_session.client.assert_not_called()
    aws_session._logs = None
    assert aws_session.logs_client
    aws_session.boto_session.client.assert_called_with("logs", region_name="us-west-2")


def test_ecr(aws_session):
    aws_session._ecr = Mock()
    assert aws_session.ecr_client
    aws_session.boto_session.client.assert_not_called()
    aws_session._ecr = None
    assert aws_session.ecr_client
    aws_session.boto_session.client.assert_called_with("ecr", region_name="us-west-2")


@patch("os.path.exists")
@pytest.mark.parametrize(
    "metadata_file_exists, initial_user_agent",
    [
        (True, None),
        (False, None),
        (True, ""),
        (False, ""),
        (True, "Boto3/1.17.18 Python/3.7.10"),
        (False, "Boto3/1.17.18 Python/3.7.10 exec-env/AWS_Lambda_python3.7"),
    ],
)
def test_populates_user_agent(os_path_exists_mock, metadata_file_exists, initial_user_agent):
    boto_session = Mock()
    boto_session.region_name = "foobar"
    braket_client = Mock()
    braket_client.meta.region_name = "foobar"
    braket_client._client_config.user_agent = initial_user_agent
    nbi_metadata_path = "/opt/ml/metadata/resource-metadata.json"
    os_path_exists_mock.return_value = metadata_file_exists
    aws_session = AwsSession(boto_session=boto_session, braket_client=braket_client)
    expected_user_agent = (
        f"{initial_user_agent} BraketSdk/{braket_sdk.__version__} "
        f"BraketSchemas/{braket_schemas.__version__} "
        f"NotebookInstance/{0 if metadata_file_exists else None}"
    )
    os_path_exists_mock.assert_called_with(nbi_metadata_path)
    assert aws_session.braket_client._client_config.user_agent == expected_user_agent


def test_retrieve_s3_object_body_success(boto_session):
    bucket_name = "braket-integ-test"
    filename = "tasks/test_task_1.json"

    mock_resource = Mock()
    boto_session.resource.return_value = mock_resource
    mock_object = Mock()
    mock_resource.Object.return_value = mock_object
    mock_body_object = Mock()
    mock_object.get.return_value = {"Body": mock_body_object}
    mock_read_object = Mock()
    mock_body_object.read.return_value = mock_read_object
    mock_read_object.decode.return_value = json.dumps(TEST_S3_OBJ_CONTENTS)
    json.dumps(TEST_S3_OBJ_CONTENTS)

    aws_session = AwsSession(boto_session=boto_session)
    return_value = aws_session.retrieve_s3_object_body(bucket_name, filename)
    assert return_value == json.dumps(TEST_S3_OBJ_CONTENTS)
    boto_session.resource.assert_called_with("s3", config=None)

    config = Mock()
    AwsSession(boto_session=boto_session, config=config).retrieve_s3_object_body(
        bucket_name, filename
    )
    boto_session.resource.assert_called_with("s3", config=config)


@pytest.mark.xfail(raises=ClientError)
def test_retrieve_s3_object_body_client_error(boto_session):
    bucket_name = "braket-integ-test"
    filename = "tasks/test_task_1.json"

    mock_resource = Mock()
    boto_session.resource.return_value = mock_resource
    mock_object = Mock()
    mock_resource.Object.return_value = mock_object
    mock_object.get.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "NoSuchKey"}}, "Operation"
    )
    aws_session = AwsSession(boto_session=boto_session)
    aws_session.retrieve_s3_object_body(bucket_name, filename)


def test_get_device(boto_session, braket_client):
    return_val = {"deviceArn": "arn1", "deviceName": "name1"}
    braket_client.get_device.return_value = return_val
    aws_session = AwsSession(boto_session=boto_session, braket_client=braket_client)
    metadata = aws_session.get_device("arn1")
    assert return_val == metadata


def test_cancel_quantum_task(aws_session):
    arn = "foo:bar:arn"
    aws_session.braket_client.cancel_quantum_task.return_value = {"quantumTaskArn": arn}

    assert aws_session.cancel_quantum_task(arn) is None
    aws_session.braket_client.cancel_quantum_task.assert_called_with(quantumTaskArn=arn)


def test_create_quantum_task(aws_session):
    arn = "foo:bar:arn"
    aws_session.braket_client.create_quantum_task.return_value = {"quantumTaskArn": arn}

    kwargs = {
        "backendArn": "arn:aws:us-west-2:abc:xyz:abc",
        "cwLogGroupArn": "arn:aws:us-west-2:abc:xyz:abc",
        "destinationUrl": "http://s3-us-west-2.amazonaws.com/task-output-bar-1/output.json",
        "program": {"ir": '{"instructions":[]}', "qubitCount": 4},
    }
    assert aws_session.create_quantum_task(**kwargs) == arn
    aws_session.braket_client.create_quantum_task.assert_called_with(**kwargs)


def test_create_quantum_task_with_job_token(aws_session):
    arn = "arn:aws:braket:us-west-2:1234567890:task/task-name"
    job_token = "arn:aws:braket:us-west-2:1234567890:job/job-name"
    aws_session.braket_client.create_quantum_task.return_value = {"quantumTaskArn": arn}

    kwargs = {
        "backendArn": "arn:aws:us-west-2:abc:xyz:abc",
        "cwLogGroupArn": "arn:aws:us-west-2:abc:xyz:abc",
        "destinationUrl": "http://s3-us-west-2.amazonaws.com/task-output-foo-1/output.json",
        "program": {"ir": '{"instructions":[]}', "qubitCount": 4},
    }
    with patch.dict(os.environ, {"AMZN_BRAKET_JOB_TOKEN": job_token}):
        assert aws_session.create_quantum_task(**kwargs) == arn
        kwargs.update({"jobToken": job_token})
        aws_session.braket_client.create_quantum_task.assert_called_with(**kwargs)


def test_get_quantum_task(aws_session):
    arn = "foo:bar:arn"
    return_value = {"quantumTaskArn": arn}
    aws_session.braket_client.get_quantum_task.return_value = return_value

    assert aws_session.get_quantum_task(arn) == return_value
    aws_session.braket_client.get_quantum_task.assert_called_with(quantumTaskArn=arn)


def test_get_quantum_task_retry(aws_session, throttling_response, resource_not_found_response):
    arn = "foo:bar:arn"
    return_value = {"quantumTaskArn": arn}

    aws_session.braket_client.get_quantum_task.side_effect = [
        ClientError(resource_not_found_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
        return_value,
    ]

    assert aws_session.get_quantum_task(arn) == return_value
    aws_session.braket_client.get_quantum_task.assert_called_with(quantumTaskArn=arn)
    assert aws_session.braket_client.get_quantum_task.call_count == 3


def test_get_quantum_task_fail_after_retries(
    aws_session, throttling_response, resource_not_found_response
):
    aws_session.braket_client.get_quantum_task.side_effect = [
        ClientError(resource_not_found_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
    ]

    with pytest.raises(ClientError):
        aws_session.get_quantum_task("some-arn")
    assert aws_session.braket_client.get_quantum_task.call_count == 3


def test_get_quantum_task_does_not_retry_other_exceptions(aws_session):
    exception_response = {
        "Error": {
            "Code": "SomeOtherException",
            "Message": "unit-test-error",
        }
    }

    aws_session.braket_client.get_quantum_task.side_effect = [
        ClientError(exception_response, "unit-test"),
    ]

    with pytest.raises(ClientError):
        aws_session.get_quantum_task("some-arn")
    assert aws_session.braket_client.get_quantum_task.call_count == 1


def test_get_job(aws_session, get_job_response):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"
    aws_session.braket_client.get_job.return_value = get_job_response

    assert aws_session.get_job(arn) == get_job_response
    aws_session.braket_client.get_job.assert_called_with(jobArn=arn)


def test_get_job_retry(
    aws_session, get_job_response, throttling_response, resource_not_found_response
):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"

    aws_session.braket_client.get_job.side_effect = [
        ClientError(resource_not_found_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
        get_job_response,
    ]

    assert aws_session.get_job(arn) == get_job_response
    aws_session.braket_client.get_job.assert_called_with(jobArn=arn)
    assert aws_session.braket_client.get_job.call_count == 3


def test_get_job_fail_after_retries(aws_session, throttling_response, resource_not_found_response):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"

    aws_session.braket_client.get_job.side_effect = [
        ClientError(resource_not_found_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
        ClientError(throttling_response, "unit-test"),
    ]

    with pytest.raises(ClientError):
        aws_session.get_job(arn)
    aws_session.braket_client.get_job.assert_called_with(jobArn=arn)
    assert aws_session.braket_client.get_job.call_count == 3


def test_get_job_does_not_retry_other_exceptions(aws_session):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"
    exception_response = {
        "Error": {
            "Code": "SomeOtherException",
            "Message": "unit-test-error",
        }
    }

    aws_session.braket_client.get_job.side_effect = [
        ClientError(exception_response, "unit-test"),
    ]

    with pytest.raises(ClientError):
        aws_session.get_job(arn)
    aws_session.braket_client.get_job.assert_called_with(jobArn=arn)
    assert aws_session.braket_client.get_job.call_count == 1


def test_cancel_job(aws_session):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"
    cancel_job_response = {
        "ResponseMetadata": {
            "RequestId": "857b0893-2073-4ad6-b828-744af8400dfe",
            "HTTPStatusCode": 200,
        },
        "cancellationStatus": "CANCELLING",
        "jobArn": "arn:aws:braket:us-west-2:1234567890:job/job-name",
    }
    aws_session.braket_client.cancel_job.return_value = cancel_job_response

    assert aws_session.cancel_job(arn) == cancel_job_response
    aws_session.braket_client.cancel_job.assert_called_with(jobArn=arn)


@pytest.mark.parametrize(
    "exception_type",
    [
        "ResourceNotFoundException",
        "ValidationException",
        "AccessDeniedException",
        "ThrottlingException",
        "InternalServiceException",
        "ConflictException",
    ],
)
def test_cancel_job_surfaces_errors(exception_type, aws_session):
    arn = "arn:aws:braket:us-west-2:1234567890:job/job-name"
    exception_response = {
        "Error": {
            "Code": "SomeOtherException",
            "Message": "unit-test-error",
        }
    }

    aws_session.braket_client.cancel_job.side_effect = [
        ClientError(exception_response, "unit-test"),
    ]

    with pytest.raises(ClientError):
        aws_session.cancel_job(arn)
    aws_session.braket_client.cancel_job.assert_called_with(jobArn=arn)
    assert aws_session.braket_client.cancel_job.call_count == 1


@pytest.mark.parametrize(
    "input,output",
    [
        (
            {},
            [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn2",
                    "deviceName": "name2",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "OFFLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn3",
                    "deviceName": "name3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname2",
                },
            ],
        ),
        (
            {"names": ["name1"]},
            [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
            ],
        ),
        (
            {"types": ["SIMULATOR"]},
            [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn2",
                    "deviceName": "name2",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "OFFLINE",
                    "providerName": "pname1",
                },
            ],
        ),
        (
            {"statuses": ["ONLINE"]},
            [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn3",
                    "deviceName": "name3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname2",
                },
            ],
        ),
        (
            {"provider_names": ["pname2"]},
            [
                {
                    "deviceArn": "arn3",
                    "deviceName": "name3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname2",
                },
            ],
        ),
        (
            {
                "provider_names": ["pname2"],
                "types": ["QPU"],
                "statuses": ["ONLINE"],
                "names": ["name3"],
            },
            [
                {
                    "deviceArn": "arn3",
                    "deviceName": "name3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname2",
                },
            ],
        ),
        (
            {
                "provider_names": ["pname1"],
                "types": ["SIMULATOR"],
                "statuses": ["ONLINE"],
            },
            [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
            ],
        ),
    ],
)
def test_search_devices(input, output, aws_session):
    return_value = [
        {
            "devices": [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn2",
                    "deviceName": "name2",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "OFFLINE",
                    "providerName": "pname1",
                },
                {
                    "deviceArn": "arn3",
                    "deviceName": "name3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname2",
                },
            ]
        }
    ]
    mock_paginator = Mock()
    mock_iterator = MagicMock()
    aws_session.braket_client.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = mock_iterator
    mock_iterator.__iter__.return_value = return_value

    assert aws_session.search_devices(**input) == output


def test_search_devices_arns(aws_session):
    return_value = [
        {
            "devices": [
                {
                    "deviceArn": "arn1",
                    "deviceName": "name1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "pname1",
                }
            ]
        }
    ]
    mock_paginator = Mock()
    mock_iterator = MagicMock()
    aws_session.braket_client.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = mock_iterator
    mock_iterator.__iter__.return_value = return_value

    assert aws_session.search_devices(arns=["arn1"]) == return_value[0]["devices"]
    mock_paginator.paginate.assert_called_with(
        filters=[
            {"name": "deviceArn", "values": ["arn1"]},
        ],
        PaginationConfig={"MaxItems": 100},
    )


def test_create_job(aws_session):
    arn = "foo:bar:arn"
    aws_session.braket_client.create_job.return_value = {"jobArn": arn}

    kwargs = {
        "jobName": "job-name",
        "roleArn": "role-arn",
        "algorithmSpecification": {
            "scriptModeConfig": {
                "entryPoint": "entry-point",
                "s3Uri": "s3-uri",
                "compressionType": "GZIP",
            }
        },
    }
    assert aws_session.create_job(**kwargs) == arn
    aws_session.braket_client.create_job.assert_called_with(**kwargs)


@pytest.mark.parametrize(
    "string, valid",
    (
        ("s3://bucket/key", True),
        ("S3://bucket/key", True),
        ("https://bucket-name-123.s3.us-west-2.amazonaws.com/key/with/dirs", True),
        ("https://bucket-name-123.S3.us-west-2.amazonaws.com/key/with/dirs", True),
        ("https://bucket-name-123.S3.us-west-2.amazonaws.com/", False),
        ("https://bucket-name-123.S3.us-west-2.amazonaws.com", False),
        ("https://S3.us-west-2.amazonaws.com", False),
        ("s3://bucket/", False),
        ("s3://bucket", False),
        ("s3://////", False),
        ("http://bucket/key", False),
        ("bucket/key", False),
    ),
)
def test_is_s3_uri(string, valid):
    assert AwsSession.is_s3_uri(string) == valid


@pytest.mark.parametrize(
    "uri, bucket, key",
    (
        (
            "s3://bucket-name-123/key/with/multiple/dirs",
            "bucket-name-123",
            "key/with/multiple/dirs",
        ),
        (
            "s3://bucket-name-123/key-with_one.dirs",
            "bucket-name-123",
            "key-with_one.dirs",
        ),
        (
            "https://bucket-name-123.s3.us-west-2.amazonaws.com/key/with/dirs",
            "bucket-name-123",
            "key/with/dirs",
        ),
        (
            "https://bucket-name-123.S3.us-west-2.amazonaws.com/key/with/dirs",
            "bucket-name-123",
            "key/with/dirs",
        ),
    ),
)
def test_parse_s3_uri(uri, bucket, key):
    assert bucket, key == AwsSession.parse_s3_uri(uri)


@pytest.mark.parametrize(
    "uri",
    (
        "s3://bucket.name-123/key-with_one.dirs",
        "http://bucket-name-123/key/with/multiple/dirs",
        "bucket-name-123/key/with/multiple/dirs",
        "s3://bucket-name-123/",
        "s3://bucket-name-123",
    ),
)
def test_parse_s3_uri_invalid(uri):
    with pytest.raises(ValueError, match=f"Not a valid S3 uri: {uri}"):
        AwsSession.parse_s3_uri(uri)


@pytest.mark.parametrize(
    "bucket, dirs",
    [
        ("bucket", ("d1", "d2", "d3")),
        ("bucket-123-braket", ("dir",)),
        pytest.param(
            "braket",
            (),
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
    ],
)
def test_construct_s3_uri(bucket, dirs):
    parsed_bucket, parsed_key = AwsSession.parse_s3_uri(AwsSession.construct_s3_uri(bucket, *dirs))
    assert parsed_bucket == bucket
    assert parsed_key == "/".join(dirs)


def test_get_default_jobs_role(aws_session, job_role_arn, job_role_name):
    iam_client = boto3.client("iam")
    with Stubber(iam_client) as stub:
        stub.add_response(
            "list_roles",
            {
                "Roles": [
                    {
                        "Arn": "arn:aws:iam::0000000000:role/nonJobsRole",
                        "RoleName": "nonJobsRole",
                        "Path": "/",
                        "RoleId": "nonJobsRole-213453451345-431513",
                        "CreateDate": time.time(),
                    }
                ]
                * 100,
                "IsTruncated": True,
                "Marker": "resp-marker",
            },
            {"PathPrefix": "/service-role/"},
        )
        stub.add_response(
            "list_roles",
            {
                "Roles": [
                    {
                        "Arn": job_role_arn,
                        "RoleName": job_role_name,
                        "Path": "/",
                        "RoleId": f"{job_role_name}-213453451345-431513",
                        "CreateDate": time.time(),
                    }
                ],
                "IsTruncated": False,
            },
            {"Marker": "resp-marker", "PathPrefix": "/service-role/"},
        )
        aws_session._iam = iam_client
        assert aws_session.get_default_jobs_role() == job_role_arn


def test_get_default_jobs_role_not_found(aws_session, job_role_arn, job_role_name):
    iam_client = boto3.client("iam")
    with Stubber(iam_client) as stub:
        stub.add_response(
            "list_roles",
            {
                "Roles": [
                    {
                        "Arn": "arn:aws:iam::0000000000:role/nonJobsRole",
                        "RoleName": "nonJobsRole",
                        "Path": "/",
                        "RoleId": "nonJobsRole-213453451345-431513",
                        "CreateDate": time.time(),
                    }
                ]
                * 100,
                "IsTruncated": True,
                "Marker": "resp-marker",
            },
            {"PathPrefix": "/service-role/"},
        )
        stub.add_response(
            "list_roles",
            {
                "Roles": [
                    {
                        "Arn": "arn:aws:iam::0000000000:role/nonJobsRole2",
                        "RoleName": "nonJobsRole2",
                        "Path": "/",
                        "RoleId": "nonJobsRole2-213453451345-431513",
                        "CreateDate": time.time(),
                    }
                ],
                "IsTruncated": False,
            },
            {"Marker": "resp-marker", "PathPrefix": "/service-role/"},
        )
        aws_session._iam = iam_client
        with pytest.raises(RuntimeError):
            aws_session.get_default_jobs_role()


def test_upload_to_s3(aws_session):
    filename = "file.txt"
    s3_uri = "s3://bucket-123/key"
    bucket, key = "bucket-123", "key"
    aws_session.upload_to_s3(filename, s3_uri)
    aws_session._s3.upload_file.assert_called_with(filename, bucket, key)


def test_upload_local_data(aws_session):
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("input-dir", "pref-dir", "sub-pref-dir").mkdir(parents=True)
        Path("input-dir", "not-pref-dir").mkdir()

        # these should all get uploaded
        Path("input-dir", "pref-dir", "sub-pref-dir", "very-nested.txt").touch()
        Path("input-dir", "pref-dir", "nested.txt").touch()
        Path("input-dir", "pref.txt").touch()
        Path("input-dir", "pref-and-more.txt").touch()

        # these should not
        Path("input-dir", "false-pref.txt").touch()
        Path("input-dir", "not-pref-dir", "pref-fake.txt").touch()

        aws_session.upload_to_s3 = Mock()
        aws_session.upload_local_data("input-dir/pref", "s3://bucket/pref")
        call_args = {args for args, kwargs in aws_session.upload_to_s3.call_args_list}
        assert call_args == {
            (
                str(Path("input-dir", "pref-dir", "sub-pref-dir", "very-nested.txt")),
                "s3://bucket/pref-dir/sub-pref-dir/very-nested.txt",
            ),
            (str(Path("input-dir", "pref-dir", "nested.txt")), "s3://bucket/pref-dir/nested.txt"),
            (str(Path("input-dir", "pref.txt")), "s3://bucket/pref.txt"),
            (str(Path("input-dir", "pref-and-more.txt")), "s3://bucket/pref-and-more.txt"),
        }
        os.chdir("..")


def test_upload_local_data_absolute(aws_session):
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "input-dir", "pref-dir", "sub-pref-dir").mkdir(parents=True)
        Path(temp_dir, "input-dir", "not-pref-dir").mkdir()

        # these should all get uploaded
        Path(temp_dir, "input-dir", "pref-dir", "sub-pref-dir", "very-nested.txt").touch()
        Path(temp_dir, "input-dir", "pref-dir", "nested.txt").touch()
        Path(temp_dir, "input-dir", "pref.txt").touch()
        Path(temp_dir, "input-dir", "pref-and-more.txt").touch()

        # these should not
        Path(temp_dir, "input-dir", "false-pref.txt").touch()
        Path(temp_dir, "input-dir", "not-pref-dir", "pref-fake.txt").touch()

        aws_session.upload_to_s3 = Mock()
        aws_session.upload_local_data(str(Path(temp_dir, "input-dir", "pref")), "s3://bucket/pref")
        call_args = {args for args, kwargs in aws_session.upload_to_s3.call_args_list}
        assert call_args == {
            (
                str(Path(temp_dir, "input-dir", "pref-dir", "sub-pref-dir", "very-nested.txt")),
                "s3://bucket/pref-dir/sub-pref-dir/very-nested.txt",
            ),
            (
                str(Path(temp_dir, "input-dir", "pref-dir", "nested.txt")),
                "s3://bucket/pref-dir/nested.txt",
            ),
            (str(Path(temp_dir, "input-dir", "pref.txt")), "s3://bucket/pref.txt"),
            (
                str(Path(temp_dir, "input-dir", "pref-and-more.txt")),
                "s3://bucket/pref-and-more.txt",
            ),
        }


def test_download_from_s3(aws_session):
    filename = "model.tar.gz"
    s3_uri = (
        "s3://amazon-braket-jobs/job-path/output/"
        "BraketJob-875981177017-job-test-20210628140446/output/model.tar.gz"
    )
    bucket, key = (
        "amazon-braket-jobs",
        "job-path/output/BraketJob-875981177017-job-test-20210628140446/output/model.tar.gz",
    )
    aws_session.download_from_s3(s3_uri, filename)
    aws_session._s3.download_file.assert_called_with(bucket, key, filename)


def test_copy_identical_s3(aws_session):
    s3_uri = "s3://bucket/key"
    aws_session.copy_s3_object(s3_uri, s3_uri)
    aws_session.boto_session.client.return_value.copy.assert_not_called()


def test_copy_s3(aws_session):
    source_s3_uri = "s3://here/now"
    dest_s3_uri = "s3://there/then"
    source_bucket, source_key = AwsSession.parse_s3_uri(source_s3_uri)
    dest_bucket, dest_key = AwsSession.parse_s3_uri(dest_s3_uri)
    aws_session.copy_s3_object(source_s3_uri, dest_s3_uri)
    aws_session._s3.copy.assert_called_with(
        {
            "Bucket": source_bucket,
            "Key": source_key,
        },
        dest_bucket,
        dest_key,
    )


def test_copy_identical_s3_directory(aws_session):
    s3_uri = "s3://bucket/prefix/"
    aws_session.copy_s3_directory(s3_uri, s3_uri)
    aws_session.boto_session.client.return_value.copy.assert_not_called()


def test_copy_s3_directory(aws_session):
    aws_session.list_keys = Mock(return_value=[f"now/key-{i}" for i in range(5)])
    source_s3_uri = "s3://here/now"
    dest_s3_uri = "s3://there/then"
    aws_session.copy_s3_directory(source_s3_uri, dest_s3_uri)
    for i in range(5):
        aws_session.s3_client.copy.assert_any_call(
            {
                "Bucket": "here",
                "Key": f"now/key-{i}",
            },
            "there",
            f"then/key-{i}",
        )


def test_list_keys(aws_session):
    bucket, prefix = "bucket", "prefix"
    aws_session.s3_client.list_objects_v2.side_effect = [
        {
            "IsTruncated": True,
            "Contents": [
                {"Key": "copy-test/copy.txt"},
                {"Key": "copy-test/copy2.txt"},
            ],
            "NextContinuationToken": "next-continuation-token",
        },
        {
            "IsTruncated": False,
            "Contents": [
                {"Key": "copy-test/nested/double-nested/double-nested.txt"},
                {"Key": "copy-test/nested/nested.txt"},
            ],
        },
    ]
    keys = aws_session.list_keys(bucket, prefix)
    assert keys == [
        "copy-test/copy.txt",
        "copy-test/copy2.txt",
        "copy-test/nested/double-nested/double-nested.txt",
        "copy-test/nested/nested.txt",
    ]


def test_default_bucket(aws_session, account_id):
    region = "test-region-0"
    aws_session.boto_session.region_name = region
    assert aws_session.default_bucket() == f"amazon-braket-{region}-{account_id}"


def test_default_bucket_given(aws_session):
    default_bucket = "default_bucket"
    aws_session._default_bucket = default_bucket
    assert aws_session.default_bucket() == default_bucket
    aws_session._s3.create_bucket.assert_not_called()


@patch.dict("os.environ", {"AMZN_BRAKET_OUT_S3_BUCKET": "default_bucket_env"})
def test_default_bucket_env_variable(boto_session, braket_client):
    aws_session = AwsSession(boto_session=boto_session, braket_client=braket_client)
    assert aws_session.default_bucket() == "default_bucket_env"


@pytest.mark.parametrize(
    "region",
    (
        "test-region-0",
        "us-east-1",
    ),
)
def test_create_s3_bucket_if_it_does_not_exist(aws_session, region, account_id):
    bucket = f"amazon-braket-{region}-{account_id}"
    aws_session._create_s3_bucket_if_it_does_not_exist(bucket, region)
    kwargs = {
        "Bucket": bucket,
        "CreateBucketConfiguration": {
            "LocationConstraint": region,
        },
    }
    if region == "us-east-1":
        del kwargs["CreateBucketConfiguration"]
    aws_session._s3.create_bucket.assert_called_with(**kwargs)
    aws_session._s3.put_public_access_block.assert_called_with(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )


@pytest.mark.parametrize(
    "error",
    (
        ClientError(
            {
                "Error": {
                    "Code": "BucketAlreadyOwnedByYou",
                    "Message": "Your previous request to create the named bucket succeeded "
                    "and you already own it.",
                }
            },
            "CreateBucket",
        ),
        ClientError(
            {
                "Error": {
                    "Code": "OperationAborted",
                    "Message": "A conflicting conditional operation is currently in progress "
                    "against this resource. Please try again.",
                }
            },
            "CreateBucket",
        ),
        pytest.param(
            ClientError(
                {
                    "Error": {
                        "Code": "OtherCode",
                        "Message": "This should fail properly.",
                    }
                },
                "CreateBucket",
            ),
            marks=pytest.mark.xfail(raises=ClientError, strict=True),
        ),
    ),
)
def test_create_s3_bucket_if_it_does_not_exist_error(aws_session, error, account_id):
    region = "test-region-0"
    bucket = f"amazon-braket-{region}-{account_id}"
    aws_session._s3.create_bucket.side_effect = error
    aws_session._create_s3_bucket_if_it_does_not_exist(bucket, region)


@pytest.mark.xfail(raises=ValueError)
def test_bucket_already_exists_for_another_account(aws_session):
    exception_response = {
        "Error": {
            "Code": "BucketAlreadyExists",
            "Message": "This should fail properly.",
        }
    }
    bucket_name, region = "some-bucket-123", "test-region"
    aws_session._s3.create_bucket.side_effect = ClientError(exception_response, "CreateBucket")
    aws_session._create_s3_bucket_if_it_does_not_exist(bucket_name, region)


@pytest.mark.parametrize(
    "limit, next_token",
    (
        (None, None),
        (10, None),
        (None, "next-token"),
        (10, "next-token"),
    ),
)
def test_describe_log_streams(aws_session, limit, next_token):
    aws_session._logs = Mock()

    log_group = "log_group"
    log_stream_prefix = "log_stream_prefix"

    describe_log_stream_args = {
        "logGroupName": log_group,
        "logStreamNamePrefix": log_stream_prefix,
        "orderBy": "LogStreamName",
    }

    if limit:
        describe_log_stream_args.update({"limit": limit})

    if next_token:
        describe_log_stream_args.update({"nextToken": next_token})

    aws_session.describe_log_streams(log_group, log_stream_prefix, limit, next_token)

    aws_session._logs.describe_log_streams.assert_called_with(**describe_log_stream_args)


@pytest.mark.parametrize(
    "next_token",
    (None, "next-token"),
)
def test_get_log_events(aws_session, next_token):
    aws_session._logs = Mock()

    log_group = "log_group"
    log_stream_name = "log_stream_name"
    start_time = "timestamp"
    start_from_head = True

    log_events_args = {
        "logGroupName": log_group,
        "logStreamName": log_stream_name,
        "startTime": start_time,
        "startFromHead": start_from_head,
    }

    if next_token:
        log_events_args.update({"nextToken": next_token})

    aws_session.get_log_events(log_group, log_stream_name, start_time, start_from_head, next_token)

    aws_session._logs.get_log_events.assert_called_with(**log_events_args)


@patch("boto3.Session")
def test_copy_session(boto_session_init, aws_session):
    boto_session_init.return_value = Mock()
    copied_session = AwsSession.copy_session(aws_session, "us-west-2")
    boto_session_init.assert_called_with(region_name="us-west-2")
    assert copied_session._default_bucket is None


@patch("boto3.Session")
def test_copy_explicit_session(boto_session_init, aws_explicit_session):
    boto_session_init.return_value = Mock()
    AwsSession.copy_session(aws_explicit_session, "us-west-2")
    boto_session_init.assert_called_with(
        aws_access_key_id="access key",
        aws_secret_access_key="secret key",
        aws_session_token="token",
        region_name="us-west-2",
    )


@patch("boto3.Session")
def test_copy_session_custom_default_bucket(mock_boto, aws_session):
    mock_boto.return_value.region_name = "us-test-1"
    aws_session._default_bucket = "my-own-default"
    aws_session._custom_default_bucket = True
    copied_session = AwsSession.copy_session(aws_session)
    assert copied_session._default_bucket == "my-own-default"
