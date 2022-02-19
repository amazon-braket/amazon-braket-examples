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

from itertools import product

import numpy as np
import pytest

from braket.ir.jaqcd.shared_models import MultiProbability

np.random.seed(1)


def pauli_strings(n_qubits: int):
    pauli_strings = list(map(lambda x: "".join(x), product(["I", "X", "Y", "Z"], repeat=n_qubits)))
    return pauli_strings[1:]  # remove identity term


def random_noise(n_qubits: int):
    return np.random.dirichlet(np.ones(4**n_qubits))[1:]  # remove identity term


@pytest.mark.parametrize("n_qubits", [1, 2, 3])
class TestMultiProbability:
    """A class with common parameters, `param1` and `param2`."""

    def test_multiprobability(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        MultiProbability(probabilities=paulis)

    def test_multiprobability_less_probabilities(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        del paulis["X" * n_qubits]
        del paulis["Z" * n_qubits]
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    @pytest.mark.parametrize("str", ["T", "s", "x"])
    def test_multiprobability_non_pauli(self, n_qubits, str):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        paulis[str * n_qubits] = 0.0
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    @pytest.mark.parametrize("value", [12, -0.1, 1.1, np.inf, None])
    def test_multiprobability_non_float(self, n_qubits, value):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        paulis["X" * n_qubits] = value
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    def test_multiprobability_empty(self, n_qubits):
        MultiProbability(probabilities={})

    @pytest.mark.xfail(raises=ValueError)
    def test_multiprobability_identity(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        paulis["I" * n_qubits] = 0.1
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    def test_multiprobability_pauli_equal_lengths(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        paulis["X"] = 0.0
        paulis["XY"] = 0.0
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    def test_multiprobability_sum_over_one(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), 10 * random_noise(n_qubits)))
        MultiProbability(probabilities=paulis)

    @pytest.mark.xfail(raises=ValueError)
    def test_multiprobability_sum_under_zero(self, n_qubits):
        paulis = dict(zip(pauli_strings(n_qubits), random_noise(n_qubits)))
        paulis["Z" * n_qubits] = -0.9
        MultiProbability(probabilities=paulis)
