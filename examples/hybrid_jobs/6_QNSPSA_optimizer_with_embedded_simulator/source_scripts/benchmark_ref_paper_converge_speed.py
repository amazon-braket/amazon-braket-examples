import pennylane as qml
from pennylane import numpy as np
import random
import json
import os
from source_scripts.utils import get_device, str2bool, train
from source_scripts.QNSPSA import QNSPSA
from braket.jobs import save_job_result
import time
import functools


def sample_gates(n_qubits, n_layers, seed):
    random.seed(seed)
    rot_gates = [qml.RX, qml.RY, qml.RZ]
    sampled_gates = []
    for i in range(n_qubits):
        gates_per_qubit = random.choices(rot_gates, k=n_layers)
        sampled_gates.append(gates_per_qubit)
    return sampled_gates


def ansatz_template(params, num_of_wires, sampled_gates, H):
    if num_of_wires < 2:
        raise ValueError(
            "Number of wires is smaller than 2. "
            "The ansatz works on at least two qubits."
        )
    if num_of_wires != len(sampled_gates):
        raise ValueError(
            "The length of list wires needs to match" "the length of sampled_gates"
        )
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
    optimizer_name = hyperparams["optimizer"]
    seed = int(hyperparams["seed"])

    dev = get_device(n_qubits, shots)

    np.random.seed(seed)
    params_init = 2 * (np.random.rand(n_qubits * n_layers) - 0.5) * np.pi
    sampled_gates = sample_gates(n_qubits, n_layers, seed)

    H = qml.PauliZ(n_qubits // 2 - 1) @ qml.PauliZ(n_qubits // 2)

    @qml.qnode(dev)
    def cost(params):
        return ansatz_template(params, n_qubits, sampled_gates, H)

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
