import os

# update pennylane version to 0.23 for QNG to be compatible with
# QAOA use cases.
os.system("pip install pennylane==0.23.0 -q")

import pennylane as qml
from pennylane import numpy as np
import random
import json
from source_scripts.utils import get_device, str2bool, train
from source_scripts.QNSPSA import QNSPSA
from braket.jobs import save_job_result
import time
import networkx as nx
from pennylane import qaoa
import functools


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
    optimizer_name = hyperparams["optimizer"]
    lr = float(hyperparams["learn_rate"])

    dev = get_device(n_qubits, shots)

    if load_init_config:
        prefix = os.environ["AMZN_BRAKET_SCRIPT_ENTRY_POINT"].split(".")[0]
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
        # initalizing all qubits into +X eigenstate.
        for w in range(n_qubits):
            qml.Hadamard(wires=w)
        gammas = params[0]
        alphas = params[1]
        # stacking building blocks for depth times.
        qml.layer(qaoa_layer, depth, gammas, alphas)

    @qml.qnode(dev)
    def cost(params):
        qaoa_circuit(params, n_qubits, depth)
        return qml.expval(cost_h)

    results = {}

    # SPSA optimizer is initialized with the QNSPSA class, with
    # disable_metric_tensor option set to be True.
    opt_choice = {
        "GD": qml.GradientDescentOptimizer,
        "QNG": qml.QNGOptimizer,
        "QNSPSA": QNSPSA,
        "SPSA": functools.partial(
            QNSPSA,
            blocking=False,
            disable_metric_tensor=True,
        ),
    }

    print(f"{optimizer_name} optimizer:")
    start_time = time.time()
    loss_recording = []

    # To account for the stochastic nature of the optimizer,
    # the traces are taken multiple times (defined by hyperparameter
    # SPSA_repeats).
    for j in range(spsa_repeats):
        print(f"Trace {j}:")
        opt = opt_choice[optimizer_name](stepsize=lr)

        params, loss_per_trace = train(
            opt,
            max_iter,
            params_init,
            cost,
        )
        loss_recording.append(loss_per_trace)
    end_time = time.time()
    results[f"{optimizer_name}_loss_per_iter"] = loss_recording
    results[f"{optimizer_name}_duration"] = end_time - start_time

    save_job_result(results)


if __name__ == "__main__":
    try:
        main()
        print("Training Successful!!")
    except BaseException as e:
        print(e)
        print("Training Fails...")
