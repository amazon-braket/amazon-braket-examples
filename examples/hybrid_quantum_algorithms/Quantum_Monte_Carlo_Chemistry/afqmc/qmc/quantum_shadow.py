import copy, os, time
import numpy as np
import pennylane as qml
import multiprocessing as mp
from dataclasses import dataclass
from scipy.linalg import det, expm, qr
from typing import Callable, List, Tuple
from afqmc.utils.linalg import reortho
from afqmc.trial_wavefunction.quantum_ovlp import QTrial

#-----------------------------------------------------------------------------------------------------
def cqa_afqmc(
    num_walkers: int,
    num_steps: int,
    dtau: float,
    trial: QTrial,
    hamiltonian,
    psi0: np.ndarray,
    max_pool: int=8,
):
    """Consistent Quantum-assisted Auxiliary-Field Quantum Monte Carlo
    Args:
        num_walkers (int): Number of walkers.
        num_steps (int): Number of (imaginary) time steps
        dtau (float): Increment of each time step
        trial (QTrial): quantum trial wavefunction.
        hamiltonian: pennylane hamiltonian class, for computing the trial state energy
        psi0 (np.ndarray): initial walker state.
        max_pool (int, optional): Max workers. Defaults to 8.
    Returns:
        energies: energies
    """
    E_shift = trial.compute_trial_energy(hamiltonian)
    walkers = [psi0] * num_walkers
    weights = [1.0] * num_walkers
    
    inputs = [
        (num_steps, dtau, trial, E_shift, walker, weight)
        for walker, weight in zip(walkers, weights)
    ]
    
    # parallelize with multiprocessing
    with mp.Pool(max_pool) as pool:
        results = list(pool.map(cqa_imag_time_evolution_wrapper, inputs))
        
    local_energies, weights = map(np.array, zip(*results))
    energies = np.real(np.average(local_energies, weights=weights, axis=0))
    
    return energies


def cqa_imag_time_evolution_wrapper(args):
    return cqa_imag_time_evolution(*args)


def cqa_imag_time_evolution(
    num_steps: int,
    dtau: float,
    trial: QTrial,
    E_shift: float,
    walker: np.ndarray,
    weight: float,
):
    # random seed for mutliprocessing
    np.random.seed(int.from_bytes(os.urandom(4), byteorder="little"))
    
    energy_list, weights = [], [1.0]
    for time in range(num_steps):
        E_loc, walker, weight = cqa_imag_time_propogator(
            dtau, trial, walker, weight, E_shift
        )
        energy_list.append(E_loc)
        weights.append(weight)
        
    weights = weights[:-1]
    return energy_list, weights


def cqa_imag_time_propogator(
    dtau: float,
    trial: QTrial,
    walker: np.ndarray,
    weight: float,
    E_shift: float,
):
    """Imaginary time propogator with quantum propagation of a single walker and energy evaluation.
    Args:
        dtau (float): imaginary time step size
        trial (QTrial): trial state as np.ndarray, e.g., for h2 HartreeFock state.
        walker (np.ndarray): normalized walker state as np.ndarray, others are the same as trial
        weight (float): weight for sampling.
        prop (ChemicalProperties): Chemical properties from q_chemistry_preparation.
        E_shift (float): Reference energy, i.e. Hartree-Fock energy
        shadow
    Returns:
        E_loc: quantum local energy
        new_walker: new walker for the next time step
        new_weight: new weight for the next time step
    """
    # First compute the bias force using the expectation value of L operators
    num_fields = len(trial.v_gamma)
    
    # compute the overlap between qtrial state and walker
    ovlp = trial.compute_ovlp(walker)
    E_loc, ovlp_dict = trial.compute_local_energy(walker, ovlp)
    E_loc = E_loc / ovlp + trial.nuclear_repulsion
    
    # update the walker
    x = np.random.normal(0.0, 1.0, size=num_fields)
    new_walker = q_propogate_walker(x, trial, dtau, walker, ovlp, ovlp_dict)    
    
    # Define the I operator and find new weight
    new_ovlp = trial.compute_ovlp(new_walker)
    arg = np.angle(new_ovlp / ovlp)
    new_weight = weight * np.exp(-dtau * (np.real(E_loc) - E_shift)) * np.max([0.0, np.cos(arg)])
    
    return E_loc, new_walker, new_weight


def q_propogate_walker(
        x: np.array, 
        trial: QTrial,
        dtau: float, 
        walker: np.ndarray,
        ovlp: float,
        ovlp_dict: dict,
    ):
    r"""This function updates the walker from imaginary time propagation.
    Args:
        x: auxiliary fields
        trial:
        dtau: imaginary time step size
        walker: walker state as np.ndarray, others are the same as trial
        ovlp: amplitude between walker and the quantum trial state
        shadow
    Returns:
        new_walker: new walker for the next time step
    """
    num_spin_orbitals, num_electrons = walker.shape
    num_fields = len(trial.v_gamma)
    v_expectation = 1.j * trial.compute_one_body_local(walker, trial.L_gamma, ovlp, ovlp_dict)
    
    # Sampling the auxiliary fields
    xbar = -np.sqrt(dtau) * (v_expectation - trial.mf_shift)
    xshifted = x - xbar
    
    # Define the B operator B(x - \bar{x})
    exp_v0 = expm(-dtau / 2 * trial.v_0)
    V = np.zeros((num_spin_orbitals, num_spin_orbitals), dtype=np.complex128)
    for i in range(num_fields):
        V += np.sqrt(dtau) * xshifted[i] * trial.v_gamma[i]
    exp_V = expm(V)
    
    # Note that v_gamma doesn't include the mf_shift, there is an additional term coming from
    # -(x - xbar)*mf_shift, this term is also a complex value.
    B = exp_v0 @ exp_V @ exp_v0
    
    # Find the new walker state
    new_walker, _ = reortho(B @ walker)
    return new_walker