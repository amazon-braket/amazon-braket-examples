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
import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError
from common_test_utils import (
    DWAVE_ARN,
    IONQ_ARN,
    RIGETTI_ARN,
    RIGETTI_REGION,
    SV1_ARN,
    TN1_ARN,
    run_and_assert,
    run_batch_and_assert,
)
from jsonschema import validate

from braket.aws import AwsDevice, AwsDeviceType, AwsQuantumTask
from braket.circuits import Circuit
from braket.device_schema.device_execution_window import DeviceExecutionWindow
from braket.device_schema.dwave import DwaveDeviceCapabilities
from braket.device_schema.rigetti import RigettiDeviceCapabilities
from braket.device_schema.simulators import GateModelSimulatorDeviceCapabilities

MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_1 = {
    "braketSchemaHeader": {
        "name": "braket.device_schema.rigetti.rigetti_device_capabilities",
        "version": "1",
    },
    "service": {
        "executionWindows": [
            {
                "executionDay": "Everyday",
                "windowStartHour": "11:00",
                "windowEndHour": "12:00",
            }
        ],
        "shotsRange": [1, 10],
    },
    "action": {
        "braket.ir.jaqcd.program": {
            "actionType": "braket.ir.jaqcd.program",
            "version": ["1"],
            "supportedOperations": ["H"],
        }
    },
    "paradigm": {
        "qubitCount": 30,
        "nativeGateSet": ["ccnot", "cy"],
        "connectivity": {"fullyConnected": False, "connectivityGraph": {"1": ["2", "3"]}},
    },
    "deviceParameters": {},
}


MOCK_GATE_MODEL_QPU_CAPABILITIES_1 = RigettiDeviceCapabilities.parse_obj(
    MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_1
)


def test_mock_rigetti_schema_1():
    validate(MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_1, RigettiDeviceCapabilities.schema())


MOCK_GATE_MODEL_QPU_1 = {
    "deviceName": "Aspen-10",
    "deviceType": "QPU",
    "providerName": "provider1",
    "deviceStatus": "OFFLINE",
    "deviceCapabilities": MOCK_GATE_MODEL_QPU_CAPABILITIES_1.json(),
}

MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_2 = {
    "braketSchemaHeader": {
        "name": "braket.device_schema.rigetti.rigetti_device_capabilities",
        "version": "1",
    },
    "service": {
        "executionWindows": [
            {
                "executionDay": "Everyday",
                "windowStartHour": "11:00",
                "windowEndHour": "12:00",
            }
        ],
        "shotsRange": [1, 10],
    },
    "action": {
        "braket.ir.jaqcd.program": {
            "actionType": "braket.ir.jaqcd.program",
            "version": ["1"],
            "supportedOperations": ["H"],
        }
    },
    "paradigm": {
        "qubitCount": 30,
        "nativeGateSet": ["ccnot", "cy"],
        "connectivity": {"fullyConnected": True, "connectivityGraph": {}},
    },
    "deviceParameters": {},
}

MOCK_GATE_MODEL_QPU_CAPABILITIES_2 = RigettiDeviceCapabilities.parse_obj(
    MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_2
)


def test_mock_rigetti_schema_2():
    validate(MOCK_GATE_MODEL_QPU_CAPABILITIES_JSON_2, RigettiDeviceCapabilities.schema())


MOCK_GATE_MODEL_QPU_2 = {
    "deviceName": "Blah",
    "deviceType": "QPU",
    "providerName": "blahhhh",
    "deviceStatus": "OFFLINE",
    "deviceCapabilities": MOCK_GATE_MODEL_QPU_CAPABILITIES_2.json(),
}

