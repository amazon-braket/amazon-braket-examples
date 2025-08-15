import json
import os
import sys
import tarfile
from itertools import cycle
from unittest import mock

import boto3
import matplotlib.pyplot as plt

import braket.aws
import braket.tracking
from braket.jobs.serialization import serialize_values
from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

plt.savefig = mock.Mock()


class Mocker:
    mock_level = "ALL"

    def __init__(self):
        self._wrapper = (
            Boto3SessionAllWrapper() if Mocker.mock_level == "ALL" else AwsSessionMinWrapper()
        )
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

    def set_create_job_side_effect(self, side_effect):
        self._wrapper.boto_client.create_job.side_effect = side_effect

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

    def set_batch_get_image_side_effect(self, side_effect):
        self._wrapper.boto_client.batch_get_image.side_effect = side_effect

    def set_program_set_result_path(self, mock_result_path):
        """Set the base path for program set mock data files."""
        AwsSessionFacade.program_set_mock_path = mock_result_path
        self._wrapper._program_set_mock_path = mock_result_path

    @property
    def region_name(self):
        return self._wrapper.region_name


def read_file(name, file_path=None):
    if file_path:
        json_path = os.path.join(os.path.dirname(file_path), name)
    else:
        json_path = os.path.join(os.path.dirname(__file__), "default_data", name)
    with open(json_path, "r") as file:
        return file.read()


def mock_default_device_calls(mocker):
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": read_file("default_capabilities.json"),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "13", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        },
    )
    mocker.set_create_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
        },
    )
    mocker.set_get_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
            "status": "COMPLETED",
            "outputS3Bucket": "Test Bucket",
            "outputS3Directory": "Test Directory",
            "shots": 10,
            "deviceArn": "Test Device Arn",
            "queueInfo": {
                "queue": "QUANTUM_TASKS_QUEUE",
                "position": "2",
                "queuePriority": "Normal",
            },
            "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
        },
    )
    mocker.set_task_result_return(read_file("default_results.json"))


def mock_default_device_program_set_calls(mocker):
    """Set up default device calls with program set support."""
    # Set up device with program set capabilities
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": read_file("default_capabilities_with_programset.json"),
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "13", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        },
    )
    
    # Set up standard quantum task mocking
    mocker.set_create_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
        },
    )
    mocker.set_get_quantum_task_result(
        {
            "quantumTaskArn": "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
            "status": "COMPLETED",
            "outputS3Bucket": "Test Bucket",
            "outputS3Directory": "Test Directory",
            "shots": 10,
            "deviceArn": "Test Device Arn",
            "queueInfo": {
                "queue": "QUANTUM_TASKS_QUEUE",
                "position": "2",
                "queuePriority": "Normal",
            },
            "ResponseMetadata": {"HTTPHeaders": {"date": ""}},
        },
    )
    
    # Set up program set mocking using default test data
    default_data_dir = os.path.join(os.path.dirname(__file__), "default_data")
    program_set_data_path = os.path.join(default_data_dir, "default_program_set_results")
    mock_program_set_calls(mocker, base_path=program_set_data_path)


def mock_default_job_calls(mocker):
    mocker.set_batch_get_image_side_effect(
        cycle(
            [
                {"images": [{"imageId": {"imageDigest": "my-digest"}}]},
                {
                    "images": [
                        {"imageId": {"imageTag": f"-py3{sys.version_info.minor}-"}},
                    ],
                },
            ],
        ),
    )
    mocker.set_search_result(
        [{"Roles": [{"RoleName": "AmazonBraketJobsExecutionRole", "Arn": "TestRoleARN"}]}],
    )
    mocker.set_create_job_result(
        {"jobArn": f"arn:aws:braket:{mocker.region_name}:000000:job/testJob"},
    )
    mocker.set_get_job_result(
        {
            "instanceConfig": {"instanceCount": 1},
            "jobName": "testJob",
            "status": "COMPLETED",
            "outputDataConfig": {"s3Path": "s3://amazon-br-invalid-path/test-path/test-results"},
            "queueInfo": {
                "position": 1,
            },
        },
    )


def mock_job_results(results):
    with open("results.json", "w") as f:
        serialized_data = serialize_values(results, PersistedJobDataFormat.PICKLED_V4)
        persisted_data = PersistedJobData(
            dataDictionary=serialized_data,
            dataFormat=PersistedJobDataFormat.PICKLED_V4,
        )
        f.write(persisted_data.json())
    with tarfile.open("model.tar.gz", "w:gz") as tar:
        tar.add("results.json")


