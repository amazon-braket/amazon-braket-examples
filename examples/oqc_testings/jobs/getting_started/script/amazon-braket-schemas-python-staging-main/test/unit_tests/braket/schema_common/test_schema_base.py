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

import pytest
from pydantic import ValidationError

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader
from braket.task_result.task_metadata_v1 import TaskMetadata


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    BraketSchemaBase()


def test_schema_base_correct(braket_schema_header):
    schema = BraketSchemaBase(braketSchemaHeader=braket_schema_header)
    assert schema.braketSchemaHeader == braket_schema_header
    assert BraketSchemaBase.parse_raw(schema.json()) == schema


@pytest.mark.xfail(raises=ValidationError)
def test_header_name_incorrect():
    BraketSchemaBase(braketSchemaHeader=120)


def test_import_schema_module():
    schema = TaskMetadata(
        id="test_id",
        deviceId="device_id",
        shots=1000,
    )
    module = BraketSchemaBase.import_schema_module(schema)
    assert schema == module.TaskMetadata.parse_raw(schema.json())


@pytest.mark.xfail(raises=ModuleNotFoundError)
def test_import_schema_module_error():
    schema = BraketSchemaBase(
        braketSchemaHeader=BraketSchemaHeader(
            name="braket.task_result.task_metadata", version="0.0"
        ),
    )
    BraketSchemaBase.import_schema_module(schema)


def test_parse_raw_schema():
    schema = TaskMetadata(
        id="test_id",
        deviceId="device_id",
        shots=1000,
    )
    assert schema == BraketSchemaBase.parse_raw_schema(schema.json())
    assert isinstance(schema, TaskMetadata)


def test_get_schema_class():
    schema = TaskMetadata(
        id="test_id",
        deviceId="device_id",
        shots=1000,
    )
    module = BraketSchemaBase.import_schema_module(schema)
    name = schema.braketSchemaHeader.name
    assert TaskMetadata == BraketSchemaBase.get_schema_class(module, name)


@pytest.mark.xfail(raises=AttributeError)
def test_get_schema_class_invalid_name():
    schema = TaskMetadata(
        id="test_id",
        deviceId="device_id",
        shots=1000,
    )
    module = BraketSchemaBase.import_schema_module(schema)
    name = schema.braketSchemaHeader.name + ".0"
    assert TaskMetadata == BraketSchemaBase.get_schema_class(module, name)


@pytest.mark.parametrize(
    "name",
    [
        "braket.device_schema.dwave.dwave_2000Q_device_level_parameters",
        "braket.device_schema.dwave.dwave_2000Q_device_parameters",
        "braket.device_schema.dwave.dwave_advantage_device_level_parameters",
        "braket.device_schema.dwave.dwave_advantage_device_parameters",
        "braket.device_schema.dwave.dwave_device_capabilities",
        "braket.device_schema.dwave.dwave_device_parameters",
        "braket.device_schema.dwave.dwave_provider_level_parameters",
        "braket.device_schema.dwave.dwave_provider_properties",
        "braket.device_schema.ionq.ionq_device_capabilities",
        "braket.device_schema.ionq.ionq_device_parameters",
        "braket.device_schema.ionq.ionq_provider_properties",
        "braket.device_schema.rigetti.rigetti_device_capabilities",
        "braket.device_schema.rigetti.rigetti_device_parameters",
        "braket.device_schema.rigetti.rigetti_provider_properties",
        "braket.device_schema.simulators.gate_model_simulator_device_capabilities",
        "braket.device_schema.simulators.gate_model_simulator_device_parameters",
        "braket.device_schema.simulators.gate_model_simulator_paradigm_properties",
        "braket.device_schema.device_service_properties",
        "braket.device_schema.gate_model_parameters",
        "braket.device_schema.gate_model_qpu_paradigm_properties",
        "braket.ir.annealing.problem",
        "braket.ir.jaqcd.program",
        "braket.ir.openqasm.program",
        "braket.task_result.annealing_task_result",
        "braket.task_result.dwave_metadata",
        "braket.task_result.gate_model_task_result",
        "braket.task_result.rigetti_metadata",
        "braket.task_result.simulator_metadata",
        "braket.task_result.task_metadata",
        "braket.jobs_data.persisted_job_data",
    ],
)
def test_no_header_typos(name):
    BraketSchemaHeader(name=name, version=1).import_schema_module()
