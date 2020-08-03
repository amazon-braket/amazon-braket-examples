# IMPORTS
import numpy as np
from scipy.optimize import minimize
from braket.circuits import Circuit, Observable


# function to implement ZZ gate using CNOT gates
def ZZgate(q1, q2, gamma):
    """
    function that returns a circuit implementing exp(-i \gamma Z_i Z_j) using CNOT gates if ZZ not supported
    """

    # get a circuit
    circ_zz = Circuit()

    # construct decomposition of ZZ
    circ_zz.cnot(q1, q2).rz(q2, gamma).cnot(q1, q2)

    return circ_zz


# function to implement evolution with driver Hamiltonian
def driver(beta, n_qubits):
    """
    Returns circuit for driver Hamiltonian U(Hb, beta)
    """
    # instantiate circuit object
    circ = Circuit()

    # apply parametrized rotation around x to every qubit
    for qubit in range(n_qubits):
        gate = Circuit().rx(qubit, 2*beta)
        circ.add(gate)

    return circ


# helper function for evolution with cost Hamiltonian
def cost_circuit(gamma, n_qubits, ising, device):
    """
    returns circuit for evolution with cost Hamiltonian
    """
    # instantiate circuit object
    circ = Circuit()

    # get all non-zero entries (edges) from Ising matrix
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))

    # apply ZZ gate for every edge (with corresponding interation strength)
    for qubit_pair in edges:
        # get interaction strength from Ising matrix
        int_strength = ising[qubit_pair[0], qubit_pair[1]]
        # for Rigetti we decompose ZZ using CNOT gates
        if device.name == 'Rigetti':
            gate = ZZgate(qubit_pair[0], qubit_pair[1], gamma*int_strength)
            circ.add(gate)
        # classical simulators and IonQ support ZZ gate
        else:
            gate = Circuit().zz(qubit_pair[0], qubit_pair[1], angle=2*gamma*int_strength)
            circ.add(gate)

    return circ


# function to build the QAOA circuit with depth p
def circuit(params, device, n_qubits, ising):
    """
    function to return full QAOA circuit; depends on device as ZZ implementation depends on gate set of backend
    """

    # initialize qaoa circuit with first Hadamard layer: for minimization start in |->
    circ = Circuit()
    X_on_all = Circuit().x(range(0, n_qubits))
    circ.add(X_on_all)
    H_on_all = Circuit().h(range(0, n_qubits))
    circ.add(H_on_all)

    # setup two parameter families
    circuit_length = int(len(params) / 2)
    gammas = params[:circuit_length]
    betas = params[circuit_length:]

    # add QAOA circuit layer blocks
    for mm in range(circuit_length):
        circ.add(cost_circuit(gammas[mm], n_qubits, ising, device))
        circ.add(driver(betas[mm], n_qubits))

    return circ


# function that computes cost function for given params
def objective_function(params, device, ising, n_qubits, n_shots, tracker):
    """
    objective function takes a list of variational parameters as input,
    and returns the cost associated with those parameters
    """

    print('==================================' * 2)
    print('Calling the quantum circuit. Cycle:', tracker['count'])

    # get a quantum circuit instance from the parameters
    qaoa_circuit = circuit(params, device, n_qubits, ising)

    # add expectation values for all non-zero ZZ terms in Hamiltonian <ZZ>
    # first define two-qubit operator ZZ
    obs = Observable.Z() @ Observable.Z()
    # get all non-zero edges
    idx = ising.nonzero()
    edges = list(zip(idx[0], idx[1]))
    # add all <ZZ> terms as required based on cost Hamitlonian
    for qubit_pair in edges:
        qaoa_circuit.expectation(obs, target=qubit_pair)

    # classically simulate the circuit
    # execute the correct device.run call depending on whether the backend is local or cloud based
    if device.name == 'DefaultSimulator':
        task = device.run(qaoa_circuit, shots=n_shots)
    else:
        task = device.run(qaoa_circuit, s3_folder,
                          shots=n_shots, poll_timeout_seconds=3*24*60*60)

    # get result for this task
    result = task.result()

    # get metadata
    metadata = result.task_metadata

    # convert results (0 and 1) to ising (-1 and 1)
    meas_ising = result.measurements
    meas_ising[meas_ising == 0] = -1

    # get all energies (for every shot): (n_shots, 1) vector
    all_energies = np.diag(np.dot(meas_ising, np.dot(ising, np.transpose(meas_ising))))

    # find minimum and corresponding classical string
    energy_min = np.min(all_energies)
    print('Minimal energy:', energy_min)
    tracker['opt_energies'].append(energy_min)
    optimal_string = meas_ising[np.argmin(all_energies)]
    print('Optimal classical string:', optimal_string)
    tracker['opt_bitstrings'].append(optimal_string)

    # store optimal (classical) result/bitstring
    if energy_min < tracker['optimal_energy']:
        tracker.update({'optimal_energy': energy_min})
        tracker.update({'optimal_bitstring': optimal_string})

    # store global minimum
    tracker['global_energies'].append(tracker['optimal_energy'])

    # get all <ZZ> expectation values
    energies = np.array(result.values)
    # get all non-zero interaction stengths from Ising matrix
    interactions = np.array([ising[q[0], q[1]] for q in edges])
    # multiply expectation values <ZZ> by J_ij
    energies_scaled = interactions * energies

    # get energy expectation value <H_C> = sum_{ij} J_{ij} <Z_i Z_j>
    energy_expect = np.round(np.sum(energies_scaled), 3)
    # print cost (could consider other definitions of cost function)
    print('Energy expectation value (cost):', energy_expect)

    # update tracker
    tracker.update({'count': tracker['count']+1, 'res': result})
    tracker['costs'].append(energy_expect)
    tracker['params'].append(params)

    return energy_expect


# The function to execute the training: run classical minimization.
def train(device, options, p, ising, n_qubits, n_shots, opt_method, tracker):
    """
    function to run QAOA algorithm for given, fixed circuit depth p
    """
    print('Starting the training.')

    print('==================================' * 2)
    print(f'OPTIMIZATION for circuit depth p={p}')

    # initialize
    cost_energy = []

    # randomly initialize variational parameters within appropriate bounds
    gamma_initial = np.random.uniform(0, 2 * np.pi, p).tolist()
    beta_initial = np.random.uniform(0, np.pi, p).tolist()
    params0 = np.array(gamma_initial + beta_initial)
    # fix starting point for first layers (not necessarily needed)
    params0[0] = 0.01
    params0[p] = 0.4
    # set bounds for search space
    bnds_gamma = [(0, 2 * np.pi) for _ in range(int(len(params0) / 2))]
    bnds_beta = [(0, np.pi) for _ in range(int(len(params0) / 2))]
    bnds = bnds_gamma + bnds_beta

    tracker['params'].append(params0)

    # run classical optimization (example: method='Nelder-Mead')
    result = minimize(
        objective_function, params0, args=(device, ising, n_qubits, n_shots, tracker),
        options=options, method=opt_method, bounds=bnds)

    # store result of classical optimization
    result_energy = result.fun
    cost_energy.append(result_energy)
    print('Final average energy (cost):', result_energy)
    result_angle = result.x
    print('Final angles:', result_angle)
    print('Training complete.')

    return result_energy, result_angle, tracker
