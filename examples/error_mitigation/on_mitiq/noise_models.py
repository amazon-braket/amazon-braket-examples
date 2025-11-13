from braket.circuits.observables import Z
from braket.devices import LocalSimulator
from braket.circuits import Circuit
from mitiq.zne import zne, ExpFactory, construct_circuits

from braket.circuits import Circuit, Gate, Observable
from braket.circuits.gates import CNot, Ry, Rx, Rz
from braket.circuits.noise_model import GateCriteria, NoiseModel, ObservableCriteria, MeasureCriteria
from braket.circuits.noises import AmplitudeDamping, BitFlip, Depolarizing, PauliChannel, PhaseFlip
from braket.circuits.noises import TwoQubitDepolarizing


_readout_noise_model = NoiseModel()
_readout_noise_model.add_noise(BitFlip(0.05), MeasureCriteria())

qd_readout = LocalSimulator("braket_dm", noise_model= _readout_noise_model)


_depol_noise_model = NoiseModel()
_depol_noise_model.add_noise(Depolarizing(0.001), GateCriteria([Ry,Rx, Rz]))
_depol_noise_model.add_noise(TwoQubitDepolarizing(0.001), GateCriteria([CNot]))

qd_depol = LocalSimulator("braket_dm", noise_model= _depol_noise_model)