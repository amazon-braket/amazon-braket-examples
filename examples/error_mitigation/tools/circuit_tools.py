from warnings import warn

import numpy as np
from qiskit.transpiler import CouplingMap, PassManager
from qiskit.transpiler.passes import VF2Layout
from qiskit_braket_provider import to_qiskit

from braket.circuits import Circuit, QubitSet
from braket.devices import Device


class QubitMap:
    def __init__(self, braket_circuit : Circuit, braket_physical : list):
        """ input a sorted braket logical circuit, """
        self.regs = {
            "virt":{
                "braket":[int(k) for k in sorted(braket_circuit.qubits)],
                "qiskit":list(range(braket_circuit.qubit_count))
                },
            "phys":{
                "braket":braket_physical,
                "qiskit":list(range(len(braket_physical)))
                }
            }
        
    def b_to_q(self, key : int, reg : str = "phys") -> int:
        assert reg in self.regs.keys()
        inp = self.regs[reg]["braket"].index(key)
        return self.regs[reg]["qiskit"][inp]

    def q_to_b(self, key : int, reg : str = "phys") -> int:
        assert reg in self.regs.keys()
        inp = self.regs[reg]["qiskit"].index(key)
        return self.regs[reg]["braket"][inp]


def restricted_circuit_layout(ansatz : Circuit, device : Device,
        ) -> Circuit:
    """ when possible to be laid out will return such a layout  """

    def score(a,b,c):
        """ simple score function """
        return 1.0*a + 1.0*b + 1.0*c
    
    limits = [0.1, 0.25, 0.05]
    steps = [lim/2 for lim in limits]
    trials = 0
    best = [1,1,1]
    final = None
    min_step = 0.0001
    
    props = device.properties.standardized
    ansatz_q = to_qiskit(ansatz, False) #now, a contiguous ordering 
    # braket_logical -> qiskit_logical 
    

    while trials < 75 and any([s > min_step for s in steps]):
        idx = trials % 3
        qubits = set()
        layout = []
        for pair, vals in props.twoQubitProperties.items():
            infidelity = vals.twoQubitGateFidelity[0].dict()['fidelity']
            infidelity = min(infidelity, 1-infidelity)
            pair = [int(k) for k in pair.split('-')]
            ro_i = props.oneQubitProperties[str(pair[0])].oneQubitFidelity[2].fidelity
            ro_j = props.oneQubitProperties[str(pair[1])].oneQubitFidelity[2].fidelity 
            ro_i, ro_j = min(1-ro_i, ro_i), min(ro_j, 1-ro_j)

            g_i =  props.oneQubitProperties[str(pair[0])].oneQubitFidelity[1].fidelity
            g_j =  props.oneQubitProperties[str(pair[1])].oneQubitFidelity[1].fidelity
            g_i, g_j = min(1-g_i, g_i), min(1-g_j, g_j)

            if all([
                infidelity < limits[0], 
                ro_i < limits[1],
                ro_j < limits[1],
                g_i < limits[2],
                g_j < limits[2]]):
                layout.append(pair)
            qubits.add(pair[0])
            qubits.add(pair[1])

        if not layout:
            limits[idx] += steps[idx]
            steps[idx] /= 2
            trials += 1
            continue
        qmap = QubitMap(ansatz, list(qubits) )
        qiskit_layout = [[qmap.b_to_q(i),qmap.b_to_q(j)] for (i,j) in layout]
        coupling_map = CouplingMap(qiskit_layout)
        pm = PassManager([VF2Layout(coupling_map, max_trials=1,time_limit=5)])
        pm.run(ansatz_q)

        if pm.property_set["VF2Layout_stop_reason"].name == "SOLUTION_FOUND":
            if score(*limits) < score(*best):
                best = limits.copy()
                zero_to_phys = pm.property_set["layout"].get_virtual_bits()
                # virt to phys
                final = {qmap.q_to_b(v._index,"virt"):qmap.q_to_b(p,"phys") for v,p in zero_to_phys.items()}


            limits[idx] -= steps[idx]
            steps[idx] /= 2
        else:
            limits[idx] += steps[idx]
            steps[idx] /= 2
        trials += 1

    if final is None:
        warn("could not find valid layout, returning original")
        return ansatz

    circuit = Circuit().add_circuit(ansatz, target_mapping = final)
    print(f'= limit(2q): {best[0]}')
    print(f'= limit(ro): {best[1]}')
    print(f'= limit(1q): {best[2]}')
    print(f' - num steps: {trials}')
    print(f' - steps: {steps}')
    # final = to_braket(final, qubit_labels=device.qubit_labels)
    return circuit, final



def multiply_gates(circuit : Circuit, gates : list[str], repetitions : int = 1) -> Circuit:
    """ multiply a gate by the number of repetitions -> generally, not an identity preserving operation """
    new = Circuit()
    for ins in circuit.instructions:
        if ins.operator.name in gates:
            for _ in range(repetitions):
                new.add_instruction(ins)
        else:
            new.add_instruction(ins)
    return new


def strip_verbatim(circuit : Circuit) -> Circuit:
    """ strip verbatim instructions from a circuit """
    new = Circuit()
    for ins in circuit.instructions:
        if "Verbatim" not in ins.operator.name:
            new.add_instruction(ins)
    return new


def convert_paulis(circ : Circuit) -> Circuit:
    """ convert Paulis to rx and rz gates """
    new = Circuit()
    for ins in circ.instructions:
        match ins.operator.name:
            case "X":
                new.rx(ins.target,np.pi)
            case "Y":
                new.rz(ins.target,np.pi)
                new.rx(ins.target,np.pi)
            case "Z":
                new.rz(ins.target,np.pi)
            case "I":
                pass
            case _:
                new.add_instruction(ins)
    return new

def fidelity_estimation(circ : Circuit, device : Device, gate : str) -> tuple[float, tuple[int,int]]:
    """ estimate the fidelity of a circuit based on a device properties and a specific gate 
    
    Returns:
        fidelity : predicted fidelity of the circuit
        (active 2q, total 2q) : tuple of the number of active 2q gates and the total number

    """
    props = device.properties.standardized
    active_qubits = QubitSet()
    active_ins = []
    total_gates = 0
    for ins in circ.instructions[::-1]:
        if ins.operator.name == gate:
            if len(active_qubits) == 0:
                active_qubits.add(ins.target[0])
                active_qubits.add(ins.target[1])
                active_ins.append('{}-{}'.format(*(int(k) for k in sorted(ins.target))))
            total_gates+=1
            i,j = ins.target
            if (i in active_qubits) or (j in active_qubits):
                active_qubits.add(i)
                active_qubits.add(j)
                active_ins.append('{}-{}'.format(*(int(k) for k in sorted(ins.target))))
    fidelities = {}
    for pair, vals in props.twoQubitProperties.items():
        if pair in active_ins:
            for item in vals.twoQubitGateFidelity:
                temp = item.dict()
                fidelities[pair]= temp['fidelity']

    predicted_fidelity = 1
    for ins in active_ins:
        predicted_fidelity*= fidelities[ins]

    return predicted_fidelity, (len(active_ins), total_gates)
