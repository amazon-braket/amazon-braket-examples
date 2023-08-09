# general imports
import math
import pickle
from collections import Counter
from datetime import datetime

import numpy as np

# AWS imports: Import Braket SDK modules
from braket.circuits import Circuit, circuit

# local imports
from utils_qft import inverse_qft


@circuit.subroutine(register=True)
def controlled_unitary(control, target_qubits, unitary):
    """
    Construct a circuit object corresponding to the controlled unitary

    Args:
        control: The qubit on which to control the gate

        target_qubits: List of qubits on which the unitary U acts

        unitary: matrix representation of the unitary we wish to implement in a controlled way
    """

    # Define projectors onto the computational basis
    p0 = np.array([[1.0, 0.0], [0.0, 0.0]])

    p1 = np.array([[0.0, 0.0], [0.0, 1.0]])

    # Instantiate circuit object
    circ = Circuit()

    # Construct numpy matrix
    id_matrix = np.eye(len(unitary))
    controlled_matrix = np.kron(p0, id_matrix) + np.kron(p1, unitary)

    # Set all target qubits
    targets = [control] + target_qubits

    # Add controlled unitary
    circ.unitary(matrix=controlled_matrix, targets=targets)

    return circ


@circuit.subroutine(register=True)
def qpe(precision_qubits, query_qubits, unitary, control_unitary=True):
    """
    Function to implement the QPE algorithm using two registers for precision (read-out) and query.
    Register qubits need not be contiguous.

    Args:
        precision_qubits: list of qubits defining the precision register

        query_qubits: list of qubits defining the query register

        unitary: Matrix representation of the unitary whose eigenvalues we wish to estimate

        control_unitary: Optional boolean flag for controlled unitaries,
                         with C-(U^{2^k}) by default (default is True),
                         or C-U controlled-unitary (2**power) times
    """
    qpe_circ = Circuit()

    # Get number of qubits
    num_precision_qubits = len(precision_qubits)
    num_query_qubits = len(query_qubits)

    # Apply Hadamard across precision register
    qpe_circ.h(precision_qubits)

    # Apply controlled unitaries. Start with the last precision_qubit, and end with the first
    for ii, qubit in enumerate(reversed(precision_qubits)):
        # Set power exponent for unitary
        power = ii

        # Alterantive 1: Implement C-(U^{2^k})
        if control_unitary:
            # Define the matrix U^{2^k}
            Uexp = np.linalg.matrix_power(unitary, 2 ** power)

            # Apply the controlled unitary C-(U^{2^k})
            qpe_circ.controlled_unitary(qubit, query_qubits, Uexp)
        # Alterantive 2: One can instead apply controlled-unitary (2**power) times to get C-U^{2^power}
        else:
            for _ in range(2 ** power):
                qpe_circ.controlled_unitary(qubit, query_qubits, unitary)

    # Apply inverse qft to the precision_qubits
    qpe_circ.inverse_qft(precision_qubits)

    return qpe_circ


# helper function to remove query bits from bitstrings
def substring(key, precision_qubits):
    """
    Helper function to get substring from keys for dedicated string positions as given by precision_qubits.
    This function is necessary to allow for arbitrary qubit mappings in the precision and query registers
    (i.e., so that the register qubits need not be contiguous.)

    Args:
        key: string from which we want to extract the substring supported only on the precision qubits

        precision_qubits: List of qubits corresponding to precision_qubits.
                          Currently assumed to be a list of integers corresponding to the indices of the qubits.
    """
    short_key = ""
    for idx in precision_qubits:
        short_key = short_key + key[idx]

    return short_key


# helper function to convert binary fractional to decimal
# reference: https://www.geeksforgeeks.org/convert-binary-fraction-decimal/
def binaryToDecimal(binary):
    """
    Helper function to convert binary string (example: '01001') to decimal

    Args:
        binary: string which to convert to decimal fraction
    """

    length = len(binary)
    fracDecimal = 0

    # Convert fractional part of binary to decimal equivalent
    twos = 2

    for ii in range(length):
        fracDecimal += (ord(binary[ii]) - ord("0")) / twos
        twos *= 2.0

    # return fractional part
    return fracDecimal


