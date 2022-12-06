import os


def pre_run(mock_utils):
    mocker = mock_utils.Mocker()
    mocker.set_get_device_result({
        "deviceType" : "QPU",
        "deviceCapabilities" : mock_utils.load_json("default_capabilities.json")
    })
    mocker.set_create_quantum_task_result({
        "quantumTaskArn" : "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
    })
    mocker.set_get_quantum_task_result({
        "quantumTaskArn" : "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
        "status" : "COMPLETED",
        "outputS3Bucket" : "Test Bucket",
        "outputS3Directory" : "Test Directory",
        "shots": 10,
        "deviceArn": "Test Device Arn",
        "ResponseMetadata": {
            "HTTPHeaders": {
                "date" : ""
            }
        }
    })
    mocker.set_cancel_quantum_task_result({
        "cancellationStatus": "CANCELLING",
    })
    mocker.set_task_result_return(mock_utils.load_json("default_results.json"))


def post_run(tb):
    log_file = tb.ref("log_file")
    os.remove(log_file)
