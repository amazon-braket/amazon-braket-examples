from braket.circuits import Circuit
from braket.circuits.circuit import subroutine
from braket.parametric import FreeParameter
import numpy as np 
import random

def readout_permutation_generator():
    pass

def readout_twirling(
        num_qubit : int,
        as_parametric : bool = False
        ) -> list[Circuit]:
    pass


@subroutine(register=True)
def rxz(qubit : int, theta1 : float,theta2 : float) -> Circuit:
    """ apply Double angle parameterizable gate"""
    return Circuit().rx(qubit, theta1).rz(qubit, theta2)


Id,X,Z,Y = (0., 0.), (np.pi,0.), (0., np.pi), (np.pi, np.pi)

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

def apply_readout_twirl(
        circ : Circuit, 
        as_parameters : bool = False, 
        instances : int = 10):
    pass

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
    