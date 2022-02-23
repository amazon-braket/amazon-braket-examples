# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from typing import Any, Dict, Optional, Sequence

from braket.circuits.quantum_operator import QuantumOperator
from braket.circuits.qubit_set import QubitSet


class Noise(QuantumOperator):
    """
    Class `Noise` represents a noise channel that operates on one or multiple qubits. Noise
    are considered as building blocks of quantum circuits that simulate noise. It can be
    used as an operator in an `Instruction` object. It appears in the diagram when user prints
    a circuit with `Noise`. This class is considered the noise channel definition containing
    the metadata that defines what the noise channel is and what it does.
    """

    def __init__(self, qubit_count: Optional[int], ascii_symbols: Sequence[str]):
        """
        Args:
            qubit_count (int, optional): Number of qubits this noise channel interacts with.
            ascii_symbols (Sequence[str]): ASCII string symbols for this noise channel. These
                are used when printing a diagram of circuits. Length must be the same as
                `qubit_count`, and index ordering is expected to correlate with target ordering
                on the instruction.

        Raises:
            ValueError: `qubit_count` is less than 1, `ascii_symbols` are None, or
                length of `ascii_symbols` is not equal to `qubit_count`
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

    @property
    def name(self) -> str:
        """
        Returns the name of the quantum operator

        Returns:
            The name of the quantum operator as a string
        """
        return self.__class__.__name__

    def to_ir(self, target: QubitSet) -> Any:
        """Returns IR object of quantum operator and target

        Args:
            target (QubitSet): target qubit(s)
        Returns:
            IR object of the quantum operator and target
        """
        raise NotImplementedError("to_ir has not been implemented yet.")

    def to_matrix(self, *args, **kwargs) -> Any:
        """Returns a list of matrices defining the Kraus matrices of the noise channel.

        Returns:
            Iterable[np.ndarray]: list of matrices defining the Kraus matrices of the noise channel.
        """
        raise NotImplementedError("to_matrix has not been implemented yet.")

    def __eq__(self, other):
        if isinstance(other, Noise):
            return self.name == other.name
        return NotImplemented

    def __repr__(self):
        return f"{self.name}('qubit_count': {self.qubit_count})"

    @classmethod
    def register_noise(cls, noise: "Noise"):
        """Register a noise implementation by adding it into the Noise class.

        Args:
            noise (Noise): Noise class to register.
        """
        setattr(cls, noise.__name__, noise)


class SingleProbabilisticNoise(Noise):
    """
    Class `SingleProbabilisticNoise` represents the bit/phase flip noise channel on N qubits
    parameterized by a single probability.
    """

    def __init__(
        self, probability: float, qubit_count: Optional[int], ascii_symbols: Sequence[str]
    ):
        """
        Args:
            probability (float): The probability that the noise occurs.
            qubit_count (int, optional): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `probability` is not `float`,
                `probability` > 1/2, or `probability` < 0
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(probability, float):
            raise TypeError("probability must be float type")
        if not (probability <= 0.5 and probability >= 0.0):
            raise ValueError("probability must be a real number in the interval [0,1/2]")
        self._probability = probability

    @property
    def probability(self) -> float:
        """
        Returns:
            probability (float): The probability that parametrizes the noise channel.
        """
        return self._probability

    def __repr__(self):
        return f"{self.name}('probability': {self.probability}, 'qubit_count': {self.qubit_count})"


class SingleProbabilisticNoise_34(Noise):
    """
    Class `SingleProbabilisticNoise` represents the Depolarizing and TwoQubitDephasing noise
    channels parameterized by a single probability.
    """

    def __init__(
        self, probability: float, qubit_count: Optional[int], ascii_symbols: Sequence[str]
    ):
        """
        Args:
            probability (float): The probability that the noise occurs.
            qubit_count (int, optional): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `probability` is not `float`,
                `probability` > 3/4, or `probability` < 0
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(probability, float):
            raise TypeError("probability must be float type")
        if not (probability <= 0.75 and probability >= 0.0):
            raise ValueError("probability must be a real number in the interval [0,3/4]")
        self._probability = probability

    @property
    def probability(self) -> float:
        """
        Returns:
            probability (float): The probability that parametrizes the noise channel.
        """
        return self._probability

    def __repr__(self):
        return f"{self.name}('probability': {self.probability}, 'qubit_count': {self.qubit_count})"


class SingleProbabilisticNoise_1516(Noise):
    """
    Class `SingleProbabilisticNoise` represents the TwoQubitDepolarizing noise channel
    parameterized by a single probability.
    """

    def __init__(
        self, probability: float, qubit_count: Optional[int], ascii_symbols: Sequence[str]
    ):
        """
        Args:
            probability (float): The probability that the noise occurs.
            qubit_count (int, optional): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `probability` is not `float`,
                `probability` > 15/16, or `probability` < 0
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(probability, float):
            raise TypeError("probability must be float type")
        if not (probability <= 0.9375 and probability >= 0.0):
            raise ValueError("probability must be a real number in the interval [0,15/16]")
        self._probability = probability

    @property
    def probability(self) -> float:
        """
        Returns:
            probability (float): The probability that parametrizes the noise channel.
        """
        return self._probability

    def __repr__(self):
        return f"{self.name}('probability': {self.probability}, 'qubit_count': {self.qubit_count})"


