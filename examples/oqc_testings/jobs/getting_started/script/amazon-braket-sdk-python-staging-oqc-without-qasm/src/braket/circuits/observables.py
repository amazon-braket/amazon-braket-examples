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

from __future__ import annotations

import functools
import itertools
import math
from typing import Dict, List, Tuple, Union

import numpy as np

from braket.circuits.gate import Gate
from braket.circuits.observable import Observable, StandardObservable
from braket.circuits.quantum_operator_helpers import (
    get_pauli_eigenvalues,
    is_hermitian,
    verify_quantum_operator_matrix_dimensions,
)


class H(StandardObservable):
    """Hadamard operation as an observable."""

    def __init__(self):
        """
        Examples:
            >>> Observable.H()
        """
        super().__init__(ascii_symbols=["H"])

    def to_ir(self) -> List[str]:
        return ["h"]

    def to_matrix(self) -> np.ndarray:
        return 1.0 / np.sqrt(2.0) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return tuple([Gate.Ry(-math.pi / 4)])


Observable.register_observable(H)


class I(Observable):  # noqa: E742, E261
    """Identity operation as an observable."""

    def __init__(self):
        """
        Examples:
            >>> Observable.I()
        """
        super().__init__(qubit_count=1, ascii_symbols=["I"])

    def to_ir(self) -> List[str]:
        return ["i"]

    def to_matrix(self) -> np.ndarray:
        return np.eye(2, dtype=complex)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return ()

    @property
    def eigenvalues(self) -> np.ndarray:
        return np.ones(2)

    def eigenvalue(self, index: int) -> float:
        return 1.0


Observable.register_observable(I)


class X(StandardObservable):
    """Pauli-X operation as an observable."""

    def __init__(self):
        """
        Examples:
            >>> Observable.X()
        """
        super().__init__(ascii_symbols=["X"])

    def to_ir(self) -> List[str]:
        return ["x"]

    def to_matrix(self) -> np.ndarray:
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return tuple([Gate.H()])


Observable.register_observable(X)


class Y(StandardObservable):
    """Pauli-Y operation as an observable."""

    def __init__(self):
        """
        Examples:
            >>> Observable.Y()
        """
        super().__init__(ascii_symbols=["Y"])

    def to_ir(self) -> List[str]:
        return ["y"]

    def to_matrix(self) -> np.ndarray:
        return np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return tuple([Gate.Z(), Gate.S(), Gate.H()])


Observable.register_observable(Y)


class Z(StandardObservable):
    """Pauli-Z operation as an observable."""

    def __init__(self):
        """
        Examples:
            >>> Observable.Z()
        """
        super().__init__(ascii_symbols=["Z"])

    def to_ir(self) -> List[str]:
        return ["z"]

    def to_matrix(self) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return ()


Observable.register_observable(Z)


