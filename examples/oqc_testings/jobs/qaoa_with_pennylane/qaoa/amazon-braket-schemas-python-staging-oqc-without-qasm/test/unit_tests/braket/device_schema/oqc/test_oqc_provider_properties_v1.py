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

import json

import pytest
from pydantic import ValidationError

from braket.device_schema.oqc.oqc_provider_properties_v1 import OqcProviderProperties


@pytest.fixture(scope="module")
def valid_input():
    input = {
        "braketSchemaHeader": {
            "name": "braket.device_schema.oqc.oqc_provider_properties",
            "version": "1",
        },
        "properties": {
            "one_qubit": {
                "0": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "1": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "2": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "3": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "4": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "5": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "6": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
                "7": {
                    "T1": 12.2,
                    "T2": 13.5,
                    "fRO": 0.99,
                    "fRB": 0.98,
                    "native_gate_fidelities": [
                        {"native_gate": "rz", "CLf": 0.99},
                        {"native_gate": "sx", "CLf": 0.99},
                        {"native_gate": "x", "CLf": 0.99},
                    ],
                    "EPE": 0.001,
                },
            },
            "two_qubit": {
                "0-1": {
                    "coupling": {"control_qubit": 0, "target_qubit": 1},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "1-2": {
                    "coupling": {"control_qubit": 1, "target_qubit": 2},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "2-3": {
                    "coupling": {"control_qubit": 2, "target_qubit": 3},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "3-4": {
                    "coupling": {"control_qubit": 3, "target_qubit": 4},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "4-5": {
                    "coupling": {"control_qubit": 4, "target_qubit": 5},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "5-6": {
                    "coupling": {"control_qubit": 5, "target_qubit": 6},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "6-7": {
                    "coupling": {"control_qubit": 6, "target_qubit": 7},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
                "7-0": {
                    "coupling": {"control_qubit": 7, "target_qubit": 0},
                    "CLf": 0.99,
                    "ECR_f": 0.99,
                },
            },
        },
    }
    return input


def test_valid(valid_input):
    result = OqcProviderProperties.parse_raw_schema(json.dumps(valid_input))
    assert result.braketSchemaHeader.name == "braket.device_schema.oqc.oqc_provider_properties"


@pytest.mark.parametrize("missing_field", ["braketSchemaHeader", "properties"])
def test_missing_field(valid_input, missing_field):
    with pytest.raises(ValidationError):
        valid_input.pop(missing_field)
        OqcProviderProperties.parse_raw_schema(json.dumps(valid_input))