class MultiQubitPauliNoise(Noise):
    """
    Class `MultiQubitPauliNoise` represents a general multi-qubit Pauli channel,
    parameterized by up to 4**N - 1 probabilities.
    """

    _allowed_substrings = {"I", "X", "Y", "Z"}

    def __init__(
        self,
        probabilities: Dict[str, float],
        qubit_count: Optional[int],
        ascii_symbols: Sequence[str],
    ):
        """[summary]

        Args:
            probabilities (Dict[str, float]): A dictionary with Pauli string as the keys,
            and the probabilities as values, i.e. {"XX": 0.1. "IZ": 0.2}.
            qubit_count (Optional[int]): The number of qubits the Pauli noise acts on.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`. Also if `probabilities` are not `float`s,
                any `probabilities` > 1, or `probabilities` < 0, or if the sum of all
                probabilities is > 1,
                or if "II" is specified as a Pauli string.
                Also if any Pauli string contains invalid strings.
                Also if the length of probabilities is greater than 4**qubit_count.
            TypeError: If the type of the dictionary keys are not strings.
                If the probabilities are not floats.
        """

        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)
        self.probabilities = probabilities

        if not probabilities:
            raise ValueError("Pauli dictionary must not be empty.")

        identity = self.qubit_count * "I"
        if identity in probabilities:
            raise ValueError(
                f"{identity} is not allowed as a key. Please enter only non-identity Pauli strings."
            )

        for pauli_string, prob in probabilities.items():
            if not isinstance(pauli_string, str):
                raise TypeError(f"Type of {pauli_string} was not a string.")
            if len(pauli_string) != self.qubit_count:
                raise ValueError(
                    (
                        "Length of each Pauli string must be equal to number of qubits. "
                        f"{pauli_string} had length {len(pauli_string)} instead of length {self.qubit_count}."  # noqa
                    )
                )
            if not isinstance(prob, float):
                raise TypeError(
                    (
                        "Probabilities must be a float type. "
                        f"The probability for {pauli_string} was of type {type(prob)}."
                    )
                )
            if not set(pauli_string) <= self._allowed_substrings:
                raise ValueError(
                    (
                        "Strings must be Pauli strings consisting of only [I, X, Y, Z]. "
                        f"Received {pauli_string}."
                    )
                )
            if prob < 0.0 or prob > 1.0:
                raise ValueError(
                    (
                        "Individual probabilities must be real numbers in the interval [0, 1]. "
                        f"Probability for {pauli_string} was {prob}."
                    )
                )
        total_prob = sum(probabilities.values())
        if total_prob > 1.0 or total_prob < 0.0:
            raise ValueError(
                (
                    "Total probability must be a real number in the interval [0, 1]. "
                    f"Total probability was {total_prob}."
                )
            )

    def __repr__(self):
        return f"{self.name}('probabilities' : {self.probabilities}, 'qubit_count': {self.qubit_count})"  # noqa


