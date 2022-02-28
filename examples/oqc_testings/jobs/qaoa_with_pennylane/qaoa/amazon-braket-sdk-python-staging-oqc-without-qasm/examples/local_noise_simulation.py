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

from braket.circuits import Circuit, Noise
from braket.devices import LocalSimulator

device = LocalSimulator("braket_dm")

circuit = Circuit().x(0).x(1).bit_flip(0, probability=0.1)
print("First example: ")
print(circuit)
print(device.run(circuit, shots=1000).result().measurement_counts)


circuit = Circuit().x(0).x(1)
noise = Noise.BitFlip(probability=0.1)
circuit.apply_gate_noise(noise)
print("Second example: ")
print(circuit)
print(device.run(circuit, shots=1000).result().measurement_counts)
