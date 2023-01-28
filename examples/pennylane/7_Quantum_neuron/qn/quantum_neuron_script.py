import json
import os
import time
import sys
import ast

import numpy as np
import matplotlib.pyplot as plt
from typing import List
from braket.aws import AwsQuantumJob, AwsSession
from braket.jobs.image_uris import Framework, retrieve_image
from braket.jobs import load_job_checkpoint, save_job_checkpoint, save_job_result
from braket.tracking import Tracker

import pennylane as qml

def init_pl_device(device_arn, n_nodes, shots, max_parallel):
    return qml.device(
        "braket.aws.qubit",
        device_arn=device_arn,
        wires=n_nodes,
        shots=shots,
        # Set s3_destination_folder=None to output task results to a default folder
        s3_destination_folder=None,
        parallel=True,
        max_parallel=max_parallel,
        # poll_timeout_seconds=30,
    )

def af(inputs:str, weights, bias, ancilla, output, n_nodes):  # af: activation function
    for qubit in range(len(inputs)):
        if(inputs[qubit]=='1'):
            qml.PauliX(qubit)
    
    for qubit in range(len(inputs)):
        qml.CRY(phi=2*weights[qubit], wires=[qubit, ancilla])
        
    qml.RY(2*bias, wires=ancilla)
    
    qml.CY(wires=[ancilla, output])
    qml.RZ(phi=-np.pi/2, wires=ancilla)
    
    for qubit in range(len(inputs)):
        qml.CRY(phi=-2*weights[qubit], wires=[qubit, ancilla])  # note '-(minus)'
        
    qml.RY(-2*bias, wires=ancilla)  # note '-(minus)'
    
    return [qml.sample(qml.PauliZ(i)) for i in range(n_nodes)]

def quantum_neuron(inputs:str, weights, bias, n_nodes, dev):
    ancilla = len(weights) # ID of an ancilla qubit
    output = len(weights) + 1   # ID of an output qubit
    
    theta = np.inner(np.array(list(inputs), dtype=int), np.array(weights)) + bias   # linear comination with numpy
    theta = theta.item()   # Convert numpy array to native python float-type
    
    af_circuit = qml.QNode(af, dev)
    sample = af_circuit(inputs, weights, bias, ancilla, output, n_nodes)
    sample = sample.T
    sample = (1 - sample.numpy()) / 2

    adopted_sample = sample[sample[:,ancilla] == 0]

    count_0 = len(adopted_sample[adopted_sample[:,output] == 0])
    count_1 = len(adopted_sample[adopted_sample[:,output] == 1])

    p_0 = count_0 / (count_0 + count_1)
    
    q_theta = np.arccos(np.sqrt(p_0))
    
    return theta, q_theta

def main():
    t = Tracker().start()
    
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]
    output_dir = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]
    job_name = os.environ["AMZN_BRAKET_JOB_NAME"]  # noqa
    checkpoint_dir = os.environ["AMZN_BRAKET_CHECKPOINT_DIR"]  # noqa
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    
    # Read the hyperparameters
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    
    n_inputs = int(hyperparams["n_inputs"])
    weights = ast.literal_eval(hyperparams["weights"])
    bias = float(hyperparams["bias"])
    shots = int(hyperparams["shots"])
    interface = hyperparams["interface"]
    max_parallel = int(hyperparams["max_parallel"])
    
    if "copy_checkpoints_from_job" in hyperparams:
        copy_checkpoints_from_job = hyperparams["copy_checkpoints_from_job"].split("/", 2)[-1]
    else:
        copy_checkpoints_from_job = None
    
    # Read input strings from input file
    with open(f"{input_dir}/input/inputs.txt") as f:
        inputs = [s.strip() for s in f.readlines()]
    
    # Prepare quantum neuron circuit
    n_nodes = n_inputs+2 # +2: ancilla and output qubit
    
    # Run quantum neuron circuit
    dev = init_pl_device(device_arn, n_nodes, shots, max_parallel)
    theta_list = []
    q_theta_list = []
    
    for i in range(2**n_inputs):
        theta, q_theta = quantum_neuron(inputs[i], weights, bias, n_nodes, dev)
        
        theta_list.append(theta)
        q_theta_list.append(q_theta)
        
    save_job_result({"theta_list": theta_list, "q_theta_list": q_theta_list, "task summary": t.quantum_tasks_statistics(), "estimated cost": t.qpu_tasks_cost() + t.simulator_tasks_cost()})

if __name__ == "__main__":
    main()