from collections.abc import Callable
from copy import deepcopy as dc
from itertools import product
from math import pi

import numpy as np

from braket.circuits import Circuit
from braket.circuits.observable import Observable
from braket.devices import Device, LocalSimulator
from braket.parametric import Parameterizable
from braket.program_sets import CircuitBinding, ProgramSet
from braket.tasks import ProgramSetQuantumTaskResult

PROGRAM_SET_LIMIT = 100

STANDARD_CONVERSION = {
    "X": lambda i : Circuit().h(i), #.measure(i), 
    "Y": lambda i : Circuit().si(i).h(i), #.measure(i),
    "Z": lambda i : Circuit(), #.measure(i),
    "I": lambda i : Circuit(), #.measure(i),
}

ANKAA_CONVERSION = {
    "X" : lambda i : Circuit().rz(i,pi/2).rx(i,np.pi/2), #.measure(i),
    "Y": lambda i : Circuit().rx(i,pi/2), #.measure(i),
    "Z": lambda i : Circuit(), #.measure(i),
    "I": lambda i : Circuit(), #.measure(i),
}

def _convert_circuit(
        circuit : Circuit, 
        parameter : dict, 
        pstr : str, 
        conversion = None,
        verbatim : bool = False) -> Circuit:
    """ """
    qubits = sorted(circuit.qubits)
    if qubits is None:
        qubits = range(len(pstr))

    basis = Circuit()
    for q,p in zip(qubits,pstr):
        if p=="I":
            continue
        basis+= conversion[p](q)

    circ = circuit.make_bound_circuit(parameter) + basis
    if verbatim:
        circ = Circuit().add_verbatim_box(circ)
    return circ.measure(qubits)

def _zip_to_pset(
        obj_list : list[tuple[Circuit,list[float],Observable]], 
        shots_per_executable : int = None,
        conversion : dict[str,Callable] = None,
        verbatim : bool = False):
    """ zip an object list to a ProgramSet """
    if conversion is None:
        conversion = STANDARD_CONVERSION
    circuits = [
        _convert_circuit(c,p,o,conversion=conversion, verbatim = verbatim) for c,p,o in zip(*zip(*obj_list))
    ]
    return ProgramSet(circuits
        , shots_per_executable=shots_per_executable)

def distribute_to_program_sets(
        circs : np.ndarray[Circuit] ,
        parameters : np.ndarray[dict],
        observables : np.ndarray[str],
        programs : list[Circuit | CircuitBinding] | None = None,
        shots_per_executable : int | list = 100,  
        conversion : dict[str,Callable] = None,
        verbatim : bool = False,
        ) -> list[ProgramSet]:
    """ convert circuits + parameters + observables to valid program sets based on program set limits 
    
    """
    n_circ = len(circs)
    n_para = len(parameters) if parameters else 1 
    n_obs = len(observables)
    
    if n_circ * n_para * n_obs > PROGRAM_SET_LIMIT: 
        print(f"-- {n_circ * n_para * n_obs} tasks required: splitting up into multiple program sets. ")
    else:
        print(f"-- able to include {n_circ * n_para * n_obs} tasks in a single program set ")
    temp = []
    psets = programs if programs else [] 
    for t, item in enumerate(product(circs, parameters, observables),1):
        item = dc(item)
        temp.append(item)
        if len(temp) == PROGRAM_SET_LIMIT or t==n_circ * n_para * n_obs:
            psets.append(
                _zip_to_pset(
                    temp, 
                    shots_per_executable=shots_per_executable,
                    conversion = conversion,
                    verbatim = verbatim))
            temp = []
    return psets

def _probs_to_ev(probabilities : dict, pauli_string : str ) -> float:
    """ process the measurement outcome for a pauli observable """
    match pauli_string:
        case str():
            non_trivial = [n for n,k in enumerate(pauli_string) if k!="I"]
        case _:
            raise NotImplementedError(f"unsupported {type(pauli_string)} format for conversion")
    return sum(
        [v*(-1)**sum([k[n]=="1" for n in non_trivial])  for k,v in probabilities.items() ]
    )

def _process_program_sets(
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
            if measurement_filter:
                data = measurement_filter(entry[0].counts, index = index)
            else:
                data = entry[0].probabilities
            if output_type == "bitstrings" or observables[index % n_bases] is None:
                results.append(data)
            else:
                temp = 0
                for (c,p) in observables[index % n_bases]:
                    temp += c * _probs_to_ev(data,p)
                results.append(temp)
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
        conversion : dict[str,Callable] = None,
        return_program_sets : bool = False, 
        verbatim : bool = False,
        ) -> np.ndarray:
    """ distribute and execute (circuits * bases * parameters) via program sets 
    
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
            - Optionally, may have 1 more dimension with variances. 

        
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
    # flatten arrays while remembering the shape 
    if isinstance(circuits, np.ndarray):
        circuits_shape = circuits.shape
        circuits_flat = circuits.flatten().tolist()
    else:
        circuits_shape = (len(circuits),)
        circuits_flat = circuits

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
    total_shape = circuits_shape + params_shape + bases_shape

    if isinstance(observables_per_basis, np.ndarray):
        observables_per_basis = observables_per_basis.flatten().tolist()    
    assert len(observables_per_basis) == len(measurement_bases)

    psets = distribute_to_program_sets(
        circs = circuits_flat,
        observables= measurement_bases,
        parameters = parameters,
        shots_per_executable=shots_per_executable,
        conversion=conversion,
        verbatim = verbatim,
    )
    pset_results = []
    print('running program sets....')
    for n,pset in enumerate(psets): # potential for catching errors in failed PSETs here
        print(f'-- running program set {n+1}/{len(psets)}')
        pset_results.append(device.run(  # noqa: PERF401
            pset, shots=pset.total_executables * pset.shots_per_executable).result()) 
    result = _process_program_sets(
        pset_results=pset_results,
        observables= observables_per_basis, 
        measurement_filter= measurement_filter,
            )
    if return_program_sets:
        return np.reshape(result, total_shape), psets
    return np.reshape(result, total_shape) # reshape to original dimension
