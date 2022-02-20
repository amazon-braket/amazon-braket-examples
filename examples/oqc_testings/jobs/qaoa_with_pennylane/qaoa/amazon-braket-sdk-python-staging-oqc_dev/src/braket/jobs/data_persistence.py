# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import os
from typing import Any, Dict

from braket.jobs.serialization import deserialize_values, serialize_values
from braket.jobs_data import PersistedJobData, PersistedJobDataFormat


def save_job_checkpoint(
    checkpoint_data: Dict[str, Any],
    checkpoint_file_suffix: str = "",
    data_format: PersistedJobDataFormat = PersistedJobDataFormat.PLAINTEXT,
) -> None:
    """
    Saves the specified `checkpoint_data` to the local output directory, specified by the container
    environment variable `CHECKPOINT_DIR`, with the filename
    `f"{job_name}(_{checkpoint_file_suffix}).json"`. The `job_name` refers to the name of the
    current job and is retrieved from the container environment variable `JOB_NAME`. The
    `checkpoint_data` values are serialized to the specified `data_format`.

    Note: This function for storing the checkpoints is only for use inside the job container
          as it writes data to directories and references env variables set in the containers.


    Args:
        checkpoint_data (Dict[str, Any]): Dict that specifies the checkpoint data to be persisted.
        checkpoint_file_suffix (str): str that specifies the file suffix to be used for
            the checkpoint filename. The resulting filename
            `f"{job_name}(_{checkpoint_file_suffix}).json"` is used to save the checkpoints.
             Default: ""
        data_format (PersistedJobDataFormat): The data format used to serialize the
            values. Note that for `PICKLED` data formats, the values are base64 encoded
            after serialization. Default: PersistedJobDataFormat.PLAINTEXT

    Raises:
        ValueError: If the supplied `checkpoint_data` is `None` or empty.
    """
    if not checkpoint_data:
        raise ValueError("The checkpoint_data argument cannot be empty.")
    checkpoint_directory = os.environ["AMZN_BRAKET_CHECKPOINT_DIR"]
    job_name = os.environ["AMZN_BRAKET_JOB_NAME"]
    checkpoint_file_path = (
        f"{checkpoint_directory}/{job_name}_{checkpoint_file_suffix}.json"
        if checkpoint_file_suffix
        else f"{checkpoint_directory}/{job_name}.json"
    )
    with open(checkpoint_file_path, "w") as f:
        serialized_data = serialize_values(checkpoint_data or {}, data_format)
        persisted_data = PersistedJobData(dataDictionary=serialized_data, dataFormat=data_format)
        f.write(persisted_data.json())


def load_job_checkpoint(job_name: str, checkpoint_file_suffix: str = "") -> Dict[str, Any]:
    """
    Loads the job checkpoint data stored for the job named 'job_name', with the checkpoint
    file that ends with the `checkpoint_file_suffix`. The `job_name` can refer to any job whose
    checkpoint data you expect to be available in the file path specified by the `CHECKPOINT_DIR`
    container environment variable.

    Note: This function for loading job checkpoints is only for use inside the job container
          as it writes data to directories and references env variables set in the containers.


    Args:
        job_name (str): str that specifies the name of the job whose checkpoints
            are to be loaded.
        checkpoint_file_suffix (str): str specifying the file suffix that is used to
            locate the checkpoint file to load. The resulting file name
            `f"{job_name}(_{checkpoint_file_suffix}).json"` is used to locate the
            checkpoint file. Default: ""

    Returns:
        Dict[str, Any]: Dict that contains the checkpoint data persisted in the checkpoint file.

    Raises:
        FileNotFoundError: If the file `f"{job_name}(_{checkpoint_file_suffix})"` could not be found
            in the directory specified by the container environment variable `CHECKPOINT_DIR`.
        ValueError: If the data stored in the checkpoint file can't be deserialized (possibly due to
            corruption).
    """
    checkpoint_directory = os.environ["AMZN_BRAKET_CHECKPOINT_DIR"]
    checkpoint_file_path = (
        f"{checkpoint_directory}/{job_name}_{checkpoint_file_suffix}.json"
        if checkpoint_file_suffix
        else f"{checkpoint_directory}/{job_name}.json"
    )
    with open(checkpoint_file_path, "r") as f:
        persisted_data = PersistedJobData.parse_raw(f.read())
        deserialized_data = deserialize_values(
            persisted_data.dataDictionary, persisted_data.dataFormat
        )
        return deserialized_data


def save_job_result(
    result_data: Dict[str, Any],
    data_format: PersistedJobDataFormat = PersistedJobDataFormat.PLAINTEXT,
) -> None:
    """
    Saves the `result_data` to the local output directory that is specified by the container
    environment variable `OUTPUT_DIR`, with the filename 'results.json'. The `result_data`
    values are serialized to the specified `data_format`.

    Note: This function for storing the results is only for use inside the job container
          as it writes data to directories and references env variables set in the containers.


    Args:
        result_data (Dict[str, Any]): Dict that specifies the result data to be persisted.
        data_format (PersistedJobDataFormat): The data format used to serialize the
            values. Note that for `PICKLED` data formats, the values are base64 encoded
            after serialization. Default: PersistedJobDataFormat.PLAINTEXT.

    Raises:
        ValueError: If the supplied `result_data` is `None` or empty.
    """
    if not result_data:
        raise ValueError("The result_data argument cannot be empty.")
    result_directory = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]
    result_path = f"{result_directory}/results.json"
    with open(result_path, "w") as f:
        serialized_data = serialize_values(result_data or {}, data_format)
        persisted_data = PersistedJobData(dataDictionary=serialized_data, dataFormat=data_format)
        f.write(persisted_data.json())
