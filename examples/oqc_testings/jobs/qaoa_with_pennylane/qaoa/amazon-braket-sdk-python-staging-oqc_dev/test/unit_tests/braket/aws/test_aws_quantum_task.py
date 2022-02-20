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

import asyncio
import json
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from common_test_utils import MockS3
from jsonschema import validate

from braket.annealing.problem import Problem, ProblemType
from braket.aws import AwsQuantumTask
from braket.aws.aws_quantum_task import _create_annealing_device_params
from braket.aws.aws_session import AwsSession
from braket.circuits import Circuit
from braket.device_schema import GateModelParameters
from braket.device_schema.dwave import (
    Dwave2000QDeviceParameters,
    DwaveAdvantageDeviceParameters,
    DwaveDeviceParameters,
)
from braket.device_schema.ionq import IonqDeviceParameters
from braket.device_schema.oqc import OqcDeviceParameters
from braket.device_schema.rigetti import RigettiDeviceParameters
from braket.device_schema.simulators import GateModelSimulatorDeviceParameters
from braket.ir.openqasm import Program as OpenQasmProgram
from braket.tasks import AnnealingQuantumTaskResult, GateModelQuantumTaskResult

S3_TARGET = AwsSession.S3DestinationFolder("foo", "bar")

IONQ_ARN = "device/qpu/ionq"
RIGETTI_ARN = "device/qpu/rigetti"
OQC_ARN = "device/qpu/oqc"
SIMULATOR_ARN = "device/quantum-simulator"

DEVICE_PARAMETERS = [
    (IONQ_ARN, IonqDeviceParameters),
    (RIGETTI_ARN, RigettiDeviceParameters),
    (OQC_ARN, OqcDeviceParameters),
    (SIMULATOR_ARN, GateModelSimulatorDeviceParameters),
]


@pytest.fixture
def aws_session():
    mock = Mock()
    _mock_metadata(mock, "RUNNING")
    return mock


@pytest.fixture
def quantum_task(aws_session):
    return AwsQuantumTask("foo:bar:arn", aws_session, poll_timeout_seconds=2)


@pytest.fixture
def circuit_task(aws_session):
    return AwsQuantumTask("foo:bar:arn", aws_session, poll_timeout_seconds=2)


@pytest.fixture
def annealing_task(aws_session):
    return AwsQuantumTask("foo:bar:arn", aws_session, poll_timeout_seconds=2)


@pytest.fixture
def arn():
    return "foo:bar:arn"


@pytest.fixture
def circuit():
    return Circuit().h(0).cnot(0, 1)


@pytest.fixture
def problem():
    return Problem(ProblemType.ISING, linear={1: 3.14}, quadratic={(1, 2): 10.08})


@pytest.fixture
def openqasm_program():
    return OpenQasmProgram(source="OPENQASM 3.0; h $0;")


def test_equality(arn, aws_session):
    quantum_task_1 = AwsQuantumTask(arn, aws_session)
    quantum_task_2 = AwsQuantumTask(arn, aws_session)
    other_quantum_task = AwsQuantumTask("different:arn", aws_session)
    non_quantum_task = quantum_task_1.id

    assert quantum_task_1 == quantum_task_2
    assert quantum_task_1 is not quantum_task_2
    assert quantum_task_1 != other_quantum_task
    assert quantum_task_1 != non_quantum_task


def test_str(quantum_task):
    expected = "AwsQuantumTask('id/taskArn':'{}')".format(quantum_task.id)
    assert str(quantum_task) == expected


def test_hash(quantum_task):
    assert hash(quantum_task) == hash(quantum_task.id)


def test_id_getter(arn, aws_session):
    quantum_task = AwsQuantumTask(arn, aws_session)
    assert quantum_task.id == arn


@pytest.mark.xfail(raises=AttributeError)
def test_no_id_setter(quantum_task):
    quantum_task.id = 123