MOCK_DWAVE_QPU_CAPABILITIES_JSON = {
    "braketSchemaHeader": {
        "name": "braket.device_schema.dwave.dwave_device_capabilities",
        "version": "1",
    },
    "provider": {
        "annealingOffsetStep": 1.45,
        "annealingOffsetStepPhi0": 1.45,
        "annealingOffsetRanges": [[1.45, 1.45], [1.45, 1.45]],
        "annealingDurationRange": [1, 2, 3],
        "couplers": [[1, 2], [1, 2]],
        "defaultAnnealingDuration": 1,
        "defaultProgrammingThermalizationDuration": 1,
        "defaultReadoutThermalizationDuration": 1,
        "extendedJRange": [1, 2, 3],
        "hGainScheduleRange": [1, 2, 3],
        "hRange": [1, 2, 3],
        "jRange": [1, 2, 3],
        "maximumAnnealingSchedulePoints": 1,
        "maximumHGainSchedulePoints": 1,
        "perQubitCouplingRange": [1, 2, 3],
        "programmingThermalizationDurationRange": [1, 2, 3],
        "qubits": [1, 2, 3],
        "qubitCount": 1,
        "quotaConversionRate": 1,
        "readoutThermalizationDurationRange": [1, 2, 3],
        "taskRunDurationRange": [1, 2, 3],
        "topology": {},
    },
    "service": {
        "executionWindows": [
            {"executionDay": "Everyday", "windowStartHour": "11:00", "windowEndHour": "12:00"}
        ],
        "shotsRange": [1, 10],
    },
    "action": {
        "braket.ir.annealing.problem": {
            "actionType": "braket.ir.annealing.problem",
            "version": ["1"],
        }
    },
    "deviceParameters": {},
}

MOCK_DWAVE_QPU_CAPABILITIES = DwaveDeviceCapabilities.parse_obj(MOCK_DWAVE_QPU_CAPABILITIES_JSON)


def test_d_wave_schema():
    validate(MOCK_DWAVE_QPU_CAPABILITIES_JSON, DwaveDeviceCapabilities.schema())


MOCK_DWAVE_QPU = {
    "deviceName": "Advantage_system1.1",
    "deviceType": "QPU",
    "providerName": "provider1",
    "deviceStatus": "ONLINE",
    "deviceCapabilities": MOCK_DWAVE_QPU_CAPABILITIES.json(),
}

MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES_JSON = {
    "braketSchemaHeader": {
        "name": "braket.device_schema.simulators.gate_model_simulator_device_capabilities",
        "version": "1",
    },
    "service": {
        "executionWindows": [
            {
                "executionDay": "Everyday",
                "windowStartHour": "11:00",
                "windowEndHour": "12:00",
            }
        ],
        "shotsRange": [1, 10],
    },
    "action": {
        "braket.ir.jaqcd.program": {
            "actionType": "braket.ir.jaqcd.program",
            "version": ["1"],
            "supportedOperations": ["H"],
        }
    },
    "paradigm": {"qubitCount": 30},
    "deviceParameters": {},
}

MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES = GateModelSimulatorDeviceCapabilities.parse_obj(
    MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES_JSON
)


def test_gate_model_sim_schema():
    validate(
        MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES_JSON, GateModelSimulatorDeviceCapabilities.schema()
    )


MOCK_GATE_MODEL_SIMULATOR = {
    "deviceName": "SV1",
    "deviceType": "SIMULATOR",
    "providerName": "provider1",
    "deviceStatus": "ONLINE",
    "deviceCapabilities": MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES.json(),
}

MOCK_DEFAULT_S3_DESTINATION_FOLDER = (
    "amazon-braket-us-test-1-00000000",
    "tasks",
)


@pytest.fixture(
    params=[
        "arn:aws:braket:us-west-1::device/quantum-simulator/amazon/sim",
        "arn:aws:braket:::device/quantum-simulator/amazon/sim",
    ]
)
def arn(request):
    return request.param


@pytest.fixture
def s3_destination_folder():
    return "bucket-foo", "key-bar"


@pytest.fixture
def circuit():
    return Circuit().h(0)


@pytest.fixture
def boto_session():
    _boto_session = Mock()
    _boto_session.region_name = RIGETTI_REGION
    return _boto_session


@pytest.fixture
def aws_session():
    _boto_session = Mock()
    _boto_session.region_name = RIGETTI_REGION

    creds = Mock()
    creds.method = "other"
    _boto_session.get_credentials.return_value = creds

    _aws_session = Mock()
    _aws_session.boto_session = _boto_session
    _aws_session._default_bucket = MOCK_DEFAULT_S3_DESTINATION_FOLDER[0]
    _aws_session.default_bucket.return_value = _aws_session._default_bucket
    _aws_session._custom_default_bucket = False
    _aws_session.account_id = "00000000"
    _aws_session.region = RIGETTI_REGION
    return _aws_session


