import networkx as nx
import os
import json

from braket.devices import LocalSimulator
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric

import pennylane as qml
from pennylane import numpy as np

from qaoa.utils import get_device


def main():    
    ########## Read environment variables ##########
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]

    
    ########## Hyperparameters ##########
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    print("hyperparams: ", hyperparams)
    
    # problem-setup hyperparams
    n_nodes = int(hyperparams["n_nodes"])
    n_edges = float(hyperparams["n_edges"])
    n_layers = int(hyperparams["n_layers"])

    # training hyperparams
    seed = int(hyperparams["seed"])
    iterations = int(hyperparams["iterations"])
    stepsize = float(hyperparams["stepsize"])
    diff_method = hyperparams["diff_method"]
    
    ########## Device ##########
    device = get_device(n_nodes)
    

    ########## Set up graph ##########
    g = nx.gnm_random_graph(n_nodes, n_edges, seed=seed)
    positions = nx.spring_layout(g, seed=seed)

    cost_h, mixer_h = qml.qaoa.max_clique(g, constrained=False)
    print('number of observables: ', len(cost_h._ops))

    def qaoa_layer(gamma, alpha):
        qml.qaoa.cost_layer(gamma, cost_h)
        qml.qaoa.mixer_layer(alpha, mixer_h)
        
    def circuit(params):
        for i in range(n_nodes): 
            qml.Hadamard(wires=i)
        qml.layer(qaoa_layer, n_layers, params[0], params[1])

    @qml.qnode(device, diff_method=diff_method)
    def cost_function(params):
        circuit(params)
        return qml.expval(cost_h)
    

    ########## Optimization ###########
    print("start optimizing...")
    np.random.seed(seed)
    params = np.random.uniform(size=[2, n_layers])

    opt = qml.AdamOptimizer(stepsize=stepsize)
    
    for i in range(iterations):
        params, cost_before = opt.step_and_cost(cost_function, params)
        
        # Log the loss before the update step as a metric
        log_metric(
            metric_name="Cost",
            value=cost_before,
            iteration_number=i,
        )

    
    final_cost = float(cost_function(params))
    log_metric(
        metric_name="Cost",
        value=final_cost,
        iteration_number=iterations,
    )
    
    save_job_result({"params": params.tolist(), "cost": final_cost})


if __name__ == "__main__":
    try:
        main()
        print("Training Successful!!")
    except BaseException as e:
        print(e)
        print("Training Fails...")
