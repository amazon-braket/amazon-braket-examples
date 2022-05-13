import pennylane as qml
from pennylane import numpy as np
import random
import json
import os
from source_scripts.utils import get_device, str2bool, train
from source_scripts.QNSPSA import QNSPSA
from braket.jobs import save_job_result
import time


def sample_gates(n_qubits, n_layers):
    rot_gates = [qml.RX, qml.RY, qml.RZ]
    sampled_gates = []
    for i in range(n_qubits):
        gates_per_qubit = random.choices(rot_gates, k=n_layers)
        sampled_gates.append(gates_per_qubit)
    return sampled_gates


def ansatz_template(params, num_of_wires, sampled_gates, H):
    if num_of_wires < 2:
        raise ValueError("Number of wires is smaller than 2. " 
                         "The ansatz works on at least two qubits.")    
    if num_of_wires != len(sampled_gates):
        raise ValueError("The length of list wires needs to match"
                         "the length of sampled_gates")    
    m = len(sampled_gates[0])
    for k in range(m - 1):
        for i in range(num_of_wires):
            qml.RY(np.pi / 4, wires=i)
            sampled_gates[i][k](params[i * m + k], wires=i)
        for i in range(0, num_of_wires - 1, 2):
            qml.CZ(wires=[i, i + 1])
        for i in range(1, num_of_wires - 1, 2):
            qml.CZ(wires=[i, i + 1])
    
    for i in range(num_of_wires):
        qml.RY(np.pi / 4, wires=i)
        sampled_gates[i][m - 1](params[i * m + m - 1], wires=i)
    return qml.expval(H)


def main(): 
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    print(hyperparams)
    
    # problem-setup hyperparams
    n_qubits = int(hyperparams["n_qubits"])
    n_layers = int(hyperparams["n_layers"]) 
    shots = int(hyperparams["shots"]) 
    max_iter = int(hyperparams["max_iter"])
    lr = float(hyperparams["learn_rate"])
    spsa_repeats = int(hyperparams["spsa_repeats"])
    
    dev = get_device(n_qubits, shots)


    params_init = 2 * (np.random.rand(n_qubits * n_layers) - 0.5) * np.pi
    sampled_gates = sample_gates(n_qubits, n_layers)
    
    H = qml.PauliZ(n_qubits // 2 - 1) @ qml.PauliZ(n_qubits // 2)
    
    @qml.qnode(dev)
    def cost(params):
        return ansatz_template(params, n_qubits, sampled_gates, H)

    results = {}    
    
    #Benchmarking: gradient descent
    print("\nGradient descent optimizer:")
    start_time = time.time()
    opt_gd = qml.GradientDescentOptimizer(stepsize=lr)            
    params, loss_recording = train(
        opt_gd, max_iter, params_init, cost,
    )                   
    end_time = time.time()
    results["gd_loss_per_iter"] = loss_recording
    results["gd_duration"] = end_time - start_time
    
    #Benchmarking: quantum natural gradient
    print("\nQuantum natural gradient optimizer:")
    start_time = time.time()
    opt_qnd = qml.QNGOptimizer(stepsize=lr)
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
            lr=lr, finite_diff_step=1e-2, 
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
            lr=lr, finite_diff_step=1e-2, 
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

