from braket.circuits import Circuit
from braket.circuits.circuit import subroutine
from braket.parametric import FreeParameter
import numpy as np 
import random
from braket.program_sets import ProgramSet
from braket.devices import Device

@subroutine(register=True)
def rxz(qubit : int, theta1 : float,theta2 : float) -> Circuit:
    """ apply Double angle parameterizable gate"""
    return Circuit().rx(qubit, theta1).rz(qubit, theta2)


def gen_pauli_circ(x : str, i : int ):
    return Circuit().__getattribute__(x.lower())(i)

Id,X,Z,Y = (0., 0.), (np.pi,0.), (0., np.pi), (np.pi, np.pi)

PAULI_TO_PARAM = {
    "I":Id,
    "X":X,
    "Y":Y,
    "Z":Z,
}

CNOT_twirling_gates = [
    (Id, Id, Id, Id),
    (Id, X, Id, X),
    (Id, Y, Z, Y),
    (Id, Z, Z, Z),
    (Y, Id, Y, X),
    (Y, X, Y, Id),
    (Y, Y, X, Z),
    (Y, Z, X, Y),
    (X, Id, X, X),
    (X, X, X, Id),
    (X, Y, Y, Z),
    (X, Z, Y, Y),
    (Z, Id, Z, Id),
    (Z, X, Z, X),
    (Z, Y, Id, Y),
    (Z, Z, Id, Z),
]
CZ_twirling_gates = [
    (Id, Id, Id, Id),
    (Id, X, Z, X),
    (Id, Y, Z, Y),
    (Id, Z, Id, Z),
    (X, Id, X, Z),
    (X, X, Y, Y),
    (X, Y, Y, X),
    (X, Z, X, Id),
    (Y, Id, Y, Z),
    (Y, X, X, Y),
    (Y, Y, X, X),
    (Y, Z, Y, Id),
    (Z, Id, Z, Id),
    (Z, X, Id, X),
    (Z, Y, Id, Y),
    (Z, Z, Z, Z),
]

twirling_gates = {
    "CZ": CZ_twirling_gates,
    "CNot": CNOT_twirling_gates,
}

def _readout_pass(circ : Circuit) -> tuple[Circuit, str]:
    """Apply readout twirling to a single circuit.
    
    Args:
        circ: Input circuit
    
    Returns:
        (Circuit, str) - list of twirled circuits and flip maps
    """
    qubits = set()
    for ins in circ.instructions:
        qubits.update(int(q) for q in ins.target)
    qubits = sorted(qubits)
    
    twirled_circ = circ.copy()
    flip_map = ['0'] * len(qubits)
    for n,q in enumerate(qubits):
        pauli = random.choice(['I','X','Y','Z'])
        twirled_circ.add(gen_pauli_circ(pauli, q))
        # if pauli in ["x","y"]:
        flip_map[n] = pauli
    return twirled_circ, "".join(flip_map)


def apply_readout_twirl(
        circ: Circuit | list[Circuit] | np.ndarray,
        num_samples: int = 5,
        ) -> tuple[np.ndarray[Circuit], np.ndarray[str]]:
    """Apply readout twirling to all qubits in circuit.
    
    Args:
        circ: Input circuit
        num_samples: Number of twirling samples
    
    Returns:
        (list[Circuit], list[dict]) - list of twirled circuits and the Pauli twirls maps
    """
    # Get all qubits used in circuit
    match circ:
        case Circuit():
            return zip(*[_readout_pass(circ) for i in range(num_samples)])
        case np.ndarray():
            circuits,bitmasks = np.empty_like(circ), np.empty_like(circ)
            for index,circuit in np.ndenumerate(circ):
                c,b = _readout_pass(circuit)
                circuits[index] = c
                bitmasks[index] = b
            return circuits, bitmasks
        case list():
            return zip(_readout_pass(circ) for i in range(num_samples))
        case _:
            raise TypeError(f"Unsupported format {type(circ)} to apply readout error.")


def _spell_check(i : int, shape : tuple) -> tuple:
    if shape is None:
        return i
    total = ()
    for n in shape[::-1]:
        total = (i % n,) + total
        i = i // n
    return total



