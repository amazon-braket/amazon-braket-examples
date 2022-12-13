

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_quantum_task_result({
        "quantumTaskArn" : "arn:aws:braket:us-west-2:000000:quantum-task/TestARN",
        "status" : "COMPLETED",
        "outputS3Bucket" : "Test Bucket",
        "outputS3Directory" : "Test Directory",
        "shots": 10,
        "deviceArn": "Test Device Arn",
        "failureReason": "Test",
        "ResponseMetadata": {
            "HTTPHeaders": {
                "date": ""
            }
        }
    })


def post_run(tb):
    pass