import pennylane as qml
import os

def get_device(n_wires):
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    device_prefix = device_string.split(":")[0]

    if device_prefix=="local":
        prefix, device_name = device_string.split("/")
        device = qml.device(device_name, 
                            wires=n_wires, 
                            custom_decomps={"MultiRZ": qml.MultiRZ.compute_decomposition})
        print("Using local simulator: ", device.name)
    else:
        device = qml.device('braket.aws.qubit', 
                             device_arn=device_string, 
                             s3_destination_folder=None,
                             wires=n_wires,
                             parallel=True,
                             max_parallel=30)
        print("Using AWS managed device: ", device.name)
        
    return device