@pytest.fixture
def device(aws_session):
    def _device(arn):
        aws_session.get_device.return_value = MOCK_GATE_MODEL_QPU_1
        aws_session.search_devices.return_value = [MOCK_GATE_MODEL_QPU_1]
        return AwsDevice(arn, aws_session)

    return _device


@pytest.mark.parametrize(
    "device_capabilities, get_device_data",
    [
        (MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES, MOCK_GATE_MODEL_SIMULATOR),
        (MOCK_GATE_MODEL_QPU_CAPABILITIES_1, MOCK_GATE_MODEL_QPU_1),
        (MOCK_DWAVE_QPU_CAPABILITIES, MOCK_DWAVE_QPU),
    ],
)
def test_device_aws_session(device_capabilities, get_device_data, arn):
    mock_session = Mock()
    mock_session.get_device.return_value = get_device_data
    mock_session.region = RIGETTI_REGION
    device = AwsDevice(arn, mock_session)
    _assert_device_fields(device, device_capabilities, get_device_data)


@patch("braket.aws.aws_device.AwsSession")
def test_device_simulator_no_aws_session(aws_session_init, aws_session):
    arn = SV1_ARN
    aws_session_init.return_value = aws_session
    aws_session.get_device.return_value = MOCK_GATE_MODEL_SIMULATOR
    device = AwsDevice(arn)
    _assert_device_fields(device, MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES, MOCK_GATE_MODEL_SIMULATOR)
    aws_session.get_device.assert_called_with(arn)


@patch("braket.aws.aws_device.AwsSession.copy_session")
@patch("braket.aws.aws_device.AwsSession")
@pytest.mark.parametrize(
    "get_device_side_effect",
    [
        [MOCK_GATE_MODEL_QPU_1],
        [
            ClientError(
                {
                    "Error": {
                        "Code": "ResourceNotFoundException",
                    }
                },
                "getDevice",
            ),
            MOCK_GATE_MODEL_QPU_1,
        ],
    ],
)
def test_device_qpu_no_aws_session(
    aws_session_init, mock_copy_session, get_device_side_effect, aws_session
):
    arn = RIGETTI_ARN
    mock_session = Mock()
    mock_session.get_device.side_effect = get_device_side_effect
    aws_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
            }
        },
        "getDevice",
    )
    aws_session_init.return_value = aws_session
    mock_copy_session.return_value = mock_session
    device = AwsDevice(arn)
    _assert_device_fields(device, MOCK_GATE_MODEL_QPU_CAPABILITIES_1, MOCK_GATE_MODEL_QPU_1)


@patch("braket.aws.aws_device.AwsSession.copy_session")
@patch("braket.aws.aws_device.AwsSession")
def test_regional_device_region_switch(aws_session_init, mock_copy_session, aws_session):
    device_region = "device-region"
    arn = f"arn:aws:braket:{device_region}::device/quantum-simulator/amazon/sim"
    aws_session_init.return_value = aws_session
    mock_session = Mock()
    mock_session.get_device.return_value = MOCK_GATE_MODEL_SIMULATOR
    mock_copy_session.return_value = mock_session
    device = AwsDevice(arn)
    aws_session.get_device.assert_not_called()
    mock_copy_session.assert_called_once()
    mock_copy_session.assert_called_with(aws_session, device_region)
    _assert_device_fields(device, MOCK_GATE_MODEL_SIMULATOR_CAPABILITIES, MOCK_GATE_MODEL_SIMULATOR)


@patch("braket.aws.aws_device.AwsSession")
@pytest.mark.parametrize(
    "get_device_side_effect, expected_exception",
    [
        (
            [
                ClientError(
                    {
                        "Error": {
                            "Code": "ResourceNotFoundException",
                        }
                    },
                    "getDevice",
                )
            ],
            ValueError,
        ),
        (
            [
                ClientError(
                    {
                        "Error": {
                            "Code": "ThrottlingException",
                        }
                    },
                    "getDevice",
                )
            ],
            ClientError,
        ),
    ],
)
def test_regional_device_raises_error(
    aws_session_init, get_device_side_effect, expected_exception, aws_session
):
    arn = "arn:aws:braket:us-west-1::device/quantum-simulator/amazon/sim"
    aws_session.get_device.side_effect = get_device_side_effect
    aws_session_init.return_value = aws_session
    with pytest.raises(expected_exception):
        AwsDevice(arn)
        aws_session.get_device.assert_called_once()


