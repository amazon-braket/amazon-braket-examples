import json
import os

import numpy as np
from scipy.optimize import minimize

from braket.aws import AwsDevice
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric
from qcbm.qcbm import QCBM, mmd_loss

np.random.seed(42)


def main():
    print("Starting QCBM basic hybrid job...")

    device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]

    hyperparams = load_hyperparameters()
    print("Hyperparameters are:", hyperparams)

    filename = f"{input_dir}/input/data.npy"
    print("Loading dataset from: ", filename)
    data = np.load(filename)

    device = AwsDevice(device_arn)
    print(f"Using device {device}")

    print("Starting circuit training...")
    params = train_circuit(device, hyperparams, data)
    print("Final parameters were:", params)

    save_job_result({"params": params.tolist()})
    print("Saved results. All done.")


def load_hyperparameters():
    """Load the Hybrid Job hyperparameters"""
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file) as f:
        hyperparams = json.load(f)
    return hyperparams


def train_circuit(device, hyperparams: dict, data: np.ndarray):
    global iteration_number  # needed for callback in scipy optimizer
    iteration_number = 0

    n_qubits = int(hyperparams["n_qubits"])
    n_layers = int(hyperparams["n_layers"])
    n_iterations = int(hyperparams["n_iterations"])

    init_params = np.random.rand(3 * n_layers * n_qubits)

    qcbm = QCBM(device, n_qubits, n_layers, data)

    def callback(x):
        global iteration_number  # global
        iteration_number += 1
        loss = mmd_loss(qcbm.probabilities(x), data)
        log_metric(
            metric_name="loss",
            value=loss,
            iteration_number=iteration_number,
        )

    res = minimize(
        lambda x: mmd_loss(qcbm.probabilities(x), data),
        x0=init_params,
        method="L-BFGS-B",
        jac=lambda x: qcbm.gradient(x),
        options={"maxiter": n_iterations},
        callback=callback,
    )
    return res.x
