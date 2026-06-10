import json
import tarfile


QUEUE_INFO = [
    {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
    {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
    {"queue": "JOBS_QUEUE", "queueSize": "0"},
]

SV1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
ANKAA_3_ARN = "arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3"
GARNET_ARN = "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet"
EMERALD_ARN = "arn:aws:braket:eu-north-1::device/qpu/iqm/Emerald"
ARIA_1_ARN = "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1"

DEVICE_SUMMARIES = [
    {
        "deviceArn": ANKAA_3_ARN,
        "deviceName": "Ankaa-3",
        "deviceType": "QPU",
        "deviceStatus": "ONLINE",
        "providerName": "Rigetti",
    },
    {
        "deviceArn": GARNET_ARN,
        "deviceName": "Garnet",
        "deviceType": "QPU",
        "deviceStatus": "ONLINE",
        "providerName": "IQM",
    },
    {
        "deviceArn": ARIA_1_ARN,
        "deviceName": "Aria 1",
        "deviceType": "QPU",
        "deviceStatus": "ONLINE",
        "providerName": "IonQ",
    },
    {
        "deviceArn": SV1_ARN,
        "deviceName": "SV1",
        "deviceType": "SIMULATOR",
        "deviceStatus": "ONLINE",
        "providerName": "Amazon Braket",
    },
]


def configure_qiskit_devices(mock_utils, mocker):
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_search_result([{"devices": DEVICE_SUMMARIES}])
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))
    mocker._wrapper.boto_client.get_device.side_effect = lambda *args, **kwargs: device_response(
        mock_utils,
        kwargs.get("deviceArn", args[0] if args else SV1_ARN),
    )


def device_response(mock_utils, arn):
    if arn == SV1_ARN or "quantum-simulator/amazon/sv1" in arn:
        return _response(mock_utils, arn, "SV1", "SIMULATOR", "Amazon Braket", "default_capabilities.json")
    if arn == EMERALD_ARN or arn == GARNET_ARN or "/iqm/" in arn:
        name = "Emerald" if "Emerald" in arn else "Garnet"
        return _response(mock_utils, arn, name, "QPU", "IQM", "iqm_garnet_device_capabilities.json")
    if arn == ANKAA_3_ARN or "/rigetti/" in arn:
        return _response(mock_utils, arn, "Ankaa-3", "QPU", "Rigetti", "rigetti_device_capabilities.json")
    if arn == ARIA_1_ARN or "/ionq/" in arn:
        return _response(
            mock_utils,
            arn,
            "Aria 1",
            "QPU",
            "IonQ",
            "ionq_forte_enterprise_device_capabilities.json",
        )
    return _response(mock_utils, arn, "Test Device", "QPU", "Test Provider", "default_capabilities.json")


def _response(mock_utils, arn, name, device_type, provider_name, capabilities_file):
    return {
        "deviceArn": arn,
        "deviceName": name,
        "deviceType": device_type,
        "deviceStatus": "ONLINE",
        "providerName": provider_name,
        "deviceCapabilities": mock_utils.read_file(capabilities_file),
        "deviceQueueInfo": QUEUE_INFO,
    }


def write_plaintext_job_results(results):
    payload = {
        "braketSchemaHeader": {
            "name": "braket.jobs_data.persisted_job_data",
            "version": "1",
        },
        "dataDictionary": results,
        "dataFormat": "plaintext",
    }
    with open("results.json", "w") as f:
        json.dump(payload, f)
    with tarfile.open("model.tar.gz", "w:gz") as tar:
        tar.add("results.json")
