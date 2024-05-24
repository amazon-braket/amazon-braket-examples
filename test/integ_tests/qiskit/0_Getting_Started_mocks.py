from qiskit import user_config


def pre_run_inject(mock_utils):
    qiskit_config = user_config.get_config()
    if qiskit_config:
        user_config.set_config("circuit_drawer", "text")

    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
        "deviceCapabilities": mock_utils.read_file("rig_pulse_device_capabilities.json", __file__),
        "deviceName": "SV1",
        "deviceQueueInfo": [
            {
            "queue": "QUANTUM_TASKS_QUEUE",
            "queuePriority": "Normal",
            "queueSize": "0"
            },
            {
            "queue": "QUANTUM_TASKS_QUEUE",
            "queuePriority": "Priority",
            "queueSize": "0"
            },
            {
            "queue": "JOBS_QUEUE",
            "queueSize": "0"
            }
        ],
        "deviceStatus": "ONLINE",
        "deviceType": "SIMULATOR",
        "providerName": "Amazon Braket"
    })
    mocker.set_get_device_result({
        "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
        "deviceCapabilities": mock_utils.read_file("rig_pulse_device_capabilities.json", __file__),
        "deviceName": "dm1",
        "deviceQueueInfo": [
            {
            "queue": "QUANTUM_TASKS_QUEUE",
            "queuePriority": "Normal",
            "queueSize": "0"
            },
            {
            "queue": "QUANTUM_TASKS_QUEUE",
            "queuePriority": "Priority",
            "queueSize": "0"
            },
            {
            "queue": "JOBS_QUEUE",
            "queueSize": "0"
            }
        ],
        "deviceStatus": "ONLINE",
        "deviceType": "SIMULATOR",
        "providerName": "Amazon Braket"
    })
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "deviceCapabilities" : mock_utils.read_file("rig_pulse_device_capabilities.json", __file__)
    })
    # get_devices device is based on arns
    mocker.set_search_result([
        {
            "devices": [
                {
                    "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
                    "deviceName": "SV1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Amazon Braket"
                },
                {
                    "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
                    "deviceName": "dm1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Amazon Braket"
                },
                {
                    "deviceArn": "arn:aws:braket:::device/quantum-simluator/amazon/tn1",
                    "deviceName": "TN1",
                    "deviceType": "SIMULATOR",
                    "deviceStatus": "ONLINE",
                    "providerName": "Amazon Braket"
                },
                {
                    "deviceArn": "arn:aws:braket:us-west-2::device/qpu/arn/TestARN",
                    "deviceName": "Aspen-M-3",
                    "deviceType": "QPU",
                    "deviceStatus": "ONLINE",
                    "providerName": "Test Provider"
                }
            ]
        }
    ])


def post_run(tb):
    pass
