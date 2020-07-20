# imports
from datetime import datetime
import numpy as np
import tarfile
import os
import pickle

# AWS imports
import boto3
from braket.circuits import Circuit
from braket.aws import AwsQuantumSimulator, AwsSession
from botocore.session import get_session


# function to submit training job
def kickoff_train(**kwargs):
    """
    function to submit Braket training job using boto3
    hit create_quantum_job API with JSON formatted file specifying the job
    """

    # setup credentials and session
    creds = get_session().get_credentials()
    session = boto3.Session(aws_access_key_id=creds.access_key,
                            aws_secret_access_key=creds.secret_key,
                            aws_session_token=creds.token,
                            region_name=kwargs['region'])
    aws_session = AwsSession(boto_session=session)

    # setup client
    braket_client = aws_session.braket_client

    # run training job tagged with custom job name
    circuit_depth = kwargs['p']
    project_name = 'qaoa-' + str(circuit_depth)
    job_name = project_name + '-' + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
    print('jobName with time stamp:', job_name)

    # call API
    quantum_job = braket_client.create_quantum_job(
        jobName=job_name,
        resourceConfig={                          # the classical part of the computation runs
            "instanceCount": 1,                   # on a single m4.xlarge instance with 50GB volume size
            "instanceType": kwargs['hardware'],
            "volumeSizeInGb": 50
        },
        outputDataConfig={
            "s3OutputPath": kwargs['output_path'] # This is where results will be stored.
        },
        stoppingCondition={
            "maxRuntimeInSeconds": 86400          # the job aborts after 1 day
        },
        sagemakerRoleArn=kwargs['role'],
        inputScriptConfig={
            "scriptS3Bucket": kwargs['bucket'],
            "scriptS3ObjectKey": kwargs['my_python_script'] # This is where your script is stored
        },
        metricDefinitions = [{                    # We are looking for the custom metric cost_avg which we are catching
            'name': "cost_avg",                   # using regex expressions from stdout. This metric is reported out to
            'regex': "cost_avg=(.*?);"            # CloudWatch
        }],
        hyperParameters={                         # You can pass any hyperparameters into your algorithm here
            'p': circuit_depth,
            'bucket': kwargs['bucket'],           # The bucket and key where your tasks are stored are required.
            'bucket_key': kwargs['bucket_key'],
            'device_type': kwargs['device_type'], # set the backend for circuit execution
            'device_arn': kwargs['device_arn'],
            'input_data': kwargs['input_data'],  # input data location
            'region': kwargs['region'],
            },
)

    # print quantum Job ARN with date, status code etc.
    # print(quantum_job_arn)

    # return job name
    return job_name, quantum_job


# custom function for retrieving data from S3 and postprocessing
def postprocess(job_name, bucket, region='us-west-1'):
    """
    function for postprocessing of job
    """

    # setup credentials and session
    creds = get_session().get_credentials()
    session = boto3.Session(aws_access_key_id=creds.access_key,
                            aws_secret_access_key=creds.secret_key,
                            aws_session_token=creds.token,
                            region_name=region)
    aws_session = AwsSession(boto_session=session)

    # get the results from S3
    # s3.download_file('BUCKET_NAME', 'OBJECT_NAME', 'FILE_NAME')
    object_key = 'results/{}/output/model.tar.gz'.format('AQxJob-' + job_name)
    tempfile = '/tmp/model.tar.gz'
    s3_client = session.client("s3")
    s3_client.download_file(bucket, object_key, tempfile)

    # unzip the results
    tar = tarfile.open(tempfile, "r:gz")
    tar.extractall(path='/tmp')

    # load the results into the notebook
    out = pickle.load(open('/tmp/out.pckl', "rb"))

    p = out['p']
    N = out['N']
    ENERGY_OPTIMAL = out['ENERGY_OPTIMAL']
    BITSTRING = out['BITSTRING']
    result_energy = out['result_energy']
    result_angle = out['result_angle']

    # clean-up temporary files
    os.remove(tempfile)

    print('Optimal energy from managed job:', ENERGY_OPTIMAL)
    print('Optimal bit-string from managed job:', BITSTRING)

    gamma = result_angle[:p]
    beta = result_angle[p:]
    pa = np.arange(1, p + 1)

    return p, N, ENERGY_OPTIMAL, BITSTRING, result_energy, result_angle, gamma, beta, pa
