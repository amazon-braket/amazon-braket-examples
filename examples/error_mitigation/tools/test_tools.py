from tools.observable_tools import matrix_to_pauli, _pauli_mul
from tools.mitigation_tools import apply_two_qubit_twirl
from braket.circuits import Circuit
from braket.circuits.observables import X,Y,Z, I
from braket.quantum_information import PauliString
from braket.parametric import FreeParameter
from braket.devices import LocalSimulator
import unittest 


class TestObservables(unittest.TestCase):
    def test_matrix_to_pauli(self):
        """Test matrix_to_pauli function."""
        # Test single Pauli matrices
        assert matrix_to_pauli(X(0).to_matrix()) == [(1.0, "X")]
        assert matrix_to_pauli(Z(0).to_matrix()) == [(1.0, "Z")]
        
        # Test two-qubit cases
        xx_result = matrix_to_pauli((X(0) @ X(1)).to_matrix())
        assert len(xx_result) == 1 and xx_result[0][1] == "XX"
        
        # Test mixed observable - construct matrix manually
        zz_mat = (Z(0) @ Z(1)).to_matrix()
        xx_mat = (X(0) @ X(1)).to_matrix()
        mixed_mat = 0.5 * zz_mat + 2.0 * xx_mat
        result = matrix_to_pauli(mixed_mat)
        coeffs = {p: c for c, p in result}
        assert abs(coeffs["ZZ"] - 0.5) < 1e-10
        assert abs(coeffs["XX"] - 2.0) < 1e-10

    def test_pauli_mul(self):
        """Test Pauli multiplication phases."""
        # XY = iZ
        pauli, phase = _pauli_mul("X", "Y")
        assert pauli == "Z" and phase == 1j
        
        # YX = -iZ  
        pauli, phase = _pauli_mul("Y", "X")
        assert pauli == "Z" and phase == -1j
        
        # XZ = -iY
        pauli, phase = _pauli_mul("X", "Z")
        assert pauli == "Y" and phase == -1j



class TestMitigationTools(unittest.TestCase):
    def test_apply_two_qubit_twirl(self):
        """Test apply_two_qubit_twirl function."""
        # Create simple circuit with CNOT gate
        circ = Circuit().h(0).cnot(0, 1)
        
        # Apply twirling with 3 samples
        twirled_circ, param_sets = apply_two_qubit_twirl(circ, num_samples=3)
        
        # Check we get correct number of parameter sets
        assert len(param_sets) == 3
        
        # Check each parameter set has correct keys for one 2Q gate
        expected_keys = {
            'i_0_q0_x', 'i_0_q0_z', 'i_0_q1_x', 'i_0_q1_z',
            'o_0_q0_x', 'o_0_q0_z', 'o_0_q1_x', 'o_0_q1_z'
        }
        for params in param_sets:
            assert set(params.keys()) == expected_keys
            # Check all values are valid angles (0 or π)
            for val in params.values():
                assert val in [0.0, 3.141592653589793]
        
        # Check circuit has correct structure: 4 RXZ + 1 CNOT + 1 H
        assert len(twirled_circ.instructions) == 10
        
        # Verify single qubit gates are preserved
        h_gates = [ins for ins in twirled_circ.instructions if ins.operator.name == 'H']
        assert len(h_gates) == 1 and h_gates[0].target[0] == 0
    
    def test_twirled_circuit_execution(self):
        """Test that twirled circuit can be executed with parameter sets."""
        # Create simple circuit
        circ = Circuit().cnot(0, 1)
        
        # Apply twirling
        twirled_circ, param_sets = apply_two_qubit_twirl(circ, num_samples=2)
        # Run with LocalSimulator using each parameter set
        device = LocalSimulator()
        for i, params in enumerate(param_sets):
            task = device.run(twirled_circ, shots=100, inputs=params)
            result = task.result()
            # Verify we get measurement results
            assert len(result.measurement_counts) > 0
            assert sum(result.measurement_counts.values()) == 100

if __name__ == "__main__":
    unittest.main()
