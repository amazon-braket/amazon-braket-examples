from importlib import import_module
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.circuits.gates import CNot
from braket.devices import LocalSimulator
from braket.parametric import FreeParameter


@pytest.fixture
def qaoa(monkeypatch):
    example_dir = Path(__file__).resolve().parents[2] / "examples/hybrid_quantum_algorithms/QAOA"
    monkeypatch.syspath_prepend(str(example_dir))
    return import_module("utils_qaoa")


@pytest.mark.parametrize("gamma", [0.37, -0.61])
def test_zz_decomposition_matches_native_gate(qaoa, gamma):
    decomposed = qaoa.ZZgate(0, 1, gamma)
    native = Circuit().zz(0, 1, 2 * gamma)

    np.testing.assert_allclose(decomposed.to_unitary(), native.to_unitary(), rtol=0, atol=1e-12)


def test_qaoa_rigetti_matches_native_distribution(qaoa):
    # Both off-diagonal entries contribute to z.T @ ising @ z.
    ising = np.array([[0.0, 0.5], [0.5, 0.0]])
    params = [FreeParameter("gamma"), FreeParameter("beta")]
    inputs = {"gamma": np.pi / 4, "beta": np.pi / 8}
    simulator = LocalSimulator()
    rigetti = Mock(spec=AwsDevice, provider_name="Rigetti")

    native = qaoa.circuit(params, simulator, 2, ising).probability()
    decomposed = qaoa.circuit(params, rigetti, 2, ising).probability()
    assert any(isinstance(instruction.operator, CNot) for instruction in decomposed.instructions)

    native_probs = simulator.run(native, shots=0, inputs=inputs).result().values[0]
    decomposed_probs = simulator.run(decomposed, shots=0, inputs=inputs).result().values[0]

    np.testing.assert_allclose(native_probs, [0.0, 0.5, 0.5, 0.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(decomposed_probs, native_probs, rtol=0, atol=1e-12)
