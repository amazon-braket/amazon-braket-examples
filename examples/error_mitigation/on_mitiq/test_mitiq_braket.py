from mitiq_braket_tools import (
    # braket_counts_executor,
    braket_expectation_executor,
    braket_measurement_executor,
)
from braket.devices import LocalSimulator
from braket.circuits.observables import Z
from mitiq import PauliString, Observable
from braket.circuits import Circuit
import unittest
from braket.aws import AwsDevice
from noise_models import qd_readout_2, qd_readout
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) # parent  
from tools.mitigation_tools import apply_readout_twirl, get_twirled_readout_dist, build_inverse_quasi_distribution, bit_mul_distribution
from tools.mitigation_tools import SparseEstimation


class TestExecutors(unittest.TestCase):
    @unittest.skip('api')
    def test_braket_executors(self):
        """Test all braket executors"""

        # Create simple test circuit
        circuit = Circuit().h(0).cnot(0, 1)
        device = LocalSimulator()
        
        # # Test counts executor
        # counts_executor = braket_counts_executor(device, shots=100, verbatim=False)
        # counts_result = counts_executor.evaluate(circuit)
        # print(f"Counts executor: {counts_result}")
        
        # Test measurement executor
        meas_executor = braket_measurement_executor(device, shots=100, verbatim=False)
        meas_result = meas_executor.evaluate(circuit, observable=Observable(PauliString("ZZ")))
        print(f"Measurement executor: {meas_result}")
        
        # Test expectation executor
        exp_executor = braket_expectation_executor(device, Z(0) @ Z(1), shots=100, verbatim=False)
        exp_result = exp_executor.evaluate(circuit)
        print(f"Expectation executor: {exp_result}")


    @unittest.skip('api')
    def test_batch(self):
        device = LocalSimulator() 
        print(device.properties.action)
        # counts_executor = braket_counts_executor(device, shots=100, verbatim=False)
        meas_executor = braket_measurement_executor(device, shots=100, verbatim=False)
        exp_executor = braket_expectation_executor(device, Z(0) @ Z(1), shots=100, verbatim=False)
        # assert counts_executor.can_batch
        assert meas_executor.can_batch
        assert exp_executor.can_batch

        new_device = AwsDevice("arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1")
        # Create a copy of actions without PROGRAM_SET support
            
        meas_executor = braket_measurement_executor(new_device, shots=100, verbatim=False)
        exp_executor = braket_expectation_executor(new_device, Z(0) @ Z(1), shots=100, verbatim=False)
        # assert counts_executor.can_batch
        assert not meas_executor.can_batch
        assert not exp_executor.can_batch

class TestMeasurement(unittest.TestCase):

    @unittest.skip('api')
    def test_rem_inverse(self):
        device = qd_readout_2
        ref_dist = get_twirled_readout_dist([1,2,3],
                                         n_twirls = 10, 
                                         shots = 10000, 
                                         device = device)
        validation = get_twirled_readout_dist([1,2,3],
                                         n_twirls = 10, 
                                         shots = 10000, 
                                         device = device)

        print(ref_dist)
        quasi1, factors1 = build_inverse_quasi_distribution(ref_dist, second_order=False)
        # quasi2, factors2 = build_inverse_quasi_distribution(ref_dist, second_order=True)
        print('first order correction: ')
        print(quasi1)
        print('Applied to reference distribution: ')
        print(bit_mul_distribution(quasi1, ref_dist,3))
        print('Applied to validation distribution: ')
        print(bit_mul_distribution(quasi1, validation,3))
        # print('second order correction')

    def test_sparse_readout(self):
        import numpy as np 
        device = qd_readout
        dist = get_twirled_readout_dist([0,1],
                                         n_twirls = 10, 
                                         shots = 100000, 
                                         device = device)
        sparse = SparseEstimation(dist)    
        circ = Circuit().x(0).x(1)
        circs, paulis = apply_readout_twirl(circ, 5)

        paulis = ["".join(["0" if p in "IZ" else "1" for p in pauli]) for pauli in paulis]
        paulis = np.array(paulis, dtype=object)
        results = []
        for n,c in enumerate(circs):
            res = device.run(c.measure(range(2)), shots= 10000).result().measurement_counts
            results.append(res)
            print(res, paulis[n], )
            print(sparse.process_single(res,n,"ZI", paulis))
        print('total estimate: ')
        print(sparse.process_multiple(results, range(5),"ZI",paulis))
        print(sparse.inverses)

if __name__ == "__main__":
    unittest.main()