import numpy as np

from braket.circuits import Circuit
from braket.circuits.gates import CZ, CNot, Rx, Ry, Rz, X, Y, Z
from braket.circuits.noise_model import (
    GateCriteria,
    MeasureCriteria,
    NoiseModel,
)
from braket.circuits.noises import (
    AmplitudeDamping,
    BitFlip,
    Depolarizing,
    TwoQubitDepolarizing,
)
from braket.devices import LocalSimulator

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
_depol_noise_model.add_noise(Depolarizing(0.001), GateCriteria([X, Y, Z, Ry, Rx, Rz]))
_depol_noise_model.add_noise(TwoQubitDepolarizing(0.05), GateCriteria([CNot, CZ]))

qd_depol = LocalSimulator("braket_dm", noise_model= _depol_noise_model)

_noise_model_total = NoiseModel()
_noise_model_total.add_noise(Depolarizing(0.001), GateCriteria([Ry, Rx, Rz, X, Y, Z]))
_noise_model_total.add_noise(AmplitudeDamping(0.001), GateCriteria([Ry,Rx, Rz]))

_noise_model_total.add_noise(TwoQubitDepolarizing(0.02), GateCriteria([CNot, CZ]))
_noise_model_total.add_noise(AmplitudeDamping(0.02), GateCriteria([CNot, CZ]))
for i in range(10):
    _noise_model_total.add_noise(BitFlip(max(0,rng.normal(0.05/2, 0.025/2))), MeasureCriteria(i))
    _noise_model_total.add_noise(AmplitudeDamping(max(0,rng.normal(0.05, 0.025))), MeasureCriteria(i))

qd_total = LocalSimulator("braket_dm", noise_model=_noise_model_total)
h = Circuit().h(0).h(1).to_unitary()

unitary = np.diag(np.exp([0,0.05*1j, 0.05*1j, 0]))
unitary = h @ unitary @ h



_noise_model_ad_2q =  NoiseModel()
_noise_model_ad_2q.add_noise(AmplitudeDamping(0.05),GateCriteria([CZ,CNot]) )
# _noise_model_ad_2q.add_noise(Kraus([unitary]), GateCriteria([CZ,CNot])) 
qd_amp = LocalSimulator("braket_dm", noise_model=_noise_model_ad_2q)

if __name__ == "__main__":
    from braket.program_sets import ProgramSet
    print(_readout_asymm)
    print(_noise_model_total)
    print(_noise_model_ad_2q)

    c = Circuit().h(0).cnot(0,1)
    _noise_model_total.apply(c)
    _noise_model_ad_2q.apply(c)

    test = Circuit().x(0).x(1).measure(range(2))

    print(qd_readout.run(test, shots = 1000).result().measurement_counts)
    print(qd_readout.run(ProgramSet([test]), shots = 1000).result()[0].entries[0].probabilities)

