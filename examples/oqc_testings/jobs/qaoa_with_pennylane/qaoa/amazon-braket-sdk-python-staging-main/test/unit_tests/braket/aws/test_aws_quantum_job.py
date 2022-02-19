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
import json
import logging
import os
import tarfile
import tempfile
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from braket.aws import AwsQuantumJob, AwsSession


@pytest.fixture
def aws_session(quantum_job_arn, job_region):
    _aws_session = Mock(spec=AwsSession)
    _aws_session.create_job.return_value = quantum_job_arn
    _aws_session.default_bucket.return_value = "default-bucket-name"
    _aws_session.get_default_jobs_role.return_value = "default-role-arn"
    _aws_session.construct_s3_uri.side_effect = (
        lambda bucket, *dirs: f"s3://{bucket}/{'/'.join(dirs)}"
    )

    def fake_copy_session(region):
        _aws_session.region = region
        return _aws_session

    _aws_session.copy_session.side_effect = fake_copy_session
    _aws_session.list_keys.return_value = ["job-path/output/model.tar.gz"]
    _aws_session.region = "us-test-1"

    _braket_client_mock = Mock(meta=Mock(region_name=job_region))
    _aws_session.braket_client = _braket_client_mock
    return _aws_session


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
                "instanceCount": 1,
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


@pytest.fixture
def generate_cancel_job_response():
    def _cancel_job_response(**kwargs):
        response = {
            "ResponseMetadata": {
                "RequestId": "857b0893-2073-4ad6-b828-744af8400dfe",
                "HTTPStatusCode": 200,
            },
            "cancellationStatus": "CANCELLING",
            "jobArn": "arn:aws:braket:us-west-2:875981177017:job/job-test-20210628140446",
        }
        response.update(kwargs)
        return response

    return _cancel_job_response


@pytest.fixture
def quantum_job_name():
    return "job-test-20210628140446"


@pytest.fixture
def job_region():
    return "us-west-2"


@pytest.fixture
def quantum_job_arn(quantum_job_name, job_region):
    return f"arn:aws:braket:{job_region}:875981177017:job/{quantum_job_name}"


@pytest.fixture
def quantum_job(quantum_job_arn, aws_session):
    return AwsQuantumJob(quantum_job_arn, aws_session)


def test_equality(quantum_job_arn, aws_session, job_region):
    new_aws_session = Mock(braket_client=Mock(meta=Mock(region_name=job_region)))
    quantum_job_1 = AwsQuantumJob(quantum_job_arn, aws_session)
    quantum_job_2 = AwsQuantumJob(quantum_job_arn, aws_session)
    quantum_job_3 = AwsQuantumJob(quantum_job_arn, new_aws_session)
    other_quantum_job = AwsQuantumJob(
        "arn:aws:braket:us-west-2:875981177017:job/other-job", aws_session
    )
    non_quantum_job = quantum_job_1.arn

    assert quantum_job_1 == quantum_job_2
    assert quantum_job_1 == quantum_job_3
    assert quantum_job_1 is not quantum_job_2
    assert quantum_job_1 is not quantum_job_3
    assert quantum_job_1 is quantum_job_1
    assert quantum_job_1 != other_quantum_job
    assert quantum_job_1 != non_quantum_job


def test_hash(quantum_job):
    assert hash(quantum_job) == hash(quantum_job.arn)


@pytest.mark.parametrize(
    "arn, expected_region",
    [
        ("arn:aws:braket:us-west-2:875981177017:job/job-name", "us-west-2"),
        ("arn:aws:braket:us-west-1:1234567890:job/job-name", "us-west-1"),
    ],
)
@patch("braket.aws.aws_quantum_job.boto3.Session")
@patch("braket.aws.aws_quantum_job.AwsSession")
def test_quantum_job_constructor_default_session(
    aws_session_mock, mock_session, arn, expected_region
):
    mock_boto_session = Mock()
    aws_session_mock.return_value = Mock()
    mock_session.return_value = mock_boto_session
    job = AwsQuantumJob(arn)
    mock_session.assert_called_with(region_name=expected_region)
    aws_session_mock.assert_called_with(boto_session=mock_boto_session)
    assert job.arn == arn
    assert job._aws_session == aws_session_mock.return_value


