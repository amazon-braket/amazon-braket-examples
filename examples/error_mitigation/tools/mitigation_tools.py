import random
from collections import defaultdict
from collections.abc import Callable
from typing import Any

import numpy as np

from braket.circuits import Circuit
from braket.circuits.gates import ISwap
from braket.devices import Device
from braket.program_sets import ProgramSet

ISWAP_TWIRLS = [
    ['i','i','i','i'],
    ['i','x','y','z'],
    ['i','y','x','z'],
    ['i','z','z','i'],
    ['x','i','z','y'],
    ['x','x','x','x'],
    ['x','y','y','x'],
    ['x','z','i','y'],
    ['y','i','z','x'],
    ['y','x','x','y'],
    ['y','y','y','y'],
    ['y','z','i','x'],
    ['z','i','i','z'],
    ['z','x','y','i'],
    ['z','y','x','i'],
    ['z','z','z','z'],
]

def gen_pauli_circ(x : str, i : int ):
    return Circuit().__getattribute__(x.lower())(i)

def _readout_pass(circ : Circuit) -> tuple[Circuit, str]:
    """Apply readout twirling to a single circuit.
    
    Args:
        circ: Input circuit
    
    Returns:
        (Circuit, str) - list of twirled circuits and flip maps
    """
    qubits = sorted([int(q) for q in circ.qubits])
    
    twirled_circ = circ.copy()
    flip_map = ['0'] * len(qubits)
    for n,q in enumerate(qubits):
        pauli = random.choice(['I','X','Y','Z'])
        twirled_circ.add(gen_pauli_circ(pauli, q))
        # if pauli in ["x","y"]:
        flip_map[n] = pauli
    return twirled_circ, "".join(flip_map)


def apply_readout_twirl(
        circ: Circuit | np.ndarray,
        num_samples: int = None,
        ) -> tuple[np.ndarray[Circuit], np.ndarray[str]]:
    """Apply readout twirling to all qubits in circuit.
    
    Args:
        circ: Input circuit or numpy array of type object with circuits 
        num_samples: Number of twirling samples | inferred if input is a numpy array 

    Note: if passing a numpy array, it must be of type object, and will be treated as a list of
    circuits to be twirled. The output will be the same shape as the input.
    
    Returns:
        (list[Circuit], list[dict]) - list of twirled circuits and the Pauli twirls maps
    """
    match circ:
        case Circuit():
            return zip(*[_readout_pass(circ) for _ in range(num_samples)])
        case np.ndarray():
            circuits,bitmasks = np.empty_like(circ), np.empty_like(circ)
            for index,circuit in np.ndenumerate(circ):
                c,b = _readout_pass(circuit)
                circuits[index] = c
                bitmasks[index] = b
            return circuits, bitmasks
        case _:
            raise TypeError(f"Unsupported format {type(circ)} to apply readout error.")

def _index_check(i : int, shape : tuple) -> tuple:
    if shape is None:
        return i
    total = ()
    for n in shape[::-1]:
        total = (i % n,) + total
        i = i // n
    return total

def iden(x):
    return x

