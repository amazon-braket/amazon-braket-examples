import json
import os
import time

import numpy as np
import pennylane as qml
from afqmc.classical_afqmc import chemistry_preparation, greens_pq, local_energy
from afqmc.quantum_afqmc_pennylane import quantum_afqmc
from braket.jobs import save_job_result
from pyscf import fci, gto


def run(
    quantum_times, num_walkers: int, num_steps: int, dtau: float, max_pool: int  # no type hint
):

    # perform HF calculations, where the geometry information and basis set are defined
    mol = gto.M(atom="H 0. 0. 0.; H 0. 0. 0.75", basis="sto-3g")
    # the atom argument provides the geometry of the molecule being studied, for example we
    # have hydrogen molecule above, where 0.75 is the bond distance in unit of angstrom;
    # for more complicated molecules, like lithium hydride, it should be:
    # gto.M(atom = ‘Li 0. 0. 0.; H 0. 0. 1.2’, basis = ‘sto-3g’)

    hf = mol.RHF()
    hf.kernel()

    # perform full configuration interaction (FCI) calculations
    myci = fci.FCI(hf)
    myci.kernel()

    # define the classical trial state, here we use the Hartree-Fock state as an example;
    # the dimension of the matrix should be (N * N_e), where N is the number of basis functions
    # here we have hf Slater determinant for hydrogen
    trial = np.array([[1, 0], [0, 1], [0, 0], [0, 0]])

    prop = chemistry_preparation(mol, hf, trial)

    # Separate the spin up and spin down channel of the trial state
    trial_up = trial[::2, ::2]
    trial_down = trial[1::2, 1::2]

    # compute its one particle Green's function
    G = [greens_pq(trial_up, trial_up), greens_pq(trial_down, trial_down)]
    Ehf = local_energy(prop.h1e, prop.eri, G, prop.nuclear_repulsion)

    print(f"The Hartree-Fock energy computed from local_energy is {np.round(Ehf, 10)}.")

    dev = qml.device("lightning.qubit", wires=4)

    quantum_times = json.loads(quantum_times)
    print(f"Runnign with quantum times:\n {quantum_times}")

    # Start QC-QFQMC computation
    start = time.time()
    quantum_energies, energies = quantum_afqmc(
        quantum_times, num_walkers, num_steps, dtau, trial, prop, max_pool=max_pool, dev=dev
    )
    elapsed = time.time() - start

    save_job_result(
        {
            "elapsed": elapsed,
            "quantum_energies": quantum_energies.tolist(),
            "energies": energies.tolist(),
        }
    )


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
