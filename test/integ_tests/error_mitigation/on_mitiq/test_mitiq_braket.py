import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'examples', 'error_mitigation','on_mitiq')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'examples', 'error_mitigation')))

import pytest
from tools.noise_models import qd_readout, qd_readout_2

from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.circuits.observables import Z
from braket.devices import LocalSimulator


@pytest.mark.mitiq
class TestExecutors(unittest.TestCase):
    
    @unittest.skip('api')
    def test_braket_executors(self):
        from mitiq import Observable, PauliString
        from mitiq_braket_tools import (
            braket_expectation_executor,
            braket_measurement_executor,
        )

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
        from mitiq_braket_tools import (
            braket_expectation_executor,
            braket_measurement_executor,
            )

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

@pytest.mark.mitiq
class TestMeasurement(unittest.TestCase):

    @unittest.skip('api')
    def test_rem_inverse(self):
        device = qd_readout_2
        from tools.mitigation_tools import (
            bit_mul_distribution,
            build_inverse_quasi_distribution,
            get_twirled_readout_dist,
        )


        ref_dist = get_twirled_readout_dist([1,2,3],
                                         n_twirls = 10, 
                                         shots = 10000, 
                                         device = device)
        validation = get_twirled_readout_dist([1,2,3],
                                         n_twirls = 10, 
                                         shots = 10000, 
                                         device = device)

        print(ref_dist)
        quasi1, _ = build_inverse_quasi_distribution(ref_dist, second_order=False)
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
        from tools.mitigation_tools import (
            SparseReadoutMitigation,
            apply_readout_twirl,
            get_twirled_readout_dist,
        )
        device = qd_readout
        dist = get_twirled_readout_dist([0,1],
                                         n_twirls = 10, 
                                         shots = 100000, 
                                         device = device)
        sparse = SparseReadoutMitigation(dist)    
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
    

if __name__ == "__main__":
    unittest.main()