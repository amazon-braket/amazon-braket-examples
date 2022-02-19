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

import pytest

TEST_S3_OBJ_CONTENTS = {
    "TaskMetadata": {
        "Id": "blah",
        "Status": "COMPLETED",
    }
}


@pytest.fixture()
def s3_key(s3_resource, s3_bucket, s3_prefix):
    obj = s3_resource.Object(s3_bucket, f"{s3_prefix}/test_task_reading.json")

    try:
        obj_body = obj.get()["Body"].read().decode("utf-8")
        assert obj_body == json.dumps(TEST_S3_OBJ_CONTENTS)
    except s3_resource.meta.client.exceptions.NoSuchKey:
        # Put s3 object
        obj.put(ACL="private", Body=json.dumps(TEST_S3_OBJ_CONTENTS, indent=4))
    except AssertionError:
        # Put s3 object
        obj.put(ACL="private", Body=json.dumps(TEST_S3_OBJ_CONTENTS, indent=4))

    return obj.key


def test_retrieve_s3_object_body(aws_session, s3_bucket, s3_key):
    obj_body = aws_session.retrieve_s3_object_body(s3_bucket, s3_key)
    assert obj_body == json.dumps(TEST_S3_OBJ_CONTENTS, indent=4)
