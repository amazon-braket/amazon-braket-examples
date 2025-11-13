from braket.circuits import Circuit
from braket.circuits.observable import Observable
from braket.circuits.observables import I,Z,X,Y, Sum, TensorProduct, StandardObservable, Hermitian
from braket.program_sets import ProgramSet, CircuitBinding
from braket.parametric import Parameterizable
from braket.tasks import ProgramSetQuantumTaskResult
from braket.devices import Device, LocalSimulator
import numpy as np
from itertools import product
import warnings
from braket.quantum_information import PauliString
from tools.observable_tools import pauli_grouping
from tools.observable_tools import matrix_to_pauli, sum_to_pauli
from collections.abc import Callable

PROGRAM_SET_LIMIT = 100
SUPPORTED_OBSERVABLES = (Observable, TensorProduct, Sum, list)

def distribute_uneven():
    pass

def _zip_to_pset(
        obj_list : list[tuple[Circuit,list[float],Observable]], 
        shots_per_executable : int = None):
    """ zip an object list to a ProgramSet """
    inputs = dict(
        zip(
            ["circuits","input_sets","observables"],
            zip(*obj_list)
        )
    )
    return ProgramSet.zip(**inputs, shots_per_executable=shots_per_executable)

def distribute_to_program_sets(
        circs : list[Circuit],
        observables : list[Observable],
        parameters : list[Parameterizable],
        programs : list[Circuit | CircuitBinding] | None = None,
        shots_per_executable : int | list = 100,  
        verbose : bool = False, 
        ) -> list[ProgramSet]:
    """ convert (circuits, observables, parameters) to valid program sets based on program set limits 

    """
    n_circ = len(circs)
    n_para = len(parameters)
    n_obs = len(observables)
    
    if verbose:
        if n_circ * n_para * n_obs > PROGRAM_SET_LIMIT: 
            print(f"-- {n_circ * n_para * n_obs} tasks required: splitting up into multiple program sets. ")
        else:
            print(f"-- able to include {n_circ * n_para * n_obs} tasks in a single program set ")
    temp = []
    psets = programs if not programs else [] 
    for item in product(circs, parameters, observables):
        if len(temp) == PROGRAM_SET_LIMIT:
            psets.append(_zip_to_pset(temp, shots_per_executable=shots_per_executable))
            temp = []
        temp.append(item)
    if len(temp) > 0:
        psets.append(_zip_to_pset(temp, shots_per_executable=shots_per_executable))
    return psets

def probs_to_ev(probabilities : dict, pauli_string : str | dict | PauliString) -> float:
    """ process the measurement outcome for a pauli observable """
    match pauli_string:
        case str():
            non_trivial = [n for n,k in enumerate(pauli_string) if k!="I"]
        case dict():
            non_trivial =  dict.keys()
        case PauliString():
            non_trivial = PauliString._nontrivial
        case _:
            raise NotImplementedError(f"unsupported {type(pauli_string)} format for conversion")
    return sum(
        [v*(-1)**sum([k[n]=="1" for n in non_trivial])  for k,v in probabilities.items() ]
    )

def process_program_sets(
        pset_results : list[ProgramSetQuantumTaskResult], 
        observables : list[Observable | None],
        output_type : str = "expectation",
        measurement_filter : Callable | None = None,
        ):
    """ process a list of program sets """
    results = []
    n_bases = len(observables)
    index = 0
    for pset in pset_results:
        for entry in pset: 
            data = entry[0].probabilities
            if measurement_filter: # apply! 
                data = measurement_filter(data)
            if output_type == "bitstrings" or observables[index % n_bases] is None:
                results.append(data)
            else:
                results.append(sum(
                    [c * probs_to_ev(data,p) for (c,p) in observables[index % n_bases]])
                    )
            index+=1
    return results

def run_with_program_sets(        
        circuits : list[Circuit],
        measurement_bases : list[Observable],
        observables_per_basis : list[list[Observable] | None],
        parameters : list[list[Parameterizable]],
        device : Device | None = None, 
        shots_per_executable : int | list = 100,  
        measurement_filter : Callable | None = None,
        verbose : bool = False, 
        ) -> list:
    """ execute a constant measurement overhead workload with program sets 
    
    Args:
        circuits (Circuit):
        measurement_bases (list): list of Observable bases to measure in
        basis_observable (list): list of (optional) list of Observables to average over per basis
            if None, 
        parameters (list) : variations to be executed over 
        device (Device) : device to run simulations on; default to local simulator 
        shots_per_executable (int) : shots to run - assume same per executable 
        measurement_filter (Callable) : optional function to process raw measurements 
        verbose

    Examples:
        >>> meas_basis = [
        >>>     Z() @ Z(),
        >>>     X() @ X()]
        >>> basis_obs   = [
        >>>     [Z(), Z()],
        >>>     [X() @ X()],
        >>> ]
        >>> basis_obs = [None, None] # returns the distributions 
    """

    assert len(observables_per_basis) == len(measurement_bases)
    psets = distribute_to_program_sets(
        circuits = circuits,
        observables= measurement_bases,
        parameters = parameters,
        shots_per_executable=shots_per_executable,
        verbose = verbose
    )
    pset_results = []
    for pset in psets:
        pset_results.append(device.run(pset).result())  # noqa: PERF401

    result = process_program_sets(
        pset_results=pset_results,
        observables= observables_per_basis, 
        measurement_filter= measurement_filter,
            )
    return np.reshape(
        result, 
        (len(circuits), len(parameters), len(measurement_bases))
        )

    
