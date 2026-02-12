import os
import sys
from collections.abc import Callable
from functools import partial

import mitiq
import numpy as np
from mitiq import MeasurementResult
from mitiq.executor import Executor
from mitiq.rem import mitigate_measurements

from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.circuits.compiler_directives import StartVerbatimBox
from braket.devices import Device
from braket.program_sets import ProgramSet
from braket.tasks import GateModelQuantumTaskResult, ProgramSetQuantumTaskResult

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))  # parent

from tools.mitigation_tools import process_readout_twirl

"""
mitiq_braket_tools.py

Contains:
    
braket_measurement_executor: 
    returns MeasurementResult objects for use with mitiq observables
braket_expectation_executor: 
    returns expectation values from **braket** observables
braket_rem_twirl_mitigator:
    assistant to help apply an inverse confusion matrix with a readout twirl 
"""


def braket_measurement_executor(
    device: Device | AwsDevice,
    shots: int,
    verbatim: bool = True,
    batch_if_possible: bool = True,
) -> Executor:
    """Executor that returns MeasurementResult objects for use with **mitiq** observables

    Args:
        device (Device): Braket quantum device or simulator
        shots (int): **total** number of shots, will be distributed to the number of batches
        verbatim (bool): whether or not to utilize verbatim circuits

    """
    if hasattr(device, "aws_session"):
        device.aws_session.add_braket_user_agent = f"mitiq-braket-tools/mitiq-{mitiq.__version__}"
    for action in device.properties.action:
        if "PROGRAM_SET" in action.name and batch_if_possible:
            max_programs = device.properties.action[action].maximumExecutables
            return Executor(
                partial(_execute_via_program_set, device, shots=shots, verbatim=verbatim),
                max_batch_size=max_programs,
            )
    return Executor(partial(_execute_via_programs, device, shots=shots, verbatim=verbatim))


def braket_expectation_executor(
    device: Device | AwsDevice,
    observable,
    shots: int,
    verbatim: bool = True,
    batch_if_possible: bool = True,
) -> Executor:
    """Executor that computes expectation values from **Braket** observables

    Args:
        device (Device): Braket quantum device or simulator
        observable: Braket observable to measure
        shots (int): number of shots per circuit
        verbatim (bool): whether or not to utilize verbatim circuits

    """

    def _execute_expectation(circuit) -> float:
        if verbatim:
            circuit = _verbatim_pass(circuit)
        task = device.run(circuit + Circuit().expectation(observable), shots=shots)
        result = task.result()
        return result.values[0]

    if hasattr(device, "aws_session"):
        device.aws_session.add_braket_user_agent = f"mitiq-braket-tools/mitiq-{mitiq.__version__}"

    for action in device.properties.action:
        if "PROGRAM_SET" in action.name and batch_if_possible:
            max_programs = device.properties.action[action].maximumExecutables
            return Executor(
                partial(
                    _execute_expectation_batch,
                    device,
                    observable=observable,
                    shots=shots,
                    verbatim=verbatim,
                ),
                max_batch_size=max_programs,
            )
    return Executor(_execute_expectation)


def braket_rem_twirl_mitigator(
    inverse_confusion_matrix: np.ndarray = None,
    bit_masks: np.ndarray = None,
) -> Callable:
    """return a function to modify a count with a inverse confusion matrix"""

    def to_run(counts: dict, index: int) -> dict:
        return mitigate_measurements(
            MeasurementResult.from_counts(process_readout_twirl(counts, index, bit_masks)),
            inverse_confusion_matrix=inverse_confusion_matrix,
        ).prob_distribution()

    return to_run


def _braket_result_to_mitiq_meas_result(
    result: GateModelQuantumTaskResult | ProgramSetQuantumTaskResult,
) -> MeasurementResult | list[MeasurementResult]:
    """convert Braket result type to mitiq result type

    Args:
        result (QuantumTaskResults):

    Returns:
        invidividual or list of mitiq.MeausurementResult objects
    """
    match result:
        case GateModelQuantumTaskResult():
            return MeasurementResult.from_counts(result.measurement_counts)
        case ProgramSetQuantumTaskResult():
            return [
                MeasurementResult.from_counts(item.counts)
                for entry in result
                for item in entry.entries
            ]
        case _:
            raise NotImplementedError(
                f"result type {type(result)} conversion to mitiq not supported"
            )


def _verbatim_pass(
    program: Circuit,
) -> Circuit:
    """makes sure the circuit is verbatim"""
    for ins in program.instructions:
        if isinstance(ins, StartVerbatimBox):
            return program
    return Circuit().add_verbatim_box(program)


def _execute_expectation_batch(
    device: Device,
    programs: list[Circuit],
    observable,
    shots: int,
    verbatim: bool = True,
) -> list[float]:
    if isinstance(programs, Circuit):
        programs = [programs]
    if verbatim:
        programs = [_verbatim_pass(program) for program in programs]
    # Add expectation measurement to each circuit
    result = device.run(
        ProgramSet.zip(
            programs,
            observables=[observable] * len(programs),
            shots_per_executable=shots // len(programs),
        )
    ).result()
    return [item.expectation for entry in result for item in entry.entries]


def _execute_via_program_set(
    device: Device,
    programs: list[Circuit],
    shots: int,
    verbatim: bool = True,
) -> list[MeasurementResult]:
    if isinstance(programs, Circuit):
        programs = [programs]
    if verbatim:
        programs = [_verbatim_pass(program) for program in programs]
    result = device.run(ProgramSet(programs, shots_per_executable=shots // len(programs))).result()
    results = _braket_result_to_mitiq_meas_result(result)
    return results if isinstance(results, list) else [results]


def _execute_via_programs(
    device: Device | AwsDevice, program: Circuit, shots: int, verbatim: bool = True
) -> MeasurementResult:
    if not isinstance(program, Circuit):
        raise TypeError("need to provide individual circuits ")
    if verbatim:
        program = _verbatim_pass(program)
    return _braket_result_to_mitiq_meas_result(device.run(program, shots=shots).result())
