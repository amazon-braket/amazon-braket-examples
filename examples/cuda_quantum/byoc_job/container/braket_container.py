# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import contextlib
import errno
import importlib
import inspect
import os
import json
import runpy
import shutil
import subprocess
import sys
import multiprocessing
from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple, Callable

import boto3

OPT_ML = os.path.join("/opt", "ml")
OPT_BRAKET = os.path.join("/opt", "braket")
CUSTOMER_CODE_PATH = os.path.join(OPT_BRAKET, "code", "customer_code")
ORIGINAL_CUSTOMER_CODE_PATH = os.path.join(CUSTOMER_CODE_PATH, "original")
EXTRACTED_CUSTOMER_CODE_PATH = os.path.join(CUSTOMER_CODE_PATH, "extracted")
ERROR_LOG_PATH = os.path.join(OPT_ML, "output")
ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, "failure")
SETUP_SCRIPT_PATH = os.path.join(OPT_BRAKET, "additional_setup")

print("Boto3 Version: ", boto3.__version__)


def _log_failure(*args, display=True):
    """
    Log failures to a file so that it can be parsed by the backend service and included in
    failure messages for a job.

    Args:
        args: variable list of text to write to the file.
    """
    Path(ERROR_LOG_PATH).mkdir(parents=True, exist_ok=True)
    with open(ERROR_LOG_FILE, 'a') as error_log:
        for text in args:
            error_log.write(text)
            if display:
                print(text)


def log_failure_and_exit(*args):
    """
    Log failures to a file so that it can be parsed by the backend service and included in
    failure messages for a job. Exists with code 0.

    Args:
        args: variable list of text to write to the file.
    """
    _log_failure(*args)
    sys.exit(0)


def create_paths():
    """
    These paths are created early on so that the rest of the code can assume that the directories
    are available when needed.
    """
    Path(CUSTOMER_CODE_PATH).mkdir(parents=True, exist_ok=True)
    Path(ORIGINAL_CUSTOMER_CODE_PATH).mkdir(parents=True, exist_ok=True)
    Path(EXTRACTED_CUSTOMER_CODE_PATH).mkdir(parents=True, exist_ok=True)
    Path(SETUP_SCRIPT_PATH).mkdir(parents=True, exist_ok=True)


def create_symlink():
    """
    The ML paths are inserted by the backend service by default. To prevent confusion we link
    the Braket paths to it (to unify them), and use the Braket paths from now on.
    """
    try:
        os.symlink(OPT_ML, OPT_BRAKET)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(f"Got unexpected exception: {e}")
            log_failure_and_exit(f"Symlink failure.\n Exception: {e}")


def download_s3_file(s3_uri: str, local_path: str) -> str:
    """
    Downloads a file to a local path.

    Args:
        s3_uri (str): the S3 URI to get the file from.
        local_path (str) : the local path to download to
    Returns:
        str: the path to the file containing the downloaded path.
    """
    s3_client = boto3.client("s3")
    parsed_url = urlparse(s3_uri, allow_fragments=False)
    s3_bucket = parsed_url.netloc
    s3_key = parsed_url.path.lstrip("/")
    local_s3_file = os.path.join(local_path, os.path.basename(s3_key))
    if not os.path.exists(local_s3_file):
        s3_client.download_file(s3_bucket, s3_key, local_s3_file)
    return local_s3_file


def download_customer_code(s3_uri: str) -> str:
    """
    Downloads the customer code to the original customer path. The code is assumed to be a single
    file in S3. The file may be a compressed archive containing all the customer code.

    Args:
        s3_uri (str): the S3 URI to get the code from.
    Returns:
        str: the path to the file containing the code.
    """
    try:
        return download_s3_file(s3_uri, ORIGINAL_CUSTOMER_CODE_PATH)
    except Exception as e:
        log_failure_and_exit(f"Unable to download code.\nException: {e}")


def unpack_code_and_add_to_path(local_s3_file: str, compression_type: str):
    """
    Unpack the customer code, if necessary. Add the customer code to the system path.

    Args:
        local_s3_file (str): the file representing the customer code.
        compression_type (str): if the customer code is stored in an archive, this value will
            represent the compression type of the archive.
    """
    if compression_type and compression_type.strip().lower() in ["gzip", "zip"]:
        try:
            shutil.unpack_archive(local_s3_file, EXTRACTED_CUSTOMER_CODE_PATH)
        except Exception as e:
            log_failure_and_exit(
                f"Got an exception while trying to unpack archive: {local_s3_file} of type: "
                f"{compression_type}.\nException: {e}"
            )
    else:
        shutil.copy(local_s3_file, EXTRACTED_CUSTOMER_CODE_PATH)
    sys.path.append(EXTRACTED_CUSTOMER_CODE_PATH)


def try_bind_hyperparameters_to_customer_method(customer_method: Callable):
    hp_file = os.getenv("AMZN_BRAKET_HP_FILE")
    if hp_file is None:
        return

    with open(hp_file) as f:
        hyperparameters = json.load(f)

    try:
        inspect.signature(customer_method).bind(**hyperparameters)
    except TypeError:
        return

    annotations = inspect.getfullargspec(customer_method).annotations
    function_args = {}
    for param in hyperparameters:
        function_args[param] = annotations.get(param, str)(
            hyperparameters[param]
        )
    return function_args


