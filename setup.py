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

from setuptools import find_namespace_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="amazon-braket-examples",
    license="Apache License 2.0",
    python_requires=">= 3.7",
    packages=find_namespace_packages(where="examples", exclude=("tests",)),
    package_dir={"": "examples"},
    install_requires=[
        "ipykernel",
        "boto3",
        "amazon-braket-sdk",
        "amazon-braket-default-simulator",
        "dwave-ocean-sdk",
        "amazon-braket-ocean-plugin",
        "amazon-braket-pennylane-plugin",
        "amazon-braket-schemas",
        "PennyLane",
    ],
    extras_require={
        "test": [
            "black",
            "flake8",
            "nbconvert",
            "isort",
            "pre-commit",
            "pylint",
            "pytest",
            "pytest-cov",
            "pytest-rerunfailures",
            "pytest-xdist",
            "tox",
        ]
    },
)
