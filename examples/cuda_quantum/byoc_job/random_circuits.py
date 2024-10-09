import numpy as np


def random_circuit_generator_factory():
    import cudaq
    def get_random_circuit(n_qubits, n_gates):   
        kernel = cudaq.make_kernel()
        qubits = kernel.qalloc(n_qubits)
    
        for _ in range(n_gates):
            gate_size = np.random.choice(["1Q", "2Q"])
            if gate_size == "2Q":
                qubit_pair = np.random.choice(range(n_qubits), size=2, replace=False)
                q0, q1 = [int(q) for q in qubit_pair]
                kernel.cz(qubits[q0], qubits[q1])
    
            else: # "1Q"
                q0 = np.random.choice(range(n_qubits))
                q0 = int(q0)
    
                gate_type = np.random.choice(["h", "rx", "ry", "rz"])
                if gate_type=="h":
                    kernel.h(qubits[q0])
                else: # "rx", "ry", "rz"
                    random_angle = float(np.random.uniform(0, np.pi))
                    add_gate = getattr(kernel, gate_type)
                    add_gate(random_angle, qubits[q0])
        return kernel
    return get_random_circuit

    
def parametric_random_circuit_generator_factory():
    import cudaq
    def get_parametric_random_circuit(n_qubits, n_gates):   
        kernel, params = cudaq.make_kernel(list)
        qubits = kernel.qalloc(n_qubits)
    
        params_counter = 0
        for _ in range(n_gates):
            gate_size = np.random.choice(["1Q", "2Q"])
            if gate_size == "2Q":
                qubit_pair = np.random.choice(range(n_qubits), size=2, replace=False)
                q0, q1 = [int(q) for q in qubit_pair]
                kernel.cz(qubits[q0], qubits[q1])
    
            else: # "1Q"
                q0 = np.random.choice(range(n_qubits))
                q0 = int(q0)
    
                gate_type = np.random.choice(["h", "rx", "ry", "rz"])
                if gate_type=="h":
                    kernel.h(qubits[q0])
                else: # "rx", "ry", "rz"
                    random_angle = params[params_counter]
                    add_gate = getattr(kernel, gate_type)
                    add_gate(random_angle, qubits[q0])
                    params_counter += 1
                    
        return kernel, params_counter
    return get_parametric_random_circuit