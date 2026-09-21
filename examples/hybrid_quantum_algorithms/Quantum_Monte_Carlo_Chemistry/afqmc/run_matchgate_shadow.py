import os, time
import numpy as np
import pennylane as qp
from pyscf import fci, gto
from afqmc.utils.shadow import random_signed_permutation
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
        num_walkers (int): number of walkers.
        num_steps (int): number of (imaginary) time steps
        dtau (float): increment of each time step
        max_pool (int): max parallelization of walkers
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
    
    # collect classical shadows. num_qubits = number of JW spin orbitals = 2 * nbasis.
    num_qubits = 2 * prop.nbasis
    dev = get_pennylane_device(n_wires=num_qubits)
    @qp.set_shots(shots=shots)
    @qp.qnode(dev)
    def hydrogen_shadow_circuit(Q):
        # NOTE: this state preparation is the H2 trial ansatz; for another molecule replace it with
        # an ansatz acting on all `num_qubits` wires.
        qp.Hadamard(wires=0)
        qp.CNOT(wires=[0, 1])

        qp.DoubleExcitation(0.12, wires=[0, 1, 2, 3])
        gaussian_givens_decomposition(Q)
        return qp.counts()
    
    Q_list = [random_signed_permutation(2*num_qubits) for _ in range(num_shadows)]

    shadow = calculate_classical_shadow(hydrogen_shadow_circuit, Q_list)
    print("The classical shadows are successfully collected.")
    
    # initial HF walker (spin-orbital Slater determinant): N = nup + ndown electrons occupy the
    # lowest N of the 2*nbasis spin orbitals.
    psi0 = np.eye(num_qubits, prop.nup + prop.ndown)

    # define the quantum trial state (evaluated entirely from the matchgate shadows)
    qtrial = QTrial(prop=prop, shadow=shadow)

    # Start QC-QFQMC computation. The reference energy E_shift = <Psi_Q|H|Psi_Q> is estimated
    # from the same matchgate shadows inside cqa_afqmc, so no separate Hamiltonian is needed.
    start = time.time()
    quantum_energies = cqa_afqmc(
        num_walkers,
        num_steps,
        dtau,
        qtrial,
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
    qp.DoubleExcitation(0.12, wires=[0,1,2,3])


def get_pennylane_device(n_wires: int) -> qp.device:
    """Create Pennylane device from the `device` keyword argument of AwsQuantumJob.create().
    See https://docs.aws.amazon.com/braket/latest/developerguide/pennylane-embedded-simulators.html
    about the format of the `device` argument. Shots are applied at the QNode via the
    `qp.set_shots` transform (setting shots on the device is deprecated).
    Args:
        n_wires (int): number of qubits to initiate the local simulator.
    Returns:
        device: The Pennylane device
    """
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    prefix, device_name = device_string.split("/")
    device = qp.device(device_name, wires=n_wires)
    print("Using simulator: ", device.name)
    return device