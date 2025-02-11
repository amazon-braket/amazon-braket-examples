import cudaq

from braket.jobs import save_job_result


@cudaq.kernel
def kernel():
    qubits = cudaq.qvector(2)
    h(qubits[0])
    cx(qubits[0], qubits[1])
    mz(qubits)


result = cudaq.sample(kernel)
measurement_probabilities = dict(result.items())
print(measurement_probabilities)

save_job_result(measurement_probabilities)
