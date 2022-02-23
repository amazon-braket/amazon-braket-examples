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

import importlib
import sys
from unittest.mock import patch

import braket.tasks


@patch("braket.ipython_utils.running_in_jupyter")
def test_nest_asyncio_not_applied(running_in_jupyter):
    running_in_jupyter.return_value = False
    importlib.reload(braket.tasks)
    assert "nest_asyncio" not in sys.modules


@patch("braket.ipython_utils.running_in_jupyter")
def test_nest_asyncio_is_applied(running_in_jupyter):
    running_in_jupyter.return_value = True
    importlib.reload(braket.tasks)
    assert "nest_asyncio" in sys.modules
