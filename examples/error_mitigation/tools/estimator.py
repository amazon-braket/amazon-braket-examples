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

PSET_LIMIT = 100

def _zip_to_pset(obj_list : list, shots_per_executable = None):
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
        shots_per_executable : int | list = 100,  
        verbose : bool = False, 
        ) -> list[ProgramSet]:
    """ convert (circuits, observables, parameters) to valid program sets based on program set limits 

    """
    n_circ = len(circs)
    n_para = len(parameters)
    n_obs = len(observables)
    
    if verbose:
        if n_circ * n_para * n_obs > PSET_LIMIT: 
            print(f"-- {n_circ * n_para * n_obs} tasks required: splitting up into multiple program sets. ")
        else:
            print(f"-- able to include {n_circ * n_para * n_obs} tasks in a single program set ")
    temp = []
    psets = []
    for item in product(circs, parameters, observables):
        if len(temp) == PSET_LIMIT:
            psets.append(_zip_to_pset(temp, shots_per_executable=shots_per_executable))
            temp = []
        temp.append(item)
    if len(temp) > 0:
        psets.append(_zip_to_pset(temp, shots_per_executable=shots_per_executable))
    return psets

def run_program_sets(psets : list[ProgramSet], device : Device) -> ProgramSetQuantumTaskResult:
    return [device.run(pset_i).result() for pset_i in psets]


def probs_to_ev(probs : dict, paulis : str) -> float:
    """ process the measurement outcome for a pauli observable """
    non_iden = [n for n,k in enumerate(paulis) if k!="I"]
    return sum(
        [v*(-1)**sum([k[n]=="1" for n in non_iden])  for k,v in probs.items() ]
    )

def process_program_sets_to_evs(
        pset_results : list[ProgramSetQuantumTaskResult], 
        true_observables : list[tuple] = None,
        ):
    """ process a list of program sets """
    evs = []
    n_obs = len(true_observables)
    index = 0
    for pset in pset_results:
        for entry in pset:
            data = entry[0].probabilities
            if true_observables[index % n_obs] is None:
                evs.append(entry[0].expectation)
            else:
                evs.append(sum(
                    [c * probs_to_ev(data,p) for (c,p) in true_observables[index % n_obs]])
                    )
            index+=1
    return evs

class Choragus:
    def __init__(self, 
                backend : Device = None,  
                obs : Observable = None,
                volume : bool = False,
                ):
        """ braket orchestrator for running circuits and jobs via program sets """
        if backend is None:
            backend = LocalSimulator()
        self._obs_circ, self._obs_full = self._process_observavble(obs)
        self.v = volume

    def _process_observable(self, obs : Observable):
        return obs, obs
    
    def __call__(self, 
                 circuits : Circuit | list[Circuit],
                 input_sets : list[dict] = None,
                 shots_per_executable : int = 100, 
                 ) -> list[float]:
        if isinstance(circuits, Circuit):
            circuits = [circuits]
        if input_sets is None:
            input_sets = [{}]
        psets = distribute_to_program_sets(
            circuits,
            self._obs_circ, 
            parameters = input_sets,
            shots_per_executable = shots_per_executable
        )
        pset_results = run_program_sets(psets)
        return process_program_sets_to_evs(
            pset_results = pset_results,
            true_observables = self._obs_full)

