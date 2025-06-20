import numpy as np

from braket.circuits import Circuit
from braket.circuits.circuit import subroutine
from braket.devices import LocalSimulator

qd = LocalSimulator("braket_dm")
tags = {}

global _keys 

@subroutine(register=True)
def hi(target) -> Circuit:
    """ single qubit identity gate """
    circ = Circuit()
    circ.h(target)
    return circ

@subroutine(register=True)
def cc_x(targets : list[int], reset : bool = True) -> Circuit:
    """ classically conditioned X-gate """
    circ = Circuit()
    if reset:
        K0, K1 = np.array([[1,0],[0,0]]), np.array([[0,1],[0,0]])
    else:
        K0, K1 = np.array([[1,0],[0,0]]), np.array([[0,0],[0,1]])

    if len(targets)>1:
        K0 = np.kron(K0, np.eye(2))
        K1 = np.kron(K1, np.array([[0,1],[1,0]]))
        for ti in targets[1:-1]:
            circ.cnot(targets[0],ti)
        return circ.kraus([targets[0],targets[-1]], [K0, K1])
    else:
        return circ.kraus(targets, [K0, K1])

@subroutine(register=True)
def cc_z(targets : list[int], reset : bool = True) -> Circuit:
    """ classically conditioned Z-gate """
    circ = Circuit()
    if reset:
        K0, K1 = np.array([[1,0],[0,0]]), np.array([[0,1],[0,0]])
    else:
        K0, K1 = np.array([[1,0],[0,0]]), np.array([[0,0],[0,1]])
    if len(targets)>1:
        K0 = np.kron(K0, np.eye(2))
        K1 = np.kron(K1, np.array([[1,0],[0,-1]]))
        for ti in targets[1:-1]:
            circ.cz(targets[0],ti)
        return circ.kraus([targets[0],targets[-1]], [K0, K1])
    else:
        return circ.kraus(targets, [K0, K1])
