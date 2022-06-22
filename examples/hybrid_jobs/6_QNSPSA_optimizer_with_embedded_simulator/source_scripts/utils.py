import pennylane as qml
import os
from pennylane import numpy as np


def get_device(n_wires, shots):
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    device_prefix = device_string.split(":")[0]

    if device_prefix == "local":
        prefix, device_name = device_string.split("/")
        if shots == 0:
            shots = None
        device = qml.device(device_name, wires=n_wires, shots=shots)
        print("Using local simulator: ", device.name)
    else:
        device = qml.device(
            "braket.aws.qubit",
            device_arn=device_string,
            s3_destination_folder=None,
            wires=n_wires,
            parallel=True,
            max_parallel=30,
            shots=shots,
        )
        print("Using AWS managed device: ", device.name)
    return device


def str2bool(logic_str):
    if logic_str == "True":
        return True
    if logic_str == "False":
        return False
    raise ValueError("Invalid boolean value.")


def train(opt, max_iter, params_init, qnode):
    loss_recording = []
    params = params_init
    for i in range(max_iter):
        params, loss = opt.step_and_cost(qnode, params)
        loss_recording.append(np.asscalar(loss))
        if i % 20 == 0:
            print(f"Step {i}:  loss = {np.asscalar(loss):.2f}")
    return params, loss_recording
