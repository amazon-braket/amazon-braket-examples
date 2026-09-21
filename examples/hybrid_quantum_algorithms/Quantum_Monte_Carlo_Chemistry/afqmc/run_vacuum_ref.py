import os, time
import numpy as np
import pennylane as qp
from pyscf import fci, gto
from afqmc.utils.chemical_preparation import chemistry_preparation
from afqmc.trial_wavefunction.quantum_vacuum_reference import QTrial
from afqmc.qmc.quantum_vacuum_reference import cqa_afqmc
from braket.jobs import save_job_result


def run(
    num_walkers: int,
    num_steps: int,
    dtau: float,
    max_pool: int,
) -> None:
    """Run the entire QC-AFQMC algorithm (vacuum-reference variant).
    Args:
        num_walkers (int): Number of walkers.
        num_steps (int): Number of (imaginary) time steps
        dtau (float): Increment of each time step
        max_pool (int): Max workers.
    """
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
    prop = chemistry_preparation(mol, hf)
    
    Angstrom_to_Bohr = 1.88973
    symbols = ["H", "H"]
    geometry = np.array([[0., 0., 0.], [0., 0., 0.75*Angstrom_to_Bohr]])
    
    hamiltonian, _ = qp.qchem.molecular_hamiltonian(symbols, geometry, charge=0, basis='sto-3g')

    # initial HF walker (spin-orbital Slater determinant) and occupied-orbital list, derived from
    # the molecule: N = nup + ndown electrons occupy the lowest N spin orbitals of 2*nbasis.
    num_electrons = prop.nup + prop.ndown
    psi0 = np.eye(2 * prop.nbasis, num_electrons)
    initial_state = list(range(num_electrons))

    # define the quantum trial state (V_T is the ansatz; it must act on 2*prop.nbasis wires)
    q_trial = QTrial(prop, initial_state, V_T)

    # Start QC-QFQMC computation
    start = time.time()
    quantum_energies = cqa_afqmc(
        num_walkers,
        num_steps,
        dtau,
        q_trial,
        hamiltonian,
        psi0,
        max_pool=max_pool,
    )
    elapsed = time.time() - start

    save_job_result(
        {
            "elapsed": elapsed,
            "quantum_energies": quantum_energies.tolist(),
        }
    )


def V_T():
    qp.DoubleExcitation(0.12, wires=[0,1,2,3])
