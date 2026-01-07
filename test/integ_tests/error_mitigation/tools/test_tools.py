import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'examples', 'error_mitigation')))

from tools.observable_tools import matrix_to_pauli, _pauli_mul, pauli_grouping, qubit_wise_commuting, tensor_from_string
from tools.mitigation_tools import process_readout_twirl, twirl_iswap, build_inverse_quasi_distribution, SparseReadoutMitigation
from tools.stat_tools import jackknife, jackknife_bias_corrected, perform_regression
from tools.circuit_tools import find_linear_chain, multiply_gates, strip_verbatim, convert_paulis
from tools.program_set_tools import  distribute_to_program_sets, _probs_to_ev, STANDARD_CONVERSION, run_with_program_sets
from braket.circuits import Circuit
from braket.circuits.observables import X, Y, Z, I
from braket.devices import LocalSimulator
import unittest 
import numpy as np

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

    def test_pauli_grouping(self):
        """Test Pauli grouping functionality."""
        paulis = [(1.0, "XX"), (0.5, "ZZ"), (0.3, "XY")]
        signatures, groups = pauli_grouping(paulis)
        assert len(signatures) == 3  # XX and XY anticommute, so separate groups
        
    def test_qubit_wise_commuting(self):
        """Test qubit-wise commutation check."""
        assert qubit_wise_commuting("XX", "XY") == False
        assert qubit_wise_commuting("XX", "XX") == True
        assert qubit_wise_commuting("XI", "XZ") == True
        assert qubit_wise_commuting("XI", "IX") == True


class TestMitigationTools(unittest.TestCase):

    def test_process_readout_twirl(self):
        """Test readout twirling."""
        # Test with simple 2-qubit case
        dist = {"000":0.8,"100":0.2}
        twirls = ["010"]
        test = process_readout_twirl(dist, 0, twirls)

        ref = {"010":0.8, "110":0.2}
        assert ref == test

    def test_iswap_twirl(self):
        """Test twirling of iSWAP gate."""
        circ = Circuit().iswap(0, 1)
        twirls = twirl_iswap(circ, 32)
        for t in twirls:
            assert abs(np.abs(np.trace(circ.to_unitary() @ np.conj(t.to_unitary()).T)) - 4) <= 1e-6

    def test_build_inverse_quasi_distribution(self):
        """Test inverse quasi-distribution construction."""
        test_dist = {"00": 0.9, "01": 0.05, "10": 0.03, "11": 0.02}
        quasi, gamma = build_inverse_quasi_distribution(test_dist, second_order=False)
        assert isinstance(quasi, dict)
        assert len(gamma) == 2  # One gamma per qubit
        assert all(g > 0 for g in gamma)  # All gammas should be positive

    def test_sparse_readout_mitigation(self):
        """Test SparseReadoutMitigation class."""
        test_dist = {"00": 0.9, "01": 0.05, "10": 0.03, "11": 0.02}
        srm = SparseReadoutMitigation(test_dist)
        
        # Test getting inverse for single qubit
        inverse = srm.get_inverse((0,))
        assert isinstance(inverse, dict)
        
        # Test marginal inversion
        test_data = {"00": 100, "01": 5, "10": 3, "11": 2}
        result = srm.invert_marginal(test_data, [0])
        assert isinstance(result, dict)


    def test_sparse_process_single(self):
        dist = {"0000":1}
        sro = SparseReadoutMitigation(dist)
        res = {"1000":1.0}
        index = 0
        bitflip = ["0101"]
        zs = ["ZIII","IZII","IIZI","IIIZ"]
        ans = [-1,-1,+1,-1]
        for z,a in zip(zs,ans):
            test = sro.process_single(res,0, z, bitflip)
            print(test)
            assert test == a 


    def test_sparse_process_single_wth_noise(self):
        """Test process_single with bit flip noise model."""
        # Bit flip noise: 10% chance of flipping each qubit
        dist = {"0000": 0.6561, "0001": 0.0729, "0010": 0.0729, "0100": 0.0729,
                "1000": 0.0729, "0011": 0.0081, "0101": 0.0081, "1001": 0.0081,
                "0110": 0.0081, "1010": 0.0081, "1100": 0.0081, "0111": 0.0009,
                "1011": 0.0009, "1101": 0.0009, "1110": 0.0009, "1111": 0.0001}
        sro = SparseReadoutMitigation(dist)
        
        # Noisy result with bit flips
        res = {"1000": 0.7, "0000": 0.2, "1100": 0.05, "1001": 0.05}
        bitflip = ["0101"]
        
        # Test Z measurement on first qubit
        result = sro.process_single(res, 0, "ZIII", bitflip)
        assert isinstance(result, (int, float, np.number))
        assert -1 <= result <= 1




