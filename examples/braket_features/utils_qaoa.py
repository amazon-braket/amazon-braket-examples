# IMPORTS
import numpy as np
from braket.aws import AwsDevice
from braket.circuits import Circuit, Observable, circuit, FreeParameter, QubitSet
from braket.devices import LocalSimulator
from scipy.optimize import minimize


# function to implement evolution with driver Hamiltonian
@circuit.subroutine(register=True)
def driver(beta, n_qubits):
    """
    Returns circuit for driver Hamiltonian U(Hb, beta)
    """
    # instantiate circuit object
    circ = Circuit()

    # apply parametrized rotation around x to every qubit
    for qubit in range(n_qubits):
        gate = Circuit().rx(qubit, beta)
        circ.add(gate)

    return circ

# helper function for evolution with cost Hamiltonian
@circuit.subroutine(register=True)
def cost_circuit(gammas, n_qubits, ising, device):
    """
    returns circuit for evolution with cost Hamiltonian
    """
    # instantiate circuit object
    circ = Circuit()

    # get all non-zero entries (edges) from Ising matrix
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))

    # apply ZZ gate for every edge (with corresponding interaction strength)
    for (ii, qubit_pair) in enumerate(edges):
        circ.zz(qubit_pair[0], qubit_pair[1], angle=gammas[ii])

    return circ


# function to build the QAOA circuit with depth p
def circuit(params, device, n_qubits, ising):
    """
    function to return full QAOA circuit; depends on device as ZZ implementation depends on gate set of backend
    """

    # initialize qaoa circuit with first Hadamard layer: for minimization start in |->
    circ = Circuit()
    H_on_all = Circuit().h(range(0, n_qubits))
    circ.add(H_on_all)

    # setup two parameter families
    circuit_length = int(len(params) / 2)
    gammas = params[:circuit_length]
    betas = params[circuit_length:]

    # add QAOA circuit layer blocks
    for mm in range(circuit_length):
        circ.cost_circuit(gammas[mm], n_qubits, ising, device)
        circ.driver(betas[mm], n_qubits)
    return circ

def cost_H(ising):
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))

    H = []
    # apply ZZ gate for every edge (with corresponding interaction strength)
    for qubit_pair in edges[1:]:
        # get interaction strength from Ising matrix
        int_strength = ising[qubit_pair[0], qubit_pair[1]]
        H.append(2*ising[qubit_pair[0], qubit_pair[1]] * Observable.Z() @ Observable.Z())
    targets = [QubitSet([edge[0], edge[1]]) for edge in edges]
    return sum(H, 2*ising[edges[0][0], edges[0][1]] * Observable.Z() @ Observable.Z()), targets

def form_inputs_dict(params, ising):
    n_params = len(params)
    params_dict = {}
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))
    split = int(n_params/2)
    for i in range(split):
        params_dict[f'beta_{i}'] = 2 * params[split + i]
        for j in range(len(edges)):
            params_dict[f'gamma_{i}_{j}'] = 2 * ising[edges[j][0], edges[j][1]] * params[i]
    
    return params_dict

def form_jacobian(n_params, gradient, ising):
    # fix jacobian
    jac = [0.0] * n_params
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))
    split = int(n_params/2)
    for i in range(split):
        # handle betas
        jac[split + i] += 2 * gradient[f'beta_{i}']
        # handle gammas
        for j in range(len(edges)):
            jac[i] += 2 * ising[edges[j][0], edges[j][1]] * gradient[f'gamma_{i}_{j}']
    
    return jac

# function that computes cost function for given params
def objective_function(params, qaoa_circuit, ising, device, tracker, verbose):
    """
    objective function takes a list of variational parameters as input,
    and returns the cost associated with those parameters
    """

    if verbose:
        print("==================================" * 2)
        print("Calling the quantum circuit. Cycle:", tracker["count"])

    # create parameter dict
    params_dict = form_inputs_dict(params, ising)
    # classically simulate the circuit
    # set the parameter values using the inputs argument
    # execute the correct device.run call depending on whether the backend is local or cloud based
    task = device.run(
        qaoa_circuit(**params_dict), shots=0, poll_timeout_seconds=3 * 24 * 60 * 60
    )

    # get result for this task
    result = task.result()
    energy = 0.0
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))
    for (term, edge) in zip(result.values, edges):
        energy += 2*ising[edge[0], edge[1]]*term
    
    # get metadata
    metadata = result.task_metadata

    tracker["opt_energies"].append(energy)

    # store optimal (classical) result/bitstring
    if energy < tracker["optimal_energy"]:
        tracker.update({"optimal_energy": energy})

    # store global minimum
    tracker["global_energies"].append(tracker["optimal_energy"])

    if verbose:
        print("Energy expectation value (cost):", energy)

    # update tracker
    tracker.update({"count": tracker["count"] + 1, "res": result})
    tracker["costs"].append(energy)
    tracker["params"].append(params)

    return energy