@pytest.mark.xfail(raises=ValueError)
def test_quantum_job_constructor_invalid_region(aws_session):
    arn = "arn:aws:braket:unknown-region:875981177017:job/quantum_job_name"
    AwsQuantumJob(arn, aws_session)


@patch("braket.aws.aws_quantum_job.boto3.Session")
def test_quantum_job_constructor_explicit_session(mock_session, quantum_job_arn, job_region):
    aws_session_mock = Mock(braket_client=Mock(meta=Mock(region_name=job_region)))
    job = AwsQuantumJob(quantum_job_arn, aws_session_mock)
    assert job._aws_session == aws_session_mock
    assert job.arn == quantum_job_arn
    mock_session.assert_not_called()


def test_metadata(quantum_job, aws_session, generate_get_job_response, quantum_job_arn):
    get_job_response_running = generate_get_job_response(status="RUNNING")
    aws_session.get_job.return_value = get_job_response_running
    assert quantum_job.metadata() == get_job_response_running
    aws_session.get_job.assert_called_with(quantum_job_arn)

    get_job_response_completed = generate_get_job_response(status="COMPLETED")
    aws_session.get_job.return_value = get_job_response_completed
    assert quantum_job.metadata() == get_job_response_completed
    aws_session.get_job.assert_called_with(quantum_job_arn)
    assert aws_session.get_job.call_count == 2


def test_metadata_caching(quantum_job, aws_session, generate_get_job_response, quantum_job_arn):
    get_job_response_running = generate_get_job_response(status="RUNNING")
    aws_session.get_job.return_value = get_job_response_running
    assert quantum_job.metadata(True) == get_job_response_running

    get_job_response_completed = generate_get_job_response(status="COMPLETED")
    aws_session.get_job.return_value = get_job_response_completed
    assert quantum_job.metadata(True) == get_job_response_running
    aws_session.get_job.assert_called_with(quantum_job_arn)
    assert aws_session.get_job.call_count == 1


def test_state(quantum_job, aws_session, generate_get_job_response, quantum_job_arn):
    state_1 = "RUNNING"
    get_job_response_running = generate_get_job_response(status=state_1)
    aws_session.get_job.return_value = get_job_response_running
    assert quantum_job.state() == state_1
    aws_session.get_job.assert_called_with(quantum_job_arn)

    state_2 = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state_2)
    aws_session.get_job.return_value = get_job_response_completed
    assert quantum_job.state() == state_2
    aws_session.get_job.assert_called_with(quantum_job_arn)
    assert aws_session.get_job.call_count == 2


def test_state_caching(quantum_job, aws_session, generate_get_job_response, quantum_job_arn):
    state_1 = "RUNNING"
    get_job_response_running = generate_get_job_response(status=state_1)
    aws_session.get_job.return_value = get_job_response_running
    assert quantum_job.state(True) == state_1

    state_2 = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state_2)
    aws_session.get_job.return_value = get_job_response_completed
    assert quantum_job.state(True) == state_1
    aws_session.get_job.assert_called_with(quantum_job_arn)
    assert aws_session.get_job.call_count == 1


@pytest.fixture()
def result_setup(quantum_job_name):
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        file_path = "results.json"

        with open(file_path, "w") as write_file:
            write_file.write(
                json.dumps(
                    {
                        "braketSchemaHeader": {
                            "name": "braket.jobs_data.persisted_job_data",
                            "version": "1",
                        },
                        "dataDictionary": {"converged": True, "energy": -0.2},
                        "dataFormat": "plaintext",
                    }
                )
            )

        with tarfile.open("model.tar.gz", "w:gz") as tar:
            tar.add(file_path, arcname=os.path.basename(file_path))

        yield

        result_dir = f"{os.getcwd()}/{quantum_job_name}"

        if os.path.exists(result_dir):
            os.remove(f"{result_dir}/results.json")
            os.rmdir(f"{result_dir}/")

        if os.path.isfile("model.tar.gz"):
            os.remove("model.tar.gz")

        os.chdir("..")


