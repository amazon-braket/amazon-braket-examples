#!/usr/bin/python3

# A sample program that runs a hybrid quantum algorithm written in PennyLane as managed job on Amazon Braket

# Imports
import os
import sys
import pickle
import json
import time
import numpy as np
import pennylane as qml

# AWS imports
import boto3
from botocore.session import get_session
from braket.aws import AwsSession


########################
# CONTAINER PATH SETUP #
########################

# Braket file directory
prefix = '/opt/ml/'

# Data location
input_path = prefix + 'input/data'
param_path = os.path.join(prefix, 'input/config/hyperparameters.json')  # Passed parameters can be retrieved here
output_path = os.path.join(prefix, 'output')  # Failure output & error messages should be written here

# Model Results
model_path = os.path.join(prefix, 'model')  # All results should be written here

# This algorithm has a single channel of input data called 'training'. Since we run in
# File mode, the input files are copied to the directory specified here.
channel_name = 'training'
training_path = os.path.join(input_path, channel_name)  # The problem definition can be found here


##################################################################################
# Retrieve hyper parameters
##################################################################################
# Parameters that were defined in the hyperparameter dict in the notebook
# can be retrieved from the param_path defined above.
# Note that the parameters are stored as a JSON string, so it is required to
# define the correct dtype upon reading (example: int).

with open(param_path, 'r') as tc:
    trainingParams = json.load(tc)
steps = int(trainingParams.get('steps', 50)) # number of optimization steps
print('Number of optimization steps:', steps)

# setup credentials and session
region = str(trainingParams.get('region', "us-west-1"))
session = boto3.Session(region_name=region)
aws_session = AwsSession(boto_session=session)

# setup s3 folder: This is where individual task results will be stored
bucket = str(trainingParams.get('bucket'))
bucket_key = str(trainingParams.get('bucket_key'))
s3_folder = (bucket, bucket_key)
print('Folder where individual task results will be stored:', s3_folder)

# set up optimizer and other hyperparameters
opt = qml.GradientDescentOptimizer(stepsize=0.4)
params = np.array([0.011, 0.012, 0.05]) # initial parameter seed


########################
# BACKEND SETUP        #
########################

# setup device/backend for circuit execution
qs3 = qml.device(
    'braket.simulator',
    wires=2,
    s3_destination_folder=s3_folder,
    backend="QS1",
    shots=1000,
    poll_timeout_seconds=1800,
    aws_session=aws_session
)


##############################
# QUANTUM ALGORITHM SETUP    #
##############################

# define variational ansatz
@qml.qnode(qs3)
def ansatz(x):
    qml.RX(x[0], wires=0)
    qml.RZ(x[1], wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RX(x[2], wires=0)
    return qml.expval(qml.PauliZ(0))


# function that computes cost function for given params
def cost(x):
    val = np.abs(ansatz(x) - 0.5) ** 2
    # send metrics to CloudWatch
    # print(f"cost={val._value};")
    print(f"cost={val};")
    return val


if __name__ == '__main__':

    ##################################################################################
    # Run optimization
    ##################################################################################

    # kick off training loop
    start = time.time()
    cost_list = []
    for i in range(steps):
        expectation = ansatz(params)
        print(f"expectation={expectation};")
        # optimize parameters with gradient descent
        params = opt.step(cost, params)
        # save current cost value to list
        cost_avg = cost(params)
        cost_list.append(cost_avg)

    # get and print final result
    expectation = ansatz(params)
    cost_final = np.abs(expectation - 0.5) ** 2

    # print optimized results
    print('Optimal expectation:', expectation)
    print('Optimal cost:', cost_final)

    # print execution time
    end = time.time()
    print('Code execution time [sec]:', end - start)

    ##################################################################################
    # Compute output and dump to pickle
    ##################################################################################
    # Everything written into the 'model_path' location defined above will be
    # returned by Braket to the S3 location defined in the notebook
    # Note that the files will be returned as a tar.gz archive
    out = {
        "expectation": expectation,
        "angles": params,
        "final_cost": cost_final,
        "cost_list": cost_list
    }
    pickle.dump(out, open(os.path.join(model_path, 'out.pckl'), "wb"))

    # A zero exit code causes the job to be marked a Succeeded.
    sys.exit(0)
