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


import pytest

from braket.jobs.serialization import deserialize_values, serialize_values
from braket.jobs_data import PersistedJobDataFormat


@pytest.mark.parametrize(
    "data_format, submitted_data, expected_serialized_data",
    [
        (
            PersistedJobDataFormat.PLAINTEXT,
            {"converged": True, "energy": -0.2},
            {"converged": True, "energy": -0.2},
        ),
        (
            PersistedJobDataFormat.PICKLED_V4,
            {"converged": True, "energy": -0.2},
            {"converged": "gASILg==\n", "energy": "gASVCgAAAAAAAABHv8mZmZmZmZou\n"},
        ),
    ],
)
def test_job_serialize_data(data_format, submitted_data, expected_serialized_data):
    serialized_data = serialize_values(submitted_data, data_format)
    assert serialized_data == expected_serialized_data


@pytest.mark.parametrize(
    "data_format, submitted_data, expected_deserialized_data",
    [
        (
            PersistedJobDataFormat.PLAINTEXT,
            {"converged": True, "energy": -0.2},
            {"converged": True, "energy": -0.2},
        ),
        (
            PersistedJobDataFormat.PICKLED_V4,
            {"converged": "gASILg==\n", "energy": "gASVCgAAAAAAAABHv8mZmZmZmZou\n"},
            {"converged": True, "energy": -0.2},
        ),
    ],
)
def test_job_deserialize_data(data_format, submitted_data, expected_deserialized_data):
    deserialized_data = deserialize_values(submitted_data, data_format)
    assert deserialized_data == expected_deserialized_data