def test_device_refresh_metadata(arn):
    mock_session = Mock()
    mock_session.get_device.return_value = MOCK_GATE_MODEL_QPU_1
    mock_session.region = RIGETTI_REGION
    device = AwsDevice(arn, mock_session)
    _assert_device_fields(device, MOCK_GATE_MODEL_QPU_CAPABILITIES_1, MOCK_GATE_MODEL_QPU_1)

    mock_session.get_device.return_value = MOCK_GATE_MODEL_QPU_2
    device.refresh_metadata()
    _assert_device_fields(device, MOCK_GATE_MODEL_QPU_CAPABILITIES_2, MOCK_GATE_MODEL_QPU_2)


def test_equality(arn):
    mock_session = Mock()
    mock_session.get_device.return_value = MOCK_GATE_MODEL_QPU_1
    mock_session.region = RIGETTI_REGION
    device_1 = AwsDevice(arn, mock_session)
    device_2 = AwsDevice(arn, mock_session)
    other_device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/bar", mock_session)
    non_device = "HI"

    assert device_1 == device_2
    assert device_1 is not device_2
    assert device_1 != other_device
    assert device_1 != non_device


def test_repr(arn):
    mock_session = Mock()
    mock_session.get_device.return_value = MOCK_GATE_MODEL_QPU_1
    mock_session.region = RIGETTI_REGION
    device = AwsDevice(arn, mock_session)
    expected = "Device('name': {}, 'arn': {})".format(device.name, device.arn)
    assert repr(device) == expected


def test_device_simulator_not_found():
    mock_session = Mock()
    mock_session.region = "test-region-1"
    mock_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
                "Message": (
                    "Braket device 'arn:aws:braket:::device/quantum-simulator/amazon/tn1' "
                    "not found in us-west-1. You can find a list of all supported device "
                    "ARNs and the regions in which they are available in the documentation: "
                    "https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html"
                ),
            }
        },
        "getDevice",
    )
    simulator_not_found = (
        "Simulator 'arn:aws:braket:::device/simulator/a/b' not found in 'test-region-1'"
    )
    with pytest.raises(ValueError, match=simulator_not_found):
        AwsDevice("arn:aws:braket:::device/simulator/a/b", mock_session)


@patch("braket.aws.aws_device.AwsSession.copy_session")
def test_device_qpu_not_found(mock_copy_session):
    mock_session = Mock()
    mock_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
                "Message": (
                    "Braket device 'arn:aws:braket:::device/quantum-simulator/amazon/tn1' "
                    "not found in us-west-1. You can find a list of all supported device "
                    "ARNs and the regions in which they are available in the documentation: "
                    "https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html"
                ),
            }
        },
        "getDevice",
    )
    mock_copy_session.return_value = mock_session
    qpu_not_found = "QPU 'arn:aws:braket:::device/qpu/a/b' not found"
    with pytest.raises(ValueError, match=qpu_not_found):
        AwsDevice("arn:aws:braket:::device/qpu/a/b", mock_session)


@patch("braket.aws.aws_device.AwsSession.copy_session")
def test_device_qpu_exception(mock_copy_session):
    mock_session = Mock()
    mock_session.get_device.side_effect = (
        ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": (
                        "Braket device 'arn:aws:braket:::device/quantum-simulator/amazon/tn1' "
                        "not found in us-west-1. You can find a list of all supported device "
                        "ARNs and the regions in which they are available in the documentation: "
                        "https://docs.aws.amazon.com/braket/latest/developerguide/braket-"
                        "devices.html"
                    ),
                }
            },
            "getDevice",
        ),
        ClientError(
            {
                "Error": {
                    "Code": "OtherException",
                    "Message": "Some other message",
                }
            },
            "getDevice",
        ),
    )
    mock_copy_session.return_value = mock_session
    qpu_exception = (
        "An error occurred \\(OtherException\\) when calling the "
        "getDevice operation: Some other message"
    )
    with pytest.raises(ClientError, match=qpu_exception):
        AwsDevice("arn:aws:braket:::device/qpu/a/b", mock_session)