def set_level(mock_level):
    Mocker.mock_level = mock_level


def mock_program_set_calls(mocker, base_path):
    """Set up mocking for program set quantum tasks.
    
    Program set results require complex S3 mocking due to their hierarchical structure:
    - Main results.json contains references to metadata and program results
    - metadata.json contains task metadata
    - programs/N/results.json contains results for each program
    - programs/N/program.json contains the OpenQASM program source  
    - programs/N/executables/M.json contains results for each executable
    
    This function configures the mocker to handle all these S3 calls automatically.
    
    Args:
        mocker: The Mocker instance
        base_path: Optional path to the program set mock data directory.
                  If not provided, no default path is set and must be configured via set_program_set_result_path()
                  
    Example:
        mocker = Mocker()
        mock_default_device_calls(mocker)  # Always required
        
        # Option 1: Provide base_path directly
        mock_program_set_calls(mocker, base_path="/path/to/program_set_data")
        
        # Option 2: Set up infrastructure first, then set path
        mock_program_set_calls(mocker)
        mocker.set_program_set_result_path("/path/to/program_set_data")
        
        # Now your program set tasks will work with full S3 mocking
        task = device.run(program_set, shots=100)
        result = task.result()  # Uses mocked S3 calls
    """
    if not os.path.isabs(base_path):
        base_path = os.path.abspath(base_path)
    mocker.set_program_set_result_path(base_path)
    main_results_path = os.path.join(base_path, "results.json")
    
    with open(main_results_path, "r") as f:
        main_results = f.read()
    mocker.set_task_result_return(main_results)


class SessionWrapper:
    def __init__(self):
        self.boto_client = mock.Mock()
        self.task_result_mock = mock.Mock()
        self.resource_mock = mock.Mock()

        return_mock = mock.Mock()
        return_mock.read.return_value.decode = self.task_result_mock
        self.resource_mock.Object.return_value.get.return_value = {"Body": return_mock}
        self.boto_client.get_caller_identity.return_value = {"Account": "TestAccount"}
        self.boto_client.get_authorization_token.return_value = {
            "authorizationData": [{"authorizationToken": "TestToken"}],
        }
        
        # Set up S3 client mock for program set results
        self._program_set_mock_path = None
        self._setup_s3_client_mock()

    def _setup_s3_client_mock(self):
        """Set up S3 client mock to handle program set S3 calls."""
        def mock_get_object(Bucket, Key):
            # Check if this is a program set S3 request
            program_set_patterns = [
                "metadata.json",
                "programs/",
                "executables/",
                "/results.json"
            ]
            is_program_set = any(pattern in Key for pattern in program_set_patterns)
            
            if is_program_set:
                content = self._handle_program_set_s3_request(Key)
                body_mock = mock.Mock()
                body_mock.read.return_value = content.encode('utf-8')
                return {"Body": body_mock}
            else:
                # Fallback to regular task result mock
                if self.task_result_mock.side_effect is not None:
                    content = next(self.task_result_mock.side_effect)
                else:
                    content = self.task_result_mock.return_value
                body_mock = mock.Mock()
                body_mock.read.return_value = content.encode('utf-8') if isinstance(content, str) else content
                return {"Body": body_mock}
        
        self.boto_client.get_object.side_effect = mock_get_object

    def _handle_program_set_s3_request(self, s3_object_key):
        """Handle S3 requests for program set files by reading from local test data."""
        # Use the configured program set mock path
        base_path = self._program_set_mock_path
        
        # Extract the relative path from the S3 key
        if "/metadata.json" in s3_object_key:
            local_path = os.path.join(base_path, "metadata.json")
        elif "/programs/" in s3_object_key:
            # Extract the part after "programs/"
            programs_part = s3_object_key.split("/programs/", 1)[1]
            local_path = os.path.join(base_path, "programs", programs_part)
        else: # s3_object_key.endswith("/results.json")
            local_path = os.path.join(base_path, "results.json")
        
        with open(local_path, "r") as f:
            content = f.read()
        return content


class Boto3SessionAllWrapper(SessionWrapper):
    def __init__(self):
        super().__init__()
        boto3.Session = self
        # Also mock boto3.client directly for program set S3 calls
        boto3.client = self.client
        self._default_region = "us-west-2"
        self._region = self._default_region

    def __call__(self, *args, **kwargs):
        # handle explicit region_name=None
        self._region = kwargs.get("region_name") or self._default_region
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
        return self._region


