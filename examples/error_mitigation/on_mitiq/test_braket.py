from braket.program_sets import ProgramSet, CircuitBinding
from braket.circuits import Circuit
from braket.circuits import FreeParameter
from braket.devices import LocalSimulator
from braket.circuits.observables import Z,X,Y
from braket.circuits.noise_model import NoiseModel

# alp = FreeParameter("alp")
# c1 = Circuit().h(0).z(1)# .measure(0).measure(1)
# c2 = Circuit().rz(0, alp).h(0).y(1)
# c3 = c2.make_bound_circuit({"alp":0.1})
# c2.measure(0).measure(1)
# c3.measure(0).measure(1)
# p1 = ProgramSet(CircuitBinding(c1, [{}],[X(0) @ X(1), Y(0) @ Y(1)]), shots_per_executable=1000)
# # p2 = ProgramSet(CircuitBinding(c3, [{}],[]), shots_per_executable=1000)

# p2 = ProgramSet([item.circuit.copy() + Circuit().expectation(obs) for item in p1 for obs in item.observables])
# # for item in p1:
# #     for obs in item.observables:

# #     print(item.circuit)
# #     print(item.observables)
qd = LocalSimulator("braket_dm", noise_model=NoiseModel())

# res1 = qd.run(p1, 1000).result()
# res2 = qd.run(p2, 1000).result()
# print(res1)

h = Circuit().h(0).h(1)
h= h + Circuit().measure(0).measure(1)
print(h)
res = LocalSimulator().run(h, shots=10000).result()
print(res)
print(res.measurement_probabilities)

# def test_circuit(
#         theta1 : FreeParameter,
#         theta2 : FreeParameter,
#         num_qubits : int):
#     circ = Circuit()
#     for i in range(num_qubits):
#         circ.rx(i,theta1)
#     for i in range(0,num_qubits-1,2):
#         circ.cz(i,i+1)
#     for i in range(num_qubits):
#         circ.rx(i,theta2)        
#     for i in range(1,num_qubits-1,2):
#         circ.cz(i,i+1)
#     return circ

# alp = FreeParameter("alp")
# bet = FreeParameter("bet")
# psi = test_circuit(alp, bet, 6).make_bound_circuit({"alp":0.0, "bet": 0.0})
# circ0 = generate_pauli_twirl_variants(psi, 1)[0]
# circ1 = circ0 + Circuit().h(0).h(1).h(2).h(3).h(4).h(5)
# print(circ0)
# for i in range(6):
#     circ0.measure(i)
#     circ1.measure(i)
# ps = ProgramSet([circ0, circ1], shots_per_executable=10000)
# res = qd.run(ps).result().entries[1].entries[0].probabilities

# print(res)


from braket.program_sets import CircuitBinding, ProgramSet


cb = CircuitBinding(Circuit().h(0), [{}, {}, {}], [X(0) @ X(1), Y(0) @ Y(1)])
ps = ProgramSet(cb, shots_per_executable=10000)



ps = ProgramSet([Circuit().h(0), Circuit().x(0)])
for item in ps:
    print(type(item))
print(ps.entries)
