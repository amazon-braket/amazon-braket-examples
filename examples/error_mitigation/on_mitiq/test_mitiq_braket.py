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

class TestExecutors(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()