class AwsSessionMinWrapper(SessionWrapper):
    def __init__(self):
        super().__init__()
        import braket.jobs.metrics_data.cwl_insights_metrics_fetcher as md

        AwsSessionFacade._wrapper = self
        AwsSessionFacade.real_get_device = braket.aws.aws_session.AwsSession.get_device
        braket.aws.aws_session.AwsSession.get_device = AwsSessionFacade.get_device
        AwsSessionFacade.real_create_quantum_task = (
            braket.aws.aws_session.AwsSession.create_quantum_task
        )
        braket.aws.aws_session.AwsSession.create_quantum_task = AwsSessionFacade.create_quantum_task
        AwsSessionFacade.real_get_quantum_task = braket.aws.aws_session.AwsSession.get_quantum_task
        braket.aws.aws_session.AwsSession.get_quantum_task = AwsSessionFacade.get_quantum_task
        AwsSessionFacade.real_cancel_quantum_task = (
            braket.aws.aws_session.AwsSession.cancel_quantum_task
        )
        braket.aws.aws_session.AwsSession.cancel_quantum_task = AwsSessionFacade.cancel_quantum_task
        AwsSessionFacade.real_retrieve_s3_object_body = (
            braket.aws.aws_session.AwsSession.retrieve_s3_object_body
        )
        braket.aws.aws_session.AwsSession.retrieve_s3_object_body = (
            AwsSessionFacade.retrieve_s3_object_body
        )
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
    program_set_mock_path = None

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
                    "quantumTaskArn"
                ]
            if device_name in AwsSessionFacade.mock_device_config:
                device_sub = AwsSessionFacade.mock_device_config[device_name]
                if device_sub == "MOCK":
                    return AwsSessionFacade._wrapper.boto_client.create_quantum_task(boto3_kwargs)[
                        "quantumTaskArn"
                    ]
                boto3_kwargs["deviceArn"] = device_sub
            task_arn = AwsSessionFacade.real_create_quantum_task(self, **boto3_kwargs)
            AwsSessionFacade.created_task_arns.add(task_arn)
            return task_arn
        return AwsSessionFacade._wrapper.boto_client.create_quantum_task(boto3_kwargs)[
            "quantumTaskArn"
        ]

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
        location = s3_object_key[: s3_object_key.rindex("/")]
        if location in AwsSessionFacade.created_task_locations:
            return AwsSessionFacade.real_retrieve_s3_object_body(self, s3_bucket, s3_object_key)
        
        # Check if this is a program set result request by looking for specific patterns
        if AwsSessionFacade._is_program_set_s3_request(s3_object_key):
            return AwsSessionFacade._handle_program_set_s3_request(s3_object_key)
        
        if AwsSessionFacade._wrapper.task_result_mock.side_effect is not None:
            return next(AwsSessionFacade._wrapper.task_result_mock.side_effect)
        return AwsSessionFacade._wrapper.task_result_mock.return_value

    def get_job_metrics(self, query_id):
        return AwsSessionFacade._wrapper.boto_client.get_query_results(query_id)["results"]

    @staticmethod
    def _is_program_set_s3_request(s3_object_key):
        """Check if the S3 request is for program set related files."""
        program_set_patterns = [
            "metadata.json",
            "programs/",
            "executables/",
            "/results.json"
        ]
        return any(pattern in s3_object_key for pattern in program_set_patterns)

    @staticmethod
    def _handle_program_set_s3_request(s3_object_key):
        """Handle S3 requests for program set files by reading from local test data."""
        # Map the S3 object key to local test file path
        base_path = AwsSessionFacade.program_set_mock_path
        if base_path is None:
            raise ValueError("Program set mock path not configured. Call set_program_set_result_path() first.")
        
        # Extract the relative path from the S3 key
        # S3 keys typically look like: "tasks/task-id/metadata.json" or "tasks/task-id/programs/0/results.json"
        if "/metadata.json" in s3_object_key:
            local_path = os.path.join(base_path, "metadata.json")
        elif "/programs/" in s3_object_key:
            # Extract the part after "programs/"
            programs_part = s3_object_key.split("/programs/", 1)[1]
            local_path = os.path.join(base_path, "programs", programs_part)
        else: # s3_object_key.endswith("/results.json")
            local_path = os.path.join(base_path, "results.json")
        
        with open(local_path, "r") as f:
            content = f.read()
        return content
