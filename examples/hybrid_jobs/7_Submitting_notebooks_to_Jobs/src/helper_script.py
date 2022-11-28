import ast
import contextlib
import glob
import json
import os
import pathlib
from typing import Any, Dict, TypeVar

import papermill as pm

PathLike = TypeVar("PathLike", str, pathlib.Path, None)


def convert_to_value(value: str) -> Any:
    """Parse any string containing a Python expression into a Python object.

    Args:
        value (str): Any value to parse. For example "1", "1.0", "str", "[1, 2]".

    Returns:
        Any: The Python object of the correct type.
    """
    with contextlib.suppress(ValueError):  # suppress error message
        return ast.literal_eval(value)
    return value


def load_jobs_hyperparams() -> Dict[str, str]:
    """Return the the Braket Jobs hyperparameters file as a dictionary.

    Returns:
        Dict[str, str]: Hyperparameters as a dictionary.
    """
    with open(os.environ["AMZN_BRAKET_HP_FILE"]) as f:
        braket_hyperparams = json.load(f)
    print(f"Braket hyperparameters are: {braket_hyperparams}")
    return braket_hyperparams


def convert_jobs_hyperparams_to_pm_params(braket_hyperparams: Dict[str, str]) -> Dict[str, Any]:
    """Converts Braket Jobs hyperparameters to Papermill parameters.

    Args:
        braket_hyperparams (Dict[str, str]): Braket Jobs hyperparameters dictionary.

    Returns:
        Dict[str, Any]: Papermill parameters.
    """
    papermill_params = {key: convert_to_value(value) for key, value in braket_hyperparams.items()}

    papermill_params["device_arn"] = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    papermill_params["results_dir"] = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]
    print(f"Papermill parameters are: {papermill_params}")
    return papermill_params


def get_notebook_name(input_dir: PathLike) -> str:
    """Returns the notebook name from an input path.

    Args:
        input_dir (PathLike): Path to notebook.


    Returns:
        str: Notebook name.
    """
    notebooks = list(glob.glob(f"{input_dir}/input/*.ipynb"))
    if len(notebooks) > 1:
        raise ValueError("To many input notebooks provided.")
    notebook_name = notebooks[0].split("/")[-1]
    return notebook_name


def run_notebook() -> None:
    """Run the notebook with Papermill."""
    results_dir = os.environ.get("AMZN_BRAKET_JOB_RESULTS_DIR")
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]

    braket_hyperparams = load_jobs_hyperparams()

    papermill_params = convert_jobs_hyperparams_to_pm_params(braket_hyperparams)

    notebook_name = get_notebook_name(input_dir)

    pm.execute_notebook(
        f"{input_dir}/input/{notebook_name}",
        f"{results_dir}/{notebook_name}",
        parameters=papermill_params,
        kernel_name="python3",
    )