class TestStatTools(unittest.TestCase):
    def test_jackknife(self):
        """Test jackknife resampling."""
        data = np.array([1, 2, 3, 4, 5])
        mu, sigma, estimates = jackknife(data, np.mean)
        assert abs(mu - 3.0) < 1e-10  # Mean should be 3
        assert len(estimates) == 5
        
    def test_jackknife_multidimensional(self):
        """Test jackknife with multidimensional data."""
        data = np.random.rand(4, 3, 2)
        mu, sigma, estimates = jackknife(data, np.mean, axis=1)
        assert estimates.shape == (3,)  # Should have 3 estimates (axis=1 has size 3)
        
    def test_jackknife_bias_corrected(self):
        """Test bias-corrected jackknife."""
        data = np.array([1, 2, 3, 4, 5])
        corrected_mu, sigma = jackknife_bias_corrected(data, np.mean)
        assert isinstance(corrected_mu, (int, float, np.number))
        assert isinstance(sigma, (int, float, np.number))
        
    def test_perform_regression(self):
        """Test regression functionality."""
        xs = np.array([1, 2, 3, 4])
        ys = np.exp(xs)  # Exponential data
        result = perform_regression(xs, ys, error=False)
        assert isinstance(result, (int, float, np.number))


class TestCircuitTools(unittest.TestCase):
    def test_find_linear_chain(self):
        """Test finding linear chain in circuit."""
        circ = Circuit().iswap(0, 1).iswap(1, 2).iswap(2, 3)
        chain = find_linear_chain(circ)
        assert len(chain) == 4
        assert set(chain) == {0, 1, 2, 3}
        
    def test_multiply_gates(self):
        """Test gate multiplication."""
        circ = Circuit().x(0).h(1)
        multiplied = multiply_gates(circ, ["X"], repetitions=3)
        x_count = sum(1 for ins in multiplied.instructions if ins.operator.name == "X")
        assert x_count == 3
        
    def test_strip_verbatim(self):
        """Test verbatim stripping."""
        circ = Circuit().x(0)
        # Add a mock verbatim instruction for testing
        ncirc = Circuit().add_verbatim_box(circ)
        stripped = strip_verbatim(ncirc)
        assert len(stripped.instructions) == len(circ.instructions)
        
    def test_convert_paulis(self):
        """Test Pauli gate conversion."""
        circ = Circuit().x(0).y(1).z(2)
        converted = convert_paulis(circ)
        # Should have rotation gates instead of Pauli gates
        gate_names = [ins.operator.name for ins in converted.instructions]
        assert "X" not in gate_names
        assert "Y" not in gate_names
        assert "Z" not in gate_names


class TestProgramSetTools(unittest.TestCase):
        
    def test_program_set_proc(self):
        """ test ordering of program set submission and recombination """
        circuits = np.array(
            [
                [
                    [Circuit().z(0).z(1).z(2),Circuit().x(2).z(0).z(1)],
                    [Circuit().z(0).x(1).z(2),Circuit().z(0).x(1).x(2)]
                    ],
                [
                    [Circuit().x(0).z(1).z(2),Circuit().x(0).z(1).x(2)],
                    [Circuit().x(0).x(1).z(2),Circuit().x(0).x(1).x(2)]
                    ]
                    ],
              dtype=object
        )

        test = run_with_program_sets(circuits, ["ZZZ"], [None], [{}])
        for ind in [(0,0,0),(0,0,1),(0,1,0),(0,1,1),(1, 0, 0),(1, 0, 1),(1, 1, 0),(1, 1, 1)]:
            assert list(test[ind+(0,0,)].keys())[0] == "".join([str(s) for s in ind])

if __name__ == "__main__":
    unittest.main()

    from braket.circuits.noise_model import NoiseModel