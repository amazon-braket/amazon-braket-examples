import fileinput
import os
import logging
from shutil import copyfile

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

demo_path = "examples/"
demo_notebooks = []


for dir_, _, files in os.walk(demo_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith(".ipynb") and "QPU" not in file_name:
            demo_notebooks.append((dir_, rel_file))


def rename_bucket(notebook_path, s3_bucket):
    with fileinput.FileInput(notebook_path, inplace=True) as file:
        for line in file:
            print(
                line.replace("amazon-braket-Your-Bucket-Name", s3_bucket).replace(
                    "amazon-braket-<bucket name>", s3_bucket
                ),
                end="",
            )


def check_tn1_availability(notebook_path, region):
    tn1_device = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
    tn1_regions = ["us-west-2", "us-east-1"]
    if region not in tn1_regions:
        with open(notebook_path) as file:
            for line in file:
                if tn1_device in line:
                    return False
    return True


def run_notebook(dir_path, notebook_path):
    nb_name, _ = os.path.splitext(os.path.basename(notebook_path))

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(kernel_name="python3")
    proc.allow_errors = True

    proc.preprocess(
        nb, {"metadata": {"path": dir_path}},
    )

    errors = []
    for cell in nb.cells:
        if "outputs" in cell:
            for output in cell["outputs"]:
                if output.output_type == "error":
                    errors.append(output)

    return errors


@pytest.mark.parametrize("dir_path, notebook", demo_notebooks)
def test_ipynb(dir_path, notebook, s3_bucket, region):
    tn1_status = check_tn1_availability(notebook, region)
    try:
        if tn1_status:
            logger.info("Testing: ", notebook)
            dest_file = notebook.replace(".ipynb", "_copy.ipynb")
            copyfile(notebook, dest_file)
            rename_bucket(dest_file, s3_bucket)
            errors = run_notebook(dir_path, dest_file)
            os.remove(dest_file)
            assert errors == [], "Errors found in {}\n{}".format(
                notebook, [errors[row]["evalue"] for row in range(len(errors))]
            )
        else:
            pytest.mark.skip(notebook)
            logger.info("Skipped testing due to device unavailable in", region)
            print("Skipped testing due to device unavailable in", region)
    except TimeoutError:
        os.remove(dest_file)
