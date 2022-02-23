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

from braket.task_result.rigetti_metadata_v1 import NativeQuilMetadata, RigettiMetadata


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    RigettiMetadata()


def test_rigetti_metadata_correct(compiled_program, native_quil_metadata):
    metadata = RigettiMetadata(
        compiledProgram=compiled_program, nativeQuilMetadata=native_quil_metadata
    )
    assert metadata.compiledProgram == compiled_program
    assert metadata.nativeQuilMetadata == native_quil_metadata
    assert RigettiMetadata.parse_raw(metadata.json()) == metadata
    assert metadata == RigettiMetadata.parse_raw_schema(metadata.json())


@pytest.mark.parametrize("compiled_program", [(""), (["random string"])])
@pytest.mark.xfail(raises=ValidationError)
def test_compiled_program_incorrect(compiled_program, native_quil_metadata):
    RigettiMetadata(
        compiledProgram=compiled_program,
        nativeQuilMetadata=native_quil_metadata,
    )


@pytest.mark.xfail(raises=ValidationError)
def test_rigetti_header_incorrect(braket_schema_header, compiled_program, native_quil_metadata):
    RigettiMetadata(
        braketSchemaHeader=braket_schema_header,
        compiledProgram=compiled_program,
        nativeQuilMetadata=native_quil_metadata,
    )


@pytest.mark.xfail(raises=ValidationError)
def test_rigetti_native_quil_metadata__incorrect():
    NativeQuilMetadata(
        finalRewiring=[32, 21],
        gateDepth=-1,
        gateVolume=-1,
        multiQubitGateDepth=-1,
        programDuration=300,
        programFidelity=0,
        qpuRuntimeEstimation=-1,
        topologicalSwaps=0,
    )
