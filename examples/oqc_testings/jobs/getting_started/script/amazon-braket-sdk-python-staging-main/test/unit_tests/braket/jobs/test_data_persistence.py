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

import json
import os
import tempfile
from dataclasses import dataclass
from unittest.mock import patch

import numpy as np
import pytest

from braket.jobs.data_persistence import load_job_checkpoint, save_job_checkpoint, save_job_result
from braket.jobs_data import PersistedJobDataFormat


@pytest.mark.parametrize(
    "job_name, file_suffix, data_format, checkpoint_data, expected_saved_data",
    [
        (
            "job_plaintext_simple_dict",
            "",
            PersistedJobDataFormat.PLAINTEXT,
            {"converged": True, "energy": -0.2},
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {"converged": True, "energy": -0.2},
                    "dataFormat": "plaintext",
                }
            ),
        ),
        (
            "job_pickled_simple_dict",
            "suffix1",
            PersistedJobDataFormat.PICKLED_V4,
            {"converged": True, "energy": -0.2},
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {
                        "converged": "gASILg==\n",
                        "energy": "gASVCgAAAAAAAABHv8mZmZmZmZou\n",
                    },
                    "dataFormat": "pickled_v4",
                }
            ),
        ),
    ],
)
def test_save_job_checkpoint(
    job_name, file_suffix, data_format, checkpoint_data, expected_saved_data
):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            save_job_checkpoint(checkpoint_data, file_suffix, data_format)

        expected_file_location = (
            f"{tmp_dir}/{job_name}_{file_suffix}.json"
            if file_suffix
            else f"{tmp_dir}/{job_name}.json"
        )
        with open(expected_file_location, "r") as expected_file:
            assert expected_file.read() == expected_saved_data


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("checkpoint_data", [{}, None])
def test_save_job_checkpoint_raises_error_empty_data(checkpoint_data):
    job_name = "foo"
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            save_job_checkpoint(checkpoint_data)


@pytest.mark.parametrize(
    "job_name, file_suffix, data_format, saved_data, expected_checkpoint_data",
    [
        (
            "job_plaintext_simple_dict",
            "",
            PersistedJobDataFormat.PLAINTEXT,
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {"converged": True, "energy": -0.2},
                    "dataFormat": "plaintext",
                }
            ),
            {"converged": True, "energy": -0.2},
        ),
        (
            "job_pickled_simple_dict",
            "",
            PersistedJobDataFormat.PICKLED_V4,
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {
                        "converged": "gASILg==\n",
                        "energy": "gASVCgAAAAAAAABHv8mZmZmZmZou\n",
                    },
                    "dataFormat": "pickled_v4",
                }
            ),
            {"converged": True, "energy": -0.2},
        ),
    ],
)
def test_load_job_checkpoint(
    job_name, file_suffix, data_format, saved_data, expected_checkpoint_data
):
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = (
            f"{tmp_dir}/{job_name}_{file_suffix}.json"
            if file_suffix
            else f"{tmp_dir}/{job_name}.json"
        )
        with open(file_path, "w") as f:
            f.write(saved_data)

        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            loaded_data = load_job_checkpoint(job_name, file_suffix)
            assert loaded_data == expected_checkpoint_data


@pytest.mark.xfail(raises=FileNotFoundError)
def test_load_job_checkpoint_raises_error_file_not_exists():
    job_name = "old_job"
    file_suffix = "correct_suffix"
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = f"{tmp_dir}/{job_name}_{file_suffix}.json"
        with open(file_path, "w") as _:
            pass

        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            load_job_checkpoint(job_name, "wrong_suffix")


@pytest.mark.xfail(raises=ValueError)
def test_load_job_checkpoint_raises_error_corrupted_data():
    job_name = "old_job_corrupted_data"
    file_suffix = "foo"
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = f"{tmp_dir}/{job_name}_{file_suffix}.json"
        with open(file_path, "w") as corrupted_file:
            corrupted_file.write(
                json.dumps(
                    {
                        "braketSchemaHeader": {
                            "name": "braket.jobs_data.persisted_job_data",
                            "version": "1",
                        },
                        "dataDictionary": {
                            "converged": "gASILg==\n",
                            "energy": "gASVCgBHv--corrupted---\n",
                        },
                        "dataFormat": "pickled_v4",
                    }
                )
            )

        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            load_job_checkpoint(job_name, file_suffix)


@dataclass
class CustomClassToPersist:
    float_val: float
    str_val: str
    bool_val: bool


def test_save_and_load_job_checkpoint():
    with tempfile.TemporaryDirectory() as tmp_dir:
        job_name = "job_name_1"
        data = {
            "np_array": np.array([1]),
            "custom_class": CustomClassToPersist(3.4, "str", True),
            "none_value": None,
            "nested_dict": {"a": {"b": False}},
        }
        with patch.dict(
            os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir, "AMZN_BRAKET_JOB_NAME": job_name}
        ):
            save_job_checkpoint(data, data_format=PersistedJobDataFormat.PICKLED_V4)
            retrieved = load_job_checkpoint(job_name)
            assert retrieved == data


@pytest.mark.parametrize(
    "data_format, result_data, expected_saved_data",
    [
        (
            PersistedJobDataFormat.PLAINTEXT,
            {"converged": True, "energy": -0.2},
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {"converged": True, "energy": -0.2},
                    "dataFormat": "plaintext",
                }
            ),
        ),
        (
            PersistedJobDataFormat.PICKLED_V4,
            {"converged": True, "energy": -0.2},
            json.dumps(
                {
                    "braketSchemaHeader": {
                        "name": "braket.jobs_data.persisted_job_data",
                        "version": "1",
                    },
                    "dataDictionary": {
                        "converged": "gASILg==\n",
                        "energy": "gASVCgAAAAAAAABHv8mZmZmZmZou\n",
                    },
                    "dataFormat": "pickled_v4",
                }
            ),
        ),
    ],
)
def test_save_job_result(data_format, result_data, expected_saved_data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(os.environ, {"AMZN_BRAKET_JOB_RESULTS_DIR": tmp_dir}):
            save_job_result(result_data, data_format)

        expected_file_location = f"{tmp_dir}/results.json"
        with open(expected_file_location, "r") as expected_file:
            assert expected_file.read() == expected_saved_data


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("result_data", [{}, None])
def test_save_job_result_raises_error_empty_data(result_data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(os.environ, {"AMZN_BRAKET_CHECKPOINT_DIR": tmp_dir}):
            save_job_result(result_data)
