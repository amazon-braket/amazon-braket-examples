import json
import os
import sys
import time
import copy
import numpy as np
import multiprocessing as mp
from scipy.linalg import expm
from tqdm import tqdm
import pennylane as qml
from pyscf import gto, scf, fci
from itertools import product
np.set_printoptions(precision=4, edgeitems=10, linewidth=150, suppress=True)

from braket.circuits import Circuit, FreeParameter
from braket.devices import LocalSimulator
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric

from afqmc.classical_afqmc import cAFQMC, G_pq, local_energy, chemistry_preparation
from afqmc.quantum_afqmc_pennylane import qAFQMC


def main():
    #####################################################################
    # We prepare the necessary operators for AFQMC calculations.        #
    #####################################################################
    # perform HF calculations
    mol = gto.M(atom = 'H 0. 0. 0.; H 0. 0. 0.75', basis = 'sto-3g')
    hf = mol.RHF()
    hf.kernel()

    # perform full configuration interaction (FCI) calculations
    myci = fci.FCI(hf)
    myci.kernel()

    trial = np.array([[1,0], [0,1], [0,0], [0,0]])
    operators = chemistry_preparation(mol, hf, trial)
    h1e, eri, nuclear_repulsion, v_0, h_chem, v_gamma, L_gamma, mf_shift, lambda_l, U_l = operators

    # Then we separate the spin up and spin down channel of the trial state
    trial_up = trial[::2,::2]
    trial_down = trial[1::2,1::2]

    # compute its one particle Green's function
    G = [G_pq(trial_up, trial_up), G_pq(trial_down, trial_down)]
    Ehf = local_energy(h1e, eri, G, nuclear_repulsion)
    print(f'The Hartree-Fock energy computed from local_energy is {np.round(Ehf, 10)}.')

    #####################################################################
    # Execution.                                                        #
    #####################################################################
    # Read the hyperparameters
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)

    num_walkers = int(hyperparams["num_walkers"])
    num_steps = int(hyperparams["num_steps"])
    dtau = float(hyperparams["dtau"] )
    max_pool = int(hyperparams["max_pool"]) 
    q_total_time = json.loads(hyperparams["q_total_time"])

    dev = get_pennylane_device(4)
    
    # Start QC-QFQMC computation
    start = time.time()
    total_time, cE_list, qE_list = qAFQMC(
        num_walkers, 
        num_steps, 
        q_total_time, 
        v_0, v_gamma, mf_shift, 
        dtau, 
        trial, h1e, eri,
        nuclear_repulsion, Ehf, h_chem, 
        lambda_l, U_l, 
        dev,
        max_pool=max_pool,
        progress_bar=False,
    )
    elapsed = time.time()-start
    
    # save results and log metrics
    print("elapsed: ", elapsed)
    print("cE_list: ", cE_list)
    print("qE_list: ", qE_list)
    save_job_result({"elapsed": elapsed, 
                     "cE_list": cE_list, 
                     "qE_list": qE_list,
                     "total_time": list(total_time), 
                     "q_total_time": list(q_total_time),                       
                }
            )
    log_metric(metric_name="elapsed", value=elapsed, iteration_number=0)        
            

def get_pennylane_device(n_wires):
    """ Create Pennylane device from the `device` keyword argument of AwsQuantumJob.create().
    See https://docs.aws.amazon.com/braket/latest/developerguide/pennylane-embedded-simulators.html
    about the format of the `device` argument.
    
    Args: 
        n_wires (int): number of qubits to initiate the local simulator. 
    
    """
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    device_prefix = device_string.split(":")[0]

    prefix, device_name = device_string.split("/")
    device = qml.device(device_name, wires=n_wires)
    print("Using local simulator: ", device.name)
        
    return device        
        
    
if __name__ == "__main__":
    try:
        main()
        print("Training Successful!!")
    except BaseException as e:
        print(e)
        print("Training Fails...")