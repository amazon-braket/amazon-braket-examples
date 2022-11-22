import os
import tarfile
import time

from boto3.session import Session
from braket.aws import AwsQuantumJob


def submit_notebook(notebook, device_arn, hyperparameters):
    job = AwsQuantumJob.create(
        device=device_arn,
        source_module="src",
        entry_point="src.runner",
        hyperparameters=hyperparameters,
        input_data=notebook,
        job_name=f"papermill-job-{int(time.time())}",
    )
    return job


def download_result_notebook(job, dir_name="result"):
    job.result()
    PATH = f"{dir_name}"
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    path = job.metadata()["outputDataConfig"]["s3Path"] + "/output/model.tar.gz"
    bucket_name = path.split("/")[2]
    output_path = "/".join(path.split("/")[3:])

    session = Session()
    s3 = session.resource("s3")
    your_bucket = s3.Bucket(bucket_name)
    your_bucket.download_file(output_path, f"{dir_name}/model.tar.gz")

    with tarfile.open(f"{dir_name}/model.tar.gz") as file:
        file.extractall(f"./{dir_name}")
