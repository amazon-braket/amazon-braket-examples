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

from braket.task_result.simulator_metadata_v1 import SimulatorMetadata


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    SimulatorMetadata()


def test_simulator_metadata_correct(execution_duration):
    metadata = SimulatorMetadata(executionDuration=execution_duration)
    assert metadata.executionDuration == execution_duration
    assert SimulatorMetadata.parse_raw(metadata.json()) == metadata
    assert metadata == SimulatorMetadata.parse_raw_schema(metadata.json())


@pytest.mark.xfail(raises=ValidationError)
def test_execution_duration_incorrect():
    execution_duration = -1
    SimulatorMetadata(executionDuration=execution_duration)


@pytest.mark.xfail(raises=ValidationError)
def test_simulator_header_incorrect(braket_schema_header, execution_duration):
    SimulatorMetadata(braketSchemaHeader=braket_schema_header, executionDuration=execution_duration)
