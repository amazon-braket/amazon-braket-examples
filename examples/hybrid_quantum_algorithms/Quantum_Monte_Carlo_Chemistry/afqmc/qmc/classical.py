import copy, os
import numpy as np
import multiprocessing as mp
from typing import List, Tuple
from dataclasses import dataclass
from scipy.linalg import det, expm, qr
from afqmc.utils.linalg import reortho
from afqmc.estimators.greens_function import gab, gab_mod
from afqmc.trial_wavefunction.single_slater import SingleSlater
from afqmc.utils.chemical_preparation import ChemicalProperties
from afqmc.estimators.local_energy import local_energy_generic_cholesky


def classical_afqmc(
    num_walkers: int,
    num_steps: int,
    dtau: float,
    trial: SingleSlater,
    prop: ChemicalProperties,
    max_pool: int = 8,
):
    """Classical Auxiliary-Field Quantum Monte Carlo
    
    Args:
        num_walkers (int): Number of walkers.
        num_steps (int): Number of (imaginary) time steps
        dtau (float): Increment of each time step
        trial: Trial wavefunction as SingleSlater or MultiSlater class, currently only supports the former
        prop (ChemicalProperties): Chemical properties.
        max_pool (int, optional): Max workers. Defaults to 8.
        
    Returns:
        energies, weights, weighted_mean: Energies,
    """
    E_shift = trial.compute_trial_energy(prop)
    walkers = [trial.psi0] * num_walkers
    weights = [1.0] * num_walkers
    
    inputs = [
        (num_steps, dtau, trial, prop, E_shift, walker, weight)
        for walker, weight in zip(walkers, weights)
    ]
    
    inputs = [
        (num_steps, dtau, trial, prop, E_shift, walker, weight)
        for walker, weight in zip(walkers, weights)
    ]
    
    # parallelize with multiprocessing
    with mp.Pool(max_pool) as pool:
        results = list(pool.map(full_imag_time_evolution_wrapper, inputs))
        
    local_energies, weights = map(np.array, zip(*results))
    energies = np.real(np.average(local_energies, weights=weights, axis=0))
    return local_energies, energies


def full_imag_time_evolution_wrapper(args):
    return full_imag_time_evolution(*args)


def full_imag_time_evolution(
    num_steps: int,
    dtau: float,
    trial,
    prop: ChemicalProperties,
    E_shift: float,
    walker: np.ndarray,
    weight: float,
):
    """ Imaginary time evolution of a single walker
    Args:
        num_steps (int): number of time steps 
        dtau (float): imaginary time step size
        trial: trial state as SingleSlater or MultiSlater class
        prop (ChemicalProperties): Chemical properties
        E_shift (float): Reference energy, i.e. Hartree-Fock energy
        walker (np.ndarray): normalized walker state as np.ndarray, others are the same as trial
        weight (float): weight for sampling.        
    """
    # random seed for multiprocessing
    np.random.seed(int.from_bytes(os.urandom(4), byteorder="little"))
    
    energy_list, weights = [], [1.0]
    for _ in range(num_steps):
        E_loc, walker, weight = imag_time_propogator(dtau, trial, walker, weight, prop, E_shift)
        energy_list.append(E_loc)
        weights.append(weight)
        
    weights = weights[:-1]
    return energy_list, weights


def imag_time_propogator(
    dtau: float,
    trial,
    walker: np.ndarray,
    weight: float,
    prop: ChemicalProperties,
    E_shift: float,
):
    """ Propagate a walker by one time step

    Args:
        dtau (float): imaginary time step size
        trial: trial state as SingleSlater or MultiSlater class
        walker (np.ndarray): normalized walker state as np.ndarray, others are the same as trial
        weight (float): weight for sampling.
        prop (ChemicalProperties): Chemical properties.
        E_shift (float): Reference energy, i.e. Hartree-Fock energy
    """
    # First compute the bias force using the expectation value of L operators
    num_fields = len(prop.v_gamma)
    
    # compute the overlap integral
    ovlp = trial.compute_ovlp(walker)
    E_loc = trial.compute_local_energy(walker)
    
    # sampling the auxiliary fields
    x = np.random.normal(0.0, 1.0, size=num_fields)
    
    # update the walker
    new_walker = propagate_walker(x, prop, dtau, trial, walker)
    
    # Define the Id operator and find new weight
    new_ovlp = trial.compute_ovlp(new_walker)
    arg = np.angle(new_ovlp / ovlp)
    new_weight = weight*np.exp(-dtau*(np.real(E_loc) - E_shift))*np.max([0.0, np.cos(arg)])
    return E_loc, new_walker, new_weight



def propagate_walker(x: np.ndarray, 
                     prop: ChemicalProperties,
                     dtau: float, 
                     trial, 
                     walker: np.ndarray, 
    ):
    r"""This function updates the walker from imaginary time propagation.

    Args:
        x: auxiliary fields
        prop:
        dtau: imaginary time step size
        trial: trial state as SingleSlater or MultiSlater class
        walker: walker state as np.ndarray, others are the same as trial

    Returns:
        new_walker: new walker for next time step
    """
    num_spin_orbitals, num_electrons = walker.shape
    num_fields = len(prop.v_gamma)
    
    v_expectation = np.array([])
    for i in prop.v_gamma:
        v_expectation = np.append(v_expectation, trial.compute_one_body_local(walker, i))
    
    xbar = -np.sqrt(dtau)*(v_expectation - trial.mf_shift)
    xshifted = x - xbar
    
    # Define the B operator B(x - \bar{x})
    exp_v0 = expm(-dtau / 2 * trial.v_0)
    V = np.zeros((num_spin_orbitals, num_spin_orbitals), dtype=np.complex128)
    for i in range(num_fields):
        V += np.sqrt(dtau) * xshifted[i] * prop.v_gamma[i]
    exp_V = expm(V)
    
    # Note that v_gamma doesn't include the mf_shift, there is an additional term coming from
    # -(x - xbar)*mf_shift, this term is also a complex value.
    B = exp_v0 @ exp_V @ exp_v0
    
    # Find the new walker state
    #new_walker = B @ walker
    new_walker, _ = reortho(B @ walker)
    
    return new_walker