# helper function for postprocessing based on measurement shots
def get_qpe_phases(measurement_counts, precision_qubits, items_to_keep=1):
    """
    Get QPE phase estimate from measurement_counts for given number of precision qubits

    Args:
        measurement_counts: measurement results from a device run

        precision_qubits: List of qubits corresponding to precision_qubits.
                          Currently assumed to be a list of integers corresponding to the indices of the qubits.

        items_to_keep: number of items to return (topmost measurement counts for precision register)
    """

    # Aggregate the results (i.e., ignore/trace out the query register qubits):

    # First get bitstrings with corresponding counts for precision qubits only
    bitstrings_precision_register = [
        substring(key, precision_qubits) for key in measurement_counts.keys()
    ]
    # Then keep only the unique strings
    bitstrings_precision_register_set = set(bitstrings_precision_register)
    # Cast as a list for later use
    bitstrings_precision_register_list = list(bitstrings_precision_register_set)

    # Now create a new dict to collect measurement results on the precision_qubits.
    # Keys are given by the measurement count substrings on the register qubits. Initialize the counts to zero.
    precision_results_dic = {key: 0 for key in bitstrings_precision_register_list}

    # Loop over all measurement outcomes
    for key in measurement_counts.keys():
        # Save the measurement count for this outcome
        counts = measurement_counts[key]
        # Generate the corresponding shortened key (supported only on the precision_qubits register)
        count_key = substring(key, precision_qubits)
        # Add these measurement counts to the corresponding key in our new dict
        precision_results_dic[count_key] += counts

    # Get topmost values only
    c = Counter(precision_results_dic)
    topmost = c.most_common(items_to_keep)
    # get decimal phases from bitstrings for topmost bitstrings
    phases_decimal = [binaryToDecimal(item[0]) for item in topmost]

    # Get decimal phases from bitstrings for all bitstrings
    # number_precision_qubits = len(precision_qubits)
    # Generate binary decimal expansion
    # phases_decimal = [int(key, 2)/(2**number_precision_qubits) for key in precision_results_dic]
    # phases_decimal = [binaryToDecimal(key) for key in precision_results_dic]

    return phases_decimal, precision_results_dic


def run_qpe(
    unitary,
    precision_qubits,
    query_qubits,
    query_circuit,
    device,
    items_to_keep=1,
    shots=1000,
    save_to_pck=False,
):
    """
    Function to run QPE algorithm end-to-end and return measurement counts.

    Args:
        precision_qubits: list of qubits defining the precision register

        query_qubits: list of qubits defining the query register

        unitary: Matrix representation of the unitary whose eigenvalues we wish to estimate

        query_circuit: query circuit for state preparation of query register

        items_to_keep: (optional) number of items to return (topmost measurement counts for precision register)

        device: Braket device backend

        shots: (optional) number of measurement shots (default is 1000)

        save_to_pck: (optional) save results to pickle file if True (default is False)
    """

    # get size of precision register and total number of qubits
    number_precision_qubits = len(precision_qubits)
    num_qubits = len(precision_qubits) + len(query_qubits)

    # Define the circuit. Start by copying the query_circuit, then add the QPE:
    circ = query_circuit
    circ.qpe(precision_qubits, query_qubits, unitary)

    # Add desired results_types
    circ.probability()

    # Run the circuit with all zeros input.
    # The query_circuit subcircuit generates the desired input from all zeros.
    task = device.run(circ, shots=shots)

    # get result for this task
    result = task.result()

    # get metadata
    metadata = result.task_metadata

    # get output probabilities (see result_types above)
    probs_values = result.values[0]

    # get measurement results
    measurements = result.measurements
    measured_qubits = result.measured_qubits
    measurement_counts = result.measurement_counts
    measurement_probabilities = result.measurement_probabilities

    # bitstrings
    format_bitstring = "{0:0" + str(num_qubits) + "b}"
    bitstring_keys = [format_bitstring.format(ii) for ii in range(2 ** num_qubits)]

    # QPE postprocessing
    phases_decimal, precision_results_dic = get_qpe_phases(
        measurement_counts, precision_qubits, items_to_keep
    )
    eigenvalues = [np.exp(2 * np.pi * 1j * phase) for phase in phases_decimal]

    # aggregate results
    out = {
        "circuit": circ,
        "task_metadata": metadata,
        "measurements": measurements,
        "measured_qubits": measured_qubits,
        "measurement_counts": measurement_counts,
        "measurement_probabilities": measurement_probabilities,
        "probs_values": probs_values,
        "bitstring_keys": bitstring_keys,
        "precision_results_dic": precision_results_dic,
        "phases_decimal": phases_decimal,
        "eigenvalues": eigenvalues,
    }

    if save_to_pck:
        # store results: dump output to pickle with timestamp in filename
        time_now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        results_file = "results-" + time_now + ".pck"
        pickle.dump(out, open(results_file, "wb"))
        # you can load results as follows
        # out = pickle.load(open(results_file, "rb"))

    return out