@pytest.mark.parametrize("state", AwsQuantumJob.TERMINAL_STATES)
def test_results_when_job_is_completed(
    quantum_job, aws_session, generate_get_job_response, result_setup, state
):
    expected_saved_data = {"converged": True, "energy": -0.2}

    get_job_response_completed = generate_get_job_response(status=state)
    quantum_job._aws_session.get_job.return_value = get_job_response_completed
    actual_data = quantum_job.result()

    job_metadata = quantum_job.metadata(True)
    s3_path = job_metadata["outputDataConfig"]["s3Path"]

    output_bucket_uri = f"{s3_path}/output/model.tar.gz"
    quantum_job._aws_session.download_from_s3.assert_called_with(
        s3_uri=output_bucket_uri, filename="model.tar.gz"
    )
    assert actual_data == expected_saved_data


def test_download_result_when_job_is_running(
    quantum_job, aws_session, generate_get_job_response, result_setup
):
    poll_timeout_seconds, poll_interval_seconds, state = 1, 0.5, "RUNNING"
    get_job_response_completed = generate_get_job_response(status=state)
    aws_session.get_job.return_value = get_job_response_completed
    job_metadata = quantum_job.metadata(True)

    with pytest.raises(
        TimeoutError,
        match=f"{job_metadata['jobName']}: Polling for job completion "
        f"timed out after {poll_timeout_seconds} seconds.",
    ):
        quantum_job.download_result(
            poll_timeout_seconds=poll_timeout_seconds, poll_interval_seconds=poll_interval_seconds
        )


def test_download_result_when_extract_path_not_provided(
    quantum_job, generate_get_job_response, aws_session, result_setup
):
    state = "COMPLETED"
    expected_saved_data = {"converged": True, "energy": -0.2}
    get_job_response_completed = generate_get_job_response(status=state)
    quantum_job._aws_session.get_job.return_value = get_job_response_completed
    job_metadata = quantum_job.metadata(True)
    job_name = job_metadata["jobName"]
    quantum_job.download_result()

    with open(f"{job_name}/results.json", "r") as file:
        actual_data = json.loads(file.read())["dataDictionary"]
        assert expected_saved_data == actual_data


def test_download_result_when_extract_path_provided(
    quantum_job, generate_get_job_response, aws_session, result_setup
):
    expected_saved_data = {"converged": True, "energy": -0.2}
    state = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state)
    aws_session.get_job.return_value = get_job_response_completed
    job_metadata = quantum_job.metadata(True)
    job_name = job_metadata["jobName"]

    with tempfile.TemporaryDirectory() as temp_dir:
        quantum_job.download_result(temp_dir)

        with open(f"{temp_dir}/{job_name}/results.json", "r") as file:
            actual_data = json.loads(file.read())["dataDictionary"]
            assert expected_saved_data == actual_data


def test_empty_dict_returned_when_result_not_saved(
    quantum_job, generate_get_job_response, aws_session
):
    state = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state)
    aws_session.get_job.return_value = get_job_response_completed

    exception_response = {
        "Error": {
            "Code": "404",
            "Message": "Not Found",
        }
    }
    quantum_job._aws_session.download_from_s3 = Mock(
        side_effect=ClientError(exception_response, "HeadObject")
    )
    assert quantum_job.result() == {}


def test_results_not_in_s3_for_download(quantum_job, generate_get_job_response, aws_session):
    state = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state)
    aws_session.get_job.return_value = get_job_response_completed
    job_metadata = quantum_job.metadata(True)
    output_s3_path = job_metadata["outputDataConfig"]["s3Path"]

    error_message = f"Error retrieving results, could not find results at '{output_s3_path}"

    exception_response = {
        "Error": {
            "Code": "404",
            "Message": "Not Found",
        }
    }
    quantum_job._aws_session.download_from_s3 = Mock(
        side_effect=ClientError(exception_response, "HeadObject")
    )
    with pytest.raises(ClientError, match=error_message):
        quantum_job.download_result()


