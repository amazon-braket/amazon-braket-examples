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
from itertools import product, repeat
from braket.circuits.observables import Sum
from braket.circuits.serialization import IRType
from copy import deepcopy as dc
PROGRAM_SET_LIMIT = 100
SUPPORTED_OBSERVABLES = (Observable, TensorProduct, Sum, list)
from tools.observable_tools import tensor_from_string

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
        circs : list[Circuit] ,
        parameters : list[dict],
        observables : list[Observable],
        programs : list[Circuit | CircuitBinding] | None = None,
        shots_per_executable : int | list = 100,  
        verbose : bool = False, 
        ) -> list[ProgramSet]:
    """ convert (circuits, observables, parameters) to valid program sets based on program set limits 

    """
    # Handle numpy arrays
    if isinstance(circs, np.ndarray):
        circs = circs.flatten().tolist()


    if isinstance(observables, np.ndarray):
        observables = observables.flatten().tolist()
    
    n_circ = len(circs)
    n_para = len(parameters) if parameters else 1 
    n_obs = len(observables)
    
    if verbose:
        if n_circ * n_para * n_obs > PROGRAM_SET_LIMIT: 
            print(f"-- {n_circ * n_para * n_obs} tasks required: splitting up into multiple program sets. ")
        else:
            print(f"-- able to include {n_circ * n_para * n_obs} tasks in a single program set ")
    temp = []
    psets = programs if programs else [] 
    for item in product(circs, parameters, observables):
        item = dc(item)
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
        shape : tuple | None = None, 
        ):
    """ process a list of program sets """
    results = []
    n_bases = len(observables)
    index = 0
    for pset in pset_results:
        for entry in pset: 
            data = entry[0].probabilities
            if measurement_filter: 
                data = measurement_filter(data, index)
            if output_type == "bitstrings" or observables[index % n_bases] is None:
                results.append(data)
            else:
                results.append(sum(
                    [c * probs_to_ev(data,p) for (c,p) in observables[index % n_bases]])
                    )
            index+=1
    return results


def run_with_program_sets(        
        circuits : list[Circuit] | np.ndarray,
        measurement_bases : list[Observable] | np.ndarray,
        observables_per_basis : list[list[Observable] | None] | np.ndarray,
        parameters : list[list[Parameterizable]] | np.ndarray,
        device : Device | None = None, 
        shots_per_executable : int | list = 100,  
        measurement_filter : Callable | None = None,
        verbose : bool = False, 
        ) -> np.ndarray:
    """ distribute and execute via program sets 
    
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

    Returns:
        np.ndarray : array of dimension (circuits.shape) + (params.shape) + (bases.shape)
        
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
    if device is None:
        device = LocalSimulator()
    # flatten numpy arrays while preserving shape 
    if isinstance(circuits, np.ndarray):
        circuits_shape = circuits.shape
        circuits_flat = circuits.flatten().tolist()
    else:
        circuits_shape = (len(circuits),)
        circuits_flat = circuits

    if hasattr(device, "_noise_model"): # HACKY PLS REMOVE K THX
        circuits_flat = [device._noise_model.apply(c) for c in circuits_flat]
    if isinstance(measurement_bases, np.ndarray):
        bases_shape = measurement_bases.shape
        measurement_bases = measurement_bases.flatten().tolist()
    else:
        bases_shape = (len(measurement_bases),)
    if isinstance(parameters, np.ndarray):
        params_shape = parameters.shape
        parameters = parameters.flatten().tolist()
    else:
        params_shape = (len(parameters),)

    if isinstance(observables_per_basis, np.ndarray):
        observables_per_basis = observables_per_basis.flatten().tolist()    
    assert len(observables_per_basis) == len(measurement_bases)

    measurement_bases = [tensor_from_string(b) for b in measurement_bases]

    psets = distribute_to_program_sets(
        circs = circuits_flat,
        observables= measurement_bases,
        parameters = parameters,
        shots_per_executable=shots_per_executable,
        verbose = verbose
    )
    pset_results = []
    for pset in psets: # potential for catching errors later here
        pset_results.append(device.run(  # noqa: PERF401
            pset, shots=pset.total_executables * pset.shots_per_executable).result()) 
    
    result = process_program_sets(
        pset_results=pset_results,
        observables= observables_per_basis, 
        measurement_filter= measurement_filter,
            )
    # Reshape to match original dimensions
    result_shape = circuits_shape + params_shape + bases_shape
    return np.reshape(result, result_shape)


def print_program_set(program_set, result=None):
    """Prints the program set and its result 
    
    From ``braket_features/program_sets/01_Getting_Started_with_Program_Sets.ipynb``
    
    Args:
        program_set: ProgramSet
        result: ProgramSetQuantumTaskResult
    
    """
    if result is not None:
        assert len(program_set) == len(result), "program_set and result must have the same length"
        print_result = True
    else:
        result = repeat((None,))
        print_result = False
    
    for i, (program, program_result) in enumerate(zip(program_set, result)):
        if isinstance(program, Circuit):
            circuit = program
            input_sets = None
            observables = None
        elif isinstance(program, CircuitBinding):
            circuit = program.circuit
            input_sets = program.input_sets
            observables = program.observables
            
        if isinstance(observables, Sum):
            sum_observable = True
            observable_list = observables.summands
        else:
            sum_observable = False
            observable_list = observables
            
        
        print(f"circuit {i}")
        print(circuit)
        
        if not print_result:
            program_result = repeat((None,))
        for j, (execution_result, (input_set, observable)) in enumerate(
            zip(
                program_result,
                product(
                    input_sets.as_list() if input_sets else (None,), 
                    observable_list if observable_list else (None,),
                )
            )
        ):
            print(f"execution {j}") 
            if input_set:
                print("\tinput_set:", input_set)
            # if observable is not None:
                # print("\tobservable:", observable.to_ir(ir_type=IRType("OPENQASM")))
            if print_result: 
                print("\tresult: ", execution_result.counts, end='')
                if observable is not None:
                    print(", expectation:", execution_result.expectation, end='')
                print()
        if sum_observable:
            print("sum observable:", observables.to_ir(ir_type=IRType("OPENQASM")))
            if print_result:
                print("\tresult: expectation:", program_result.expectation(), end='')
            print()
        print('-'*80)
    print(f"Total executions: {program_set.total_executables}")
