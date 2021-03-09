# import datetime
# import fileinput
# import logging
# import os
# from shutil import copyfile

# import nbformat
# import pytest
# from nbconvert.preprocessors import ExecutePreprocessor

# test_path = "examples/"
# test_notebooks = []

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# CURRENT_UTC = datetime.datetime.utcnow()
# CURRENT_TIME = CURRENT_UTC.time().strftime("%H:%M:%S")
# CURRENT_DAY = CURRENT_UTC.weekday()


# for dir_, _, files in os.walk(test_path):
#     for file_name in files:
#         if file_name.endswith(".ipynb"):
#             rel_file = os.path.join(dir_, file_name)
#             test_notebooks.append((dir_, rel_file))


# def rigetti_availability():
#     rigetti_start_time = str(datetime.time(15, 0))
#     rigetti_end_time = str(datetime.time(19, 0))

#     if rigetti_start_time < CURRENT_TIME < rigetti_end_time:
#         return True
#     return False


# def ionq_availabilty():
#     ionq_start_time = str(datetime.time(13, 0))
#     ionq_end_time = str(datetime.time(21, 0))

#     if (ionq_start_time < CURRENT_TIME < ionq_end_time) and CURRENT_DAY < 5:
#         return True
#     return False


# def check_devices_notebooks(notebook_path, keyword):
#     ionq_device = "arn:aws:braket:::device/qpu/ionq/ionQdevice"
#     rigetti_device = "arn:aws:braket:::device/qpu/rigetti/Aspen-8"
#     print("KeyWord:", keyword)
#     if keyword == "both":
#         with open(notebook_path) as file:
#             for line in file:
#                 if ionq_device in line or rigetti_device in line:
#                     return True
#     if keyword == "rigetti":
#         with open(notebook_path) as file:
#             for line in file:
#                 if rigetti_device in line:
#                     return True
#     if keyword == "ionq":
#         with open(notebook_path) as file:
#             for line in file:
#                 if ionq_device in line:
#                     return True
#     return False


# # Working
# def get_testing_status(notebook_path):
#     if rigetti_availability() is False and ionq_availabilty() is False:
#         return check_devices_notebooks(notebook_path, "both")
#     if rigetti_availability() is False:
#         return check_devices_notebooks(notebook_path, "rigetti")
#     if ionq_availabilty() is False:
#         return check_devices_notebooks(notebook_path, "ionq")


# def rename_bucket(notebook_path, s3_bucket):
#     with fileinput.FileInput(notebook_path, inplace=True) as file:
#         for line in file:
#             print(
#                 line.replace("amazon-braket-Your-Bucket-Name", s3_bucket).replace(
#                     "amazon-braket-<bucket name>", s3_bucket
#                 ),
#                 end="",
#             )


# def run_notebook(dir_path, notebook_path):
#     nb_name, _ = os.path.splitext(os.path.basename(notebook_path))
#     dirname = os.path.dirname(notebook_path)

#     with open(notebook_path) as f:
#         nb = nbformat.read(f, as_version=4)

#     proc = ExecutePreprocessor(timeout=600, kernel_name="python3")
#     proc.allow_errors = True

#     proc.preprocess(
#         nb, {"metadata": {"path": dir_path}},
#     )
#     output_path = os.path.join(dirname, "{}_all_output.ipynb".format(nb_name))

#     with open(output_path, mode="wt") as f:
#         nbformat.write(nb, f)

#     errors = []
#     for cell in nb.cells:
#         if "outputs" in cell:
#             for output in cell["outputs"]:
#                 if output.output_type == "error":
#                     errors.append(output)

#     os.remove(output_path)

#     return errors


# @pytest.mark.parametrize("dir_path, notebook", test_notebooks)
# def test_ipynb(dir_path, notebook, s3_bucket):
#     status = get_testing_status(notebook)
#     try:
#         if status is True:
#             logger.info("Skipping test due to device unavailabilty.")
#         else:
#             logger.info("Initiating Test")
#             dest_file = notebook.replace(".ipynb", "_copy.ipynb")
#             copyfile(notebook, dest_file)
#             rename_bucket(dest_file, s3_bucket)
#             errors = run_notebook(dir_path, dest_file)
#             os.remove(dest_file)
#             assert errors == [], "Errors found in {}\n{}".format(
#                 notebook, [errors[row]["evalue"] for row in range(len(errors))]
#             )
#     except TimeoutError:
#         logger.info("Timeout Error for", notebook)
#         os.remove(dest_file)