def test_results_raises_error_for_non_404_errors(
    quantum_job, generate_get_job_response, aws_session
):
    state = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state)
    aws_session.get_job.return_value = get_job_response_completed

    error = "An error occurred \\(402\\) when calling the SomeObject operation: Something"

    exception_response = {
        "Error": {
            "Code": "402",
            "Message": "Something",
        }
    }
    quantum_job._aws_session.download_from_s3 = Mock(
        side_effect=ClientError(exception_response, "SomeObject")
    )
    with pytest.raises(ClientError, match=error):
        quantum_job.result()


@patch("braket.aws.aws_quantum_job.AwsQuantumJob.download_result")
def test_results_json_file_not_in_tar(
    result_download, quantum_job, aws_session, generate_get_job_response
):
    state = "COMPLETED"
    get_job_response_completed = generate_get_job_response(status=state)
    quantum_job._aws_session.get_job.return_value = get_job_response_completed
    assert quantum_job.result() == {}


@pytest.fixture
def entry_point():
    return "test-source-module.entry_point:func"


@pytest.fixture
def bucket():
    return "braket-region-id"


@pytest.fixture(
    params=[
        None,
        "aws.location/custom-jobs:tag.1.2.3",
        "other.uri/custom-name:tag",
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
def source_module(request, bucket, s3_prefix):
    if request.param == "local_source":
        return "test-source-module"
    elif request.param == "s3_source":
        return AwsSession.construct_s3_uri(bucket, "test-source-prefix", "source.tar.gz")


@pytest.fixture
def role_arn():
    return "arn:aws:iam::0000000000:role/AmazonBraketInternalSLR"


@pytest.fixture(
    params=[
        "arn:aws:braket:us-test-1::device/qpu/test/device-name",
        "arn:aws:braket:::device/qpu/test/device-name",
    ]
)
def device_arn(request):
    return request.param


@pytest.fixture
def prepare_job_args(aws_session, device_arn):
    return {
        "device": device_arn,
        "source_module": Mock(),
        "entry_point": Mock(),
        "image_uri": Mock(),
        "job_name": Mock(),
        "code_location": Mock(),
        "role_arn": Mock(),
        "hyperparameters": Mock(),
        "input_data": Mock(),
        "instance_config": Mock(),
        "stopping_condition": Mock(),
        "output_data_config": Mock(),
        "copy_checkpoints_from_job": Mock(),
        "checkpoint_config": Mock(),
        "aws_session": aws_session,
        "tags": Mock(),
    }


def test_str(quantum_job):
    expected = f"AwsQuantumJob('arn':'{quantum_job.arn}')"
    assert str(quantum_job) == expected


def test_arn(quantum_job_arn, aws_session):
    quantum_job = AwsQuantumJob(quantum_job_arn, aws_session)
    assert quantum_job.arn == quantum_job_arn


def test_name(quantum_job_arn, quantum_job_name, aws_session):
    quantum_job = AwsQuantumJob(quantum_job_arn, aws_session)
    assert quantum_job.name == quantum_job_name


@pytest.mark.xfail(raises=AttributeError)
def test_no_arn_setter(quantum_job):
    quantum_job.arn = 123


@pytest.mark.parametrize("wait_until_complete", [True, False])
@patch("braket.aws.aws_quantum_job.AwsQuantumJob.logs")
@patch("braket.aws.aws_quantum_job.prepare_quantum_job")
def test_create_job(
    mock_prepare_quantum_job,
    mock_logs,
    aws_session,
    prepare_job_args,
    quantum_job_arn,
    wait_until_complete,
):
    test_response_args = {"testArgs": "MyTestArg"}
    mock_prepare_quantum_job.return_value = test_response_args
    job = AwsQuantumJob.create(wait_until_complete=wait_until_complete, **prepare_job_args)
    mock_prepare_quantum_job.assert_called_with(**prepare_job_args)
    aws_session.create_job.assert_called_with(**test_response_args)
    if wait_until_complete:
        mock_logs.assert_called_once()
    else:
        mock_logs.assert_not_called()
    assert job.arn == quantum_job_arn


def test_create_fake_arg():
    unexpected_kwarg = "create\\(\\) got an unexpected keyword argument 'fake_arg'"
    with pytest.raises(TypeError, match=unexpected_kwarg):
        AwsQuantumJob.create(
            device="device",
            source_module="source",
            fake_arg="fake_value",
        )


def test_cancel_job(quantum_job_arn, aws_session, generate_cancel_job_response):
    cancellation_status = "CANCELLING"
    aws_session.cancel_job.return_value = generate_cancel_job_response(
        cancellationStatus=cancellation_status
    )
    quantum_job = AwsQuantumJob(quantum_job_arn, aws_session)
    status = quantum_job.cancel()
    aws_session.cancel_job.assert_called_with(quantum_job_arn)
    assert status == cancellation_status


@pytest.mark.xfail(raises=ClientError)
def test_cancel_job_surfaces_exception(quantum_job, aws_session):
    exception_response = {
        "Error": {
            "Code": "ValidationException",
            "Message": "unit-test-error",
        }
    }
    aws_session.cancel_job.side_effect = ClientError(exception_response, "cancel_job")
    quantum_job.cancel()


@pytest.mark.parametrize(
    "generate_get_job_response_kwargs",
    [
        {
            "status": "RUNNING",
        },
        {
            "status": "COMPLETED",
        },
        {
            "status": "COMPLETED",
            "startedAt": datetime.datetime(2021, 1, 1, 1, 0, 0, 0),
        },
        {"status": "COMPLETED", "endedAt": datetime.datetime(2021, 1, 1, 1, 0, 0, 0)},
        {
            "status": "COMPLETED",
            "startedAt": datetime.datetime(2021, 1, 1, 1, 0, 0, 0),
            "endedAt": datetime.datetime(2021, 1, 1, 1, 0, 0, 0),
        },
    ],
)
@patch(
    "braket.jobs.metrics_data.cwl_insights_metrics_fetcher."
    "CwlInsightsMetricsFetcher.get_metrics_for_job"
)
def test_metrics(
    metrics_fetcher_mock,
    quantum_job,
    aws_session,
    generate_get_job_response,
    generate_get_job_response_kwargs,
):
    get_job_response_running = generate_get_job_response(**generate_get_job_response_kwargs)
    aws_session.get_job.return_value = get_job_response_running

    expected_metrics = {"Test": [1]}
    metrics_fetcher_mock.return_value = expected_metrics
    metrics = quantum_job.metrics()
    assert metrics == expected_metrics


@pytest.fixture
def log_stream_responses():
    return (
        ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "This shouldn't get raised...",
                }
            },
            "DescribeLogStreams",
        ),
        {"logStreams": []},
        {"logStreams": [{"logStreamName": "stream-1"}]},
    )


