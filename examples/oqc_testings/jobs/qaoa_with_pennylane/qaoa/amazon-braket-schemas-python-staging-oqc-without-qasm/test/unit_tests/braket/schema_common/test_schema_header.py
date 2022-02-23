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

import pytest
from pydantic import ValidationError

from braket.schema_common.schema_header import BraketSchemaHeader


@pytest.fixture
def name():
    return "braket.test.schema"


@pytest.fixture
def version():
    return "1.0"


@pytest.mark.xfail(raises=ValidationError)
def test_missing_properties():
    BraketSchemaHeader()


def test_schema_header_correct(name, version):
    header = BraketSchemaHeader(name=name, version=version)
    assert header.name == name
    assert header.version == version
    assert BraketSchemaHeader.parse_raw(header.json()) == header


@pytest.mark.xfail(raises=ValidationError)
def test_header_name_incorrect(version):
    BraketSchemaHeader(name="", version=version)


@pytest.mark.xfail(raises=ValidationError)
def test_header_version_incorrect(name):
    BraketSchemaHeader(name=name, version="")