def get_twirled_readout_dist(qubits : list, 
                         n_twirls : int = 5,
                         shots : int = 1000,
                         device : Device = None,
                         processor : Callable = None, 
                         ) -> np.ndarray:
    """ get readout distribution through twirling and ProgramSets
    
    qubits : bool = qubits"""
    circuit = Circuit()
    for i in qubits:
        circuit.i(i)

    if processor is None:
        processor = iden
    variants, masks = apply_readout_twirl(circuit, n_twirls)
    pset = ProgramSet(
        [processor(v) for v in variants], 
        shots_per_executable= shots // n_twirls)
    results = device.run(pset, shots = shots).result()
    base = {}
    for item, mask in zip(results, masks):
        mask = "".join("1" if m in ["X","Y"] else "0" for m in mask)
        for k, v in item.entries[0].counts.items():
            kp = ''.join(str(int(a) ^ int(b)) for a, b in zip(k, mask))
            base[kp] = base.get(kp, 0) + v
    base = {k: v / shots for k, v in base.items()}
    return base 

def _bit_addition(b1,b2,nq):
    return '{:0{}b}'.format(int(b1,2)^int(b2,2),nq)

def bit_mul_distribution(dist_a : dict, dist_b : dict, nq : int):
    new = defaultdict(float)
    for k_a,v_a in dist_a.items():
        for k_b,v_b in dist_b.items():
            new[_bit_addition(k_a,k_b, nq)]+= v_a * v_b 
    return new 

def build_inverse_quasi_distribution(
        reference : dict,
        second_order : bool = False) -> tuple[dict[str:float],list]:
    """ from a reference dict, build the inverse quasi distribtuion

    First order approximation starts from tensored inversion of single qubit flips 
    """
    nq = len(next(iter(reference.keys())))
    shots = sum(reference.values())
    q = defaultdict(float)
    q['0'*nq] = 1
    reference = {k:v/shots for k,v in reference.items()}
    # 
    quasi_factors = []
    marginals = np.zeros(nq)
    for k,v in reference.items():
        for n in range(nq):
            marginals[n] += v*(0)**(k[n]=="1") 
    for n,p0 in enumerate(marginals):
        temp = defaultdict(float)
        gamma = 1/(2*p0-1)
        for k,v in q.items():
            kp = k[:n] + "1" + k[n+1:]
            temp[k]+= v*p0*gamma
            temp[kp]-= v*(1-p0)*gamma
            q = temp
        quasi_factors.append(gamma) # -> first order correction 

    if not second_order:
        return q, quasi_factors
    p_q = bit_mul_distribution(q,reference, nq)
    qp = defaultdict(float)
    gamma = 1/(2*p_q['0'*nq]-1)
    assert gamma > 0, f"error threshold exceeded: {reference}, {qp}"
    quasi_factors.append(gamma)
    print(f'effective shot overhead: {quasi_factors}')
    for k,v in p_q.items():
        qp[k] = v*gamma * (-1)**(k != '0'*nq)
    return bit_mul_distribution(qp,q,nq), quasi_factors


def process_readout_twirl(
        counts : dict, 
        index : int | tuple, 
        bit_masks : list | np.ndarray
        ):
    """ apply corrections to a readout twirl """
    if isinstance(index, int):
        index = _index_check(index, getattr(bit_masks, "shape", None))
    if isinstance(bit_masks, np.ndarray):
        assert len(index) == len(bit_masks.shape), "Need to supply a proper bit mask index"
        bit_mask = bit_masks[index]
    else:
        bit_mask = bit_masks[index] if isinstance(index, int) else bit_masks[index[0]] 
    def _bit_addition(k : str,j : str):
        assert len(k)==len(j)
        return ''.join(["0" if a==b else "1" for a,b in zip(k,j)])
    return {_bit_addition(key,bit_mask):v for key,v in counts.items()}

def generate_bit_mask(twirls : np.ndarray, pauli_bases : list) -> np.ndarray:
    """ from observable and twirl, generate bit mask """
    bit_masks = np.zeros(twirls.shape + (1, len(pauli_bases)), dtype=object)
    for n,i in np.ndenumerate(twirls):
        for m,b in enumerate(pauli_bases):
            new = []
            for twirl,base in zip(b, i):
                if base == "I":
                    base == "Z"
                if twirl == base or twirl=="I" or base == "I":
                    new.append("0")
                else:
                    new.append("1")
            bit_masks[n + (0,m)] = "".join(new)
    return bit_masks


def twirl_iswap(circ, repetitions : int = 1) -> list[Circuit]:
    """ apply twirling operation for ISwap gates """
    circuits = [Circuit() for _ in range(repetitions)]
    for ins in circ.instructions:
        if isinstance(ins.operator, ISwap):
            for i in range(repetitions):
                twirl = random.choice(ISWAP_TWIRLS)
                circuits[i]+= gen_pauli_circ(twirl[0],ins.target[0])
                circuits[i]+= gen_pauli_circ(twirl[1],ins.target[1])
                circuits[i].add_instruction(ins)
                circuits[i]+= gen_pauli_circ(twirl[2],ins.target[0])
                circuits[i]+= gen_pauli_circ(twirl[3],ins.target[1])
        else:
            for i in range(repetitions):
                circuits[i].add_instruction(ins)
    return circuits


class SparseReadoutMitigation:
    """ class for applying readout error mitigation to sparse observables

    This happens by 
    - 1. Creating a reduced probability distribution over targeted qubits
    - 2. Apply the appropriate inverse 
    - 3. Calculate the expectation value

    Arguments:

    """
    def __init__(self, 
            readout_distributon : dict,
            correction_method : Callable = None,
            inversion_method : Callable = None, 
            ):
        
        self.inverses = {}
        self.dist = readout_distributon
        if correction_method is None:
            inversion_method = self._standard_inversion
            correction_method = self._standard_correction
        self._inversion_method = inversion_method
        self._apply_correction = correction_method
        self.sq_error = None
        self._gamma = {}

    def _standard_inversion(self, index : tuple[int], **kwargs) -> dict:
        """ given a list of qubits, create a marginal distribution, and get quasi dist """
        if len(index) == 0:
            return self.dist

        temp = defaultdict(lambda : 0)
        for k,v in self.dist.items():
            temp["".join(k[n] for n in index)]+= v

        quasi, gamma  = build_inverse_quasi_distribution(temp, False)
        self._gamma[index] = gamma
        return quasi


    def _standard_correction(self, data : dict, inverse : Any):
        """ apply a given inverse to a distribution """
        tally = sum(list(data.values()))
        data = {k: v/tally for k,v in data.items()}
        return bit_mul_distribution(data, inverse, len(list(data.keys())[0]))
        

    def get_inverse(self, index : tuple):
        """ creates an inverse confusion matrix for a given qubit """
        
        if index not in self.inverses:
            self.inverses[index] = self._inversion_method(index)
        return self.inverses[index]

    def process_single(self, result : dict, index : int, pauli_string : str,
                 bit_masks : np.ndarray) -> float:
        """ """
        non_trivial = [n for n,k in enumerate(pauli_string) if k!="I"]
        temp = process_readout_twirl(result, index, bit_masks)
        temp = self.invert_marginal(temp, non_trivial)
        return sum([v*(-1)**k.count("1") for k,v in temp.items()])

    def invert_marginal(self, dist : dict, qubits : list[int]):
        """ given a list of qubits, create a marginal distribution, save inverse, continue 
        
        Note, we ALWAYS sort qubits, to prevent any sort of weird reordering. 
        
        """
        key = tuple(sorted(qubits))
        inverse = self.get_inverse(key)
        data = defaultdict(lambda : 0)
        for k,v in dist.items():
            data["".join(k[n] for n in key)]+= v
        return self._apply_correction(data, inverse)