def test_metadata(quantum_task):
    metadata_1 = {"status": "RUNNING"}
    quantum_task._aws_session.get_quantum_task.return_value = metadata_1
    assert quantum_task.metadata() == metadata_1
    quantum_task._aws_session.get_quantum_task.assert_called_with(quantum_task.id)

    metadata_2 = {"status": "COMPLETED"}
    quantum_task._aws_session.get_quantum_task.return_value = metadata_2
    assert quantum_task.metadata(use_cached_value=True) == metadata_1


def test_metadata_call_if_none(quantum_task):
    metadata_1 = {"status": "RUNNING"}
    quantum_task._aws_session.get_quantum_task.return_value = metadata_1
    assert quantum_task.metadata(use_cached_value=True) == metadata_1
    quantum_task._aws_session.get_quantum_task.assert_called_with(quantum_task.id)


def test_state(quantum_task):
    state_1 = "RUNNING"
    _mock_metadata(quantum_task._aws_session, state_1)
    assert quantum_task.state() == state_1
    quantum_task._aws_session.get_quantum_task.assert_called_with(quantum_task.id)

    state_2 = "COMPLETED"
    _mock_metadata(quantum_task._aws_session, state_2)
    assert quantum_task.state(use_cached_value=True) == state_1

    state_3 = "FAILED"
    _mock_metadata(quantum_task._aws_session, state_3)
    assert quantum_task.state() == state_3

    state_4 = "CANCELLED"
    _mock_metadata(quantum_task._aws_session, state_4)
    assert quantum_task.state() == state_4


def test_cancel(quantum_task):
    future = quantum_task.async_result()

    assert not future.done()
    quantum_task.cancel()

    assert quantum_task.result() is None
    assert future.cancelled()
    quantum_task._aws_session.cancel_quantum_task.assert_called_with(quantum_task.id)


def test_cancel_without_fetching_result(quantum_task):
    quantum_task.cancel()

    assert quantum_task.result() is None
    assert quantum_task._future.cancelled()
    quantum_task._aws_session.cancel_quantum_task.assert_called_with(quantum_task.id)


def asyncio_get_event_loop_side_effect(*args, **kwargs):
    yield ValueError("unit-test-exception")
    mock = MagicMock()
    while True:
        yield mock


@patch("braket.aws.aws_quantum_task.asyncio")
def test_initialize_asyncio_event_loop_if_required(mock_asyncio, quantum_task):
    mock_asyncio.get_event_loop.side_effect = asyncio_get_event_loop_side_effect()
    mock_asyncio.set_event_loop.return_value = MagicMock()
    mock_asyncio.new_event_loop.return_value = MagicMock()

    quantum_task._get_future()

    assert mock_asyncio.get_event_loop.call_count == 2
    assert mock_asyncio.set_event_loop.call_count == 1
    assert mock_asyncio.new_event_loop.call_count == 1


def test_result_circuit(circuit_task):
    _mock_metadata(circuit_task._aws_session, "COMPLETED")
    _mock_s3(circuit_task._aws_session, MockS3.MOCK_S3_RESULT_GATE_MODEL)

    expected = GateModelQuantumTaskResult.from_string(MockS3.MOCK_S3_RESULT_GATE_MODEL)
    assert circuit_task.result() == expected

    s3_bucket = circuit_task.metadata()["outputS3Bucket"]
    s3_object_key = circuit_task.metadata()["outputS3Directory"]
    circuit_task._aws_session.retrieve_s3_object_body.assert_called_with(
        s3_bucket, f"{s3_object_key}/results.json"
    )


def test_result_annealing(annealing_task):
    _mock_metadata(annealing_task._aws_session, "COMPLETED")
    _mock_s3(annealing_task._aws_session, MockS3.MOCK_S3_RESULT_ANNEALING)

    expected = AnnealingQuantumTaskResult.from_string(MockS3.MOCK_S3_RESULT_ANNEALING)
    assert annealing_task.result() == expected

    s3_bucket = annealing_task.metadata()["outputS3Bucket"]
    s3_object_key = annealing_task.metadata()["outputS3Directory"]
    annealing_task._aws_session.retrieve_s3_object_body.assert_called_with(
        s3_bucket, f"{s3_object_key}/results.json"
    )


