import os
import boto3
import unittest.mock as mock
import braket.tracking
import matplotlib.pyplot as plt


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

    def set_search_devices_result(self, result):
        self._wrapper.boto_client.get_paginator.return_value.paginate.return_value = result

    def set_cancel_quantum_task_result(self, result):
        self._wrapper.boto_client.cancel_quantum_task.return_value = result

    def set_task_result_return(self, result):
        self._wrapper.task_result_mock.return_value = result


def load_json(name, file_path = None):
    if file_path:
        json_path = os.path.join(os.path.dirname(file_path), name)
    else:
        json_path = os.path.join(os.path.dirname(__file__), "default_data", name)
    with open(json_path, "r") as file:
        return file.read()


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

    def region_name(self, *args, **kwargs):
        return mock.Mock()

    def get_credentials(self, *args, **kwargs):
        return mock.Mock()


class AwsSessionMinWrapper(SessionWrapper):
    def __init__(self):
        super().__init__()
        import braket.aws.aws_session
        self.real_create_quantum_task = braket.aws.aws_session.AwsSession.create_quantum_task
        braket.aws.aws_session.AwsSession.create_quantum_task = self.create_quantum_task
        self.real_get_quantum_task = braket.aws.aws_session.AwsSession.get_quantum_task
        braket.aws.aws_session.AwsSession.get_quantum_task = self.get_quantum_task
        self.real_cancel_quantum_task = braket.aws.aws_session.AwsSession.cancel_quantum_task
        braket.aws.aws_session.AwsSession.cancel_quantum_task = self.cancel_quantum_task
        self.real_retrieve_s3_object_body = braket.aws.aws_session.AwsSession.retrieve_s3_object_body
        braket.aws.aws_session.AwsSession.retrieve_s3_object_body = self.retrieve_s3_object_body

    def create_quantum_task(self, **boto3_kwargs):
        return self.boto_client.create_quantum_task(boto3_kwargs)["quantumTaskArn"]

    def get_quantum_task(self, arn):
        return self.boto_client.get_quantum_task(arn)

    def cancel_quantum_task(self, arn):
        return self.boto_client.cancel_quantum_task(arn)

    def retrieve_s3_object_body(self, s3_bucket, s3_object_key):
        return self.task_result_mock.return_value

