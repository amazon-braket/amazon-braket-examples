import os
import boto3
import unittest.mock as mock
import braket.tracking
import matplotlib.pyplot as plt
import json
import braket.aws


plt.savefig = mock.Mock()


class Mocker:
    mock_level = "ALL"

    def __init__(self):
        self._wrapper = Boto3SessionAllWrapper() if Mocker.mock_level == "ALL" else AwsSessionMinWrapper()
        braket.tracking.Tracker = mock.Mock()
        tracker = braket.tracking.Tracker().start()
        tracker.qpu_tasks_cost.return_value = 0
        tracker.simulator_tasks_cost.return_value = 0

    def set_get_device_result(self, result):
        self._wrapper.boto_client.get_device.return_value = result

    def set_create_quantum_task_result(self, result):
        self._wrapper.boto_client.create_quantum_task.return_value = result

    def set_get_quantum_task_result(self, result):
        self._wrapper.boto_client.get_quantum_task.return_value = result

    def set_cancel_quantum_task_result(self, result):
        self._wrapper.boto_client.cancel_quantum_task.return_value = result

    def set_task_result_return(self, result):
        self._wrapper.task_result_mock.return_value = result

    def set_task_result_side_effect(self, side_effect):
        self._wrapper.task_result_mock.side_effect = side_effect

    def set_search_result(self, result):
        self._wrapper.boto_client.get_paginator.return_value.paginate.return_value = result

    def set_create_job_result(self, result):
        self._wrapper.boto_client.create_job.return_value = result

    def set_get_job_result(self, result):
        self._wrapper.boto_client.get_job.return_value = result

    def set_cancel_job_result(self, result):
        self._wrapper.boto_client.cancel_job.return_value = result

    def set_log_streams_result(self, result):
        self._wrapper.boto_client.describe_log_streams.return_value = result

    def set_start_query_result(self, result):
        self._wrapper.boto_client.start_query.return_value = result

    def set_get_query_results_result(self, result):
        self._wrapper.boto_client.get_query_results.return_value = result

    def set_list_objects_v2_result(self, result):
        self._wrapper.boto_client.list_objects_v2.return_value = result

    @property
    def region_name(self):
        return self._wrapper.region_name


def read_file(name, file_path = None):
    if file_path:
        json_path = os.path.join(os.path.dirname(file_path), name)
    else:
        json_path = os.path.join(os.path.dirname(__file__), "default_data", name)
    with open(json_path, "r") as file:
        return file.read()


def mock_default_device_calls(mocker):
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "deviceCapabilities" : read_file("default_capabilities.json")
    })
    mocker.set_create_quantum_task_result({
        "quantumTaskArn" : "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
    })
    mocker.set_get_quantum_task_result({
        "quantumTaskArn" : "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
        "status" : "COMPLETED",
        "outputS3Bucket" : "Test Bucket",
        "outputS3Directory" : "Test Directory",
        "shots": 10,
        "deviceArn": "Test Device Arn",
        "ResponseMetadata": {
            "HTTPHeaders": {
                "date": ""
            }
        }
    })
    mocker.set_task_result_return(read_file("default_results.json"))


def set_level(mock_level):
    Mocker.mock_level = mock_level


class SessionWrapper():
    def __init__(self):
        self.boto_client = mock.Mock()
        self.task_result_mock = mock.Mock()
        self.resource_mock = mock.Mock()

        return_mock = mock.Mock()
        return_mock.read.return_value.decode = self.task_result_mock
        self.resource_mock.Object.return_value.get.return_value = {
            "Body": return_mock
        }
        self.boto_client.get_caller_identity.return_value = {
            "Account": "TestAccount"
        }
        self.boto_client.meta.region_name = "us-west-2"
        self.boto_client.get_authorization_token.return_value = {
            "authorizationData" : [
                {
                    "authorizationToken" : "TestToken"
                }
            ]
        }


class Boto3SessionAllWrapper(SessionWrapper):
    def __init__(self):
        super().__init__()
        boto3.Session = self

    def __call__(self, *args, **kwargs):
        return self

    def client(self, *args, **kwargs):
        return self.boto_client

    def resource(self, *args, **kwargs):
        return self.resource_mock

    def profile_name(self, *args, **kwargs):
        return mock.Mock()

    def get_credentials(self, *args, **kwargs):
        return mock.Mock()

    @property
    def region_name(self):
        return "us-west-2"


