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

import datetime
import fileinput
import logging
import os
import traceback
from shutil import copyfile

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_EXCLUSIVE_DEVICE_REGIONS = {
    "arn:aws:braket:::device/quantum-simulator/amazon/tn1": [
        "us-west-2",
        "us-east-1",
    ],
}

test_path = "examples/"
test_notebooks = []

CURRENT_UTC = datetime.datetime.utcnow()
CURRENT_TIME = CURRENT_UTC.time().strftime("%H:%M:%S")

# Currently adding rigetti notebooks to skip as files, since other notebook files also have rigetti arn.
EXCLUDED_NOTEBOOKS = [
    "2_Running_quantum_circuits_on_QPU_devices.ipynb",
    "Allocating_Qubits_on_QPU_Devices.ipynb",
    "Verbatim_Compilation.ipynb",
    "Hyperparameter_tuning.ipynb",
    "bring_your_own_container.ipynb",
    "Getting_started.ipynb",
    "Using_PennyLane_with_Braket_Jobs.ipynb"
    ""
]


def _rigetti_availability(file_name):
    rigetti_start_time = str(datetime.time(15, 0))
    rigetti_end_time = str(datetime.time(19, 0))
    is_within_time_window = rigetti_start_time < CURRENT_TIME < rigetti_end_time
    if file_name in EXCLUDED_NOTEBOOKS and not is_within_time_window:
        return False
    return True


for dir_, _, files in os.walk(test_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith("copy.ipynb"):
            os.remove(rel_file)
        if file_name.endswith(".ipynb") and _rigetti_availability(file_name) and \
                not file_name.endswith("bring_your_own_container.ipynb"):
            test_notebooks.append((dir_, rel_file))


def _rename_bucket(notebook_path, s3_bucket):
    with fileinput.FileInput(notebook_path, inplace=True) as file:
        for line in file:
            print(
                line.replace("amazon-braket-Your-Bucket-Name", s3_bucket).replace(
                    "amazon-braket-<bucket name>", s3_bucket
                ),
                end="",
            )


def _check_exclusive_device_availability(notebook_path, region):
    for device, availability in _EXCLUSIVE_DEVICE_REGIONS.items():
        if region not in availability:
            with open(notebook_path) as file:
                for line in file:
                    if device in line:
                        return device, False
    return device, True


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
def test_ipynb(dir_path, notebook, s3_bucket, region):
    device_arn, device_status = _check_exclusive_device_availability(notebook, region)
    try:
        if device_status:
            logger.info(f"Testing {notebook}")
            dest_file = notebook.replace(".ipynb", "_copy.ipynb")
            copyfile(notebook, dest_file)
            _rename_bucket(dest_file, s3_bucket)
            errors = _run_notebook(dir_path, dest_file)
            assert errors == [], "Errors found in {}\n{}".format(
                notebook, [errors[row]["evalue"] for row in range(len(errors))]
            )
        else:
            pytest.skip()
            logger.info(f"Skipped testing due to {device_arn} unavailable in {region}")
    except TimeoutError:
        logger.error(traceback.print_exc())
    finally:
        os.remove(dest_file)
