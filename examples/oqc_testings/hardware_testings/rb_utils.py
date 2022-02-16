import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from braket.circuits import Circuit, Gate, Instruction, Noise
from braket.devices import LocalSimulator
from scipy.optimize import curve_fit


def _single_cliffords():
    cliffords = []
    for g in [Gate.I(), Gate.X(), Gate.Y(), Gate.Z()]:
        cliffords.append([g])
        cliffords.append([g, Gate.S()])
        cliffords.append([g, Gate.H()])
        cliffords.append([g, Gate.S(), Gate.H()])
        cliffords.append([g, Gate.H(), Gate.S()])
        cliffords.append([g, Gate.S(), Gate.H(), Gate.S()])
    return cliffords

def _random_single_qubit_clifford():
    return random.choice(_single_cliffords())

def _random_one_qubit_rigetti():
    return random.choice([Gate.Rx(np.pi/2), Gate.Rz(np.pi/2)])

def _random_two_qubit_rigetti():
    return random.choice([Gate.CZ(), Gate.CPhaseShift(np.pi/2), Gate.XY(np.pi/2)])

def random_clifford_circuit(depth: int = 2, qubit: int = 0):
    circ = Circuit()
    for i in range(depth):
        clifford = _random_single_qubit_clifford()
        for c in clifford:
            instr = Instruction(c, qubit)
            circ.add_instruction(instr)
    inverse = circ.adjoint()  # is there a better way to do the inverse?
    circ.add_circuit(inverse)
    return circ

def get_gate(qhp, qubit):
    if qhp=='rigetti':
        if len(qubit)==1:
            return _random_one_qubit_rigetti()
        elif len(qubit)==2:
            return _random_two_qubit_rigetti()

def random_circuit(qhp: str = 'rigetti', depth: int = 2, qubit: int = [0]):
    circ = Circuit()
    for i in range(depth):
        gate = get_gate(qhp, qubit)
        instr = Instruction(gate, qubit)
        circ.add_instruction(instr)
    inverse = circ.adjoint()  # is there a better way to do the inverse?
    circ.add_circuit(inverse)
    return circ


def randomizing_benchmarking_simulator_1q(device,
                                         s3_folder = None, 
                                         depth_list: List[int] = [2, 4, 8, 16], 
                                         repeats: int = 2, 
                                         shots: int = 100):
    qubit = [0]
    rb_results = []
    for depth in depth_list:
        for r in range(repeats):
#             circ = random_clifford_circuit(depth)
            circ = random_circuit('rigetti', depth, qubit=qubit)
            noise = Noise.Depolarizing(0.01)
            circ.apply_gate_noise(noise, target_qubits=qubit)
            noise = Noise.BitFlip(0.04)
            circ.apply_readout_noise(noise)
            
            result = device.run(circ, shots=shots).result()
            prob = result.measurement_probabilities["0"]
            dict = {"depth": depth, "repeat": r, "prob": prob}
            rb_results.append(dict)
    return pd.DataFrame(rb_results)


def randomizing_benchmarking_simulator_2q(device,
                                         s3_folder = None, 
                                         depth_list: List[int] = [2, 4, 8, 16], 
                                         repeats: int = 2, 
                                         shots: int = 100):
    qubit = [0,1]
    rb_results = []
    for depth in depth_list:
        for r in range(repeats):
#             circ = random_clifford_circuit(depth)
            circ = random_circuit('rigetti', depth, qubit=qubit)
            noise = Noise.TwoQubitDepolarizing(0.05)
            circ.apply_gate_noise(noise, target_qubits=qubit)
            noise = Noise.BitFlip(0.04)
            circ.apply_readout_noise(noise)
            
            result = device.run(circ, shots=shots).result()
            prob = result.measurement_probabilities["00"]
            dict = {"depth": depth, "repeat": r, "prob": prob}
            rb_results.append(dict)
    return pd.DataFrame(rb_results)


def randomizing_benchmarking_hardware_1q(device,
                                         qhp='rigetti',
                                         s3_folder = None, 
                                         depth_list: List[int] = [2, 4, 8, 16], 
                                         repeats: int = 2, 
                                         shots: int = 100):
    qubit = [0]
    rb_results = []
    for depth in depth_list:
        for r in range(repeats):
#             circ = random_clifford_circuit(depth)
            circ = Circuit().add_verbatim_box(random_circuit(qhp, depth, qubit=qubit))
            
            result = device.run(circ, s3_folder, shots=shots, disable_qubit_rewiring=True).result()
            prob = result.measurement_probabilities["0"]
            dict = {"depth": depth, "repeat": r, "prob": prob}
            rb_results.append(dict)
    return pd.DataFrame(rb_results)


def randomizing_benchmarking_hardware_2q(device,
                                         qhp='rigetti',
                                         s3_folder = None, 
                                         depth_list: List[int] = [2, 4, 8, 16], 
                                         repeats: int = 2, 
                                         shots: int = 100):
    qubit = [0,1]
    rb_results = []
    for depth in depth_list:
        for r in range(repeats):
#             circ = random_clifford_circuit(depth)
            circ = Circuit().add_verbatim_box(random_circuit(qhp, depth, qubit=qubit))
            
            result = device.run(circ, s3_folder, shots=shots, disable_qubit_rewiring=True).result()
            prob = result.measurement_probabilities["00"]
            dict = {"depth": depth, "repeat": r, "prob": prob}
            rb_results.append(dict)
    return pd.DataFrame(rb_results)



def rb_fit_fun_1q(x, a, alpha):
    return a * alpha ** x + 0.5

def rb_fit_fun_2q(x, a, alpha, c):
    return a * alpha ** x + c