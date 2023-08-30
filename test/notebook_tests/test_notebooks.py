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
    "bring_your_own_container.ipynb",
    "qnspsa_with_embedded_simulator.ipynb",
    "Parallelize_training_for_QML.ipynb",
    "Embedded_simulators_in_Braket_Jobs.ipynb",
    # Temporarily exclude Aquila notebooks
    "01_Introduction_to_Aquila.ipynb",
    "02_Ordered_phases_in_Rydberg_systems.ipynb",
    "03_Parallel_tasks_on_Aquila.ipynb"
]


for dir_, _, files in os.walk(test_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith("copy.ipynb"):
            os.remove(rel_file)
        if file_name.endswith(".ipynb") and file_name not in EXCLUDED_NOTEBOOKS:
            test_notebooks.append((dir_, rel_file))


def _check_exclusive_device_availability(notebook_path, unavailable_devices):
    with open(notebook_path) as file:
        content = file.read()
        for device in unavailable_devices:
            if device.arn in content:
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
