from qiskit_braket_provider import to_braket, to_qiskit
from braket.circuits import Circuit, Gate
from braket.device_schema import  DeviceCapabilities
from braket.devices import Device
import numpy as np
from braket.circuits import QubitSet
from qiskit import transpile

def _vf2_callback(**kwargs):
    """
    callback for successful VF2 layout pass
    """
    pass_name = kwargs['pass_'].__class__.__name__
    if pass_name == "VF2Layout":
        stop_reason = kwargs['pass_'].property_set["VF2Layout_stop_reason"]
        if not stop_reason.name == "SOLUTION_FOUND":
            raise Exception

def restricted_circuit_layout(ansatz : Circuit, device : Device) -> Circuit:
    """ find a layout with the VF2 pass by tapering the layout """

    def score(a,b,c):
        """ custom score function prioritizing first arg """
        return 1.0*a + 1.0*b + 1.0*c
    
    limits = [0.1, 0.25, 0.05]
    steps = [l/2 for l in limits]
    trials = 0
    best = [1,1,1]
    final = None
    min_step = 0.0001
    
    props = device.properties.standardized
    ansatz_q = to_qiskit(ansatz, False)


    while trials < 75 and any([s > min_step for s in steps]):
        idx = trials % 3
        qubits = set()
        layout = []
        for pair, vals in props.twoQubitProperties.items():
            infidelity = 1 - vals.twoQubitGateFidelity[0].dict()['fidelity']
            pair = [int(k) for k in pair.split('-')]
            ro_i = 1 - props.oneQubitProperties[str(pair[0])].oneQubitFidelity[2].fidelity
            ro_j = 1 - props.oneQubitProperties[str(pair[1])].oneQubitFidelity[2].fidelity 
            
            g_i =  1-props.oneQubitProperties[str(pair[0])].oneQubitFidelity[1].fidelity
            g_j =  1-props.oneQubitProperties[str(pair[1])].oneQubitFidelity[1].fidelity
            if all([
                infidelity < limits[0], 
                ro_i < limits[1],
                ro_j < limits[1],
                g_i < limits[2],
                g_j < limits[2]]):
                layout.append(pair)
            qubits.add(pair[0])
            qubits.add(pair[1])

        maps = {k:n for n,k in enumerate(qubits)}
        new_layout = [[maps[i],maps[j]] for (i,j) in layout] + [[maps[j],maps[i]] for (i,j) in layout]

        try:
            trial = transpile(ansatz_q, 
                            coupling_map=new_layout, 
                            optimization_level=2, 
                            callback=_vf2_callback)
            if score(*limits) < score(*best):
                best = limits.copy()
                final = trial
            limits[idx] -= steps[idx]
            steps[idx] /= 2
        except Exception as e:
            limits[idx] += steps[idx]
            steps[idx] /= 2
        # print(limits,steps, score(*limits), fail)
        trials += 1

    if final is None:
        raise RuntimeError("Failed to find valid circuit layout within constraints")
    
    final = to_braket(final, braket_device=device, optimization_level=0)

    print(f'= limit(2q): {best[0]}')
    print(f'= limit(ro): {best[1]}')
    print(f'= limit(1q): {best[2]}')
    print(f' - num steps: {trials}')
    print(f' - steps: {steps}')
    return final


def find_linear_chain(circ : Circuit) -> list:
    """ find the chain corresponding to a circuit """
    chain = []
    length = -1
    iters = 0
    while len(chain) != length and iters < 25:
        iters += 1
        length = len(chain)
        for ins in circ.instructions:
            if len(ins.target) == 2:
                if len(chain) == 0:
                    chain = [ins.target[0], ins.target[1]]
                else:
                    if ins.target[0] == chain[0] and ins.target[1] != chain[1]:
                        chain.insert(0, ins.target[1])
                    elif ins.target[1] == chain[0] and ins.target[0] != chain[1]:
                        chain.insert(0, ins.target[0])
                    elif len(chain) >= 2 and ins.target[0] == chain[-1] and ins.target[1] != chain[-2]:
                        chain.append(ins.target[1])
                    elif len(chain) >= 2 and ins.target[1] == chain[-1] and ins.target[0] != chain[-2]:
                        chain.append(ins.target[0])
    if len(chain) < len(circ.qubits):
        raise ValueError("2Q chain not found")
    return chain


def multiply_gates(circuit : Circuit, gates : list[str], repetitions : int = 1) -> Circuit:
    """ multiply a gate by the number of repetitions -> does not really preserve a circuit"""
    new = Circuit()
    for ins in circuit.instructions:
        if ins.operator.name in gates:
            for _ in range(repetitions):
                new.add_instruction(ins)
        else:
            new.add_instruction(ins)
    return new


def strip_verbatim(circuit : Circuit) -> Circuit:
    """ strip verbatim from a circuit """
    new = Circuit()
    for ins in circuit.instructions:
        if "Verbatim" not in ins.operator.name:
            new.add_instruction(ins)
    return new


def convert_paulis(circ : Circuit) -> Circuit:
    """ convert Paulis to """
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

def fidelity_estimation(circ : Circuit, device : Device, gate : str):
    """ estimate the fidelity of a circuit based on a device properties and a specific gate """
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

if __name__ == "__main__":
    from braket.devices import Devices
    from braket.aws import AwsDevice

    ankaa = AwsDevice(Devices.Rigetti.Ankaa3)

    def test_circuit(
            num_qubits : int):
        circ = Circuit()
        for i in range(num_qubits):
            circ.rz(i,0.0001,)
        for i in range(0,num_qubits-1,2):
            circ.iswap(i,i+1)
        for i in range(num_qubits):
            circ.rz(i,0.0001,)
        for i in range(1,num_qubits-1,2):
            circ.iswap(i,i+1)
        for i in range(num_qubits):
            circ.rz(i,0.0001,)
        for i in range(0,num_qubits-1,2):
            circ.iswap(i,i+1)
        for i in range(num_qubits):
            circ.rz(i,0.0001,)
        for i in range(1,num_qubits-1,2):
            circ.iswap(i,i+1)
        return circ

    ansatz = test_circuit(num_qubits=30)

    native_ansatz = restricted_circuit_layout(ansatz, ankaa)
    print(native_ansatz)

    chain = find_linear_chain(native_ansatz)
    print(chain)

    fid, ins = fidelity_estimation(native_ansatz,ankaa, "ISwap")
    print(fid,ins)