@pytest.mark.xfail(raises=TypeError)
def test_result_invalid_type(circuit_task):
    _mock_metadata(circuit_task._aws_session, "COMPLETED")
    _mock_s3(circuit_task._aws_session, json.dumps(MockS3.MOCK_TASK_METADATA))
    circuit_task.result()


def test_result_circuit_cached(circuit_task):
    _mock_metadata(circuit_task._aws_session, "COMPLETED")
    expected = GateModelQuantumTaskResult.from_string(MockS3.MOCK_S3_RESULT_GATE_MODEL)
    circuit_task._result = expected
    assert circuit_task.result() == expected
    assert not circuit_task._aws_session.retrieve_s3_object_body.called


def test_no_result(circuit_task):
    _mock_metadata(circuit_task._aws_session, "FAILED")
    circuit_task._result = None
    assert circuit_task.result() is None
    assert not circuit_task._aws_session.retrieve_s3_object_body.called


@pytest.mark.parametrize(
    "result_string",
    [MockS3.MOCK_S3_RESULT_GATE_MODEL, MockS3.MOCK_S3_RESULT_GATE_MODEL_WITH_RESULT_TYPES],
)
def test_result_cached_future(circuit_task, result_string):
    _mock_metadata(circuit_task._aws_session, "COMPLETED")
    _mock_s3(circuit_task._aws_session, result_string)
    circuit_task.result()

    _mock_s3(circuit_task._aws_session, "")
    expected = GateModelQuantumTaskResult.from_string(MockS3.MOCK_S3_RESULT_GATE_MODEL)
    assert circuit_task.result() == expected


@pytest.mark.parametrize(
    "status, result",
    [
        ("COMPLETED", GateModelQuantumTaskResult.from_string(MockS3.MOCK_S3_RESULT_GATE_MODEL)),
        ("FAILED", None),
    ],
)
def test_async_result(circuit_task, status, result):
    def set_result_from_callback(future):
        # Set the result_from_callback variable in the enclosing functions scope
        nonlocal result_from_callback
        result_from_callback = future.result()

    _mock_metadata(circuit_task._aws_session, "RUNNING")
    _mock_s3(circuit_task._aws_session, MockS3.MOCK_S3_RESULT_GATE_MODEL)

    future = circuit_task.async_result()

    # test the different ways to get the result from async

    # via callback
    result_from_callback = None
    future.add_done_callback(set_result_from_callback)

    # via asyncio waiting for result
    _mock_metadata(circuit_task._aws_session, status)
    event_loop = asyncio.get_event_loop()
    result_from_waiting = event_loop.run_until_complete(future)

    # via future.result(). Note that this would fail if the future is not complete.
    result_from_future = future.result()

    assert result_from_callback == result
    assert result_from_waiting == result
    assert result_from_future == result


def test_failed_task(quantum_task):
    _mock_metadata(quantum_task._aws_session, "FAILED")
    _mock_s3(quantum_task._aws_session, MockS3.MOCK_S3_RESULT_GATE_MODEL)
    result = quantum_task.result()
    assert result is None


def test_timeout_completed(aws_session):
    _mock_metadata(aws_session, "RUNNING")
    _mock_s3(aws_session, MockS3.MOCK_S3_RESULT_GATE_MODEL)

    # Setup the poll timing such that the timeout will occur after one API poll
    quantum_task = AwsQuantumTask(
        "foo:bar:arn",
        aws_session,
        poll_timeout_seconds=0.5,
        poll_interval_seconds=1,
    )
    assert quantum_task.result() is None
    _mock_metadata(aws_session, "COMPLETED")
    assert quantum_task.state() == "COMPLETED"
    assert quantum_task.result() == GateModelQuantumTaskResult.from_string(
        MockS3.MOCK_S3_RESULT_GATE_MODEL
    )
    # Cached status is still COMPLETED, so result should be fetched
    _mock_metadata(aws_session, "RUNNING")
    quantum_task._result = None
    assert quantum_task.result() == GateModelQuantumTaskResult.from_string(
        MockS3.MOCK_S3_RESULT_GATE_MODEL
    )