# The function to execute the training: run classical minimization.
def train(
    device, options, p, ising, n_qubits, opt_method, tracker, params0, verbose=True
):
    """
    function to run QAOA algorithm for given ising matrix, fixed circuit depth p
    """
    print("Starting the training.")

    print("==================================" * 2)
    print(f"OPTIMIZATION for circuit depth p={p}")

    if not verbose:
        print('Param "verbose" set to False. Will not print intermediate steps.')
        print("==================================" * 2)

    # initialize
    cost_energy = []

    # set bounds for search space
    bnds_gamma = [(0, 2 * np.pi) for _ in range(int(len(params0) / 2))]
    bnds_beta = [(0, np.pi) for _ in range(int(len(params0) / 2))]
    bnds = bnds_gamma + bnds_beta

    tracker["params"].append(params0)
     
    gamma_params = [[FreeParameter(f"gamma_{i}_{j}") for j in range(len(ising.nonzero()[0]))] for i in range(p)]
    beta_params = [FreeParameter(f"beta_{i}") for i in range(p)]
    params = gamma_params + beta_params
    H, targets = cost_H(ising)
    qaoa_circ = circuit(params, device, n_qubits, ising)
    for (term, target) in zip(H.summands, targets):
        qaoa_circ.expectation(observable=term._unscaled(), target=target)
    
    print('Initial energy: ', objective_function(params0, qaoa_circ, ising, device, tracker, False))
    # run classical optimization (example: method='Nelder-Mead')
    result = minimize(
        objective_function,
        params0,
        jac=False,
        args=(qaoa_circ, ising, device, tracker, verbose),
        options=options,
        method=opt_method,
        bounds=bnds,
    )

    # store result of classical optimization
    result_energy = result.fun
    cost_energy.append(result_energy)
    print("Final average energy (cost):", result_energy)
    result_angle = result.x
    print("Final angles:", result_angle)
    print("Training complete.")

    return result_energy, result_angle, tracker

# function that computes cost function and gradient for given params
def objective_function_adjoint(params, qaoa_circuit, ising, device, tracker, verbose):
    """
    objective function takes a list of variational parameters as input,
    and returns the cost associated with those parameters
    """

    if verbose:
        print("==================================" * 2)
        print("Calling the quantum circuit. Cycle:", tracker["count"])

    # create parameter dict
    params_dict = form_inputs_dict(params, ising) 
    # classically simulate the circuit
    # set the parameter values using the inputs argument
    # execute the correct device.run call depending on whether the backend is local or cloud based
    task = device.run(
        qaoa_circuit, shots=0, inputs=params_dict, poll_timeout_seconds=3 * 24 * 60 * 60
    )

    # get result for this task
    result = task.result()
    gradient = result.values[0]
    energy = gradient['expectation']
    # get metadata
    metadata = result.task_metadata

    tracker["opt_energies"].append(energy)

    # store optimal energy 
    if energy < tracker["optimal_energy"]:
        tracker.update({"optimal_energy": energy})

    # store global minimum
    tracker["global_energies"].append(tracker["optimal_energy"])

    if verbose:
        print("Energy expectation value (cost):", energy)

    # update tracker
    tracker.update({"count": tracker["count"] + 1, "res": result})
    tracker["costs"].append(energy)
    tracker["params"].append(params)
    jac = form_jacobian(len(params), gradient["gradient"], ising)
    return energy, jac


# The function to execute the training: run classical minimization.
def train_adjoint(
    device, options, p, ising, n_qubits, opt_method, tracker, params0, verbose=True
):
    """
    function to run QAOA algorithm for given, fixed circuit depth p
    """
    print("Starting the training.")

    print("==================================" * 2)
    print(f"OPTIMIZATION for circuit depth p={p}")

    if not verbose:
        print('Param "verbose" set to False. Will not print intermediate steps.')
        print("==================================" * 2)

    # initialize
    cost_energy = []

    # set bounds for search space
    bnds_gamma = [(0, 2 * np.pi) for _ in range(int(len(params0) / 2))]
    bnds_beta = [(0, np.pi) for _ in range(int(len(params0) / 2))]
    bnds = bnds_gamma + bnds_beta

    tracker["params"].append(params0)
    
    gamma_params = [[FreeParameter(f"gamma_{i}_{j}") for j in range(len(ising.nonzero()[0]))] for i in range(p)]
    beta_params = [FreeParameter(f"beta_{i}") for i in range(p)]
    params = gamma_params + beta_params
    qaoa_circ = circuit(params, device, n_qubits, ising)
    
    H, targets = cost_H(ising)
    qaoa_circ.adjoint_gradient(observable=H, target=targets, parameters=[])
    
    print('Initial energy: ', objective_function_adjoint(params0, qaoa_circ, ising, device, tracker, False)[0])
    # run classical optimization (example: method='Nelder-Mead')
    result = minimize(
        objective_function_adjoint,
        params0,
        jac=True, # objective function will return both f and its jacobian
        args=(qaoa_circ, ising, device, tracker, verbose),
        options=options,
        method=opt_method,
        bounds=bnds,
    )

    # store result of classical optimization
    result_energy = result.fun
    cost_energy.append(result_energy)
    print("Final average energy (cost):", result_energy)
    result_angle = result.x
    print("Final angles:", result_angle)
    print("Training complete.")

    return result_energy, result_angle, tracker
