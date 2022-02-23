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

import pytest
from jsonschema import validate
from pydantic import ValidationError

from braket.jobs_data.persisted_job_data_v1 import PersistedJobData, PersistedJobDataFormat


def test_persisted_job_data_fields():
    data_dict = {"key_1": "value_1", "iterations": 2, "more_keys": True}
    data_format = PersistedJobDataFormat.PLAINTEXT
    persisted = PersistedJobData(dataDictionary=data_dict, dataFormat=data_format)
    assert persisted.dataDictionary == data_dict
    assert persisted.dataFormat == data_format


@pytest.mark.xfail(raises=ValidationError)
def test_persisted_job_data_missing_data_format():
    PersistedJobData(dataDictionary={"a": 1})


@pytest.mark.xfail(raises=ValidationError)
def test_persisted_job_data_missing_data_dictionary():
    PersistedJobData(dataFormat=PersistedJobDataFormat.PLAINTEXT)


def test_json_validates_against_schema():
    persisted_job_data = PersistedJobData(
        dataDictionary={"a": 1}, dataFormat=PersistedJobDataFormat.PLAINTEXT
    )
    validate(json.loads(persisted_job_data.json()), persisted_job_data.schema())


def test_persisted_job_data_parses_json():
    json_str = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.jobs_data.persisted_job_data",
                "version": "1",
            },
            "dataDictionary": {"converged": True, "energy": -0.2},
            "dataFormat": "plaintext",
        }
    )
    persisted_data = PersistedJobData.parse_raw(json_str)
    assert persisted_data.dataDictionary == {"converged": True, "energy": -0.2}
    assert persisted_data.dataFormat == PersistedJobDataFormat.PLAINTEXT
