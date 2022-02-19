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

from braket.ir.annealing import Problem, ProblemType
from braket.ir.jaqcd import CNot
from braket.ir.jaqcd import Program as JaqcdProgram
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.schema_common.schema_header import BraketSchemaHeader
from braket.task_result.additional_metadata import AdditionalMetadata
from braket.task_result.dwave_metadata_v1 import DwaveMetadata, DwaveTiming
from braket.task_result.oqc_metadata_v1 import OqcMetadata
from braket.task_result.rigetti_metadata_v1 import NativeQuilMetadata, RigettiMetadata
from braket.task_result.task_metadata_v1 import TaskMetadata


@pytest.fixture
def braket_schema_header():
    return BraketSchemaHeader(name="test_schema", version="1.0")


@pytest.fixture
def active_variables():
    return [2, 3, 4]


@pytest.fixture
def compiled_program():
    return "DECLARE ro BIT[2]\n"


@pytest.fixture
def native_quil_metadata():
    return NativeQuilMetadata(
        finalRewiring=[32, 21],
        gateDepth=5,
        gateVolume=6,
        multiQubitGateDepth=1,
        programDuration=300.1,
        programFidelity=0.8989,
        qpuRuntimeEstimation=191.21,
        topologicalSwaps=0,
    )


@pytest.fixture
def rigetti_metadata(compiled_program, native_quil_metadata):
    return RigettiMetadata(
        compiledProgram=compiled_program, nativeQuilMetadata=native_quil_metadata
    )


@pytest.fixture
def dwave_timing():
    return DwaveTiming(
        qpuSamplingTime=1575,
        qpuAnnealTimePerSample=20,
        qpuReadoutTimePerSample=274,
        qpuAccessTime=10917,
        qpuAccessOverheadTime=3382,
        qpuProgrammingTime=9342,
        qpuDelayTimePerSample=21,
        totalPostProcessingTime=117,
        postProcessingOverheadTime=117,
        totalRealTime=10917,
        runTimeChip=1575,
        annealTimePerRun=20,
        readoutTimePerRun=274,
    )


@pytest.fixture
def dwave_metadata(active_variables, dwave_timing, braket_schema_header):
    return DwaveMetadata(
        activeVariables=active_variables,
        timing=dwave_timing,
    )


@pytest.fixture
def oqc_metadata(compiled_program):
    return OqcMetadata(executedProgram=compiled_program)


@pytest.fixture
def problem():
    return Problem(
        type=ProblemType.QUBO,
        linear={0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333},
        quadratic={"0,4": 0.667, "0,5": -1, "1,4": 0.667, "1,5": 0.667},
    )


@pytest.fixture
def additional_metadata_annealing(problem, dwave_metadata):
    return AdditionalMetadata(action=problem, dwaveMetadata=dwave_metadata)


@pytest.fixture
def jacqd_program():
    return JaqcdProgram(instructions=[CNot(control=0, target=1)])


@pytest.fixture
def openqasm_program():
    return OpenQASMProgram(source="OPENQASM 3.0; cnot $0, $1;")


@pytest.fixture
def additional_metadata_gate_model(jacqd_program, rigetti_metadata):
    return AdditionalMetadata(action=jacqd_program, rigettiMetadata=rigetti_metadata)


@pytest.fixture
def id():
    return "task_id"


@pytest.fixture
def device_id():
    return "device_id"


@pytest.fixture
def shots():
    return 1000


@pytest.fixture
def task_metadata(id, device_id, shots):
    return TaskMetadata(id=id, deviceId=device_id, shots=shots)


@pytest.fixture
def execution_duration():
    return 100
