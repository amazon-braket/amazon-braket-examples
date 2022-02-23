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

from functools import singledispatch
from typing import Optional, Set, Union

import pkg_resources

from braket.annealing.problem import Problem
from braket.circuits import Circuit
from braket.circuits.circuit_helpers import validate_circuit_and_shots
from braket.device_schema import DeviceActionType, DeviceCapabilities
from braket.devices.device import Device
from braket.simulator import BraketSimulator
from braket.tasks import AnnealingQuantumTaskResult, GateModelQuantumTaskResult
from braket.tasks.local_quantum_task import LocalQuantumTask

_simulator_devices = {
    entry.name: entry for entry in pkg_resources.iter_entry_points("braket.simulators")
}


class LocalSimulator(Device):
    """A simulator meant to run directly on the user's machine.

    This class wraps a BraketSimulator object so that it can be run and returns
    results using constructs from the SDK rather than Braket IR.
    """

    def __init__(self, backend: Union[str, BraketSimulator] = "default"):
        """
        Args:
            backend (Union[str, BraketSimulator]): The name of the simulator backend or
                the actual simulator instance to use for simulation. Defaults to the
                `default` simulator backend name.
        """
        delegate = _get_simulator(backend)
        super().__init__(
            name=delegate.__class__.__name__,
            status="AVAILABLE",
        )
        self._delegate = delegate

    def run(
        self,
        task_specification: Union[Circuit, Problem],
        shots: int = 0,
        *args,
        **kwargs,
    ) -> LocalQuantumTask:
        """Runs the given task with the wrapped local simulator.

        Args:
            task_specification (Union[Circuit, Problem]):
            shots (int, optional): The number of times to run the circuit or annealing problem.
                Default is 0, which means that the simulator will compute the exact
                results based on the task specification.
                Sampling is not supported for shots=0.
            *args: Positional args to pass to the `BraketSimulator`
            **kwargs: Keyword arguments to pass to the `BraketSimulator`

        Returns:
            LocalQuantumTask: A LocalQuantumTask object containing the results
            of the simulation

        Note:
            If running a circuit, the number of qubits will be passed
            to the backend as the argument after the circuit itself.

        Examples:
            >>> circuit = Circuit().h(0).cnot(0, 1)
            >>> device = LocalSimulator("default")
            >>> device.run(circuit, shots=1000)
        """
        result = _run_internal(task_specification, self._delegate, shots, *args, **kwargs)
        return LocalQuantumTask(result)

    @property
    def properties(self) -> DeviceCapabilities:
        """DeviceCapabilities: Return the device properties

        Please see `braket.device_schema` in amazon-braket-schemas-python_

        .. _amazon-braket-schemas-python: https://github.com/aws/amazon-braket-schemas-python"""
        return self._delegate.properties

    @staticmethod
    def registered_backends() -> Set[str]:
        """Gets the backends that have been registered as entry points

        Returns:
            Set[str]: The names of the available backends that can be passed
            into LocalSimulator's constructor
        """
        return set(_simulator_devices.keys())


@singledispatch
def _get_simulator(simulator):
    raise TypeError("Simulator must either be a string or a BraketSimulator instance")


@_get_simulator.register
def _(backend_name: str):
    if backend_name in _simulator_devices:
        device_class = _simulator_devices[backend_name].load()
        return device_class()
    else:
        raise ValueError(f"Only the following devices are available {_simulator_devices.keys()}")


@_get_simulator.register
def _(backend_impl: BraketSimulator):
    return backend_impl


@singledispatch
def _run_internal(
    task_specification, simulator: BraketSimulator, shots: Optional[int] = None, *args, **kwargs
):
    raise NotImplementedError(f"Unsupported task type {type(task_specification)}")


@_run_internal.register
def _(circuit: Circuit, simulator: BraketSimulator, shots, *args, **kwargs):
    if DeviceActionType.JAQCD not in simulator.properties.action:
        raise NotImplementedError(f"{type(simulator)} does not support qubit gate-based programs")
    validate_circuit_and_shots(circuit, shots)
    program = circuit.to_ir()
    qubits = circuit.qubit_count
    results = simulator.run(program, qubits, shots, *args, **kwargs)
    return GateModelQuantumTaskResult.from_object(results)


@_run_internal.register
def _(problem: Problem, simulator: BraketSimulator, shots, *args, **kwargs):
    if DeviceActionType.ANNEALING not in simulator.properties.action:
        raise NotImplementedError(f"{type(simulator)} does not support quantum annealing problems")
    ir = problem.to_ir()
    results = simulator.run(ir, shots, *args, *kwargs)
    return AnnealingQuantumTaskResult.from_object(results)