@patch("braket.aws.aws_device.AwsSession.copy_session")
def test_device_non_qpu_region_error(mock_copy_session):
    mock_session = Mock()
    mock_session.get_device.side_effect = ClientError(
        {
            "Error": {
                "Code": "ExpiredTokenError",
                "Message": ("Some other error that isn't ResourceNotFoundException"),
            }
        },
        "getDevice",
    )
    mock_copy_session.return_value = mock_session
    expired_token = (
        "An error occurred \\(ExpiredTokenError\\) when calling the getDevice operation: "
        "Some other error that isn't ResourceNotFoundException"
    )
    with pytest.raises(ClientError, match=expired_token):
        AwsDevice("arn:aws:braket:::device/qpu/a/b", mock_session)


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_no_extra(aws_quantum_task_mock, device, circuit):
    _run_and_assert(
        aws_quantum_task_mock,
        device,
        circuit,
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_positional_args(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    _run_and_assert(
        aws_quantum_task_mock, device, circuit, s3_destination_folder, 100, 86400, 0.25, ["foo"]
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_kwargs(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    _run_and_assert(
        aws_quantum_task_mock,
        device,
        circuit,
        s3_destination_folder,
        extra_kwargs={"bar": 1, "baz": 2},
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_shots(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    _run_and_assert(aws_quantum_task_mock, device, circuit, s3_destination_folder, 100)


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_shots_kwargs(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    _run_and_assert(
        aws_quantum_task_mock,
        device,
        circuit,
        s3_destination_folder,
        100,
        extra_kwargs={"bar": 1, "baz": 2},
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_qpu_no_shots(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    run_and_assert(
        aws_quantum_task_mock,
        device(RIGETTI_ARN),
        MOCK_DEFAULT_S3_DESTINATION_FOLDER,
        AwsDevice.DEFAULT_SHOTS_QPU,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        circuit,
        s3_destination_folder,
        None,
        None,
        None,
        None,
        None,
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_default_bucket_not_called(aws_quantum_task_mock, device, circuit, s3_destination_folder):
    device = device(RIGETTI_ARN)
    run_and_assert(
        aws_quantum_task_mock,
        device,
        MOCK_DEFAULT_S3_DESTINATION_FOLDER,
        AwsDevice.DEFAULT_SHOTS_QPU,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        circuit,
        s3_destination_folder,
        None,
        None,
        None,
        None,
        None,
    )
    device._aws_session.default_bucket.assert_not_called()


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_shots_poll_timeout_kwargs(
    aws_quantum_task_mock, device, circuit, s3_destination_folder
):
    _run_and_assert(
        aws_quantum_task_mock,
        device,
        circuit,
        s3_destination_folder,
        100,
        86400,
        extra_kwargs={"bar": 1, "baz": 2},
    )


@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_with_positional_args_and_kwargs(
    aws_quantum_task_mock, device, circuit, s3_destination_folder
):
    _run_and_assert(
        aws_quantum_task_mock,
        device,
        circuit,
        s3_destination_folder,
        100,
        86400,
        0.25,
        ["foo"],
        {"bar": 1, "baz": 2},
    )


@patch.dict(
    os.environ,
    {"AMZN_BRAKET_TASK_RESULTS_S3_URI": "s3://env_bucket/env/path"},
)
@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_env_variables(aws_quantum_task_mock, device, circuit, arn):
    device(arn).run(circuit)
    assert aws_quantum_task_mock.call_args_list[0][0][3] == ("env_bucket", "env/path")


@patch("braket.aws.aws_session.AwsSession")
@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_batch_no_extra(aws_quantum_task_mock, aws_session_mock, device, circuit):
    _run_batch_and_assert(
        aws_quantum_task_mock,
        aws_session_mock,
        device,
        [circuit for _ in range(10)],
    )


@patch("braket.aws.aws_session.AwsSession")
@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_batch_with_shots(
    aws_quantum_task_mock, aws_session_mock, device, circuit, s3_destination_folder
):
    _run_batch_and_assert(
        aws_quantum_task_mock,
        aws_session_mock,
        device,
        [circuit for _ in range(10)],
        s3_destination_folder,
        1000,
    )


@patch("braket.aws.aws_session.AwsSession")
@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_batch_with_max_parallel_and_kwargs(
    aws_quantum_task_mock, aws_session_mock, device, circuit, s3_destination_folder
):
    _run_batch_and_assert(
        aws_quantum_task_mock,
        aws_session_mock,
        device,
        [circuit for _ in range(10)],
        s3_destination_folder,
        1000,
        20,
        50,
        extra_kwargs={"bar": 1, "baz": 2},
    )


@patch.dict(
    os.environ,
    {"AMZN_BRAKET_TASK_RESULTS_S3_URI": "s3://env_bucket/env/path"},
)
@patch("braket.aws.aws_quantum_task.AwsQuantumTask.create")
def test_run_batch_env_variables(aws_quantum_task_mock, device, circuit, arn):
    device(arn).run_batch([circuit])
    assert aws_quantum_task_mock.call_args_list[0][0][3] == ("env_bucket", "env/path")


def _run_and_assert(
    aws_quantum_task_mock,
    device_factory,
    circuit,
    s3_destination_folder=None,  # Treated as positional arg
    shots=None,  # Treated as positional arg
    poll_timeout_seconds=None,  # Treated as positional arg
    poll_interval_seconds=None,  # Treated as positional arg
    extra_args=None,
    extra_kwargs=None,
):
    run_and_assert(
        aws_quantum_task_mock,
        device_factory("arn:aws:braket:::device/quantum-simulator/amazon/sim"),
        MOCK_DEFAULT_S3_DESTINATION_FOLDER,
        AwsDevice.DEFAULT_SHOTS_SIMULATOR,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        circuit,
        s3_destination_folder,
        shots,
        poll_timeout_seconds,
        poll_interval_seconds,
        extra_args,
        extra_kwargs,
    )


def _run_batch_and_assert(
    aws_quantum_task_mock,
    aws_session_mock,
    device_factory,
    circuits,
    s3_destination_folder=None,  # Treated as positional arg
    shots=None,  # Treated as positional arg
    max_parallel=None,  # Treated as positional arg
    max_connections=None,  # Treated as positional arg
    poll_timeout_seconds=None,  # Treated as a positional arg
    poll_interval_seconds=None,  # Treated as positional arg
    extra_args=None,
    extra_kwargs=None,
):
    run_batch_and_assert(
        aws_quantum_task_mock,
        aws_session_mock,
        device_factory("arn:aws:braket:::device/quantum-simulator/amazon/sim"),
        MOCK_DEFAULT_S3_DESTINATION_FOLDER,
        AwsDevice.DEFAULT_SHOTS_SIMULATOR,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        circuits,
        s3_destination_folder,
        shots,
        max_parallel,
        max_connections,
        poll_timeout_seconds,
        poll_interval_seconds,
        extra_args,
        extra_kwargs,
    )


def _assert_device_fields(device, expected_properties, expected_device_data):
    assert device.name == expected_device_data.get("deviceName")
    assert device.properties == expected_properties
    assert device.status == expected_device_data.get("deviceStatus")
    assert device.provider_name == expected_device_data.get("providerName")
    assert device.type == AwsDeviceType(expected_device_data.get("deviceType"))
    if device.topology_graph:
        assert device.topology_graph.edges == device._construct_topology_graph().edges


@patch("braket.aws.aws_device.AwsSession.copy_session")
def test_get_devices(mock_copy_session, aws_session):
    aws_session.search_devices.side_effect = [
        # us-west-1
        [
            {
                "deviceArn": SV1_ARN,
                "deviceName": "SV1",
                "deviceType": "SIMULATOR",
                "deviceStatus": "ONLINE",
                "providerName": "Amazon Braket",
            }
        ],
        ValueError("should not be reachable"),
    ]
    aws_session.get_device.side_effect = [
        MOCK_GATE_MODEL_SIMULATOR,
        ValueError("should not be reachable"),
    ]
    session_for_region = Mock()
    session_for_region.search_devices.side_effect = [
        # us-east-1
        [
            {
                "deviceArn": IONQ_ARN,
                "deviceName": "IonQ Device",
                "deviceType": "QPU",
                "deviceStatus": "ONLINE",
                "providerName": "IonQ",
            },
        ],
        # us-west-2
        [
            {
                "deviceArn": DWAVE_ARN,
                "deviceName": "Advantage_system1.1",
                "deviceType": "QPU",
                "deviceStatus": "ONLINE",
                "providerName": "D-Wave",
            },
            # Should not be reached because already instantiated in us-west-1
            {
                "deviceArn": SV1_ARN,
                "deviceName": "SV1",
                "deviceType": "SIMULATOR",
                "deviceStatus": "ONLINE",
                "providerName": "Amazon Braket",
            },
        ],
        # Only two regions to search outside of current
        ValueError("should not be reachable"),
    ]
    session_for_region.get_device.side_effect = [
        MOCK_DWAVE_QPU,
        MOCK_GATE_MODEL_QPU_2,
        ValueError("should not be reachable"),
    ]
    mock_copy_session.return_value = session_for_region
    # Search order: us-east-1, us-west-1, us-west-2
    results = AwsDevice.get_devices(
        arns=[SV1_ARN, DWAVE_ARN, IONQ_ARN],
        provider_names=["Amazon Braket", "D-Wave", "IonQ"],
        statuses=["ONLINE"],
        aws_session=aws_session,
    )
    assert [result.name for result in results] == ["Advantage_system1.1", "Blah", "SV1"]


@patch("braket.aws.aws_device.AwsSession.copy_session")
def test_get_devices_simulators_only(mock_copy_session, aws_session):
    aws_session.search_devices.side_effect = [
        [
            {
                "deviceArn": SV1_ARN,
                "deviceName": "SV1",
                "deviceType": "SIMULATOR",
                "deviceStatus": "ONLINE",
                "providerName": "Amazon Braket",
            }
        ],
        ValueError("should not be reachable"),
    ]
    aws_session.get_device.side_effect = [
        MOCK_GATE_MODEL_SIMULATOR,
        ValueError("should not be reachable"),
    ]
    session_for_region = Mock()
    session_for_region.search_devices.side_effect = ValueError("should not be reachable")
    session_for_region.get_device.side_effect = ValueError("should not be reachable")
    mock_copy_session.return_value = session_for_region
    results = AwsDevice.get_devices(
        arns=[SV1_ARN, TN1_ARN],
        types=["SIMULATOR"],
        provider_names=["Amazon Braket"],
        statuses=["ONLINE"],
        aws_session=aws_session,
    )
    # Only one region should be searched
    assert [result.name for result in results] == ["SV1"]


@pytest.mark.xfail(raises=ValueError)
def test_get_devices_invalid_order_by():
    AwsDevice.get_devices(order_by="foo")


@patch("braket.aws.aws_device.datetime")
def test_get_device_availability(mock_utc_now):
    class Expando(object):
        pass

    class MockDevice(AwsDevice):
        def __init__(self, status, *execution_window_args):
            self._status = status
            self._properties = Expando()
            self._properties.service = Expando()
            execution_windows = []
            for execution_day, window_start_hour, window_end_hour in execution_window_args:
                execution_windows.append(
                    DeviceExecutionWindow.parse_raw(
                        json.dumps(
                            {
                                "executionDay": execution_day,
                                "windowStartHour": window_start_hour,
                                "windowEndHour": window_end_hour,
                            }
                        )
                    )
                )
            self._properties.service.executionWindows = execution_windows

    test_sets = (
        {
            "test_devices": (
                ("always_on_device", MockDevice("ONLINE", ("Everyday", "00:00", "23:59:59"))),
                ("offline_device", MockDevice("OFFLINE", ("Everyday", "00:00", "23:59:59"))),
                ("retired_device", MockDevice("RETIRED", ("Everyday", "00:00", "23:59:59"))),
                ("missing_schedule_device", MockDevice("ONLINE")),
            ),
            "test_items": (
                (datetime(2021, 12, 6, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 7, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 8, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 9, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 10, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 11, 10, 0, 0), (1, 0, 0, 0)),
                (datetime(2021, 12, 12, 10, 0, 0), (1, 0, 0, 0)),
            ),
        },
        {
            "test_devices": (
                ("midday_everyday_device", MockDevice("ONLINE", ("Everyday", "07:00", "17:00"))),
                ("midday_weekday_device", MockDevice("ONLINE", ("Weekdays", "07:00", "17:00"))),
                ("midday_weekend_device", MockDevice("ONLINE", ("Weekend", "07:00", "17:00"))),
                ("evening_everyday_device", MockDevice("ONLINE", ("Everyday", "17:00", "07:00"))),
                ("evening_weekday_device", MockDevice("ONLINE", ("Weekdays", "17:00", "07:00"))),
                ("evening_weekend_device", MockDevice("ONLINE", ("Weekend", "17:00", "07:00"))),
            ),
            "test_items": (
                (datetime(2021, 12, 6, 5, 0, 0), (0, 0, 0, 1, 0, 1)),
                (datetime(2021, 12, 6, 10, 0, 0), (1, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 6, 20, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 7, 5, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 7, 10, 0, 0), (1, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 7, 20, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 8, 5, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 8, 10, 0, 0), (1, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 8, 20, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 9, 5, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 9, 10, 0, 0), (1, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 9, 20, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 10, 5, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 10, 10, 0, 0), (1, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 10, 20, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 11, 5, 0, 0), (0, 0, 0, 1, 1, 0)),
                (datetime(2021, 12, 11, 10, 0, 0), (1, 0, 1, 0, 0, 0)),
                (datetime(2021, 12, 11, 20, 0, 0), (0, 0, 0, 1, 0, 1)),
                (datetime(2021, 12, 12, 5, 0, 0), (0, 0, 0, 1, 0, 1)),
                (datetime(2021, 12, 12, 10, 0, 0), (1, 0, 1, 0, 0, 0)),
                (datetime(2021, 12, 12, 20, 0, 0), (0, 0, 0, 1, 0, 1)),
            ),
        },
        {
            "test_devices": (
                ("monday_device", MockDevice("ONLINE", ("Monday", "07:00", "17:00"))),
                ("tuesday_device", MockDevice("ONLINE", ("Tuesday", "07:00", "17:00"))),
                ("wednesday_device", MockDevice("ONLINE", ("Wednesday", "07:00", "17:00"))),
                ("thursday_device", MockDevice("ONLINE", ("Thursday", "07:00", "17:00"))),
                ("friday_device", MockDevice("ONLINE", ("Friday", "07:00", "17:00"))),
                ("saturday_device", MockDevice("ONLINE", ("Saturday", "07:00", "17:00"))),
                ("sunday_device", MockDevice("ONLINE", ("Sunday", "07:00", "17:00"))),
                (
                    "monday_friday_device",
                    MockDevice(
                        "ONLINE", ("Monday", "07:00", "17:00"), ("Friday", "07:00", "17:00")
                    ),
                ),
            ),
            "test_items": (
                (datetime(2021, 12, 6, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 6, 10, 0, 0), (1, 0, 0, 0, 0, 0, 0, 1)),
                (datetime(2021, 12, 6, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 7, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 7, 10, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 7, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 8, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 8, 10, 0, 0), (0, 0, 1, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 8, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 9, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 9, 10, 0, 0), (0, 0, 0, 1, 0, 0, 0, 0)),
                (datetime(2021, 12, 9, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 10, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 10, 10, 0, 0), (0, 0, 0, 0, 1, 0, 0, 1)),
                (datetime(2021, 12, 10, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 11, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 11, 10, 0, 0), (0, 0, 0, 0, 0, 1, 0, 0)),
                (datetime(2021, 12, 11, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 12, 5, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
                (datetime(2021, 12, 12, 10, 0, 0), (0, 0, 0, 0, 0, 0, 1, 0)),
                (datetime(2021, 12, 12, 20, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
            ),
        },
    )

    for test_set in test_sets:
        for test_item in test_set["test_items"]:
            test_date = test_item[0]
            mock_utc_now.utcnow.return_value = test_date

            # flake8: noqa: C501
            for i in range(len(test_item[1])):
                device_name = test_set["test_devices"][i][0]
                device = test_set["test_devices"][i][1]
                expected = bool(test_item[1][i])
                actual = device.is_available
                assert (
                    expected == actual
                ), f"device_name: {device_name}, test_date: {test_date}, expected: {expected}, actual: {actual}"
