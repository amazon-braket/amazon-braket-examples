# Copyright 2019-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import boto3
import pytest
from botocore.exceptions import ClientError
from braket.aws.aws_session import AwsSession


@pytest.fixture(scope="session")
def boto_session():
    profile_name = os.environ["AWS_PROFILE"]
    return boto3.session.Session(profile_name=profile_name)


@pytest.fixture(scope="session")
def region(boto_session):
    return boto_session.region_name


@pytest.fixture(scope="session")
def aws_session(boto_session):
    return AwsSession(boto_session)


@pytest.fixture(scope="session")
def s3_resource(boto_session):
    return boto_session.resource("s3")


@pytest.fixture(scope="session")
def s3_client(boto_session):
    return boto_session.client("s3")


@pytest.fixture(scope="session")
def account_id(boto_session):
    return boto_session.client("sts").get_caller_identity()["Account"]


@pytest.fixture(scope="session")
def s3_bucket(s3_resource, s3_client, account_id, boto_session):
    """Create / get S3 bucket for tests"""

    region_name = boto_session.region_name
    bucket_name = f"amazon-braket-notebook-tests-{account_id}"
    bucket = s3_resource.Bucket(bucket_name)

    try:
        # Determine if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            bucket.create(
                ACL="private",
                CreateBucketConfiguration={"LocationConstraint": region_name},
            )

    return bucket_name


@pytest.fixture(scope="module")
def s3_destination_folder(s3_bucket, s3_prefix):
    return (s3_bucket, s3_prefix)
