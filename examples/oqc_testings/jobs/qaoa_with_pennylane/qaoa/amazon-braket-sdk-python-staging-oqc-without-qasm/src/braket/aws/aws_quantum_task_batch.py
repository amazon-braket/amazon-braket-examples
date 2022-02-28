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

import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Set, Union

from braket.annealing import Problem
from braket.aws.aws_quantum_task import AwsQuantumTask
from braket.aws.aws_session import AwsSession
from braket.circuits import Circuit


class AwsQuantumTaskBatch:
    """Executes a batch of quantum tasks in parallel.

    Using this class can yield vast speedups over executing tasks sequentially,
    and is particularly useful for computations that can be parallelized,
    such as calculating quantum gradients or statistics of terms in a Hamiltonian.

    Note: there is no benefit to using this method with QPUs outside of their execution windows,
    since results will not be available until the window opens.
    """

    MAX_CONNECTIONS_DEFAULT = 100
    MAX_RETRIES = 3

    def __init__(
        self,
        aws_session: AwsSession,
        device_arn: str,
        task_specifications: List[Union[Circuit, Problem]],
        s3_destination_folder: AwsSession.S3DestinationFolder,
        shots: int,
        max_parallel: int,
        max_workers: int = MAX_CONNECTIONS_DEFAULT,
        poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        *aws_quantum_task_args,
        **aws_quantum_task_kwargs,
    ):
        """Creates a batch of quantum tasks.

        Args:
            aws_session (AwsSession): AwsSession to connect to AWS with.
            device_arn (str): The ARN of the quantum device.
            task_specification (Union[Circuit, Problem]): The specification of the task
                to run on device.
            s3_destination_folder (AwsSession.S3DestinationFolder): NamedTuple, with bucket
                for index 0 and key for index 1, that specifies the Amazon S3 bucket and folder
                to store task results in.
            shots (int): The number of times to run the task on the device. If the device is a
                simulator, this implies the state is sampled N times, where N = `shots`.
                `shots=0` is only available on simulators and means that the simulator
                will compute the exact results based on the task specification.
            max_parallel (int): The maximum number of tasks to run on AWS in parallel.
                Batch creation will fail if this value is greater than the maximum allowed
                concurrent tasks on the device.
            max_workers (int): The maximum number of thread pool workers. Default: 100
            poll_timeout_seconds (float): The polling timeout for `AwsQuantumTask.result()`,
                in seconds. Default: 5 days.
            poll_interval_seconds (float): The polling interval for results in seconds.
                Default: 1 second.
            *aws_quantum_task_args: Variable length positional arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.
            **aws_quantum_task_kwargs: Variable length keyword arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.
        """
        self._tasks = AwsQuantumTaskBatch._execute(
            aws_session,
            device_arn,
            task_specifications,
            s3_destination_folder,
            shots,
            max_parallel,
            max_workers,
            poll_timeout_seconds,
            poll_interval_seconds,
            *aws_quantum_task_args,
            **aws_quantum_task_kwargs,
        )
        self._aws_session = aws_session
        self._results = None
        self._unsuccessful = set()

        # Cache execution inputs for retries.
        self._device_arn = device_arn
        self._task_specifications = task_specifications
        self._s3_destination_folder = s3_destination_folder
        self._shots = shots
        self._max_parallel = max_parallel
        self._max_workers = max_workers
        self._poll_timeout_seconds = poll_timeout_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._aws_quantum_task_args = aws_quantum_task_args
        self._aws_quantum_task_kwargs = aws_quantum_task_kwargs

    @staticmethod
    def _execute(
        aws_session,
        device_arn,
        task_specifications,
        s3_destination_folder,
        shots,
        max_parallel,
        max_workers,
        poll_timeout_seconds,
        poll_interval_seconds,
        *args,
        **kwargs,
    ):
        max_threads = min(max_parallel, max_workers)
        remaining = [0 for _ in task_specifications]
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            task_futures = [
                executor.submit(
                    AwsQuantumTaskBatch._create_task,
                    remaining,
                    aws_session,
                    device_arn,
                    task,
                    s3_destination_folder,
                    shots,
                    poll_timeout_seconds=poll_timeout_seconds,
                    poll_interval_seconds=poll_interval_seconds,
                    *args,
                    **kwargs,
                )
                for task in task_specifications
            ]
        tasks = [future.result() for future in task_futures]
        return tasks

    @staticmethod
    def _create_task(
        remaining,
        aws_session,
        device_arn,
        task_specification,
        s3_destination_folder,
        shots,
        poll_interval_seconds,
        *args,
        **kwargs,
    ):
        task = AwsQuantumTask.create(
            aws_session,
            device_arn,
            task_specification,
            s3_destination_folder,
            shots,
            poll_interval_seconds=poll_interval_seconds,
            *args,
            **kwargs,
        )

        remaining.pop()

        # If the task hits a terminal state before all tasks have been created,
        # it can be returned immediately
        while remaining:
            if task.state() in AwsQuantumTask.TERMINAL_STATES:
                break
            time.sleep(poll_interval_seconds)
        return task

    def results(self, fail_unsuccessful=False, max_retries=MAX_RETRIES, use_cached_value=True):
        """Retrieves the result of every task in the batch.

        Polling for results happens in parallel; this method returns when all tasks
        have reached a terminal state. The result of this method is cached.

        Args:
            fail_unsuccessful (bool): If set to `True`, this method will fail
                if any task in the batch fails to return a result even after
                `max_retries` retries.
            max_retries (int): Maximum number of times to retry any failed tasks,
                i.e. any tasks in the `FAILED` or `CANCELLED` state or that didn't
                complete within the timeout. Default: 3.
            use_cached_value (bool): If `False`, will refetch the results from S3,
                even when results have already been cached. Default: `True`.

        Returns:
            List[AwsQuantumTask]: The results of all of the tasks in the batch.
                `FAILED`, `CANCELLED`, or timed out tasks will have a result of None
        """
        if not self._results or not use_cached_value:
            self._results = AwsQuantumTaskBatch._retrieve_results(self._tasks, self._max_workers)
            self._unsuccessful = {
                task.id for task, result in zip(self._tasks, self._results) if not result
            }

        retries = 0
        while self._unsuccessful and retries < max_retries:
            self.retry_unsuccessful_tasks()
            retries = retries + 1

        if fail_unsuccessful and self._unsuccessful:
            raise RuntimeError(
                f"{len(self._unsuccessful)} tasks failed to complete after {max_retries} retries"
            )
        return self._results

    @staticmethod
    def _retrieve_results(tasks, max_workers):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            result_futures = [executor.submit(task.result) for task in tasks]
        return [future.result() for future in result_futures]

    def retry_unsuccessful_tasks(self):
        """Retries any tasks in the batch without valid results.

        This method should only be called after `results()` has been called at least once.
        The method will generate new tasks for any failed tasks, so `self.task` and
        `self.results()` may return different values after a call to this method.

        Returns:
            bool: Whether or not all retried tasks completed successfully.
        """
        if not self._results:
            raise RuntimeError("results() should be called before attempting to retry")
        unsuccessful_indices = [index for index, result in enumerate(self._results) if not result]
        # Return early if there's nothing to retry
        if not unsuccessful_indices:
            return True
        retried_tasks = AwsQuantumTaskBatch._execute(
            self._aws_session,
            self._device_arn,
            [self._task_specifications[i] for i in unsuccessful_indices],
            self._s3_destination_folder,
            self._shots,
            self._max_parallel,
            self._max_workers,
            self._poll_timeout_seconds,
            self._poll_interval_seconds,
            *self._aws_quantum_task_args,
            **self._aws_quantum_task_kwargs,
        )
        for index, task in zip(unsuccessful_indices, retried_tasks):
            self._tasks[index] = task

        retried_results = AwsQuantumTaskBatch._retrieve_results(retried_tasks, self._max_workers)
        for index, result in zip(unsuccessful_indices, retried_results):
            self._results[index] = result
        self._unsuccessful = {
            task.id for task, result in zip(retried_tasks, retried_results) if not result
        }
        return not self._unsuccessful

    @property
    def tasks(self) -> List[AwsQuantumTask]:
        """List[AwsQuantumTask]: The tasks in this batch, as a list of AwsQuantumTask objects"""
        return list(self._tasks)

    @property
    def size(self) -> int:
        """int: The number of tasks in the batch"""
        return len(self._tasks)

    @property
    def unfinished(self) -> Set[str]:
        """Set[str]: The IDs of all the tasks in the batch that have yet to complete"""
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            status_futures = {task.id: executor.submit(task.state) for task in self._tasks}
        unfinished = set()
        for task_id in status_futures:
            status = status_futures[task_id].result()
            if status not in AwsQuantumTask.TERMINAL_STATES:
                unfinished.add(task_id)
            if status in AwsQuantumTask.NO_RESULT_TERMINAL_STATES:
                self._unsuccessful.add(task_id)
        return unfinished

    @property
    def unsuccessful(self) -> Set[str]:
        """Set[str]: The IDs of all the FAILED, CANCELLED, or timed out tasks in the batch."""
        return set(self._unsuccessful)
