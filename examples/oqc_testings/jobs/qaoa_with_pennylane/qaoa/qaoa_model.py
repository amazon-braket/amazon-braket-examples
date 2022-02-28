import pennylane as qml
from qaoa.qaoa_algorithm_script import init_pl_device


def qaoa_model(device_arn, hyperparameters, graph):
    max_parallel = int(hyperparameters['max_parallel'])
    shots = int(hyperparameters['shots'])
    p = int(hyperparameters['p'])
    num_nodes = len(graph.nodes)
    
    # dev = init_pl_device(device_arn, num_nodes=num_nodes, shots=100, max_parallel=30)
    dev = qml.device("default.qubit", wires=num_nodes, shots=1000)

    cost_h, mixer_h = qml.qaoa.maxcut(graph)

    def qaoa_layer(gamma, alpha):
        qml.qaoa.cost_layer(gamma, cost_h)
        qml.qaoa.mixer_layer(alpha, mixer_h)

    @qml.qnode(dev) 
    def circuit(params):
        for i in range(num_nodes):
            qml.Hadamard(wires=i)
        qml.layer(qaoa_layer, p, params[0], params[1])
        return qml.sample()

    return circuit