@pytest.fixture
def log_events_responses():
    return (
        {"nextForwardToken": None, "events": [{"timestamp": 1, "message": "hi there #1"}]},
        {"nextForwardToken": None, "events": []},
        {
            "nextForwardToken": None,
            "events": [
                {"timestamp": 1, "message": "hi there #1"},
                {"timestamp": 2, "message": "hi there #2"},
            ],
        },
        {"nextForwardToken": None, "events": []},
        {
            "nextForwardToken": None,
            "events": [
                {"timestamp": 2, "message": "hi there #2"},
                {"timestamp": 2, "message": "hi there #2a"},
                {"timestamp": 3, "message": "hi there #3"},
            ],
        },
        {"nextForwardToken": None, "events": []},
    )


def test_logs(
    quantum_job,
    generate_get_job_response,
    log_events_responses,
    log_stream_responses,
    capsys,
):
    quantum_job._aws_session.get_job.side_effect = (
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="COMPLETED"),
    )
    quantum_job._aws_session.describe_log_streams.side_effect = log_stream_responses
    quantum_job._aws_session.get_log_events.side_effect = log_events_responses

    quantum_job.logs(wait=True, poll_interval_seconds=0)

    captured = capsys.readouterr()
    assert captured.out == "\n".join(
        (
            "..",
            "hi there #1",
            "hi there #2",
            "hi there #2a",
            "hi there #3",
            "",
        )
    )


