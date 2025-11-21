from braket.circuits.observables import Z
from braket.devices import LocalSimulator
from braket.circuits import Circuit

from braket.circuits import Circuit, Gate, Observable
from braket.circuits.gates import CNot, Ry, Rx, Rz, CZ
from braket.circuits.noise_model import GateCriteria, NoiseModel, ObservableCriteria, MeasureCriteria
from braket.circuits.noises import AmplitudeDamping, BitFlip, Depolarizing, PauliChannel, PhaseFlip
from braket.circuits.noises import TwoQubitDepolarizing
from braket.registers import Qubit, QubitSetInput
# from braket.emulation.local_emulator import LocalEmulator
import numpy as np

rng = np.random.default_rng(seed=49)

_readout_noise_model = NoiseModel()
_readout_noise_model.add_noise(BitFlip(0.05), MeasureCriteria())

_readout_asymm = NoiseModel()
for i in range(10):
    _readout_asymm.add_noise(BitFlip(max(0,rng.normal(0.05, 0.025))), MeasureCriteria(i))
    _readout_asymm.add_noise(AmplitudeDamping(max(0,rng.normal(0.05, 0.025))), MeasureCriteria(i))

qd_readout = LocalSimulator("braket_dm", noise_model= _readout_noise_model)
qd_readout_2 = LocalSimulator("braket_dm", noise_model = _readout_asymm)

_depol_noise_model = NoiseModel()
_depol_noise_model.add_noise(Depolarizing(0.001), GateCriteria([Ry,Rx, Rz]))
_depol_noise_model.add_noise(TwoQubitDepolarizing(0.05), GateCriteria([CNot, CZ]))

qd_depol = LocalSimulator("braket_dm", noise_model= _depol_noise_model)

_noise_model_total = NoiseModel()
_noise_model_total.add_noise(Depolarizing(0.001), GateCriteria([Ry,Rx, Rz]))
_noise_model_total.add_noise(TwoQubitDepolarizing(0.05), GateCriteria([CNot, CZ]))
for i in range(10):
    pass
    _noise_model_total.add_noise(BitFlip(max(0,rng.normal(0.05/2, 0.025/2))), MeasureCriteria(i))
    # _noise_model_total.add_noise(AmplitudeDamping(max(0,rng.normal(0.01, 0.0025))), MeasureCriteria(i))

qd_total = LocalSimulator("braket_dm", noise_model=_noise_model_total)

if __name__ == "__main__":
    print(_readout_asymm)
    print(_noise_model_total)