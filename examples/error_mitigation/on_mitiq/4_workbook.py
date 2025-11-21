import sys
import os
import numpy as np
from braket.circuits import Circuit
from braket.parametric import FreeParameter
np.set_printoptions(precision=3, linewidth=500, suppress=True)
from noise_models import qd_depol, qd_total
from functools import reduce
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) # parent  
from tools.observable_tools import pauli_grouping
from tools.program_set_tools import run_with_program_sets
from mitiq.zne import construct_circuits, combine_results, RichardsonFactory
from mitiq.pt import generate_pauli_twirl_variants
from tools.mitigation_tools import apply_readout_twirl, get_twirled_readout_dist
from mitiq_braket_tools import braket_rem_twirl_mitigator
from braket.quantum_information import PauliString
from mitiq.rem import generate_inverse_confusion_matrix

def ising_hamiltonian(
        hopping : float, 
        self_interaction : float, 
        num_qubits : int):
    hamiltonian = []
    n = num_qubits
    for i in range(num_qubits):
        hamiltonian.append(
            (self_interaction,i*"I"+"Z"+(n-i-1)*"I")
            )
        if i>0:
            hamiltonian.append(
                (hopping, (i-1)*"I"+"XX"+(n-i-1)*"I"))
    return hamiltonian

ham = ising_hamiltonian(0.5,1,6)
matrix = reduce(np.add,[c*(PauliString(p).to_unsigned_observable(include_trivial=True).to_matrix()) for c,p in ham])
print(matrix)

bases, pauli_terms = pauli_grouping(ising_hamiltonian(0.5,1,6))
print(bases)
print(f'number of distinct circuits: {len(bases)}') 



def test_circuit(
        theta1 : FreeParameter,
        theta2 : FreeParameter,
        num_qubits : int):
    circ = Circuit()
    for i in range(num_qubits):
        circ.rx(i,theta1)
    for i in range(0,num_qubits-1,2):
        circ.cz(i,i+1)
    for i in range(num_qubits):
        circ.rx(i,theta2)        
    for i in range(1,num_qubits-1,2):
        circ.cz(i,i+1)
    return circ

alp = FreeParameter("alp")
bet = FreeParameter("bet")

ansatz = test_circuit(alp, bet, 6)

# the strategy we perform is a bit different - we will randomly twirl the measurement sequence, and then apply


shot_total = 10000

scale_factors = [1,5,9]
num_twirls = 1

parameters = {"alp":0.0, "bet":0.0}

target_circuit = ansatz.make_bound_circuit(parameters)

circuits = np.array([generate_pauli_twirl_variants(c, num_circuits=num_twirls) for c in construct_circuits(target_circuit, scale_factors=scale_factors)], dtype=object)

circuits, bit_masks =  apply_readout_twirl(circuits)
for item in np.nditer(circuits, flags = ["refs_ok"]):
    # print(item)
    item.item().measure(range(6))

bit_masks = np.reshape(bit_masks, circuits.shape + (1, 1))
bit_masks = np.broadcast_to(bit_masks, circuits.shape+ (1, len(bases),))



dist = get_twirled_readout_dist([0,1,2,3,4,5],100, shots = 2*shot_total, device = qd_total)
# bit flip distribution
print(dist)

cm = np.zeros((2**6, 2**6))
for i in range(2**6):
    for j in range(2**6):
        cm[i, j] = dist.get(bin(i^j)[2:].zfill(6), 0)
# print(cm)
# for rows in cm:
#     print(rows)

qubit_errors = [0] * 6
for k,v in dist.items():
    for n in range(6):
        if k[n]=="1":
            qubit_errors[n]+= v
print('single qubit readout errors')
print(qubit_errors)
mats = [generate_inverse_confusion_matrix(1,p0=i,p1=i) for i in qubit_errors]
icm = reduce(np.kron, mats, np.array([[1]]))

# near_i  = icm @ cm
# for row in near_i:
#     print(row)



measurement_filter = braket_rem_twirl_mitigator(
    icm, bit_masks=bit_masks
)

test = run_with_program_sets(
    circuits, bases, pauli_terms, parameters = [{}], device = qd_total,
    measurement_filter= measurement_filter, 
    shots_per_executable=shot_total // num_twirls)

# the output of test is a dim_circ + dim_para + dim_bases, which is (3,10), (1,) and (2,) respectively

print(test.shape)

# first sum over the observables 
twirled = np.sum(test, axis=(3))
print(twirled)
# then, average over the twirls 
zne_results = np.average(twirled, axis = (1,2))
print(zne_results)
mitigated = combine_results(scale_factors=scale_factors, results = zne_results, extrapolation_method=RichardsonFactory.extrapolate)
# extra_tail = combine_results(scale_factors=scale_factors + [100], results = zne_results.tolist() + [0,], extrapolation_method=RichardsonFactory.extrapolate)

print('noisy_result: ',)
print(zne_results[0])
print('mitigated result: ',)
print(mitigated)
# print('extra with 0 added: ',)
# print(extra_tail)
print('Improvement: ')

statevector = target_circuit.to_unitary()[:,0]
statevector = statevector.reshape((2**6,1))
ideal = (np.conj(statevector).T @ matrix @ statevector)[0,0]
print(f"Ideal Expectation: {ideal}")

delta= abs(zne_results[0] - ideal)
rel_err = abs(mitigated - ideal)
print(f"{(1 - rel_err / delta) * 100 :.2f}% reduction in error")
print(f"{delta / rel_err :.1f}x improvement")