class TensorProduct(Observable):
    """Tensor product of observables"""

    def __init__(self, observables: List[Observable]):
        """
        Args:
            observables (List[Observable]): List of observables for tensor product

        Examples:
            >>> t1 = Observable.Y() @ Observable.X()
            >>> t1.to_matrix()
            array([[0.+0.j, 0.+0.j, 0.-0.j, 0.-1.j],
            [0.+0.j, 0.+0.j, 0.-1.j, 0.-0.j],
            [0.+0.j, 0.+1.j, 0.+0.j, 0.+0.j],
            [0.+1.j, 0.+0.j, 0.+0.j, 0.+0.j]])
            >>> t2 = Observable.Z() @ t1
            >>> t2.factors
            (Z('qubit_count': 1), Y('qubit_count': 1), X('qubit_count': 1))

        Note: You must provide the list of observables for the tensor product to be evaluated
        in the order that you want the tensor product to be calculated.
        For `TensorProduct(observables=[ob1, ob2, ob3])`, the tensor product's matrix is the
        result of the tensor product of `ob1`, `ob2`, `ob3`, or `np.kron(np.kron(ob1.to_matrix(),
        ob2.to_matrix()), ob3.to_matrix())`.
        """
        flattened_observables = []
        for obs in observables:
            if isinstance(obs, TensorProduct):
                for nested_obs in obs.factors:
                    flattened_observables.append(nested_obs)
            else:
                flattened_observables.append(obs)
        self._factors = tuple(flattened_observables)
        qubit_count = sum([obs.qubit_count for obs in flattened_observables])
        display_name = "@".join([obs.ascii_symbols[0] for obs in flattened_observables])
        super().__init__(qubit_count=qubit_count, ascii_symbols=[display_name] * qubit_count)
        self._factor_dimensions = tuple(
            len(factor.to_matrix()) for factor in reversed(self._factors)
        )
        self._eigenvalue_indices = {}
        self._all_eigenvalues = None

    def to_ir(self) -> List[str]:
        ir = []
        for obs in self.factors:
            ir.extend(obs.to_ir())
        return ir

    @property
    def factors(self) -> Tuple[Observable, ...]:
        """Tuple[Observable]: The observables that comprise this tensor product."""
        return self._factors

    def to_matrix(self) -> np.ndarray:
        return functools.reduce(np.kron, [obs.to_matrix() for obs in self.factors])

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        gates = []
        for obs in self.factors:
            gates.extend(obs.basis_rotation_gates)
        return tuple(gates)

    @property
    def eigenvalues(self):
        if self._all_eigenvalues is None:
            self._all_eigenvalues = TensorProduct._compute_eigenvalues(
                self._factors, self.qubit_count
            )
        return self._all_eigenvalues

    def eigenvalue(self, index: int) -> float:
        if index in self._eigenvalue_indices:
            return self._eigenvalue_indices[index]
        dimension = 2**self.qubit_count
        if index >= dimension:
            raise ValueError(
                f"Index {index} requested but observable has at most {dimension} eigenvalues"
            )
        # Calculating the eigenvalue amounts to converting the index to a new heterogeneous base
        # and multiplying the eigenvalues of each factor at the corresponding digit
        product = 1
        quotient = index
        for i in range(len(self._factors)):
            quotient, remainder = divmod(quotient, self._factor_dimensions[i])
            product *= self._factors[-i - 1].eigenvalue(remainder)
        self._eigenvalue_indices[index] = product
        return self._eigenvalue_indices[index]

    def __repr__(self):
        return "TensorProduct(" + ", ".join([repr(o) for o in self.factors]) + ")"

    def __eq__(self, other):
        return self.matrix_equivalence(other)

    @staticmethod
    def _compute_eigenvalues(observables: Tuple[Observable], num_qubits: int) -> np.ndarray:
        if False in [isinstance(observable, StandardObservable) for observable in observables]:
            # Tensor product of observables contains a mixture
            # of standard and non-standard observables
            eigenvalues = np.array([1])
            for k, g in itertools.groupby(observables, lambda x: isinstance(x, StandardObservable)):
                if k:
                    # Subgroup g contains only standard observables.
                    eigenvalues = np.kron(eigenvalues, get_pauli_eigenvalues(len(list(g))))
                else:
                    # Subgroup g contains only non-standard observables.
                    for nonstandard in g:
                        # loop through all non-standard observables
                        eigenvalues = np.kron(eigenvalues, nonstandard.eigenvalues)
        else:
            eigenvalues = get_pauli_eigenvalues(num_qubits=num_qubits)

        eigenvalues.setflags(write=False)
        return eigenvalues


Observable.register_observable(TensorProduct)


