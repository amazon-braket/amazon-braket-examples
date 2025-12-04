from braket.circuits import Circuit
from mitiq.executor import Executor
from braket.devices import Device
from braket.circuits.circuit import subroutine
import numpy as np
from braket.program_sets import ProgramSet
from mitiq import MeasurementResult
from braket.tasks import ProgramSetQuantumTaskResult, GateModelQuantumTaskResult
from braket.circuits.compiler_directives import EndVerbatimBox, StartVerbatimBox
from functools import partial
from mitiq.rem import mitigate_measurements
from collections.abc import Callable
from braket.program_sets import CircuitBinding

"""
mitiq_braket_tools.py

Contains three executors ->
    
braket_measurement_executor: 
    returns MeasurementResult objects for use with mitiq observables
braket_counts_executor: 
    returns raw measurement counts
braket_expectation_executor: 
    returns expectation values from **braket** observables

"""


def _braket_result_to_mitiq_meas_result(
        result :GateModelQuantumTaskResult | ProgramSetQuantumTaskResult,
        ) -> MeasurementResult | list[MeasurementResult]:
    """ convert Braket result type to mitiq result type 
    
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
            raise NotImplementedError(f"result type {type(result)} conversion to mitiq not supported")

def _verbatim_pass(
        program : Circuit,
    ) -> Circuit:
    """ makes sure the circuit is verbatim """
    for ins in program.instructions:
        if isinstance(ins, StartVerbatimBox):
            return program
    return Circuit().add_verbatim_box(program)


# def _execute_counts_batch(
#         device : Device, 
#         programs : list[Circuit],
#         shots : int,
#         verbatim : bool = True,
#         ) -> list[MeasurementResult]:
#     if isinstance(programs, Circuit):
#         programs = [programs]
#     if verbatim:
#         programs = [_verbatim_pass(program) for program in programs]
#     result = device.run(
#         ProgramSet(programs, shots_per_executable = shots // len(programs))
#                         ).result()
#     return [
#         MeasurementResult.from_counts(item.counts) for entry in result for item in entry.entries]

def _execute_expectation_batch(
        device : Device, 
        programs : list[Circuit],
        observable,
        shots : int,
        verbatim : bool = True,
        ) -> list[float]:
    if isinstance(programs, Circuit):
        programs = [programs]
    if verbatim:
        programs = [_verbatim_pass(program) for program in programs]
    # Add expectation measurement to each circuit
    result = device.run(ProgramSet.zip(
        programs, observables= [observable] * len(programs),
        shots_per_executable = shots // len(programs)
            )
        ).result()
    return [item.expectation for entry in result for item in entry.entries]

def _execute_via_program_set(
        device : Device, 
        programs : list[Circuit],
        shots : int,
        verbatim : bool = True,
        ) -> list[MeasurementResult]:
    if isinstance(programs, Circuit):
        programs = [programs]
    if verbatim:
        programs = [_verbatim_pass(program) for program in programs]
    result = device.run(
        ProgramSet(programs, shots_per_executable = shots // len(programs))
                        ).result()
    results = _braket_result_to_mitiq_meas_result(result)
    return results if isinstance(results, list) else [results]

def _execute_via_programs(
        device : Device, 
        program : Circuit,
        shots : int,
        verbatim : bool = True
        ) -> MeasurementResult:
    if not isinstance(program, Circuit):
        raise TypeError("need to provide individual circuits ")
    if verbatim:
        program = _verbatim_pass(program)
    return _braket_result_to_mitiq_meas_result(device.run(program, shots = shots).result())

def braket_measurement_executor(
        device : Device,
        shots : int,
        verbatim : bool = True,
        batch_if_possible : bool = True,
                          ) -> Executor:
    """ Executor that returns MeasurementResult objects for use with **mitiq** observables

    Args:
        device (Device): Braket quantum device or simulator 
        shots (int): **total** numb=er of shots, will be distributed to the number of batches 
        verbatim (bool): whether or not to utilize verbatim circuits

    """
    for action in device.properties.action:
        if "PROGRAM_SET" in action.name and batch_if_possible:
            max_programs = device.properties.action[action].maximumExecutables
            return Executor(
                partial(_execute_via_program_set, device, shots=shots, verbatim=verbatim),
            max_batch_size=max_programs)
    return Executor(
        partial(_execute_via_programs, device, shots=shots, verbatim=verbatim))

"""
main executor functions 
"""


def braket_expectation_executor(
        device : Device,
        observable,
        shots : int,
        verbatim : bool = True,
        batch_if_possible : bool = True,
                          ) -> Executor:
    """ Executor that computes expectation values from **Braket** observables

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
    
    for action in device.properties.action:
        if "PROGRAM_SET" in action.name and batch_if_possible:
            max_programs = device.properties.action[action].maximumExecutables
            return Executor(
                partial(_execute_expectation_batch, device, observable=observable, shots=shots, verbatim=verbatim),
                max_batch_size=max_programs)
    return Executor(_execute_expectation)


"""
tools for helping with readout mitigation with mitiq
"""


def process_readout_twirl(
        counts : dict, 
        index : int, 
        bit_masks : list | np.ndarray
        ):
    """ """
    i = _spell_check(index, getattr(bit_masks, "shape", None))
    bit_mask = bit_masks[i] 

    def _bit_addition(k,j):
        return ''.join(str(int(a) ^ int(b)) for a, b in zip(k, bit_mask))
    return {_bit_addition(k,bit_mask):v for k,v in counts.items()}



def _spell_check(i : int, shape : tuple) -> tuple:
    total = ()
    for n in shape[::-1]:
        total = (i % n,) + total
        i = i // n
    return total



def braket_rem_twirl_mitigator(
        inverse_confusion_matrix : np.ndarray = None,
        bit_masks : np.ndarray = None,
        ) -> Callable:
    """ return a function to modify a count with a inverse confusion matrix """
    
    def to_run(counts : dict, index : int) -> dict:
        return mitigate_measurements(
            MeasurementResult.from_counts(
                process_readout_twirl(counts, index, bit_masks)
                ),
            inverse_confusion_matrix=inverse_confusion_matrix
            ).prob_distribution()

    return to_run

if __name__ == "__main__":
    pass