@patch.dict("os.environ", {"JPY_PARENT_PID": "True"})
def test_logs_multiple_instances(
    quantum_job,
    generate_get_job_response,
    log_events_responses,
    log_stream_responses,
    capsys,
):
    quantum_job._aws_session.get_job.side_effect = (
        generate_get_job_response(status="RUNNING", instanceConfig={"instanceCount": 2}),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="COMPLETED"),
    )
    log_stream_responses[-1]["logStreams"].append({"logStreamName": "stream-2"})
    quantum_job._aws_session.describe_log_streams.side_effect = log_stream_responses

    event_counts = {
        "stream-1": 0,
        "stream-2": 0,
    }

    def get_log_events(log_group, log_stream, start_time, start_from_head, next_token):
        log_events_dict = {
            "stream-1": log_events_responses,
            "stream-2": log_events_responses,
        }
        log_events_dict["stream-1"] += (
            {
                "nextForwardToken": None,
                "events": [],
            },
            {
                "nextForwardToken": None,
                "events": [],
            },
        )
        log_events_dict["stream-2"] += (
            {
                "nextForwardToken": None,
                "events": [
                    {"timestamp": 3, "message": "hi there #3"},
                    {"timestamp": 4, "message": "hi there #4"},
                ],
            },
            {
                "nextForwardToken": None,
                "events": [],
            },
        )
        event_counts[log_stream] += 1
        return log_events_dict[log_stream][event_counts[log_stream]]

    quantum_job._aws_session.get_log_events.side_effect = get_log_events

    quantum_job.logs(wait=True, poll_interval_seconds=0)

    captured = capsys.readouterr()
    assert captured.out == "\n".join(
        (
            "..",
            "\x1b[34mhi there #1\x1b[0m",
            "\x1b[35mhi there #1\x1b[0m",
            "\x1b[34mhi there #2\x1b[0m",
            "\x1b[35mhi there #2\x1b[0m",
            "\x1b[34mhi there #2a\x1b[0m",
            "\x1b[35mhi there #2a\x1b[0m",
            "\x1b[34mhi there #3\x1b[0m",
            "\x1b[35mhi there #3\x1b[0m",
            "\x1b[35mhi there #4\x1b[0m",
            "",
        )
    )


def test_logs_error(quantum_job, generate_get_job_response, capsys):
    quantum_job._aws_session.get_job.side_effect = (
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="RUNNING"),
        generate_get_job_response(status="COMPLETED"),
    )
    quantum_job._aws_session.describe_log_streams.side_effect = (
        ClientError(
            {
                "Error": {
                    "Code": "UnknownCode",
                    "Message": "Some error message",
                }
            },
            "DescribeLogStreams",
        ),
    )

    with pytest.raises(ClientError, match="Some error message"):
        quantum_job.logs(wait=True, poll_interval_seconds=0)


def test_initialize_session_for_valid_non_regional_device(aws_session, caplog):
    device_arn = "arn:aws:braket:::device/qpu/test/device-name"
    first_region = aws_session.region
    logger = logging.getLogger(__name__)

    aws_session.get_device.side_effect = [
        ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                }
            },
            "getDevice",
        ),
        ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                }
            },
            "getDevice",
        ),
        device_arn,
    ]

    caplog.set_level(logging.INFO)
    AwsQuantumJob._initialize_session(aws_session, device_arn, logger)

    assert f"Changed session region from '{first_region}' to '{aws_session.region}'" in caplog.text


