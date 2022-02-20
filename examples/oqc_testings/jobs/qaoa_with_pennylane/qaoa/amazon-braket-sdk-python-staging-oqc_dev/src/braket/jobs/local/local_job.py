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

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Union

from braket.aws.aws_session import AwsSession
from braket.jobs.config import CheckpointConfig, OutputDataConfig, S3DataSourceConfig
from braket.jobs.image_uris import Framework, retrieve_image
from braket.jobs.local.local_job_container import _LocalJobContainer
from braket.jobs.local.local_job_container_setup import setup_container
from braket.jobs.metrics_data.definitions import MetricStatistic, MetricType
from braket.jobs.metrics_data.log_metrics_parser import LogMetricsParser
from braket.jobs.quantum_job import QuantumJob
from braket.jobs.quantum_job_creation import prepare_quantum_job
from braket.jobs.serialization import deserialize_values
from braket.jobs_data import PersistedJobData


class LocalQuantumJob(QuantumJob):
    """Amazon Braket implementation of a quantum job that runs locally."""

    @classmethod
    def create(
        cls,
        device: str,
        source_module: str,
        entry_point: str = None,
        image_uri: str = None,
        job_name: str = None,
        code_location: str = None,
        role_arn: str = None,
        hyperparameters: Dict[str, Any] = None,
        input_data: Union[str, Dict, S3DataSourceConfig] = None,
        output_data_config: OutputDataConfig = None,
        checkpoint_config: CheckpointConfig = None,
        aws_session: AwsSession = None,
    ) -> LocalQuantumJob:
        """Creates and runs job by setting up and running the customer script in a local
         docker container.

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

            role_arn (str): This field is currently not used for local jobs. Local jobs will use
                the current role's credentials. This may be subject to change.

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

            output_data_config (OutputDataConfig): Specifies the location for the output of the job.
                Default: OutputDataConfig(s3Path=f's3://{default_bucket_name}/jobs/{job_name}/data',
                kmsKeyId=None).

            checkpoint_config (CheckpointConfig): Configuration that specifies the location where
                checkpoint data is stored.
                Default: CheckpointConfig(localPath='/opt/jobs/checkpoints',
                s3Uri=f's3://{default_bucket_name}/jobs/{job_name}/checkpoints').

            aws_session (AwsSession): AwsSession for connecting to AWS Services.
                Default: AwsSession()

        Returns:
            LocalQuantumJob: The representation of a local Braket Job.
        """
        create_job_kwargs = prepare_quantum_job(
            device=device,
            source_module=source_module,
            entry_point=entry_point,
            image_uri=image_uri,
            job_name=job_name,
            code_location=code_location,
            role_arn=role_arn,
            hyperparameters=hyperparameters,
            input_data=input_data,
            output_data_config=output_data_config,
            checkpoint_config=checkpoint_config,
            aws_session=aws_session,
        )

        job_name = create_job_kwargs["jobName"]
        if os.path.isdir(job_name):
            raise ValueError(
                f"A local directory called {job_name} already exists. "
                f"Please use a different job name."
            )

        session = aws_session or AwsSession()
        algorithm_specification = create_job_kwargs["algorithmSpecification"]
        if "containerImage" in algorithm_specification:
            image_uri = algorithm_specification["containerImage"]["uri"]
        else:
            image_uri = retrieve_image(Framework.BASE, session.region)

        with _LocalJobContainer(image_uri) as container:
            env_variables = setup_container(container, session, **create_job_kwargs)
            container.run_local_job(env_variables)
            container.copy_from("/opt/ml/model", job_name)
            with open(os.path.join(job_name, "log.txt"), "w") as log_file:
                log_file.write(container.run_log)
            if "checkpointConfig" in create_job_kwargs:
                checkpoint_config = create_job_kwargs["checkpointConfig"]
                if "localPath" in checkpoint_config:
                    checkpoint_path = checkpoint_config["localPath"]
                    container.copy_from(checkpoint_path, os.path.join(job_name, "checkpoints"))
            run_log = container.run_log
        return LocalQuantumJob(f"local:job/{job_name}", run_log)

    def __init__(self, arn: str, run_log: str = None):
        """
        Args:
            arn (str): The ARN of the job.
            run_log (str, Optional): The container output log of running the job with the given arn.
        """
        if not arn.startswith("local:job/"):
            raise ValueError(f"Arn {arn} is not a valid local job arn")
        self._arn = arn
        self._run_log = run_log
        self._name = arn.partition("job/")[-1]
        if not run_log and not os.path.isdir(self.name):
            raise ValueError(f"Unable to find local job results for {self.name}")

    @property
    def arn(self) -> str:
        """str: The ARN (Amazon Resource Name) of the quantum job."""
        return self._arn

    @property
    def name(self) -> str:
        """str: The name of the quantum job."""
        return self._name

    @property
    def run_log(self) -> str:
        """str:  The container output log from running the job."""
        if not self._run_log:
            try:
                with open(os.path.join(self.name, "log.txt"), "r") as log_file:
                    self._run_log = log_file.read()
            except FileNotFoundError:
                raise ValueError(f"Unable to find logs in the local job directory {self.name}.")
        return self._run_log

    def state(self, use_cached_value: bool = False) -> str:
        """The state of the quantum job."""
        return "COMPLETED"

    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        """When running the quantum job in local mode, the metadata is not available."""
        pass

    def cancel(self) -> str:
        """When running the quantum job in local mode, the cancelling a running is not possible."""
        pass

    def download_result(
        self,
        extract_to=None,
        poll_timeout_seconds: float = QuantumJob.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = QuantumJob.DEFAULT_RESULTS_POLL_INTERVAL,
    ) -> None:
        """When running the quantum job in local mode, results are automatically stored locally."""
        pass

    def result(
        self,
        poll_timeout_seconds: float = QuantumJob.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = QuantumJob.DEFAULT_RESULTS_POLL_INTERVAL,
    ) -> Dict[str, Any]:
        """Retrieves the job result persisted using save_job_result() function."""
        try:
            with open(os.path.join(self.name, "results.json"), "r") as f:
                persisted_data = PersistedJobData.parse_raw(f.read())
                deserialized_data = deserialize_values(
                    persisted_data.dataDictionary, persisted_data.dataFormat
                )
                return deserialized_data
        except FileNotFoundError:
            raise ValueError(f"Unable to find results in the local job directory {self.name}.")

    def metrics(
        self,
        metric_type: MetricType = MetricType.TIMESTAMP,
        statistic: MetricStatistic = MetricStatistic.MAX,
    ) -> Dict[str, List[Any]]:
        """Gets all the metrics data, where the keys are the column names, and the values are a list
        containing the values in each row. For example, the table:
            timestamp energy
              0         0.1
              1         0.2
        would be represented as:
        { "timestamp" : [0, 1], "energy" : [0.1, 0.2] }
        values may be integers, floats, strings or None.

        Args:
            metric_type (MetricType): The type of metrics to get. Default: MetricType.TIMESTAMP.

            statistic (MetricStatistic): The statistic to determine which metric value to use
                when there is a conflict. Default: MetricStatistic.MAX.

        Returns:
            Dict[str, List[Union[str, float, int]]] : The metrics data.
        """
        parser = LogMetricsParser()
        current_time = str(time.time())
        for line in self.run_log.splitlines():
            if line.startswith("Metrics -"):
                parser.parse_log_message(current_time, line)
        return parser.get_parsed_metrics(metric_type, statistic)

    def logs(self, wait: bool = False, poll_interval_seconds: int = 5) -> None:
        """Display container logs for a given job"""
        return print(self.run_log)