class Hermitian(Observable):
    """Hermitian matrix as an observable."""

    # Cache of eigenpairs
    _eigenpairs = {}

    def __init__(self, matrix: np.ndarray, display_name: str = "Hermitian"):
        """
        Args:
            matrix (numpy.ndarray): Hermitian matrix that defines the observable.
            display_name (str): Name to use for an instance of this Hermitian matrix
                observable for circuit diagrams. Defaults to `Hermitian`.

        Raises:
            ValueError: If `matrix` is not a two-dimensional square matrix,
                or has a dimension length that is not a positive power of 2,
                or is not Hermitian.

        Examples:
            >>> Observable.Hermitian(matrix=np.array([[0, 1],[1, 0]]))
        """
        verify_quantum_operator_matrix_dimensions(matrix)
        self._matrix = np.array(matrix, dtype=complex)
        if not is_hermitian(self._matrix):
            raise ValueError(f"{self._matrix} is not hermitian")

        qubit_count = int(np.log2(self._matrix.shape[0]))
        eigendecomposition = Hermitian._get_eigendecomposition(self._matrix)
        self._eigenvalues = eigendecomposition["eigenvalues"]
        self._diagonalizing_gates = (
            Gate.Unitary(matrix=eigendecomposition["eigenvectors"].conj().T),
        )

        super().__init__(qubit_count=qubit_count, ascii_symbols=[display_name] * qubit_count)

    def to_ir(self) -> List[List[List[List[float]]]]:
        return [
            [[[element.real, element.imag] for element in row] for row in self._matrix.tolist()]
        ]

    def to_matrix(self) -> np.ndarray:
        return self._matrix

    def __eq__(self, other) -> bool:
        return self.matrix_equivalence(other)

    @property
    def basis_rotation_gates(self) -> Tuple[Gate, ...]:
        return self._diagonalizing_gates

    @property
    def eigenvalues(self):
        return self._eigenvalues

    def eigenvalue(self, index: int) -> float:
        return self._eigenvalues[index]

    @staticmethod
    def _get_eigendecomposition(matrix) -> Dict[str, np.ndarray]:
        """
        Decomposes the Hermitian matrix into its eigenvectors and associated eigenvalues.
        The eigendecomposition is cached so that if another Hermitian observable
        is created with the same matrix, the eigendecomposition doesn't have to
        be recalculated.

        Returns:
            Dict[str, np.ndarray]: The keys are "eigenvectors_conj_t", mapping to the
            conjugate transpose of a matrix whose columns are the eigenvectors of the matrix,
            and "eigenvalues", a list of associated eigenvalues in the order of their
            corresponding eigenvectors in the "eigenvectors" matrix. These cached values
            are immutable.
        """
        mat_key = tuple(matrix.flatten().tolist())
        if mat_key not in Hermitian._eigenpairs:
            eigenvalues, eigenvectors = np.linalg.eigh(matrix)
            eigenvalues.setflags(write=False)
            Hermitian._eigenpairs[mat_key] = {
                "eigenvectors": eigenvectors,
                "eigenvalues": eigenvalues,
            }
        return Hermitian._eigenpairs[mat_key]

    def __repr__(self):
        matrix_str = np.array2string(self.to_matrix()).replace("\n", ",")
        return f"{self.name}('qubit_count': {self.qubit_count}, 'matrix': {matrix_str})"


Observable.register_observable(Hermitian)


def observable_from_ir(ir_observable: List[Union[str, List[List[List[float]]]]]) -> Observable:
    """
    Create an observable from the IR observable list. This can be a tensor product of
    observables or a single observable.

    Args:
        ir_observable (List[Union[str, List[List[List[float]]]]]): observable as defined in IR

    Return:
        Observable: observable object
    """
    if len(ir_observable) == 1:
        return _observable_from_ir_list_item(ir_observable[0])
    else:
        observable = TensorProduct([_observable_from_ir_list_item(obs) for obs in ir_observable])
        return observable


def _observable_from_ir_list_item(observable: Union[str, List[List[List[float]]]]) -> Observable:
    if observable == "i":
        return I()
    elif observable == "h":
        return H()
    elif observable == "x":
        return X()
    elif observable == "y":
        return Y()
    elif observable == "z":
        return Z()
    else:
        try:
            matrix = np.array(
                [[complex(element[0], element[1]) for element in row] for row in observable]
            )
            return Hermitian(matrix)
        except Exception as e:
            raise ValueError(f"Invalid observable specified: {observable} error: {e}")