class PauliNoise(Noise):
    """
    Class `PauliNoise` represents the a single-qubit Pauli noise channel
    acting on one qubit. It is parameterized by three probabilities.
    """

    def __init__(
        self,
        probX: float,
        probY: float,
        probZ: float,
        qubit_count: Optional[int],
        ascii_symbols: Sequence[str],
    ):
        """
        Args:
            probX [float], probY [float], probZ [float]: The coefficients of the Kraus operators
                in the channel.
            qubit_count (int, optional): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

        Raises:
            ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `probX` or `probY` or `probZ`
                is not `float`, `probX` or `probY` or `probZ` > 1.0, or
                `probX` or `probY` or `probZ` < 0.0, or `probX`+`probY`+`probZ` > 1
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(probX, float):
            raise TypeError("probX must be float type")
        if not (probX <= 1.0 and probX >= 0.0):
            raise ValueError("probX must be a real number in the interval [0,1]")
        if not isinstance(probY, float):
            raise TypeError("probY must be float type")
        if not (probY <= 1.0 and probY >= 0.0):
            raise ValueError("probY must be a real number in the interval [0,1]")
        if not isinstance(probZ, float):
            raise TypeError("probZ must be float type")
        if not (probZ <= 1.0 and probZ >= 0.0):
            raise ValueError("probZ must be a real number in the interval [0,1]")
        if probX + probY + probZ > 1:
            raise ValueError("the sum of probX, probY, probZ cannot be larger than 1")

        self._probX = probX
        self._probY = probY
        self._probZ = probZ

    @property
    def probX(self) -> float:
        """
        Returns:
            probX (float): The probability of a Pauli X error.
        """
        return self._probX

    @property
    def probY(self) -> float:
        """
        Returns:
            probY (float): The probability of a Pauli Y error.
        """
        return self._probY

    @property
    def probZ(self) -> float:
        """
        Returns:
            probZ (float): The probability of a Pauli Z error.
        """
        return self._probZ

    def __repr__(self):
        return f"{self.name}('probX': {self.probX}, 'probY': {self.probY}, \
'probZ': {self.probZ}, 'qubit_count': {self.qubit_count})"


class DampingNoise(Noise):
    """
    Class `DampingNoise` represents a damping noise channel
    on N qubits parameterized by gamma.
    """

    def __init__(self, gamma: float, qubit_count: Optional[int], ascii_symbols: Sequence[str]):
        """
        Args:
            gamma (float): Probability of damping.
            qubit_count (int, optional): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

            Raises:
                ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `gamma` is not `float`,
                `gamma` > 1.0, or `gamma` < 0.0.
        """
        super().__init__(qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(gamma, float):
            raise TypeError("gamma must be float type")
        if not (gamma <= 1.0 and gamma >= 0.0):
            raise ValueError("gamma must be a real number in the interval [0,1]")
        self._gamma = gamma

    @property
    def gamma(self) -> float:
        """
        Returns:
            gamma (float): Probability of damping.
        """
        return self._gamma

    def __repr__(self):
        return f"{self.name}('gamma': {self.gamma}, 'qubit_count': {self.qubit_count})"


class GeneralizedAmplitudeDampingNoise(DampingNoise):
    """
    Class `GeneralizedAmplitudeDampingNoise` represents the generalized amplitude damping
    noise channel on N qubits parameterized by gamma and probability.
    """

    def __init__(
        self,
        gamma: float,
        probability: float,
        qubit_count: Optional[int],
        ascii_symbols: Sequence[str],
    ):
        """
        Args:
            gamma (float): Probability of damping.
            probability (float): Probability of the system being excited by the environment.
            qubit_count (int): The number of qubits to apply noise.
            ascii_symbols (Sequence[str]): ASCII string symbols for the noise. These are used when
                printing a diagram of a circuit. The length must be the same as `qubit_count`, and
                index ordering is expected to correlate with the target ordering on the instruction.

            Raises:
                ValueError: If the `qubit_count` is less than 1, `ascii_symbols` are `None`, or
                `ascii_symbols` length != `qubit_count`, `probability` or `gamma` is not `float`,
                `probability` > 1.0, or `probability` < 0.0, `gamma` > 1.0, or `gamma` < 0.0.
        """
        super().__init__(gamma=gamma, qubit_count=qubit_count, ascii_symbols=ascii_symbols)

        if not isinstance(probability, float):
            raise TypeError("probability must be float type")
        if not (probability <= 1.0 and probability >= 0.0):
            raise ValueError("probability must be a real number in the interval [0,1]")
        self._probability = probability

    @property
    def probability(self) -> float:
        """
        Returns:
            probability (float): Probability of the system being excited by the environment.
        """
        return self._probability

    def __repr__(self):
        return f"{self.name}('gamma': {self.gamma}, 'probability': {self.probability}, \
'qubit_count': {self.qubit_count})"
