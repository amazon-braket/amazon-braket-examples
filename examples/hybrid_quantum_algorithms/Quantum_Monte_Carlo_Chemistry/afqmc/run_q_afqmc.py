import json
import os
import time

import numpy as np
import pennylane as qml
from pyscf import fci, gto

np.set_printoptions(precision=4, edgeitems=10, linewidth=150, suppress=True)


from afqmc.classical_afqmc import chemistry_preparation
from afqmc.quantum_afqmc_pennylane import qAFQMC
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric


def run(
    num_walkers: int,
    num_steps: int,
    dtau: float,
    max_pool: int,
    q_total_time: str,
):
    #####################################################################
    # We prepare the necessary operators for AFQMC calculations.        #
    #####################################################################
    # perform HF calculations
    mol = gto.M(atom="H 0. 0. 0.; H 0. 0. 0.75", basis="sto-3g")
    hf = mol.RHF()
    hf.kernel()

    # perform full configuration interaction (FCI) calculations
    myci = fci.FCI(hf)
    myci.kernel()

    trial = np.array([[1, 0], [0, 1], [0, 0], [0, 0]])
    properties = chemistry_preparation(mol, hf, trial)

    q_total_time = json.loads(q_total_time)

    dev = get_pennylane_device(4)

    # Start QC-QFQMC computation
    start = time.time()
    ctimes, qtimes, cE_list, qE_list, E_list = qAFQMC(
        q_total_time,
        num_walkers,
        num_steps,
        dtau,
        trial,
        properties,
        dev,
        max_pool=max_pool,
        progress_bar=False,
        log_metrics=True,
    )
    elapsed = time.time() - start

    # save results and log metrics
    print("elapsed: ", elapsed)
    print("cE_list: ", cE_list)
    print("qE_list: ", qE_list)
    save_job_result(
        {
            "elapsed": elapsed,
            "cE_list": cE_list,
            "qE_list": qE_list,
            "E_list": E_list,
            "ctimes": list(ctimes),
            "qtimes": list(qtimes),
        }
    )
    log_metric(metric_name="elapsed", value=elapsed, iteration_number=0)


def get_pennylane_device(n_wires):
    """Create Pennylane device from the `device` keyword argument of AwsQuantumJob.create().
    See https://docs.aws.amazon.com/braket/latest/developerguide/pennylane-embedded-simulators.html
    about the format of the `device` argument.

    Args:
        n_wires (int): number of qubits to initiate the local simulator.

    """
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    prefix, device_name = device_string.split("/")
    device = qml.device(device_name, wires=n_wires)
    print("Using simulator: ", device.name)
    return device
