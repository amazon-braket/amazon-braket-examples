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

from setuptools import find_namespace_packages, setup


setup(
    name="amazon-braket-examples",
    version = "1.0.0",
    author="Amazon Web Services",
    license="Apache License 2.0",
    python_requires=">= 3.8.2",
    url="https://github.com/aws/amazon-braket-examples",
    description=(
        "The primary repository for Amazon Braket tutorials"
    ),
    keywords="Amazon AWS Quantum",
)
