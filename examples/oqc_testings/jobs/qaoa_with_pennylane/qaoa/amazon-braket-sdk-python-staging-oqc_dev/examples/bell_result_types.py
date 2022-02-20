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

from braket.circuits import Circuit, Observable
from braket.devices import LocalSimulator

device = LocalSimulator()

print("Example for shots=0")
# Result types can be requested in the circuit
# Example of result types for shots=0
bell = (
    Circuit()
    .h(0)
    .cnot(0, 1)
    .probability(target=[0])
    .expectation(observable=Observable.Z(), target=[1])
    .amplitude(state=["00"])
    .state_vector()
)

# State vector and amplitude can only be requested when shots=0 for a simulator
# When shots=0 for a simulator, probability, expectation, variance are the exact values,
# not calculated from measurements
# Users cannot request Sample as a result when shots=0
result = device.run(bell).result()
print("Marginal probability for target 0 in computational basis:", result.values[0])
print("Expectation of target 1 in the computational basis:", result.values[1])
print("Amplitude of state 00:", result.values[2])
print("State vector:", result.values[3])

print("\nExample for shots>0")
# Example of result types for shots > 0
bell = (
    Circuit()
    .h(0)
    .cnot(0, 1)
    .expectation(observable=Observable.Y() @ Observable.X(), target=[0, 1])
    .variance(observable=Observable.Y() @ Observable.X(), target=[0, 1])
    .sample(observable=Observable.Y() @ Observable.X(), target=[0, 1])
)

# When shots>0 for a simulator, probability, expectation, variance are calculated from measurements
# Users can request sample as a result when shots > 0
result = device.run(bell, shots=100).result()
print("Expectation of target 0, 1 in the basis of Pauli-Y @ Pauli-X:", result.values[0])
print("Variance of target 0, 1 in the basis of Pauli-Y @ Pauli-X:", result.values[1])
print("Samples of target 0, 1 in the basis of Pauli-Y @ Pauli-X:", result.values[2])

# Probability, sample, expectation, and variance are also supported for QPU devices
