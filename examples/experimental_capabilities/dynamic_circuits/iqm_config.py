from math import pi

from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.circuits.circuit import subroutine
from braket.devices.devices import Devices

tags = {}

qd = AwsDevice(Devices.IQM.Garnet)

global _keys
_keys = 0

@subroutine(register=True)
def x(target) -> Circuit:
    circ = Circuit()
    circ.prx(target, pi, 0)
    return circ

@subroutine(register=True)
def ry(target, theta) -> Circuit:
    circ = Circuit()
    circ.prx(target, theta,pi/2)
    return circ

@subroutine(register=True)
def rx(target, theta) -> Circuit:
    circ = Circuit()
    circ.prx(target, theta, 0)
    return circ

@subroutine(register=True)
def rz(target, theta) -> Circuit:
    circ = Circuit()
    circ.prx(target, pi, 0).prx(target, pi, theta/2)
    return circ

@subroutine(register=True)
def h(target) -> Circuit:
    circ = Circuit()
    circ.prx(target, pi/2,pi/2).prx(target, pi, 0) 
    return circ

@subroutine(register=True)
def hi(target) -> Circuit:
    circ = Circuit()
    circ.prx(target, -pi, 0).prx(target, -pi/2,pi/2)
    return circ

@subroutine(register=True)
def s(target) -> Circuit:
    circ = Circuit()
    circ.rz(target, pi/2)
    return circ 

@subroutine(register=True)
def si(target) -> Circuit:
    circ = Circuit()
    circ.rz(target, -pi/2)
    return circ 

@subroutine(register=True)
def cnot(control, target) -> Circuit:
    qc = Circuit().prx(target, pi/2, pi/2).prx(target, pi, 0)
    qc.cz(control,target)
    qc.prx(target, -pi, 0).prx(target, -pi/2, pi/2)
    return qc

@subroutine(register=True)
def cc_x(targets : list[int], reset : bool = True) -> Circuit:
    """ classically conditioned X-gate from one to many """
    global _keys
    circ = Circuit().measure_ff(targets[0], _keys)

    if reset:
        circ.cc_prx(targets[0], pi, 0, _keys)
    for ti in targets[1:]:
        circ.cc_prx(ti, pi, 0, _keys)

    _keys += 1
    return circ

@subroutine(register=True)
def cc_z(targets : list[int], reset : bool = True) -> Circuit:
    """ classically conditioned Z-gate from one to many """
    global _keys

    circ = Circuit().measure_ff(targets[0], _keys)

    if reset:
        circ.cc_prx(targets[0], pi, 0, _keys)
    for ti in targets[1:]:
        circ.h(ti)
        circ.cc_prx(ti, pi, 0, _keys)
        circ.hi(ti)
    _keys += 1
    return circ
