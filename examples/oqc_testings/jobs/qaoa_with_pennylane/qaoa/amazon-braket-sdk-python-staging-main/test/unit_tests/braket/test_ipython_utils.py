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

import sys
from unittest.mock import Mock

import braket.ipython_utils as ipython_utils


def test_running_in_jupyter():
    assert not ipython_utils.running_in_jupyter()


def test_ipython_imported_but_ipython_none():
    _mock_ipython(None)
    assert not ipython_utils.running_in_jupyter()


def test_ipython_imported_but_not_in_jupyter():
    _mock_ipython(MockIPython(None))
    assert not ipython_utils.running_in_jupyter()


def test_ipython_imported_and_in_jupyter():
    _mock_ipython(MockIPython("non empty kernel"))
    assert ipython_utils.running_in_jupyter()


def get_ipython():
    pass


def _mock_ipython(get_ipython_result):
    module = sys.modules["test_ipython_utils"]
    sys.modules["IPython"] = module

    get_ipython = Mock(return_value=get_ipython_result)
    sys.modules["IPython"].__dict__["get_ipython"] = get_ipython


class MockIPython:
    def __init__(self, kernel):
        self.kernel = kernel
