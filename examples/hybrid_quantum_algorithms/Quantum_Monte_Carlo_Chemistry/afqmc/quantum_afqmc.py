import json
import numpy as np
from afqmc.utils.chemical_preparation import chemistry_preparation
from afqmc.utils.shadow import shadow_from_json
from afqmc.trial_wavefunction.quantum_ovlp import QTrial
from afqmc.qmc.quantum_shadow import cqa_afqmc
from pyscf import gto


def run(time_steps: int, delta_tau: float, shadows_file_path, num_walkers: int = 2):
    print("Running QC-AFQMC calculation")

    # perform HF calculations
    mol = gto.M(atom="H 0. 0. 0.; H 0. 0. 0.75", basis="sto-3g")
    hf = mol.RHF()
    hf.kernel()

    prop = chemistry_preparation(mol, hf)

    # load the matchgate shadows (compact {output, Q_save} JSON) straight into the compact in-memory
    # format -- no dense covariance/rotation matrices are materialized.
    with open(shadows_file_path, 'r') as file:
        matchgates = json.load(file)
    shadow = shadow_from_json(matchgates['output'], matchgates['Q_save'])
    print("The matchgate shadows are successfully loaded.")

    # initial HF walker (spin-orbital Slater determinant): N = nup + ndown electrons occupy the
    # lowest N of the 2*nbasis spin orbitals.
    psi0 = np.eye(2 * prop.nbasis, prop.nup + prop.ndown)

    # quantum trial state, evaluated entirely from the shadows; its E_shift and mf_shift are taken
    # from the classical Hartree-Fock reference (noiseless, no circuit -- no Hamiltonian needed here).
    qtrial = QTrial(prop=prop, shadow=shadow)

    local_energies, weights = cqa_afqmc(
        num_walkers=num_walkers,
        num_steps=time_steps,
        dtau=delta_tau,
        trial=qtrial,
        psi0=psi0,
        max_pool=num_walkers,
    )

    print("Calculation finished!")

    return {
        "local_energies_real": np.real(local_energies).tolist(),
        "local_energies_imag": np.imag(local_energies).tolist(),
        "weights": np.real(weights).tolist(),
    }
