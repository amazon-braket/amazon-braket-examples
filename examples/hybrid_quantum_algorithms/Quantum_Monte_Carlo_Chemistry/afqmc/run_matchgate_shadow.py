import os, time
import numpy as np
import pennylane as qml
from pyscf import fci, gto
from afqmc.utils.shadow import calculate_classical_shadow
from afqmc.utils.matchgate import gaussian_givens_decomposition
from afqmc.utils.chemical_preparation import chemistry_preparation
from afqmc.trial_wavefunction.quantum_ovlp import QTrial
from afqmc.qmc.quantum_shadow import cqa_afqmc
from braket.jobs import save_job_result


def run(
    num_shadows: int,
    shots: int,
    num_walkers: int,
    num_steps: int,
    dtau: float,
    max_pool: int,
) -> None:
    """Run the entire QC-AFQMC algorithm.
    Args:
        num_shadows (int): number of shadow circuits
        shots (int): number of shots for measurement
        num_walkers (int): Number of walkers.
        num_steps (int): Number of (imaginary) time steps
        dtau (float): Increment of each time step
        quantum_evaluations_every_n_steps (int): How often to evaluate the energy using quantum
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
    
    # collect classical shadows
    num_qubits = 4
    dev = get_pennylane_device(n_wires=num_qubits, shots=shots)
    @qml.qnode(dev)
    def hydrogen_shadow_circuit(Q):
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        qml.DoubleExcitation(0.12, wires=[0, 1, 2, 3])
        gaussian_givens_decomposition(Q)
        return qml.counts()
    
    shadow = calculate_classical_shadow(hydrogen_shadow_circuit, num_shadows, num_qubits)
    print("The classical shadows are successfully collected.")
    
    Angstrom_to_Bohr = 1.88973
    symbols = ["H", "H"]
    geometry = np.array([[0., 0., 0.], [0., 0., 0.75*Angstrom_to_Bohr]])
    
    hamiltonian, _ = qml.qchem.molecular_hamiltonian(symbols, geometry, charge=0, basis='sto-3g')
    psi0 = np.array([[1, 0], [0, 1], [0, 0], [0, 0]])
    
    # define the quantum trial state
    qtrial = QTrial(prop=prop, initial_state=[0, 1], ansatz_circuit=V_T, ifshadow=True, shadow=shadow)
    
    # Start QC-QFQMC computation
    start = time.time()
    quantum_energies = cqa_afqmc(
        num_walkers,
        num_steps,
        dtau,
        qtrial,
        hamiltonian,
        psi0,
        max_pool=48,
    )
    elapsed = time.time() - start

    save_job_result(
        {
            "elapsed": elapsed,
            "quantum_energies": quantum_energies.tolist(),
        }
    )


def V_T():
    qml.DoubleExcitation(0.12, wires=[0,1,2,3])


def get_pennylane_device(n_wires: int, shots: int) -> qml.device:
    """Create Pennylane device from the `device` keyword argument of AwsQuantumJob.create().
    See https://docs.aws.amazon.com/braket/latest/developerguide/pennylane-embedded-simulators.html
    about the format of the `device` argument.
    Args:
        n_wires (int): number of qubits to initiate the local simulator.
    Returns:
        device: The Pennylane device
    """
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    prefix, device_name = device_string.split("/")
    device = qml.device(device_name, wires=n_wires, shots=shots)
    print("Using simulator: ", device.name)
    return device