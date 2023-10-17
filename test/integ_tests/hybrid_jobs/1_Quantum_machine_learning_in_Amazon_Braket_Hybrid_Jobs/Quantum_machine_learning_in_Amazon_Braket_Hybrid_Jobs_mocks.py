import sys
import tarfile
from itertools import cycle
from unittest.mock import patch

import numpy as np
from braket.jobs_data import PersistedJobData, PersistedJobDataFormat

from braket.jobs.serialization import serialize_values

mock_cloudpickle = patch('cloudpickle.dumps', return_value='serialize')


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_search_result([
        {
            "Roles": [
                {
                    "RoleName": "AmazonBraketJobsExecutionRole",
                    "Arn": "TestRoleARN"
                }
            ]
        }
    ])
    mocker.set_create_job_result({
        "jobArn": f"arn:aws:braket:{mocker.region_name}:000000:job/testJob"
    })
    mocker.set_get_job_result({
        "instanceConfig": {
            "instanceCount": 1
        },
        "jobName": "testJob",
        "status": "COMPLETED",
        "outputDataConfig": {
            "s3Path": "s3://amazon-br-invalid-path/test-path/test-results"
        }
    })
    mocker.set_log_streams_result({
        "logStreams": []
    })
    mocker.set_start_query_result({
        "queryId": "TestId"
    })
    mocker.set_get_query_results_result({
        "status": "Complete",
        "results": [
            [
                {"field": "@message", "value": "iteration_number=0;loss=0;"},
                {"field": "@timestamp", "value": "0"}
            ],
        ]
    })
    mocker.set_batch_get_image_side_effect(
        cycle([
            {"images": [{"imageId": {"imageDigest": "my-digest"}}]},
            {
                "images": [
                    {"imageId": {"imageTag": f"-py3{sys.version_info.minor}-"}},
                ]
            },
        ])
    )
    default_job_results = {
        'params': np.array(
            [
                0.77996265, 0.52813787, 0.61299074, -0.09124156, 0.17680213,
                -0.02222335, 0.91524364, -0.31786518, 0.64940861, 0.62663773,
                0.87611417, -0.0715285, -0.00379581, 1.04400452, 0.20672916,
                0.94888017, 0.55607485, 1.03805133, 1.08456977, -0.75108754,
                1.13637642, 0.72634854, 0.93536659, 0.17868376, 0.79434158,
                0.05315669, 0.81228023, -0.62405866, 0.10342629, -0.8736394
            ]
        ),
        'task summary': {},
        'estimated cost': 0.0,
    }

    with open("results.json", "w") as f:
        serialized_data = serialize_values(default_job_results, PersistedJobDataFormat.PICKLED_V4)
        persisted_data = PersistedJobData(
            dataDictionary=serialized_data,
            dataFormat=PersistedJobDataFormat.PICKLED_V4,
        )
        f.write(persisted_data.json())
    with tarfile.open("model.tar.gz", "w:gz") as tar:
        tar.add("results.json")
    mock_cloudpickle.start()


def post_run(tb):
    tb.inject(
        """
        import os
        os.remove("model.tar.gz")
        os.remove("results.json")
        """
    )
    mock_cloudpickle.stop()
