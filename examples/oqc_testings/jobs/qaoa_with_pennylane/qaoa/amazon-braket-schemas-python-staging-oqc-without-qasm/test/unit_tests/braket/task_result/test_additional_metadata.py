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

from braket.task_result.additional_metadata import AdditionalMetadata


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    AdditionalMetadata()


def test_additional_metadata_correct_annealing(problem, dwave_metadata):
    metadata = AdditionalMetadata(action=problem, dwaveMetadata=dwave_metadata)
    assert metadata.action == problem
    assert metadata.dwaveMetadata == dwave_metadata
    assert AdditionalMetadata.parse_raw(metadata.json()) == metadata


def test_additional_metadata_correct_gate_model(program):
    metadata = AdditionalMetadata(action=program)
    assert metadata.action == program
    assert AdditionalMetadata.parse_raw(metadata.json()) == metadata


def test_additional_metadata_oqc(oqc_metadata, program):
    metadata = AdditionalMetadata(action=program, oqcMetadata=oqc_metadata)
    assert metadata.oqcMetadata == oqc_metadata
    assert AdditionalMetadata.parse_raw(metadata.json()) == metadata


@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_action(dwave_metadata):
    AdditionalMetadata(action=dwave_metadata)


@pytest.mark.xfail(raises=ValidationError)
def test_incorrect_dwave_metadata(program):
    AdditionalMetadata(dwaveMetadata=program)
