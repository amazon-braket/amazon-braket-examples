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

import json
import os
import time

import networkx as nx
import numpy as np
import pennylane as qml
from matplotlib import pyplot as plt

from braket.jobs import load_job_checkpoint, save_job_checkpoint, save_job_result
from braket.jobs.metrics import log_metric

import qaoa_source.qaoa_utils as qaoa_utils  # isort:skip


def init_pl_device(device_arn, num_nodes, shots, max_parallel):
    return qml.device(
        "braket.aws.qubit",
        device_arn=device_arn,
        wires=num_nodes,
        shots=shots,
        # Set s3_destination_folder=None to output task results to a default folder
        s3_destination_folder=None,
        parallel=True,
        max_parallel=max_parallel,
        # poll_timeout_seconds=30,
    )


def start_here():
    # lets see the env variables
    # print statements can be viewed in cloudwatch
    print(os.environ)

    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]
    output_dir = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]
    job_name = os.environ["AMZN_BRAKET_JOB_NAME"]  # noqa
    checkpoint_dir = os.environ["AMZN_BRAKET_CHECKPOINT_DIR"]  # noqa
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]

    # Read the hyperparameters
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    print(hyperparams)

    p = int(hyperparams["p"])
    seed = int(hyperparams["seed"])
    max_parallel = int(hyperparams["max_parallel"])
    num_iterations = int(hyperparams["num_iterations"])
    stepsize = float(hyperparams["stepsize"])
    shots = int(hyperparams["shots"])
    pl_interface = hyperparams["interface"]
    if "copy_checkpoints_from_job" in hyperparams:
        copy_checkpoints_from_job = hyperparams["copy_checkpoints_from_job"].split("/", 2)[-1]
    else:
        copy_checkpoints_from_job = None

    interface = qaoa_utils.QAOAInterface.get_interface(pl_interface)

    # Read graph from input file
    g = nx.read_adjlist(f"{input_dir}/input-graph/input-data.adjlist", nodetype=int)
    num_nodes = len(g.nodes)

    # Draw graph to an output file
    positions = nx.spring_layout(g, seed=seed)
    nx.draw(g, with_labels=True, pos=positions, node_size=600)
    plt.savefig(f"{output_dir}/graph.png")

    # Set up the QAOA problem
    cost_h, mixer_h = qml.qaoa.maxcut(g)

    def qaoa_layer(gamma, alpha):
        qml.qaoa.cost_layer(gamma, cost_h)
        qml.qaoa.mixer_layer(alpha, mixer_h)

    def circuit(params, **kwargs):
        for i in range(num_nodes):
            qml.Hadamard(wires=i)
        qml.layer(qaoa_layer, p, params[0], params[1])

    dev = init_pl_device(device_arn, num_nodes, shots, max_parallel)

    np.random.seed(seed)
    cost_function = qml.ExpvalCost(circuit, cost_h, dev, optimize=True, interface=pl_interface)

    # Load checkpoint if it exists
    if copy_checkpoints_from_job:
        checkpoint_1 = load_job_checkpoint(
            copy_checkpoints_from_job,
            checkpoint_file_suffix="checkpoint-1",
        )
        start_iteration = checkpoint_1["iteration"]
        params = interface.initialize_params(np.array(checkpoint_1["params"]))
        print("Checkpoint loaded")
    else:
        start_iteration = 0
        params = interface.initialize_params(0.01 * np.random.uniform(size=[2, p]))

    optimizer = interface.get_sgd_optimizer(stepsize, params)
    print("Optimization start")

    for iteration in range(start_iteration, num_iterations):
        t0 = time.time()

        # Evaluates the cost, then does a gradient step to new params
        params, cost_before = interface.get_cost_and_step(cost_function, params, optimizer)
        # Convert params to a Numpy array so they're easier to handle for us
        np_params = interface.convert_params_to_numpy(params)

        t1 = time.time()

        if iteration == 0:
            print("Initial cost:", cost_before)
        else:
            print(f"Cost at step {iteration}:", cost_before)

        # Log the loss before the update step as a metric
        log_metric(
            metric_name="Cost",
            value=cost_before,
            iteration_number=iteration,
        )

        # Save the current params and previous cost to a checkpoint
        save_job_checkpoint(
            checkpoint_data={
                "iteration": iteration + 1,
                "params": np_params.tolist(),
                "cost_before": cost_before,
            },
            checkpoint_file_suffix="checkpoint-1",
        )

        print(f"Completed iteration {iteration + 1}")
        print(f"Time to complete iteration: {t1 - t0} seconds")

    final_cost = float(cost_function(params))
    log_metric(
        metric_name="Cost",
        value=final_cost,
        iteration_number=num_iterations,
    )

    print(f"Cost at step {num_iterations}:", final_cost)

    # We're done with the job, so save the result.
    # This will be returned in job.result()
    save_job_result({"params": np_params.tolist(), "cost": final_cost})