def get_twirled_readout_dist(qubits : list, 
                         n_twirls : int = 5, 
                         shots : int = 1000,
                         device : Device = None,
                         ) -> np.ndarray:
    """ get confusion matrix through twirling and PRogramSsets"""
    circuit = Circuit()
    for i in qubits:
        circuit.i(i)
    variants, masks = apply_readout_twirl(circuit, n_twirls)
    if hasattr(device, "_noise_model") and device._noise_model: # TODO: REMOVE PLEASE WITH EMULATORS
        variants = [device._noise_model.apply(v.measure(qubits)) for v in variants]
    pset = ProgramSet(variants, shots_per_executable= shots // n_twirls)
    results = device.run(pset).result()

    base = {}
    for item, mask in zip(results, masks):
        mask = "".join("1" if m in ["X","Y"] else "0" for m in mask)
        for k, v in item.entries[0].counts.items():
            kp = ''.join(str(int(a) ^ int(b)) for a, b in zip(k, mask))
            base[kp] = base.get(kp, 0) + v
    base = {k: v / shots for k, v in base.items()}
    return base 


def process_readout_twirl(
        counts : dict, 
        index : int, 
        bit_masks : list | np.ndarray
        ):
    i = _spell_check(index, getattr(bit_masks, "shape", None))
    bit_mask = bit_masks[i] 

    def _bit_addition(k,j):
        return ''.join(str(int(a) ^ int(b)) for a, b in zip(k, bit_mask))
    return {_bit_addition(k,bit_mask):v for k,v in counts.items()}


def apply_two_qubit_twirl(circ : Circuit, num_samples : int = 5) -> tuple[Circuit, list[dict[str,float]]]:
    """ twirl 2Q gates and returns list of parameters 
    
    Args:
        circ (Circuit): input braket circuit
        num_samples (int): number of parameter sets to generate

    Returns:
        Circuit: parameterized quantum circuit
        list[dict]: list of parameter dictionaries for Braket
    
    """
    twirled_circuit = Circuit()
    param_sets = [{} for _ in range(num_samples)]
    gate_count = 0
    
    for ins in circ.instructions:
        if ins.operator.qubit_count == 2:
            q0, q1 = int(ins.target[0]), int(ins.target[1])
            twirls = twirling_gates[ins.operator.name]
            
            # Add parameterized gates before and after the 2Q gate
            twirled_circuit.add(
                rxz(q0, FreeParameter(f'i_{gate_count}_q{q0}_x'), FreeParameter(f'i_{gate_count}_q{q0}_z')))
            twirled_circuit.add(
                rxz(q1, FreeParameter(f'i_{gate_count}_q{q1}_x'), FreeParameter(f'i_{gate_count}_q{q1}_z')))
            twirled_circuit.add_instruction(ins)
            twirled_circuit.add(
                rxz(q0, FreeParameter(f'o_{gate_count}_q{q0}_x'), FreeParameter(f'o_{gate_count}_q{q0}_z')))
            twirled_circuit.add(
                rxz(q1, FreeParameter(f'o_{gate_count}_q{q1}_x'), FreeParameter(f'o_{gate_count}_q{q1}_z')))
            
            # Generate random twirling parameters for each sample
            for i in range(num_samples):
                twirl = random.choice(twirls)
                param_sets[i].update({
                    f'i_{gate_count}_q{q0}_x': twirl[0][0], f'i_{gate_count}_q{q0}_z': twirl[0][1],
                    f'i_{gate_count}_q{q1}_x': twirl[1][0], f'i_{gate_count}_q{q1}_z': twirl[1][1],
                    f'o_{gate_count}_q{q0}_x': twirl[2][0], f'o_{gate_count}_q{q0}_z': twirl[2][1],
                    f'o_{gate_count}_q{q1}_x': twirl[3][0], f'o_{gate_count}_q{q1}_z': twirl[3][1]
                })
            gate_count += 1
        else:
            twirled_circuit.add_instruction(ins)
    
    return twirled_circuit, param_sets
    