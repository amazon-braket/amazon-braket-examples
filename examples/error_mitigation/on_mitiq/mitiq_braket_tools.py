# Please note, the items in this director 

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
from typing import Callable
from tools.mitigation_tools import process_readout_twirl

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
            return MeasurementResult.from_counts(result.measurement_probabilities)
        case ProgramSetQuantumTaskResult():
            measurement_results = []
            for entry in result:
                for item in entry.entries:
                    measurement_results.extend(
                        MeasurementResult.from_counts(item.counts))
            return measurement_results
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
    return _braket_result_to_mitiq_meas_result(result)

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

def braket_executor(
        device : Device,
        shots : int,
        verbatim : bool = True,
                          ) -> Executor:
    """ Simple execution of a mitiq protocol via Braket ; observables supported via mitiq

    Args:
        device (Device): Braket quantum device or simulator 
        shots (int): **total** number of shots, will be distributed to the number of batches 
        verbatim (bool): whether or not to utilize verbatim circuits. if True, circuits need to match
            the current device topology and characteristics. assuming inputs are compatible. 

    """

    for action in device.properties.action:
        if "PROGRAM_SET" in action.name:
            max_programs = device.properties.action[action].maximumExecutables
        return Executor(
            partial(_execute_via_program_set, shots=shots, verbatim=verbatim),
            max_batch_size=max_programs)
    return Executor(
        partial(_execute_via_programs,shots=shots, verbatim=verbatim))



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



def test_braket_executor():
    """Test the braket executor with local simulator"""
    from braket.devices import LocalSimulator
    
    # Create simple test circuit
    circuit = Circuit().h(0).cnot(0, 1)
    
    # Test with local simulator
    device = LocalSimulator()
    executor = braket_executor(device, shots=100, verbatim=False)
    
    # Execute circuit
    result = executor([circuit])[0]
    
    # Basic validation
    assert isinstance(result, MeasurementResult)
    assert len(result.bitstrings) > 0
    print(f"Test passed: Got {len(result.bitstrings)} measurements")

if __name__ == "__main__":
    test_braket_executor()