def test_initialize_session_for_valid_regional_device(aws_session, caplog):
    device_arn = f"arn:aws:braket:{aws_session.region}::device/qpu/test/device-name"
    logger = logging.getLogger(__name__)
    aws_session.get_device.return_value = device_arn
    caplog.set_level(logging.INFO)
    AwsQuantumJob._initialize_session(aws_session, device_arn, logger)
    assert not caplog.text


@pytest.mark.parametrize(
    "get_device_side_effect, expected_exception",
    [
        (
            [
                ClientError(
                    {
                        "Error": {
                            "Code": "ResourceNotFoundException",
                        }
                    },
                    "getDevice",
                )
            ],
            ValueError,
        ),
        (
            [
                ClientError(
                    {
                        "Error": {
                            "Code": "ThrottlingException",
                        }
                    },
                    "getDevice",
                )
            ],
            ClientError,
        ),
    ],
)
def test_regional_device_raises_error(
    get_device_side_effect, expected_exception, aws_session, caplog
):
    device_arn = f"arn:aws:braket:{aws_session.region}::device/qpu/test/device-name"
    aws_session.get_device.side_effect = get_device_side_effect
    logger = logging.getLogger(__name__)
    caplog.set_level(logging.INFO)
    with pytest.raises(expected_exception):
        AwsQuantumJob._initialize_session(aws_session, device_arn, logger)
        aws_session.get_device.assert_called_with(device_arn)
        assert not caplog.text


def test_regional_device_switches(aws_session, caplog):
    original_region = aws_session.region
    device_region = "us-east-1"
    device_arn = f"arn:aws:braket:{device_region}::device/qpu/test/device-name"
    mock_session = Mock()
    mock_session.get_device.side_effect = device_arn
    aws_session.copy_session.side_effect = [mock_session]
    logger = logging.getLogger(__name__)
    caplog.set_level(logging.INFO)

    assert mock_session == AwsQuantumJob._initialize_session(aws_session, device_arn, logger)

    aws_session.copy_session.assert_called_with(region=device_region)
    mock_session.get_device.assert_called_with(device_arn)
    assert f"Changed session region from '{original_region}' to '{device_region}'" in caplog.text


def test_initialize_session_for_invalid_device(aws_session, device_arn):
    logger = logging.getLogger(__name__)
    aws_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
            }
        },
        "getDevice",
    )

    device_not_found = f"'{device_arn}' not found."
    with pytest.raises(ValueError, match=device_not_found):
        AwsQuantumJob._initialize_session(aws_session, device_arn, logger)


def test_no_region_routing_simulator(aws_session):
    logger = logging.getLogger(__name__)

    aws_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
            }
        },
        "getDevice",
    )

    device_arn = "arn:aws:braket:::device/simulator/test/device-name"
    device_not_found = f"Simulator '{device_arn}' not found in 'us-test-1'"
    with pytest.raises(ValueError, match=device_not_found):
        AwsQuantumJob._initialize_session(aws_session, device_arn, logger)


def test_exception_in_credentials_session_region(device_arn, aws_session):
    logger = logging.getLogger(__name__)

    aws_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "SomeOtherErrorMessage",
            }
        },
        "getDevice",
    )

    error_message = (
        "An error occurred \\(SomeOtherErrorMessage\\) "
        "when calling the getDevice operation: Unknown"
    )
    with pytest.raises(ClientError, match=error_message):
        AwsQuantumJob._initialize_session(aws_session, device_arn, logger)


def test_exceptions_in_all_device_regions(aws_session):
    device_arn = "arn:aws:braket:::device/qpu/test/device-name"
    logger = logging.getLogger(__name__)

    aws_session.get_device.side_effect = [
        ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                }
            },
            "getDevice",
        ),
        ClientError(
            {
                "Error": {
                    "Code": "SomeOtherErrorMessage",
                }
            },
            "getDevice",
        ),
    ]

    error_message = (
        "An error occurred \\(SomeOtherErrorMessage\\) "
        "when calling the getDevice operation: Unknown"
    )
    with pytest.raises(ClientError, match=error_message):
        AwsQuantumJob._initialize_session(aws_session, device_arn, logger)
