import pennylane as qml
from pennylane import numpy as np
import random
import json
import os
from source_scripts.utils import get_device, str2bool, train
from source_scripts.QNSPSA import QNSPSA
from braket.jobs import save_job_result
import time
import networkx as nx
from pennylane import qaoa


def main(): 
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    print(hyperparams)
    
    # problem-setup hyperparams
    load_init_config = str2bool(hyperparams["load_init_config"])
    n_qubits = int(hyperparams["n_qubits"])
    edges = int(hyperparams["edges"])
    depth = int(hyperparams["depth"]) 
    seed = int(hyperparams["seed"])
    shots = int(hyperparams["shots"]) 
    max_iter = int(hyperparams["max_iter"])
    spsa_repeats = int(hyperparams["spsa_repeats"])
    
    dev = get_device(n_qubits, shots)

    if load_init_config:
        prefix = os.environ["AMZN_BRAKET_SCRIPT_ENTRY_POINT"].split('.')[0]
        print(prefix)
        params_init_file = os.path.join(
            os.getcwd(),
            prefix,
            f"qaoa_params_init_{n_qubits}_qubits_{depth}_layers.npy",
        )
        
        params_init = np.load(params_init_file)
    else:
        params_init = 2 * np.pi * (np.random.rand(2, depth) - 0.5) 
     
    g = nx.gnm_random_graph(n_qubits, edges, seed=seed)
    cost_h, mixer_h = qaoa.maxcut(g)
    
    def qaoa_layer(gamma, alpha):
        qaoa.cost_layer(gamma, cost_h)
        qaoa.mixer_layer(alpha, mixer_h)
    
    def qaoa_circuit(params, n_qubits, depth):
        #initalizing all qubits into +X eigenstate. 
        for w in range(n_qubits):
            qml.Hadamard(wires=w)
        gammas = params[0]
        alphas = params[1]
        #stacking building blocks for depth times.
        qml.layer(qaoa_layer, depth, gammas, alphas)
    
    @qml.qnode(dev)
    def cost(params):
        qaoa_circuit(params, n_qubits, depth)
        return qml.expval(cost_h)         
    
    results = {}    
    
    #Benchmarking: gradient descent
    print("\nGradient descent optimizer:")
    start_time = time.time()
    opt_gd = qml.GradientDescentOptimizer(stepsize=1e-2)            
    params, loss_recording = train(
        opt_gd, max_iter, params_init, cost,
    )                   
    end_time = time.time()
    results["gd_loss_per_iter"] = loss_recording
    results["gd_duration"] = end_time - start_time
    
    #Benchmarking: quantum natural gradient
    print("\nQuantum natural gradient optimizer:")
    start_time = time.time()
    opt_qnd = qml.QNGOptimizer(stepsize=5e-2)
    params, loss_recording = train(
        opt_qnd, max_iter, params_init, cost,
    )      
    end_time = time.time()
    results["qng_loss_per_iter"] = loss_recording    
    results["qng_duration"] = end_time - start_time
        
    #Benchmarking: QN-SPSA
    # To account for the stochastic nature of the optimizer,
    # the traces are taken multiple times (defined by hyperparameter
    # SPSA_repeats).
    print("\nQN-SPSA optimizer:")
    start_time = time.time()
    loss_recording = []   
    for j in range(spsa_repeats):
        print(f"Trace {j}:")
        opt_qnspsa = QNSPSA(
            lr=0.1, finite_diff_step=1e-2, 
            resamplings=1, blocking=True,
        )        
        params, loss_per_trace = train(
            opt_qnspsa, max_iter, params_init, cost,
        )                              
        loss_recording.append(loss_per_trace)
    end_time = time.time()
    results["qnspsa_loss_per_iter"] = loss_recording    
    results["qnspsa_duration"] = end_time - start_time
    
    #Benchmarking: SPSA
    # SPSA optimizer is initialized with the QNSPSA class, with 
    # disable_metric_tensor option set to be True.
    
    # To account for the stochastic nature of the optimizer,
    # the traces are taken multiple times (defined by hyperparameter
    # SPSA_repeats).
    print("\nSPSA optimizer:")
    start_time = time.time()
    loss_recording = []    
    for j in range(spsa_repeats):
        print(f"Trace {j}:")
        opt_spsa = QNSPSA(
            lr=2e-2, finite_diff_step=1e-2, 
            resamplings=1, blocking=False,
            disable_metric_tensor=True,
        )
        params, loss_per_trace = train(
            opt_spsa, max_iter, params_init, cost,
        )                        
        loss_recording.append(loss_per_trace)
    end_time = time.time()
    results["spsa_loss_per_iter"] = loss_recording    
    results["spsa_duration"] = end_time - start_time                
            
    save_job_result(results)
    
    
if __name__ == "__main__":    
    try:
        main()
        print("Training Successful!!")
    except BaseException as e:
        print(e)
        print("Training Fails...")

