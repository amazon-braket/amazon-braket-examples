import ast
import glob
import json
import os

import papermill as pm


def convert_to_value(value):
    try:
        return ast.literal_eval(value)
    except ValueError:
        return value


def load_hyperparams():
    # Load Braket Jobs hyperparameters
    with open(os.environ["AMZN_BRAKET_HP_FILE"]) as f:
        braket_hyperparams = json.load(f)

    print(f"Braket hyperparameters are: {braket_hyperparams}")

    # Convert Braket hyperparameters to Papermill parameters
    papermill_params = {}
    for key, value in braket_hyperparams.items():
        papermill_params[key] = convert_to_value(value)

    papermill_params["device_arn"] = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    papermill_params["results_dir"] = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]

    print(f"Papermill parameters are: {papermill_params}")
    return papermill_params


def run_notebook():
    papermill_params = load_hyperparams()

    results_dir = os.environ.get("AMZN_BRAKET_JOB_RESULTS_DIR")
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]

    notebooks = list(glob.glob(f"{input_dir}/input/*.ipynb"))
    print(f"Notebooks are {notebooks}")

    if len(notebooks) > 1:
        raise ValueError("To many input notebooks provided.")

    notebook_name = notebooks[0].split("/")[-1]
    filename = f"{input_dir}/input/{notebook_name}"
    print("Loading dataset from: ", filename)

    print(f"Saving results to {results_dir}/{notebook_name}")

    pm.execute_notebook(
        filename,
        f"{results_dir}/{notebook_name}",
        parameters=papermill_params,
        kernel_name="python3",
    )


run_notebook()
