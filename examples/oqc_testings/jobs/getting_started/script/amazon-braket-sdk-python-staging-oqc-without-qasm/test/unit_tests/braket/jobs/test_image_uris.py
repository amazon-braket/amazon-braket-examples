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

from braket.jobs.image_uris import Framework, retrieve_image


@pytest.mark.parametrize(
    "region, framework, expected_uri",
    [
        (
            "us-west-1",
            Framework.BASE,
            "292282985366.dkr.ecr.us-west-1.amazonaws.com/"
            "amazon-braket-base-jobs:1.0-cpu-py37-ubuntu18.04",
        ),
        (
            "us-east-1",
            Framework.PL_TENSORFLOW,
            "292282985366.dkr.ecr.us-east-1.amazonaws.com/amazon-braket-tensorflow-jobs:"
            "2.4.1-cpu-py37-ubuntu18.04",
        ),
        (
            "us-west-2",
            Framework.PL_PYTORCH,
            "292282985366.dkr.ecr.us-west-2.amazonaws.com/"
            "amazon-braket-pytorch-jobs:1.8.1-cpu-py37-ubuntu18.04",
        ),
    ],
)
def test_retrieve_image_default_version(region, framework, expected_uri):
    assert retrieve_image(framework, region) == expected_uri


@pytest.mark.parametrize(
    "region, framework",
    [
        ("eu-west-1", Framework.BASE),
        (None, Framework.BASE),
        ("us-west-1", None),
        ("us-west-1", "foo"),
    ],
)
@pytest.mark.xfail(raises=ValueError)
def test_retrieve_image_incorrect_input(region, framework):
    retrieve_image(framework, region)
