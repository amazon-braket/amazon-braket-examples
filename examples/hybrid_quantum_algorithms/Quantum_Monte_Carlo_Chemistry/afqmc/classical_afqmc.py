import numpy as np
from afqmc.utils.chemical_preparation import chemistry_preparation
from afqmc.trial_wavefunction.single_slater import SingleSlater
from afqmc.qmc.classical import classical_afqmc
from pyscf import gto


def run(time_steps: int, delta_tau: float, num_walkers: int = 2):
    print("Running classical AFQMC calculation")

    # perform HF calculations
    mol = gto.M(atom="H 0. 0. 0.; H 0. 0. 0.75", basis="sto-3g")
    hf = mol.RHF()
    hf.kernel()

    psi0 = np.array([[1, 0], [0, 1], [0, 0], [0, 0]])
    prop = chemistry_preparation(mol, hf)
    trial = SingleSlater(prop, psi0)

    local_energies, weights = classical_afqmc(
        num_walkers=num_walkers,
        num_steps=time_steps,
        dtau=delta_tau,
        trial=trial,
        prop=prop,
        max_pool=num_walkers,
    )

    print("Calculation finished!")

    return {
        "local_energies_real": np.real(local_energies).tolist(),
        "local_energies_imag": np.imag(local_energies).tolist(),
        "weights": np.real(weights).tolist(),
    }