def test_timeout_no_result_terminal_state(aws_session):
    _mock_metadata(aws_session, "RUNNING")
    _mock_s3(aws_session, MockS3.MOCK_S3_RESULT_GATE_MODEL)

    # Setup the poll timing such that the timeout will occur after one API poll
    quantum_task = AwsQuantumTask(
        "foo:bar:arn",
        aws_session,
        poll_timeout_seconds=0.5,
        poll_interval_seconds=1,
    )
    assert quantum_task.result() is None

    _mock_metadata(aws_session, "FAILED")
    assert quantum_task.result() is None


@pytest.mark.xfail(raises=ValueError)
def test_create_invalid_s3_folder(aws_session, arn, circuit):
    AwsQuantumTask.create(aws_session, arn, circuit, ("bucket",), 1000)


@pytest.mark.xfail(raises=TypeError)
def test_create_invalid_task_specification(aws_session, arn):
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    AwsQuantumTask.create(aws_session, arn, "foo", S3_TARGET, 1000)


def test_create_openqasm_program(aws_session, arn, openqasm_program):
    aws_session.create_quantum_task.return_value = arn
    shots = 21
    AwsQuantumTask.create(aws_session, SIMULATOR_ARN, openqasm_program, S3_TARGET, shots)

    _assert_create_quantum_task_called_with(
        aws_session,
        SIMULATOR_ARN,
        openqasm_program.json(),
        S3_TARGET,
        shots,
    )


@pytest.mark.parametrize("device_arn,device_parameters_class", DEVICE_PARAMETERS)
def test_from_circuit_with_shots(device_arn, device_parameters_class, aws_session, circuit):
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    shots = 53

    task = AwsQuantumTask.create(aws_session, device_arn, circuit, S3_TARGET, shots)
    assert task == AwsQuantumTask(mocked_task_arn, aws_session)

    _assert_create_quantum_task_called_with(
        aws_session,
        device_arn,
        circuit.to_ir().json(),
        S3_TARGET,
        shots,
        device_parameters_class(
            paradigmParameters=GateModelParameters(
                qubitCount=circuit.qubit_count, disableQubitRewiring=False
            )
        ),
    )


@pytest.mark.parametrize(
    "device_arn,device_parameters_class", [(RIGETTI_ARN, RigettiDeviceParameters)]
)
def test_from_circuit_with_disabled_rewiring(
    device_arn, device_parameters_class, aws_session, circuit
):
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    shots = 53

    task = AwsQuantumTask.create(
        aws_session, device_arn, circuit, S3_TARGET, shots, disable_qubit_rewiring=True
    )
    assert task == AwsQuantumTask(mocked_task_arn, aws_session)

    _assert_create_quantum_task_called_with(
        aws_session,
        device_arn,
        circuit.to_ir().json(),
        S3_TARGET,
        shots,
        device_parameters_class(
            paradigmParameters=GateModelParameters(
                qubitCount=circuit.qubit_count, disableQubitRewiring=True
            )
        ),
    )


@pytest.mark.parametrize(
    "device_arn,device_parameters_class", [(RIGETTI_ARN, RigettiDeviceParameters)]
)
def test_from_circuit_with_verbatim(device_arn, device_parameters_class, aws_session):
    circ = Circuit().add_verbatim_box(Circuit().h(0))
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    shots = 1337

    task = AwsQuantumTask.create(
        aws_session,
        device_arn,
        circ,
        S3_TARGET,
        shots,
        disable_qubit_rewiring=True,
    )
    assert task == AwsQuantumTask(mocked_task_arn, aws_session)

    _assert_create_quantum_task_called_with(
        aws_session,
        device_arn,
        circ.to_ir().json(),
        S3_TARGET,
        shots,
        device_parameters_class(
            paradigmParameters=GateModelParameters(
                qubitCount=circ.qubit_count, disableQubitRewiring=True
            )
        ),
    )


