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

import logging
import os
import traceback

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_path = "examples/"
test_notebooks = []

# These notebooks would not be tested.
EXCLUDED_NOTEBOOKS = [
    "bring_your_own_container.ipynb"
]

# These notebooks would not be tested unless the devices used in the notebook
# are available at the time of the test run.
NOTEBOOKS_REQUIRING_DEVICE_AVAILABILITY = [
    "2_Running_quantum_circuits_on_QPU_devices.ipynb",
    "Allocating_Qubits_on_QPU_Devices.ipynb",
    "Verbatim_Compilation.ipynb",
    "Using_the_tensor_network_simulator_TN1.ipynb",
    "TN1_demo_local_vs_non-local_random_circuits.ipynb",
    "Getting_Started_with_OpenQASM_on_Braket.ipynb"
]


for dir_, _, files in os.walk(test_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith("copy.ipynb"):
            os.remove(rel_file)
        if file_name.endswith(".ipynb") and file_name not in EXCLUDED_NOTEBOOKS:
            test_notebooks.append((dir_, rel_file))


def _check_exclusive_device_availability(notebook_path, unavailable_devices):
    if notebook_path.split("/")[-1] not in NOTEBOOKS_REQUIRING_DEVICE_AVAILABILITY:
        return "None", True

    with open(notebook_path) as file:
        for line in file:
            for device in unavailable_devices:
                if device.arn in line:
                    return device.arn, False

    return "None", True


def _run_notebook(dir_path, notebook_path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(kernel_name="python3")
    proc.allow_errors = True
    proc.preprocess(nb, {"metadata": {"path": dir_path}})

    return [
        output
        for cell in nb.cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]

@pytest.mark.parametrize("dir_path, notebook", test_notebooks)
def test_ipynb(dir_path, notebook, region, unavailable_devices):
    device_arn, device_status = _check_exclusive_device_availability(notebook, unavailable_devices)
    try:
        if device_status:
            logger.info(f"Testing {notebook}")
            errors = _run_notebook(dir_path, notebook)
            assert errors == [], "Errors found in {}\n{}".format(
                notebook, [errors[row]["evalue"] for row in range(len(errors))]
            )
        else:
            pytest.skip()
            logger.info(f"Skipped testing due to {device_arn} unavailable in {region}")
    except TimeoutError:
        logger.error(traceback.print_exc())