class AwsSessionMinWrapper(SessionWrapper):
    def __init__(self):
        super().__init__()
        import braket.jobs.metrics_data.cwl_insights_metrics_fetcher as md
        AwsSessionFacade._wrapper = self
        AwsSessionFacade.real_get_device = braket.aws.aws_session.AwsSession.get_device
        braket.aws.aws_session.AwsSession.get_device = AwsSessionFacade.get_device
        AwsSessionFacade.real_create_quantum_task = braket.aws.aws_session.AwsSession.create_quantum_task
        braket.aws.aws_session.AwsSession.create_quantum_task = AwsSessionFacade.create_quantum_task
        AwsSessionFacade.real_get_quantum_task = braket.aws.aws_session.AwsSession.get_quantum_task
        braket.aws.aws_session.AwsSession.get_quantum_task = AwsSessionFacade.get_quantum_task
        AwsSessionFacade.real_cancel_quantum_task = braket.aws.aws_session.AwsSession.cancel_quantum_task
        braket.aws.aws_session.AwsSession.cancel_quantum_task = AwsSessionFacade.cancel_quantum_task
        AwsSessionFacade.real_retrieve_s3_object_body = braket.aws.aws_session.AwsSession.retrieve_s3_object_body
        braket.aws.aws_session.AwsSession.retrieve_s3_object_body = AwsSessionFacade.retrieve_s3_object_body
        braket.aws.aws_session.AwsSession.create_job = AwsSessionFacade.create_job
        braket.aws.aws_session.AwsSession.get_job = AwsSessionFacade.get_job
        braket.aws.aws_session.AwsSession.cancel_job = AwsSessionFacade.cancel_job
        braket.aws.aws_session.AwsSession.copy_s3_directory = AwsSessionFacade.copy_s3_directory
        md.CwlInsightsMetricsFetcher._get_metrics_results_sync = AwsSessionFacade.get_job_metrics
        braket.aws.aws_quantum_job.AwsQuantumJob._attempt_results_download = mock.Mock()
        AwsSessionMinWrapper.parse_device_config()

    @staticmethod
    def parse_device_config():
        mock_device_config_str = os.getenv("MOCK_DEVICE_CONFIG")
        AwsSessionFacade.mock_device_config = (
            json.loads(mock_device_config_str) if mock_device_config_str else {}
        )
        unsupported_device_config_str = os.getenv("UNSUPPORTED_DEVICE_CONFIG")
        AwsSessionFacade.unsupported_device_config = (
            set(json.loads(unsupported_device_config_str)) if unsupported_device_config_str else {}
        )

    @property
    def region_name(self):
        return boto3.session.Session().region_name


class AwsSessionFacade(braket.aws.AwsSession):
    created_task_arns = set()
    created_task_locations = set()

    def get_device(self, arn):
        device_name = arn.split("/")[-1]
        if device_name in AwsSessionFacade.unsupported_device_config:
            return AwsSessionFacade._wrapper.boto_client.get_device(arn)
        return AwsSessionFacade.real_get_device(self, arn)

    def create_quantum_task(self, **boto3_kwargs):
        if boto3_kwargs and boto3_kwargs["deviceArn"]:
            device_arn = boto3_kwargs["deviceArn"]
            device_name = device_arn.split("/")[-1]
            if device_name in AwsSessionFacade.unsupported_device_config:
                return AwsSessionFacade._wrapper.boto_client.create_quantum_task(boto3_kwargs)[
                    "quantumTaskArn"]
            if device_name in AwsSessionFacade.mock_device_config:
                device_sub = AwsSessionFacade.mock_device_config[device_name]
                if device_sub == "MOCK":
                    return AwsSessionFacade._wrapper.boto_client.create_quantum_task(boto3_kwargs)[
                        "quantumTaskArn"]
                else:
                    boto3_kwargs["deviceArn"] = device_sub
            task_arn = AwsSessionFacade.real_create_quantum_task(self, **boto3_kwargs)
            AwsSessionFacade.created_task_arns.add(task_arn)
            return task_arn
        return AwsSessionFacade._wrapper.boto_client.create_quantum_task(boto3_kwargs)[
            "quantumTaskArn"]

    def get_quantum_task(self, arn):
        if arn in AwsSessionFacade.created_task_arns:
            task_data = AwsSessionFacade.real_get_quantum_task(self, arn)
            AwsSessionFacade.created_task_locations.add(task_data["outputS3Directory"])
            return task_data
        return AwsSessionFacade._wrapper.boto_client.get_quantum_task(arn)

    def cancel_quantum_task(self, arn):
        if arn in AwsSessionFacade.created_task_arns:
            return AwsSessionFacade.real_cancel_quantum_task(self, arn)
        return AwsSessionFacade._wrapper.boto_client.cancel_quantum_task(arn)

    def create_job(self, **boto3_kwargs):
        return AwsSessionFacade._wrapper.boto_client.create_job(boto3_kwargs)["jobArn"]

    def get_job(self, arn):
        return AwsSessionFacade._wrapper.boto_client.get_job(arn)

    def cancel_job(self, arn):
        return AwsSessionFacade._wrapper.boto_client.cancel_job(arn)

    def copy_s3_directory(self, source_s3_path, destination_s3_path):
        return

    def retrieve_s3_object_body(self, s3_bucket, s3_object_key):
        location = s3_object_key[:s3_object_key.rindex("/")]
        if location in AwsSessionFacade.created_task_locations:
            return AwsSessionFacade.real_retrieve_s3_object_body(self, s3_bucket, s3_object_key)
        if AwsSessionFacade._wrapper.task_result_mock.side_effect is not None:
            return next(AwsSessionFacade._wrapper.task_result_mock.side_effect)
        return AwsSessionFacade._wrapper.task_result_mock.return_value

    def get_job_metrics(self, query_id):
        return AwsSessionFacade._wrapper.boto_client.get_query_results(query_id)["results"]

