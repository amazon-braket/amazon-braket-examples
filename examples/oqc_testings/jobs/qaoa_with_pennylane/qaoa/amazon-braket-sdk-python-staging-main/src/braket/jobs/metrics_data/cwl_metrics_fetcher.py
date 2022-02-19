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

import time
from logging import Logger, getLogger
from typing import Dict, List, Union

from braket.aws.aws_session import AwsSession
from braket.jobs.metrics_data.definitions import MetricStatistic, MetricType
from braket.jobs.metrics_data.log_metrics_parser import LogMetricsParser


class CwlMetricsFetcher(object):
    LOG_GROUP_NAME = "/aws/braket/jobs"

    def __init__(
        self,
        aws_session: AwsSession,
        poll_timeout_seconds: float = 10,
        logger: Logger = getLogger(__name__),
    ):
        """
        Args:
            aws_session (AwsSession): AwsSession to connect to AWS with.
            poll_timeout_seconds (float): The polling timeout for retrieving the metrics,
                in seconds. Default: 10 seconds.
            logger (Logger): Logger object with which to write logs, such as task statuses
                while waiting for task to be in a terminal state. Default is `getLogger(__name__)`
        """
        self._poll_timeout_seconds = poll_timeout_seconds
        self._logger = logger
        self._logs_client = aws_session.logs_client

    @staticmethod
    def _is_metrics_message(message):
        """
        Returns true if a given message is designated as containing Metrics.

        Args:
            message (str): The message to check.

        Returns:
            True if the given message is designated as containing Metrics; False otherwise.
        """
        if message:
            return "Metrics -" in message
        return False

    def _parse_metrics_from_log_stream(
        self,
        stream_name: str,
        timeout_time: float,
        parser: LogMetricsParser,
    ) -> None:
        """
        Synchronously retrieves the algorithm metrics logged in a given job log stream.

        Args:
            stream_name (str): The name of the log stream.
            timeout_time (float) : We stop getting metrics if the current time is beyond
                the timeout time.
            parser (LogMetricsParser) : The CWL metrics parser.

        Returns:
            None
        """
        kwargs = {
            "logGroupName": self.LOG_GROUP_NAME,
            "logStreamName": stream_name,
            "startFromHead": True,
            "limit": 10000,
        }

        previous_token = None
        while time.time() < timeout_time:
            response = self._logs_client.get_log_events(**kwargs)
            for event in response.get("events"):
                message = event.get("message")
                if self._is_metrics_message(message):
                    parser.parse_log_message(event.get("timestamp"), message)
            next_token = response.get("nextForwardToken")
            if not next_token or next_token == previous_token:
                return
            previous_token = next_token
            kwargs["nextToken"] = next_token
        self._logger.warning("Timed out waiting for all metrics. Data may be incomplete.")

    def _get_log_streams_for_job(self, job_name: str, timeout_time: float) -> List[str]:
        """
        Retrieves the list of log streams relevant to a job.

        Args:
            job_name (str): The name of the job.
            timeout_time (float) : Metrics cease getting streamed if the current time exceeds
                the timeout time.
        Returns:
            List[str] : A list of log stream names for the given job.
        """
        kwargs = {
            "logGroupName": self.LOG_GROUP_NAME,
            "logStreamNamePrefix": job_name + "/algo-",
        }
        log_streams = []
        while time.time() < timeout_time:
            response = self._logs_client.describe_log_streams(**kwargs)
            streams = response.get("logStreams")
            if streams:
                for stream in streams:
                    name = stream.get("logStreamName")
                    if name:
                        log_streams.append(name)
            next_token = response.get("nextToken")
            if not next_token:
                return log_streams
            kwargs["nextToken"] = next_token
        self._logger.warning("Timed out waiting for all metrics. Data may be incomplete.")
        return log_streams

    def get_metrics_for_job(
        self,
        job_name: str,
        metric_type: MetricType = MetricType.TIMESTAMP,
        statistic: MetricStatistic = MetricStatistic.MAX,
    ) -> Dict[str, List[Union[str, float, int]]]:
        """
        Synchronously retrieves all the algorithm metrics logged by a given Job.

        Args:
            job_name (str): The name of the Job. The name must be exact to ensure only the relevant
                metrics are retrieved.
            metric_type (MetricType): The type of metrics to get. Default is MetricType.TIMESTAMP.
            statistic (MetricStatistic): The statistic to determine which metric value to use
             when there is a conflict. Default is MetricStatistic.MAX.

        Returns:
            Dict[str, List[Union[str, float, int]]] : The metrics data, where the keys
             are the column names and the values are a list containing the values in each row.
              For example, the table:
                timestamp energy
                0         0.1
                1         0.2
                would be represented as:
                { "timestamp" : [0, 1], "energy" : [0.1, 0.2] }
                values may be integers, floats, strings or None.
        """
        timeout_time = time.time() + self._poll_timeout_seconds

        parser = LogMetricsParser()

        log_streams = self._get_log_streams_for_job(job_name, timeout_time)
        for log_stream in log_streams:
            self._parse_metrics_from_log_stream(log_stream, timeout_time, parser)

        return parser.get_parsed_metrics(metric_type, statistic)
