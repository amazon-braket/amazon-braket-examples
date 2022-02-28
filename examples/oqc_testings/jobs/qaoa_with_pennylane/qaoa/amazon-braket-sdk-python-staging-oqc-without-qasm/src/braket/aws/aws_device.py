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
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from botocore.errorfactory import ClientError
from networkx import Graph, complete_graph, from_edgelist

from braket.annealing.problem import Problem
from braket.aws.aws_quantum_task import AwsQuantumTask
from braket.aws.aws_quantum_task_batch import AwsQuantumTaskBatch
from braket.aws.aws_session import AwsSession
from braket.circuits import Circuit
from braket.device_schema import DeviceCapabilities, ExecutionDay, GateModelQpuParadigmProperties
from braket.device_schema.dwave import DwaveProviderProperties
from braket.devices.device import Device
from braket.schema_common import BraketSchemaBase


class AwsDeviceType(str, Enum):
    """Possible AWS device types"""

    SIMULATOR = "SIMULATOR"
    QPU = "QPU"


class AwsDevice(Device):
    """
    Amazon Braket implementation of a device.
    Use this class to retrieve the latest metadata about the device and to run a quantum task on the
    device.
    """

    REGIONS = ("us-east-1", "us-west-1", "us-west-2")

    DEFAULT_SHOTS_QPU = 1000
    DEFAULT_SHOTS_SIMULATOR = 0
    DEFAULT_MAX_PARALLEL = 10

    _GET_DEVICES_ORDER_BY_KEYS = frozenset({"arn", "name", "type", "provider_name", "status"})

    def __init__(self, arn: str, aws_session: Optional[AwsSession] = None):
        """
        Args:
            arn (str): The ARN of the device
            aws_session (AwsSession, optional): An AWS session object. Default is `None`.

        Note:
            Some devices (QPUs) are physically located in specific AWS Regions. In some cases,
            the current `aws_session` connects to a Region other than the Region in which the QPU is
            physically located. When this occurs, a cloned `aws_session` is created for the Region
            the QPU is located in.

            See `braket.aws.aws_device.AwsDevice.DEVICE_REGIONS` for the AWS Regions provider
            devices are located in.
        """
        super().__init__(name=None, status=None)
        self._arn = arn
        self._properties = None
        self._provider_name = None
        self._topology_graph = None
        self._type = None
        self._aws_session = self._get_session_and_initialize(aws_session or AwsSession())

    def run(
        self,
        task_specification: Union[Circuit, Problem],
        s3_destination_folder: Optional[AwsSession.S3DestinationFolder] = None,
        shots: Optional[int] = None,
        poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        *aws_quantum_task_args,
        **aws_quantum_task_kwargs,
    ) -> AwsQuantumTask:
        """
        Run a quantum task specification on this device. A task can be a circuit or an
        annealing problem.

        Args:
            task_specification (Union[Circuit, Problem]): Specification of task
                (circuit or annealing problem) to run on device.
            s3_destination_folder (AwsSession.S3DestinationFolder, optional): The S3 location to
                save the task's results to. Default is `<default_bucket>/tasks` if evoked
                outside of a Braket Job, `<Job Bucket>/jobs/<job name>/tasks` if evoked inside of
                a Braket Job.
            shots (int, optional): The number of times to run the circuit or annealing problem.
                Default is 1000 for QPUs and 0 for simulators.
            poll_timeout_seconds (float): The polling timeout for `AwsQuantumTask.result()`,
                in seconds. Default: 5 days.
            poll_interval_seconds (float): The polling interval for `AwsQuantumTask.result()`,
                in seconds. Default: 1 second.
            *aws_quantum_task_args: Variable length positional arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.
            **aws_quantum_task_kwargs: Variable length keyword arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.

        Returns:
            AwsQuantumTask: An AwsQuantumTask that tracks the execution on the device.

        Examples:
            >>> circuit = Circuit().h(0).cnot(0, 1)
            >>> device = AwsDevice("arn1")
            >>> device.run(circuit, ("bucket-foo", "key-bar"))

            >>> circuit = Circuit().h(0).cnot(0, 1)
            >>> device = AwsDevice("arn2")
            >>> device.run(task_specification=circuit,
            >>>     s3_destination_folder=("bucket-foo", "key-bar"))

            >>> circuit = Circuit().h(0).cnot(0, 1)
            >>> device = AwsDevice("arn3")
            >>> device.run(task_specification=circuit,
            >>>     s3_destination_folder=("bucket-foo", "key-bar"), disable_qubit_rewiring=True)

            >>> problem = Problem(
            >>>     ProblemType.ISING,
            >>>     linear={1: 3.14},
            >>>     quadratic={(1, 2): 10.08},
            >>> )
            >>> device = AwsDevice("arn4")
            >>> device.run(problem, ("bucket-foo", "key-bar"),
            >>>     device_parameters={
            >>>         "providerLevelParameters": {"postprocessingType": "SAMPLING"}}
            >>> )

        See Also:
            `braket.aws.aws_quantum_task.AwsQuantumTask.create()`
        """
        return AwsQuantumTask.create(
            self._aws_session,
            self._arn,
            task_specification,
            s3_destination_folder
            or (
                AwsSession.parse_s3_uri(os.environ.get("AMZN_BRAKET_TASK_RESULTS_S3_URI"))
                if "AMZN_BRAKET_TASK_RESULTS_S3_URI" in os.environ
                else None
            )
            or (self._aws_session.default_bucket(), "tasks"),
            shots if shots is not None else self._default_shots,
            poll_timeout_seconds=poll_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            *aws_quantum_task_args,
            **aws_quantum_task_kwargs,
        )

    def run_batch(
        self,
        task_specifications: List[Union[Circuit, Problem]],
        s3_destination_folder: Optional[AwsSession.S3DestinationFolder] = None,
        shots: Optional[int] = None,
        max_parallel: Optional[int] = None,
        max_connections: int = AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT,
        poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        *aws_quantum_task_args,
        **aws_quantum_task_kwargs,
    ) -> AwsQuantumTaskBatch:
        """Executes a batch of tasks in parallel

        Args:
            task_specifications (List[Union[Circuit, Problem]]): List of  circuits
                or annealing problems to run on device.
            s3_destination_folder (AwsSession.S3DestinationFolder, optional): The S3 location to
                save the tasks' results to. Default is `<default_bucket>/tasks` if evoked
                outside of a Braket Job, `<Job Bucket>/jobs/<job name>/tasks` if evoked inside of
                a Braket Job.
            shots (int, optional): The number of times to run the circuit or annealing problem.
                Default is 1000 for QPUs and 0 for simulators.
            max_parallel (int, optional): The maximum number of tasks to run on AWS in parallel.
                Batch creation will fail if this value is greater than the maximum allowed
                concurrent tasks on the device. Default: 10
            max_connections (int): The maximum number of connections in the Boto3 connection pool.
                Also the maximum number of thread pool workers for the batch. Default: 100
            poll_timeout_seconds (float): The polling timeout for `AwsQuantumTask.result()`,
                in seconds. Default: 5 days.
            poll_interval_seconds (float): The polling interval for results in seconds.
                Default: 1 second.
            *aws_quantum_task_args: Variable length positional arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.
            **aws_quantum_task_kwargs: Variable length keyword arguments for
                `braket.aws.aws_quantum_task.AwsQuantumTask.create()`.

        Returns:
            AwsQuantumTaskBatch: A batch containing all of the tasks run

        See Also:
            `braket.aws.aws_quantum_task_batch.AwsQuantumTaskBatch`
        """
        return AwsQuantumTaskBatch(
            AwsSession.copy_session(self._aws_session, max_connections=max_connections),
            self._arn,
            task_specifications,
            s3_destination_folder
            or (
                AwsSession.parse_s3_uri(os.environ.get("AMZN_BRAKET_TASK_RESULTS_S3_URI"))
                if "AMZN_BRAKET_TASK_RESULTS_S3_URI" in os.environ
                else None
            )
            or (self._aws_session.default_bucket(), "tasks"),
            shots if shots is not None else self._default_shots,
            max_parallel=max_parallel if max_parallel is not None else self._default_max_parallel,
            max_workers=max_connections,
            poll_timeout_seconds=poll_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            *aws_quantum_task_args,
            **aws_quantum_task_kwargs,
        )

    def refresh_metadata(self) -> None:
        """
        Refresh the `AwsDevice` object with the most recent Device metadata.
        """
        self._populate_properties(self._aws_session)

    def _get_session_and_initialize(self, session):
        device_region = self._arn.split(":")[3]
        return (
            self._get_regional_device_session(session)
            if device_region
            else self._get_non_regional_device_session(session)
        )

    def _get_regional_device_session(self, session):
        device_region = self._arn.split(":")[3]
        region_session = (
            session
            if session.region == device_region
            else AwsSession.copy_session(session, device_region)
        )
        try:
            self._populate_properties(region_session)
            return region_session
        except ClientError as e:
            raise ValueError(f"'{self._arn}' not found") if e.response["Error"][
                "Code"
            ] == "ResourceNotFoundException" else e

    def _get_non_regional_device_session(self, session):
        current_region = session.region
        try:
            self._populate_properties(session)
            return session
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                if "qpu" not in self._arn:
                    raise ValueError(f"Simulator '{self._arn}' not found in '{current_region}'")
            else:
                raise e
        # Search remaining regions for QPU
        for region in frozenset(AwsDevice.REGIONS) - {current_region}:
            region_session = AwsSession.copy_session(session, region)
            try:
                self._populate_properties(region_session)
                return region_session
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise e
        raise ValueError(f"QPU '{self._arn}' not found")

    def _populate_properties(self, session):
        metadata = session.get_device(self._arn)
        self._name = metadata.get("deviceName")
        self._status = metadata.get("deviceStatus")
        self._type = AwsDeviceType(metadata.get("deviceType"))
        self._provider_name = metadata.get("providerName")
        qpu_properties = metadata.get("deviceCapabilities")
        self._properties = BraketSchemaBase.parse_raw_schema(qpu_properties)
        self._topology_graph = self._construct_topology_graph()

    @property
    def type(self) -> str:
        """str: Return the device type"""
        return self._type

    @property
    def provider_name(self) -> str:
        """str: Return the provider name"""
        return self._provider_name

    @property
    def arn(self) -> str:
        """str: Return the ARN of the device"""
        return self._arn

    @property
    def is_available(self) -> bool:
        """bool: Return if the device is currently available"""
        if self.status != "ONLINE":
            return False

        is_available_result = False

        current_datetime_utc = datetime.utcnow()
        for execution_window in self.properties.service.executionWindows:
            weekday = current_datetime_utc.weekday()
            current_time_utc = current_datetime_utc.time().replace(microsecond=0)

            if (
                execution_window.windowEndHour < execution_window.windowStartHour
                and current_time_utc < execution_window.windowEndHour
            ):
                weekday = (weekday - 1) % 7

            matched_day = execution_window.executionDay == ExecutionDay.EVERYDAY
            matched_day = matched_day or (
                execution_window.executionDay == ExecutionDay.WEEKDAYS and weekday < 5
            )
            matched_day = matched_day or (
                execution_window.executionDay == ExecutionDay.WEEKENDS and weekday > 4
            )
            ordered_days = (
                ExecutionDay.MONDAY,
                ExecutionDay.TUESDAY,
                ExecutionDay.WEDNESDAY,
                ExecutionDay.THURSDAY,
                ExecutionDay.FRIDAY,
                ExecutionDay.SATURDAY,
                ExecutionDay.SUNDAY,
            )
            matched_day = matched_day or (
                execution_window.executionDay in ordered_days
                and ordered_days.index(execution_window.executionDay) == weekday
            )

            matched_time = (
                execution_window.windowStartHour < execution_window.windowEndHour
                and execution_window.windowStartHour
                <= current_time_utc
                <= execution_window.windowEndHour
            ) or (
                execution_window.windowEndHour < execution_window.windowStartHour
                and (
                    current_time_utc >= execution_window.windowStartHour
                    or current_time_utc <= execution_window.windowEndHour
                )
            )

            is_available_result = is_available_result or (matched_day and matched_time)

        return is_available_result

    @property
    # TODO: Add a link to the boto3 docs
    def properties(self) -> DeviceCapabilities:
        """DeviceCapabilities: Return the device properties

        Please see `braket.device_schema` in amazon-braket-schemas-python_

        .. _amazon-braket-schemas-python: https://github.com/aws/amazon-braket-schemas-python"""
        return self._properties

    @property
    def topology_graph(self) -> Graph:
        """Graph: topology of device as a networkx `Graph` object.
        Returns `None` if the topology is not available for the device.

        Examples:
            >>> import networkx as nx
            >>> device = AwsDevice("arn1")
            >>> nx.draw_kamada_kawai(device.topology_graph, with_labels=True, font_weight="bold")

            >>> topology_subgraph = device.topology_graph.subgraph(range(8))
            >>> nx.draw_kamada_kawai(topology_subgraph, with_labels=True, font_weight="bold")

            >>> print(device.topology_graph.edges)
        """
        return self._topology_graph

    def _construct_topology_graph(self) -> Graph:
        """
        Construct topology graph. If no such metadata is available, return `None`.

        Returns:
            Graph: topology of QPU as a networkx `Graph` object.
        """
        if hasattr(self.properties, "paradigm") and isinstance(
            self.properties.paradigm, GateModelQpuParadigmProperties
        ):
            if self.properties.paradigm.connectivity.fullyConnected:
                return complete_graph(int(self.properties.paradigm.qubitCount))
            adjacency_lists = self.properties.paradigm.connectivity.connectivityGraph
            edges = []
            for item in adjacency_lists.items():
                i = item[0]
                edges.extend([(int(i), int(j)) for j in item[1]])
            return from_edgelist(edges)
        elif hasattr(self.properties, "provider") and isinstance(
            self.properties.provider, DwaveProviderProperties
        ):
            edges = self.properties.provider.couplers
            return from_edgelist(edges)
        else:
            return None

    @property
    def _default_shots(self):
        return (
            AwsDevice.DEFAULT_SHOTS_QPU if "qpu" in self.arn else AwsDevice.DEFAULT_SHOTS_SIMULATOR
        )

    @property
    def _default_max_parallel(self):
        return AwsDevice.DEFAULT_MAX_PARALLEL

    def __repr__(self):
        return "Device('name': {}, 'arn': {})".format(self.name, self.arn)

    def __eq__(self, other):
        if isinstance(other, AwsDevice):
            return self.arn == other.arn
        return NotImplemented

    @staticmethod
    def get_devices(
        arns: Optional[List[str]] = None,
        names: Optional[List[str]] = None,
        types: Optional[List[AwsDeviceType]] = None,
        statuses: Optional[List[str]] = None,
        provider_names: Optional[List[str]] = None,
        order_by: str = "name",
        aws_session: Optional[AwsSession] = None,
    ) -> List[AwsDevice]:
        """
        Get devices based on filters and desired ordering. The result is the AND of
        all the filters `arns`, `names`, `types`, `statuses`, `provider_names`.

        Examples:
            >>> AwsDevice.get_devices(provider_names=['Rigetti'], statuses=['ONLINE'])
            >>> AwsDevice.get_devices(order_by='provider_name')
            >>> AwsDevice.get_devices(types=['SIMULATOR'])

        Args:
            arns (List[str], optional): device ARN list, default is `None`
            names (List[str], optional): device name list, default is `None`
            types (List[AwsDeviceType], optional): device type list, default is `None`
                QPUs will be searched for all regions and simulators will only be
                searched for the region of the current session.
            statuses (List[str], optional): device status list, default is `None`
            provider_names (List[str], optional): provider name list, default is `None`
            order_by (str, optional): field to order result by, default is `name`.
                Accepted values are ['arn', 'name', 'type', 'provider_name', 'status']
            aws_session (AwsSession, optional) aws_session: An AWS session object.
                Default is `None`.

        Returns:
            List[AwsDevice]: list of AWS devices
        """

        if order_by not in AwsDevice._GET_DEVICES_ORDER_BY_KEYS:
            raise ValueError(
                f"order_by '{order_by}' must be in {AwsDevice._GET_DEVICES_ORDER_BY_KEYS}"
            )
        types = (
            frozenset(types) if types else frozenset({device_type for device_type in AwsDeviceType})
        )
        aws_session = aws_session if aws_session else AwsSession()
        device_map = {}
        session_region = aws_session.boto_session.region_name
        search_regions = (
            (session_region,) if types == {AwsDeviceType.SIMULATOR} else AwsDevice.REGIONS
        )
        for region in search_regions:
            session_for_region = (
                aws_session
                if region == session_region
                else AwsSession.copy_session(aws_session, region)
            )
            # Simulators are only instantiated in the same region as the AWS session
            types_for_region = sorted(
                types if region == session_region else types - {AwsDeviceType.SIMULATOR}
            )
            region_device_arns = [
                result["deviceArn"]
                for result in session_for_region.search_devices(
                    arns=arns,
                    names=names,
                    types=types_for_region,
                    statuses=statuses,
                    provider_names=provider_names,
                )
            ]
            device_map.update(
                {
                    arn: AwsDevice(arn, session_for_region)
                    for arn in region_device_arns
                    if arn not in device_map
                }
            )
        devices = list(device_map.values())
        devices.sort(key=lambda x: getattr(x, order_by))
        return devices
