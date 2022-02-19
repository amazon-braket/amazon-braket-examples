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
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from braket.jobs.metrics_data.definitions import MetricStatistic, MetricType


class QuantumJob(ABC):
    DEFAULT_RESULTS_POLL_TIMEOUT = 864000
    DEFAULT_RESULTS_POLL_INTERVAL = 5

    @property
    @abstractmethod
    def arn(self) -> str:
        """str: The ARN (Amazon Resource Name) of the quantum job."""

    @property
    @abstractmethod
    def name(self) -> str:
        """str: The name of the quantum job."""

    @abstractmethod
    def state(self, use_cached_value: bool = False) -> str:
        """The state of the quantum job.

        Args:
            use_cached_value (bool, optional): If `True`, uses the value most recently retrieved
                value from the Amazon Braket `GetJob` operation. If `False`, calls the
                `GetJob` operation to retrieve metadata, which also updates the cached
                value. Default = `False`.
        Returns:
            str: The value of `status` in `metadata()`. This is the value of the `status` key
            in the Amazon Braket `GetJob` operation.

        See Also:
            `metadata()`
        """

    @abstractmethod
    def logs(self, wait: bool = False, poll_interval_seconds: int = 5) -> None:
        """Display logs for a given job, optionally tailing them until job is complete.

        If the output is a tty or a Jupyter cell, it will be color-coded
        based on which instance the log entry is from.

        Args:
            wait (bool): `True` to keep looking for new log entries until the job completes;
                otherwise `False`. Default: `False`.

            poll_interval_seconds (int): The interval of time, in seconds, between polling for
                new log entries and job completion (default: 5).

        Raises:
            RuntimeError: If waiting and the job fails.
        """
        # The loop below implements a state machine that alternates between checking the job status
        # and reading whatever is available in the logs at this point. Note, that if we were
        # called with wait == False, we never check the job status.
        #
        # If wait == TRUE and job is not completed, the initial state is TAILING
        # If wait == FALSE, the initial state is COMPLETE (doesn't matter if the job really is
        # complete).
        #
        # The state table:
        #
        # STATE               ACTIONS                        CONDITION             NEW STATE
        # ----------------    ----------------               -----------------     ----------------
        # TAILING             Read logs, Pause, Get status   Job complete          JOB_COMPLETE
        #                                                    Else                  TAILING
        # JOB_COMPLETE        Read logs, Pause               Any                   COMPLETE
        # COMPLETE            Read logs, Exit                                      N/A
        #
        # Notes:
        # - The JOB_COMPLETE state forces us to do an extra pause and read any items that got to
        #   Cloudwatch after the job was marked complete.

    @abstractmethod
    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        """Gets the job metadata defined in Amazon Braket.

        Args:
            use_cached_value (bool, optional): If `True`, uses the value most recently retrieved
                from the Amazon Braket `GetJob` operation, if it exists; if does not exist,
                `GetJob` is called to retrieve the metadata. If `False`, always calls
                `GetJob`, which also updates the cached value. Default: `False`.
        Returns:
            Dict[str, Any]: Dict that specifies the job metadata defined in Amazon Braket.
        """

    @abstractmethod
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

    @abstractmethod
    def cancel(self) -> str:
        """Cancels the job.

        Returns:
            str: Indicates the status of the job.

        Raises:
            ClientError: If there are errors invoking the CancelJob API.
        """

    @abstractmethod
    def result(
        self,
        poll_timeout_seconds: float = DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = DEFAULT_RESULTS_POLL_INTERVAL,
    ) -> Dict[str, Any]:
        """Retrieves the job result persisted using save_job_result() function.

        Args:
            poll_timeout_seconds (float): The polling timeout, in seconds, for `result()`.
                Default: 10 days.

            poll_interval_seconds (float): The polling interval, in seconds, for `result()`.
                Default: 5 seconds.


        Returns:
            Dict[str, Any]: Dict specifying the job results.

        Raises:
            RuntimeError: if job is in a FAILED or CANCELLED state.
            TimeoutError: if job execution exceeds the polling timeout period.
        """

    @abstractmethod
    def download_result(
        self,
        extract_to=None,
        poll_timeout_seconds: float = DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = DEFAULT_RESULTS_POLL_INTERVAL,
    ) -> None:
        """Downloads the results from the job output S3 bucket and extracts the tar.gz
        bundle to the location specified by `extract_to`. If no location is specified,
        the results are extracted to the current directory.

        Args:
            extract_to (str): The directory to which the results are extracted. The results
                are extracted to a folder titled with the job name within this directory.
                Default= `Current working directory`.

            poll_timeout_seconds: (float): The polling timeout, in seconds, for `download_result()`.
                Default: 10 days.

            poll_interval_seconds: (float): The polling interval, in seconds, for
                `download_result()`.Default: 5 seconds.

        Raises:
            RuntimeError: if job is in a FAILED or CANCELLED state.
            TimeoutError: if job execution exceeds the polling timeout period.
        """
