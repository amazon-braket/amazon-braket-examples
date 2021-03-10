import fileinput
import os
import logging
import nbformat
import pytest
import traceback

from shutil import copyfile
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_EXCLUSIVE_DEVICE_REGIONS = {
    "TN1": {
        "ARN": "arn:aws:braket:::device/quantum-simulator/amazon/tn1",
        "REGION": [
            "us-west-2",
            "us-east-1",
        ],
    }
}

demo_path = "examples/"
demo_notebooks = []


for dir_, _, files in os.walk(demo_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith(".ipynb") and "QPU" not in file_name:
            demo_notebooks.append((dir_, rel_file))


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
    device_arn = _EXCLUSIVE_DEVICE_REGIONS["TN1"]["ARN"]
    if region not in _EXCLUSIVE_DEVICE_REGIONS["TN1"]["REGION"]:
        with open(notebook_path) as file:
            for line in file:
                if device_arn in line:
                    return device_arn, False
    return device_arn, True


def _run_notebook(dir_path, notebook_path):

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(kernel_name="python3")
    proc.allow_errors = True

    proc.preprocess(
        nb,
        {"metadata": {"path": dir_path}},
    )

    return [
        output
        for cell in nb.cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]


@pytest.mark.parametrize("dir_path, notebook", demo_notebooks)
def test_ipynb(dir_path, notebook, s3_bucket, region):
    device_arn, device_status = _check_exclusive_device_availability(notebook, region)
    try:
        if device_status:
            logger.info(f"Testing {notebook}")
            dest_file = notebook.replace(".ipynb", "_copy.ipynb")
            copyfile(notebook, dest_file)
            _rename_bucket(dest_file, s3_bucket)
            errors = _run_notebook(dir_path, dest_file)
            os.remove(dest_file)
            assert errors == [], "Errors found in {}\n{}".format(
                notebook, [errors[row]["evalue"] for row in range(len(errors))]
            )
        else:
            logger.info(f"Skipped testing due to {device_arn} unavailable in {region}")
    except TimeoutError:
        os.remove(dest_file)
        logger.error(traceback.print_exc())
