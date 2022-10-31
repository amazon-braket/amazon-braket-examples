import glob
import json
import os

import papermill as pm

os.system("pip install jupyter black papermill boto3")


def load_hyperparams():
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    with open(hp_file) as f:
        params = json.load(f)
    print(params)

    hyperparams = {}
    for key, value in params.items():
        hyperparams[key] = int(value)  # ["default"])  # convert to int for now
    print(hyperparams)
    hyperparams["device_arn"] = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    hyperparams["fig_dir"] = os.environ["AMZN_BRAKET_DEVICE_ARN"]

    print(hyperparams)

    return hyperparams


def run_notebook():

    hyperparams = load_hyperparams()

    resultsdir = os.environ.get("AMZN_BRAKET_JOB_RESULTS_DIR")
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]
    notebooks = list(glob.glob(f"{input_dir}/input/*.ipynb"))
    print("Notebooks are")
    print(notebooks)

    if len(notebooks) > 1:
        raise Exception("To many input notebooks provided.")

    notebook_name = notebooks[0].split("/")[-1]
    filename = f"{input_dir}/input/{notebook_name}"
    print("Loading dataset from: ", filename)

    print("Saving to")
    print(f"{resultsdir}/{notebook_name}")
    os.system("jupyter kernelspec list")
    pm.execute_notebook(
        filename,
        f"{resultsdir}/{notebook_name}",
        parameters=hyperparams,
        kernel_name="python3",
    )


run_notebook()
