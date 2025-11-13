# Please note, the items in this director 

from braket.circuits import Circuit
from mitiq.executor import Executor
from braket.emulation.local_emulator import LocalEmulator
from braket.aws import AwsDevice
from braket.circuits.circuit import subroutine
from braket.parametric import FreeParameter
import numpy as np
import random
from mitiq.calibration import Calibrator, ZNE_SETTINGS

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

    from braket.circuits.observables import Z
    from braket.devices import LocalSimulator
    from braket.circuits import Circuit
    import numpy as np
    from mitiq.zne import zne, ExpFactory, construct_circuits

    from braket.circuits import Circuit, Gate, Observable
    from braket.circuits.gates import CNot, Ry
    from braket.circuits.noise_model import GateCriteria, NoiseModel, ObservableCriteria, MeasureCriteria
    from braket.circuits.noises import AmplitudeDamping, BitFlip, Depolarizing, PauliChannel, PhaseFlip
    from braket.circuits.noises import TwoQubitDepolarizing


    noise_model = NoiseModel()
    noise_model.add_noise(AmplitudeDamping(0.0005), GateCriteria(Ry))
    noise_model.add_noise(Depolarizing(0.0001), GateCriteria())
    noise_model.add_noise(TwoQubitDepolarizing(0.005), GateCriteria(CNot))
    noise_model.add_noise(BitFlip(0.03), MeasureCriteria())

    qd = LocalSimulator("braket_dm", noise_model= noise_model)

    qc = Circuit().ry(0,0.5).cnot(0,1).x(0).x(1).cnot(0,1).ry(0,-0.5)

    print(qc)
    print(noise_model.apply(qc))


    circ = construct_circuits(qc, [1,3,5])

    print(circ[0])
    print(circ[1])
    print(circ[2])
    obs = Z(0) @ Z(1)

    # est=  Choragus(obs=[obs])

    # print(est(circ,shots_per_executable=100))