@pytest.mark.xfail(raises=ValueError)
def test_from_circuit_with_verbatim_qubit_rewiring_not_disabled(aws_session):
    circ = Circuit().add_verbatim_box(Circuit().h(0))
    shots = 57
    AwsQuantumTask.create(aws_session, RIGETTI_ARN, circ, S3_TARGET, shots)


@pytest.mark.xfail(raises=ValueError)
def test_from_circuit_with_shots_value_error(aws_session, arn, circuit):
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    AwsQuantumTask.create(aws_session, arn, circuit, S3_TARGET, 0)


@pytest.mark.parametrize(
    "device_parameters,arn",
    [
        (
            {
                "providerLevelParameters": {
                    "postprocessingType": "OPTIMIZATION",
                    "annealingOffsets": [3.67, 6.123],
                    "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                    "annealingDuration": 1,
                    "autoScale": False,
                    "beta": 0.2,
                    "chains": [[0, 1, 5], [6]],
                    "compensateFluxDrift": False,
                    "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                    "initialState": [1, 3, 0, 1],
                    "maxResults": 1,
                    "programmingThermalizationDuration": 625,
                    "readoutThermalizationDuration": 256,
                    "reduceIntersampleCorrelation": False,
                    "reinitializeState": True,
                    "resultFormat": "RAW",
                    "spinReversalTransformCount": 100,
                }
            },
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system1",
        ),
        (
            {
                "deviceLevelParameters": {
                    "postprocessingType": "OPTIMIZATION",
                    "beta": 0.2,
                    "annealingOffsets": [3.67, 6.123],
                    "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                    "annealingDuration": 1,
                    "autoScale": False,
                    "chains": [[0, 1, 5], [6]],
                    "compensateFluxDrift": False,
                    "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                    "initialState": [1, 3, 0, 1],
                    "maxResults": 1,
                    "programmingThermalizationDuration": 625,
                    "readoutThermalizationDuration": 256,
                    "reduceIntersampleCorrelation": False,
                    "reinitializeState": True,
                    "resultFormat": "RAW",
                    "spinReversalTransformCount": 100,
                }
            },
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
        ),
        pytest.param(
            {
                "deviceLevelParameters": {
                    "postprocessingType": "OPTIMIZATION",
                    "beta": 0.2,
                    "annealingOffsets": [3.67, 6.123],
                    "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                    "annealingDuration": 1,
                    "autoScale": False,
                    "chains": [[0, 1, 5], [6]],
                    "compensateFluxDrift": False,
                    "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                    "initialState": [1, 3, 0, 1],
                    "maxResults": 1,
                    "programmingThermalizationDuration": 625,
                    "readoutThermalizationDuration": 256,
                    "reduceIntersampleCorrelation": False,
                    "reinitializeState": True,
                    "resultFormat": "RAW",
                    "spinReversalTransformCount": 100,
                }
            },
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system1",
            # this doesn't fail... yet
            # marks=pytest.mark.xfail(reason='beta not a valid parameter for Advantage device'),
        ),
        pytest.param(
            {
                "deviceLevelParameters": {
                    "postprocessingType": "OPTIMIZATION",
                    "beta": 0.2,
                    "annealingOffsets": [3.67, 6.123],
                    "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                    "annealingDuration": 1,
                    "autoScale": False,
                    "chains": [[0, 1, 5], [6]],
                    "compensateFluxDrift": False,
                    "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                    "initialState": [1, 3, 0, 1],
                    "maxResults": 1,
                    "programmingThermalizationDuration": 625,
                    "readoutThermalizationDuration": 256,
                    "reduceIntersampleCorrelation": False,
                    "reinitializeState": True,
                    "resultFormat": "RAW",
                    "spinReversalTransformCount": 100,
                }
            },
            "arn:aws:braket:::device/qpu/d-wave/fake_arn",
            marks=pytest.mark.xfail(reason="Bad ARN"),
        ),
        (
            {
                "deviceLevelParameters": {
                    "postprocessingType": "OPTIMIZATION",
                    "annealingOffsets": [3.67, 6.123],
                    "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                    "annealingDuration": 1,
                    "autoScale": False,
                    "beta": 0.2,
                    "chains": [[0, 1, 5], [6]],
                    "compensateFluxDrift": False,
                    "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                    "initialState": [1, 3, 0, 1],
                    "maxResults": 1,
                    "programmingThermalizationDuration": 625,
                    "readoutThermalizationDuration": 256,
                    "reduceIntersampleCorrelation": False,
                    "reinitializeState": True,
                    "resultFormat": "RAW",
                    "spinReversalTransformCount": 100,
                }
            },
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
        ),
        (
            DwaveDeviceParameters.parse_obj(
                {
                    "providerLevelParameters": {
                        "postprocessingType": "OPTIMIZATION",
                        "annealingOffsets": [3.67, 6.123],
                        "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                        "annealingDuration": 1,
                        "autoScale": False,
                        "beta": 0.2,
                        "chains": [[0, 1, 5], [6]],
                        "compensateFluxDrift": False,
                        "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                        "initialState": [1, 3, 0, 1],
                        "maxResults": 1,
                        "programmingThermalizationDuration": 625,
                        "readoutThermalizationDuration": 256,
                        "reduceIntersampleCorrelation": False,
                        "reinitializeState": True,
                        "resultFormat": "RAW",
                        "spinReversalTransformCount": 100,
                    }
                }
            ),
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system1",
        ),
        (
            DwaveDeviceParameters.parse_obj(
                {
                    "deviceLevelParameters": {
                        "postprocessingType": "OPTIMIZATION",
                        "annealingOffsets": [3.67, 6.123],
                        "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                        "annealingDuration": 1,
                        "autoScale": False,
                        "beta": 0.2,
                        "chains": [[0, 1, 5], [6]],
                        "compensateFluxDrift": False,
                        "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                        "initialState": [1, 3, 0, 1],
                        "maxResults": 1,
                        "programmingThermalizationDuration": 625,
                        "readoutThermalizationDuration": 256,
                        "reduceIntersampleCorrelation": False,
                        "reinitializeState": True,
                        "resultFormat": "RAW",
                        "spinReversalTransformCount": 100,
                    }
                },
            ),
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system1",
        ),
        (
            DwaveAdvantageDeviceParameters.parse_obj(
                {
                    "deviceLevelParameters": {
                        "annealingOffsets": [3.67, 6.123],
                        "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                        "annealingDuration": 1,
                        "autoScale": False,
                        "beta": 0.2,
                        "chains": [[0, 1, 5], [6]],
                        "compensateFluxDrift": False,
                        "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                        "initialState": [1, 3, 0, 1],
                        "maxResults": 1,
                        "programmingThermalizationDuration": 625,
                        "readoutThermalizationDuration": 256,
                        "reduceIntersampleCorrelation": False,
                        "reinitializeState": True,
                        "resultFormat": "RAW",
                        "spinReversalTransformCount": 100,
                    }
                },
            ),
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system1",
        ),
        (
            Dwave2000QDeviceParameters.parse_obj(
                {
                    "deviceLevelParameters": {
                        "postprocessingType": "OPTIMIZATION",
                        "annealingOffsets": [3.67, 6.123],
                        "annealingSchedule": [[13.37, 10.08], [3.14, 1.618]],
                        "annealingDuration": 1,
                        "autoScale": False,
                        "beta": 0.2,
                        "chains": [[0, 1, 5], [6]],
                        "compensateFluxDrift": False,
                        "fluxBiases": [1.1, 2.2, 3.3, 4.4],
                        "initialState": [1, 3, 0, 1],
                        "maxResults": 1,
                        "programmingThermalizationDuration": 625,
                        "readoutThermalizationDuration": 256,
                        "reduceIntersampleCorrelation": False,
                        "reinitializeState": True,
                        "resultFormat": "RAW",
                        "spinReversalTransformCount": 100,
                    }
                }
            ),
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
        ),
        (
            Dwave2000QDeviceParameters.parse_obj({"deviceLevelParameters": {}}),
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
        ),
        pytest.param(
            {},
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
        ),
    ],
)
def test_from_annealing(device_parameters, aws_session, arn, problem):
    mocked_task_arn = "task-arn-1"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    task = AwsQuantumTask.create(
        aws_session,
        arn,
        problem,
        S3_TARGET,
        1000,
        device_parameters=device_parameters,
    )
    assert task == AwsQuantumTask(mocked_task_arn, aws_session)
    annealing_parameters = _create_annealing_device_params(device_parameters, device_arn=arn)
    validate(
        json.loads(annealing_parameters.json(exclude_none=True)), annealing_parameters.schema()
    )
    _assert_create_quantum_task_called_with(
        aws_session,
        arn,
        problem.to_ir().json(),
        S3_TARGET,
        1000,
        annealing_parameters,
    )


