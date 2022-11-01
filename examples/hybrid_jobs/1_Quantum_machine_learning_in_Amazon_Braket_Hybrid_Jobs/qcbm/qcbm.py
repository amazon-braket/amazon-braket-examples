import numpy as np

from braket.circuits import Circuit


class QCBM:
    """Quantum circuit Born machine.

    Example: n_layers = 1, n_qubits = 2
    T  : |    0    |    1    |    2    |3|4|Result Types|

    q0 : -Rx(0.667)-Rz(0.783)-Rx(0.257)-C-X-Probability--
                                        | | |
    q1 : -Rx(0.549)-Rz(0.878)-Rx(0.913)-X-C-Probability--

    T  : |    0    |    1    |    2    |3|4|Result Types|

    """

    def __init__(self, device, n_qubits, n_layers, data):
        """Quantum circuit Born machine.
        Consists of `n_layers`, where each layer is a rotation layer (rx, rz, rx)
        followed by an entangling layer of cnot gates.

        Args:
            device (braket.devices): Amazon Braket device to use (could be AwsDevice()
                or LocalSimulator())
            n_qubits (int): Number of qubits
            n_layers (int): Number of layers
            data (np.ndarray): Target probabilities
        """
        self.device = device
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.neighbors = [(i, (i + 1) % n_qubits) for i in range(n_qubits)]
        self.data = data  # target probabilities
        self.shots = 10_000

    def entangler(self, circ):
        for i, j in self.neighbors:
            circ.cnot(i, j)

    def rotation_layer(self, circ, params):
        for n in range(self.n_qubits):
            circ.rx(n, params[n, 0])
            circ.rz(n, params[n, 1])
            circ.rx(n, params[n, 2])

    def create_circuit(self, params):
        """Creates a QCBM circuit, and returns the probabilities

        Args:
            params (np.ndarray): Parameters for the rotation gates in the circuit,
                length = 3 * n_qubits * n_layers

        Returns:
            circ (braket.circuit): Circuit with parameters fixed to `params`.
        """
        try:
            params = params.reshape(self.n_layers, self.n_qubits, 3)
        except:
            print(
                "Length of initial parameters was not correct. Expected: "
                + f"{self.n_layers*self.n_qubits*3} but got {len(params)}."
            )
        circ = Circuit()
        self.rotation_layer(circ, params[0])
        for L in range(1, self.n_layers):
            self.entangler(circ)
            self.rotation_layer(circ, params[L])
        self.entangler(circ)
        circ.probability()
        return circ

    def probabilities(self, params: np.ndarray):
        circ = self.create_circuit(params)
        probs = self.device.run(circ, shots=self.shots).result().values[0]
        return probs

    def gradient(self, params: np.ndarray):
        """Gradient for QCBM via:
        Liu, Jin-Guo, and Lei Wang.
        “Differentiable Learning of Quantum Circuit Born Machine.”
        Physical Review A 98, no. 6 (December 19, 2018): 062324.
        https://doi.org/10.1103/PhysRevA.98.062324.

        Args:
            qcbm (QCBM): QCBM class
            data (np.ndarray): Probability vector for the data
            params (np.ndarray): Parameters for the rotation gates in the QCBM

        Returns:
            grad (np.ndarray): Gradient vector
        """
        qcbm_probs = self.probabilities(params)
        shift = np.ones_like(params) * np.pi / 2
        shifted_params = np.stack([params + np.diag(shift), params - np.diag(shift)]).reshape(
            2 * len(params), len(params)
        )
        circuits = [self.create_circuit(p) for p in shifted_params]

        try:  # try parallel simulations, max_parallel=10 by default
            result = self.device.run_batch(circuits, shots=self.shots).results()
        except:  # fallback to sequential simulator
            result = [self.device.run(c, shots=self.shots).result() for c in circuits]

        res = [result[i].values[0] for i in range(len(circuits))]
        res = np.array(res).reshape(2, len(params), 2 ** self.n_qubits)

        grad = np.zeros(len(params))
        for i in range(len(params)):
            print(f"updating parameter: {i}")
            grad_pos = compute_kernel(qcbm_probs, res[0][i]) - compute_kernel(qcbm_probs, res[1][i])
            grad_neg = compute_kernel(self.data, res[0][i]) - compute_kernel(self.data, res[1][i])
            grad[i] = grad_pos - grad_neg
        return grad


def compute_kernel(px: np.ndarray, py: np.ndarray, sigma_list=[0.1, 1]):
    r"""Gaussian radial basis function (RBF) kernel.

    K(x, y) = sum_\sigma exp(-|x-y|^2/(2\sigma^2 ))

    Args:
        px (np.ndarray): Probability distribution
        py (np.ndarray): Target probability distribution
        sigma_list (list, optional): [description]. Defaults to [0.1, 1].

    Returns:
        kernel (float): Value of the Gaussian RBF function for kernel(px, py).
    """
    x = np.arange(len(px))
    y = np.arange(len(py))
    K = sum(np.exp(-np.abs(x[:, None] - y[None, :]) ** 2 / (2 * s ** 2)) for s in sigma_list)
    kernel = px @ K @ py
    return kernel


def mmd_loss(px: np.ndarray, py: np.ndarray, sigma_list=[0.1, 1]):
    r"""Maximum Mean Discrepancy loss (MMD).

    MMD determines if two distributions are equal by looking at the difference between
    their means in feature space.

    MMD(x, y) = | \sum_{j=1}^N \phi(y_j) - \sum_{i=1}^N \phi(x_i) |_2^2

    With a RBF kernel, we apply the kernel trick to expand MMD to

    MMD(x, y) = \sum_{j=1}^N \sum_{j'=1}^N k(y_j, y_{j'})
                + \sum_{i=1}^N \sum_{i'=1}^N k(x_i, x_{i'})
                - 2 \sum_{j=1}^N \sum_{i=1}^N k(y_j, x_i)

    For the RBF kernel, MMD is zero if and only if the distributions are identical.

    Args:
        px (np.ndarray): Probability distribution
        py (np.ndarray): Target probability distribution
        sigma_list (list, optional): [description]. Defaults to [0.1, 1].

    Returns:
        mmd (float): Value of the MMD loss
    """

    mmd_xx = compute_kernel(px, px, sigma_list)
    mmd_yy = compute_kernel(py, py, sigma_list)
    mmd_xy = compute_kernel(px, py, sigma_list)
    return mmd_xx + mmd_yy - 2 * mmd_xy
