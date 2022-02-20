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


def running_in_jupyter():
    """
    Determine if running within Jupyter.

    Inspired by https://github.com/ipython/ipython/issues/11694

    Returns:
        bool: True if running in Jupyter, else False.
    """
    in_ipython = False
    in_ipython_kernel = False

    # if IPython hasn't been imported, there's nothing to check
    if "IPython" in sys.modules:
        get_ipython = sys.modules["IPython"].__dict__["get_ipython"]

        ip = get_ipython()
        in_ipython = ip is not None

    if in_ipython:
        in_ipython_kernel = getattr(ip, "kernel", None) is not None

    return in_ipython_kernel