@pytest.mark.parametrize("device_arn,device_parameters_class", DEVICE_PARAMETERS)
def test_create_with_tags(device_arn, device_parameters_class, aws_session, circuit):
    mocked_task_arn = "task-arn-tags"
    aws_session.create_quantum_task.return_value = mocked_task_arn
    shots = 53
    tags = {"state": "washington"}

    task = AwsQuantumTask.create(aws_session, device_arn, circuit, S3_TARGET, shots, tags=tags)
    assert task == AwsQuantumTask(mocked_task_arn, aws_session)
    _assert_create_quantum_task_called_with(
        aws_session,
        device_arn,
        circuit.to_ir().json(),
        S3_TARGET,
        shots,
        device_parameters_class(
            paradigmParameters=GateModelParameters(qubitCount=circuit.qubit_count)
        ),
        tags,
    )


def test_init_new_thread(aws_session, arn):
    tasks_list = []
    threading.Thread(target=_init_and_add_to_list, args=(aws_session, arn, tasks_list)).start()
    time.sleep(0.1)
    assert len(tasks_list) == 1


@patch("braket.aws.aws_quantum_task.boto3.Session")
def test_aws_session_for_task_arn(mock_session):
    region = "us-west-2"
    arn = f"arn:aws:aqx:{region}:account_id:quantum-task:task_id"
    mock_boto_session = Mock()
    mock_session.return_value = mock_boto_session
    mock_boto_session.region_name = region
    aws_session = AwsQuantumTask._aws_session_for_task_arn(arn)
    mock_session.assert_called_with(region_name=region)
    assert aws_session.boto_session == mock_boto_session


def _init_and_add_to_list(aws_session, arn, task_list):
    task_list.append(AwsQuantumTask(arn, aws_session))


def _assert_create_quantum_task_called_with(
    aws_session, arn, task_description, s3_results_prefix, shots, device_parameters=None, tags=None
):
    test_kwargs = {
        "deviceArn": arn,
        "outputS3Bucket": s3_results_prefix[0],
        "outputS3KeyPrefix": s3_results_prefix[1],
        "action": task_description,
        "shots": shots,
    }
    if device_parameters is not None:
        test_kwargs.update({"deviceParameters": device_parameters.json(exclude_none=True)})
    if tags is not None:
        test_kwargs.update({"tags": tags})
    aws_session.create_quantum_task.assert_called_with(**test_kwargs)


def _mock_metadata(aws_session, state):
    aws_session.get_quantum_task.return_value = {
        "status": state,
        "outputS3Bucket": S3_TARGET.bucket,
        "outputS3Directory": S3_TARGET.key,
    }


def _mock_s3(aws_session, result):
    aws_session.retrieve_s3_object_body.return_value = result