def get_code_setup_parameters() -> Tuple[str, str, str]:
    """
    Returns the code setup parameters:
        s3_uri: the S3 location where the code is stored.
        entry_point: the entrypoint into the code.
        compression_type: the compression used to archive the code (optional)
    These values are stored in environment variables, however, we also allow the storing of
    these values in the hyperparameters to facilitate testing in local mode.
    If the s3_uri or entry_point can not be found, the script will exit with an error.

    Returns:
        str, str, str: the code setup parameters as described above.
    """
    s3_uri = os.getenv('AMZN_BRAKET_SCRIPT_S3_URI')
    entry_point = os.getenv('AMZN_BRAKET_SCRIPT_ENTRY_POINT')
    compression_type = os.getenv('AMZN_BRAKET_SCRIPT_COMPRESSION_TYPE')
    if s3_uri and entry_point:
        return s3_uri, entry_point, compression_type
    hyperparameters_env = os.getenv('SM_HPS')
    if hyperparameters_env:
        try:
            hyperparameters = json.loads(hyperparameters_env)
            if not s3_uri:
                s3_uri = hyperparameters.get("AMZN_BRAKET_SCRIPT_S3_URI")
            if not entry_point:
                entry_point = hyperparameters.get("AMZN_BRAKET_SCRIPT_ENTRY_POINT")
            if not compression_type:
                compression_type = hyperparameters.get("AMZN_BRAKET_SCRIPT_COMPRESSION_TYPE")
        except Exception as e:
            log_failure_and_exit("Hyperparameters not specified in env")
    if not s3_uri:
        log_failure_and_exit("No customer script specified")
    if not entry_point:
        log_failure_and_exit("No customer entry point specified")
    return s3_uri, entry_point, compression_type


def install_additional_requirements() -> None:
    """
    Search for requirements from requirements.txt and install them.
    """
    try:
        print("Checking for Additional Requirements")
        for root, _, files in os.walk(EXTRACTED_CUSTOMER_CODE_PATH):
            if "requirements.txt" in files:
                requirements_file_path = os.path.join(root, "requirements.txt")
                subprocess.run(
                    ["python", "-m", "pip", "install", "-r", requirements_file_path],
                    cwd=EXTRACTED_CUSTOMER_CODE_PATH
                )
        print("Additional Requirements Check Finished")
    except Exception as e:
        log_failure_and_exit(f"Unable to install requirements.\nException: {e}")


def extract_customer_code(entry_point: str) -> Callable:
    """
    Converts entry point to a runnable function.
    """
    if entry_point.find(":") >= 0:
        str_module, _, str_method = entry_point.partition(":")
        customer_module = importlib.import_module(str_module)
        print("**** customer_module ****")
        print(dir(customer_module)) 
        customer_code = getattr(customer_module, str_method)
    else:
        def customer_code():
            # equivalent to `python -m entry_point`
            return runpy.run_module(entry_point, run_name="__main__")
    return customer_code


@contextlib.contextmanager
def in_extracted_code_dir():
    current_dir = os.getcwd()
    try:
        os.chdir(EXTRACTED_CUSTOMER_CODE_PATH)
        yield
    finally:
        os.chdir(current_dir)


def wrap_customer_code(customer_method: Callable) -> Callable:
    def wrapped_customer_code(**kwargs):
        try:
            with in_extracted_code_dir():
                return customer_method(**kwargs)
        except Exception as e:
            exception_type = type(e).__name__
            exception_string = (
                exception_type
                if not str(e)
                else f"{exception_type}: {e}"
            )
            _log_failure(exception_string, display=False)
            raise e
    return wrapped_customer_code


def kick_off_customer_script(customer_code: Callable) -> multiprocessing.Process:
    """
    Runs the customer script as a separate process.

    Args:
        customer_code (Callable): The customer method to be run.

    Returns:
        Process: the process handle to the running process.
    """
    print("Running Code As Process")
    wrapped_customer_code = wrap_customer_code(customer_code)
    process_kwargs = {"target": wrapped_customer_code}

    function_args = try_bind_hyperparameters_to_customer_method(customer_code)
    if function_args is not None:
        process_kwargs["kwargs"] = function_args

    customer_code_process = multiprocessing.Process(**process_kwargs)
    customer_code_process.start()
    return customer_code_process


def join_customer_script(customer_code_process: multiprocessing.Process):
    """
    Joins the process running the customer code.

    Args:
        customer_code_process (Process): the process running the customer code.
    """
    try:
        customer_code_process.join()
    except Exception as e:
        log_failure_and_exit(f"Job did not exit gracefully.\nException: {e}")
    print("Code Run Finished")
    return customer_code_process.exitcode


def run_customer_code() -> None:
    """
    Downloads and runs the customer code. If the customer code exists
    with a non-zero exit code, this function will log a failure and
    exit.
    """
    # Add wait time to resolve race condition
    import time
    rank = int(os.getenv('OMPI_COMM_WORLD_NODE_RANK', "0"))
    time.sleep(rank)
    
    s3_uri, entry_point, compression_type = get_code_setup_parameters()
    local_s3_file = download_customer_code(s3_uri)
    unpack_code_and_add_to_path(local_s3_file, compression_type)

    install_additional_requirements()
    customer_executable = extract_customer_code(entry_point)
    customer_process = kick_off_customer_script(customer_executable)
    if (exit_code := join_customer_script(customer_process)) != 0:
        sys.exit(exit_code)


def setup_and_run():
    """
    This method sets up the Braket container, then downloads and runs the customer code.
    """
    print("Beginning Setup")
    create_symlink()
    create_paths()
    run_customer_code()


if __name__ == "__main__":
    setup_and_run()