# Amazon Braket Python SDK

[![Latest Version](https://img.shields.io/pypi/v/amazon-braket-sdk.svg)](https://pypi.python.org/pypi/amazon-braket-sdk)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/amazon-braket-sdk.svg)](https://pypi.python.org/pypi/amazon-braket-sdk)
[![Build Status](https://img.shields.io/github/workflow/status/aws/amazon-braket-sdk-python/Python%20package/main?logo=github)](https://github.com/aws/amazon-braket-sdk-python/actions?query=workflow%3A%22Python+package%22)
[![codecov](https://codecov.io/gh/aws/amazon-braket-sdk-python/branch/main/graph/badge.svg?token=1lsqkZL3Ll)](https://codecov.io/gh/aws/amazon-braket-sdk-python)
[![Documentation Status](https://img.shields.io/readthedocs/amazon-braket-sdk-python.svg?logo=read-the-docs)](https://amazon-braket-sdk-python.readthedocs.io/en/latest/?badge=latest)
[![Code Style: Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)

The Amazon Braket Python SDK is an open source library that provides a framework that you can use to interact with quantum computing hardware devices through Amazon Braket.

## Prerequisites
Before you begin working with the Amazon Braket SDK, make sure that you've installed or configured the following prerequisites.

### Python 3.7.2 or greater
Download and install Python 3.7.2 or greater from [Python.org](https://www.python.org/downloads/).

### Git
Install Git from https://git-scm.com/downloads. Installation instructions are provided on the download page.

### IAM user or role with required permissions
As a managed service, Amazon Braket performs operations on your behalf on the AWS hardware that is managed by Amazon Braket. Amazon Braket can perform only operations that the user permits. You can read more about which permissions are necessary in the AWS Documentation.

The Braket Python SDK should not require any additional permissions aside from what is required for using Braket. However, if you are using an IAM role with a path in it, you should grant permission for iam:GetRole.

To learn more about IAM user, roles, and policies, see [Adding and Removing IAM Identity Permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html).

### Boto3 and setting up AWS credentials

Follow the installation [instructions](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for Boto3 and setting up AWS credentials.

**Note:** Make sure that your AWS region is set to one supported by Amazon Braket. You can check this in your AWS configuration file, which is located by default at `~/.aws/config`.

### Configure your AWS account with the resources necessary for Amazon Braket
If you are new to Amazon Braket, onboard to the service and create the resources necessary to use Amazon Braket using the [AWS console](https://console.aws.amazon.com/braket/home ).

## Installing the Amazon Braket Python SDK

The Amazon Braket Python SDK can be installed with pip as follows:

```bash
pip install amazon-braket-sdk
```

You can also install from source by cloning this repository and running a pip install command in the root directory of the repository:

```bash
git clone https://github.com/aws/amazon-braket-sdk-python.git
cd amazon-braket-sdk-python
pip install .
```

### Check the version you have installed
You can view the version of the amazon-braket-sdk you have installed by using the following command:
```bash
pip show amazon-braket-sdk
```

You can also check your version of `amazon-braket-sdk` from within Python:

```
>>> import braket._sdk as braket_sdk
>>> braket_sdk.__version__
```

### Updating the Amazon Braket Python SDK
You can update the version of the amazon-braket-sdk you have installed by using the following command:
```bash
pip install amazon-braket-sdk --upgrade --upgrade-strategy eager
```

## Usage

### Running a circuit on an AWS simulator

```python
import boto3
from braket.aws import AwsDevice
from braket.circuits import Circuit

device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")
s3_folder = ("amazon-braket-Your-Bucket-Name", "folder-name") # Use the S3 bucket you created during onboarding

bell = Circuit().h(0).cnot(0, 1)
task = device.run(bell, s3_folder, shots=100)
print(task.result().measurement_counts)
```

The code sample imports the Amazon Braket framework, then defines the device to use (the SV1 AWS simulator). The `s3_folder` statement defines the Amazon S3 bucket for the task result and the folder in the bucket to store the task result. This folder is created when you run the task. It then creates a Bell Pair circuit, executes the circuit on the simulator and prints the results of the job. This example can be found in `../examples/bell.py`.

### Running multiple tasks at once

Many quantum algorithms need to run multiple independent circuits, and submitting the circuits in parallel can be faster than submitting them one at a time. In particular, parallel task processing provides a significant speed up when using simulator devices. The following example shows how to run a batch of tasks on SV1:

```python
circuits = [bell for _ in range(5)]
batch = device.run_batch(circuits, s3_folder, shots=100)
print(batch.results()[0].measurement_counts)  # The result of the first task in the batch
```

### Running a hybrid job

```python
from braket.aws import AwsQuantumJob

job = AwsQuantumJob.create(
    device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    source_module="job.py",
    entry_point="job:run_job",
    wait_until_complete=True,
)
print(job.result())
```
where `run_job` is a function in the file `job.py`.


The code sample imports the Amazon Braket framework, then creates a hybrid job with the entry point being the `run_job` function. The hybrid job creates quantum tasks against the SV1 AWS Simulator. The job runs synchronously, and prints logs until it completes. The complete example can be found in `../examples/job.py`.

### Available Simulators
Amazon Braket provides access to two types of simulators: fully managed simulators, available through the Amazon Braket service, and the local simulators that are part of the Amazon Braket SDK.

- Fully managed simulators offer high-performance circuit simulations. These simulators can handle circuits larger than circuits that run on quantum hardware. For example, the SV1 state vector simulator shown in the previous examples requires approximately 1 or 2 hours to complete a 34-qubit, dense, and square circuit (circuit depth = 34), depending on the type of gates used and other factors.
- The Amazon Braket Python SDK includes an implementation of quantum simulators that can run circuits on your local, classic hardware. For example the braket_sv local simulator is well suited for rapid prototyping on small circuits up to 25 qubits, depending on the hardware specifications of your Braket notebook instance or your local environment. An example of how to execute the task locally is included in the repository  `../examples/local_bell.py`.

For a list of available simulators and their features, consult the [Amazon Braket Developer Guide](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html).

### Debugging logs

Tasks sent to QPUs don't always run right away. To view task status, you can enable debugging logs. An example of how to enable these logs is included in repo: `../examples/debug_bell.py`. This example enables task logging so that status updates are continuously printed to the terminal after a quantum task is executed. The logs can also be configured to save to a file or output to another stream. You can use the debugging example to get information on the tasks you submit, such as the current status, so that you know when your task completes.

### Running a Quantum Algorithm on a Quantum Computer
With Amazon Braket, you can run your quantum circuit on a physical quantum computer.

The following example executes the same Bell Pair example described to validate your configuration on a Rigetti quantum computer.

```python
import boto3
from braket.circuits import Circuit
from braket.aws import AwsDevice

device = AwsDevice("arn:aws:braket:::device/qpu/rigetti/Aspen-8")
s3_folder = ("amazon-braket-Your-Bucket-Name", "RIGETTI") # Use the S3 bucket you created during onboarding

bell = Circuit().h(0).cnot(0, 1)
task = device.run(bell, s3_folder) 
print(task.result().measurement_counts)
```

When you execute your task, Amazon Braket polls for a result. By default, Braket polls for 5 days; however, it is possible to change this by modifying the `poll_timeout_seconds` parameter in `AwsDevice.run`, as in the example below. Keep in mind that if your polling timeout is too short, results may not be returned within the polling time, such as when a QPU is unavailable, and a local timeout error is returned. You can always restart the polling by using `task.result()`.

```python
task = device.run(bell, s3_folder, poll_timeout_seconds=86400)  # 1 day 
print(task.result().measurement_counts)
```

To select a quantum hardware device, specify its ARN as the value of the `device_arn` argument. A list of available quantum devices and their features can be found in the [Amazon Braket Developer Guide](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html).

**Important** Tasks may not run immediately on the QPU. The QPUs only execute tasks during execution windows. To find their execution windows, please refer to the [AWS console](https://console.aws.amazon.com/braket/home) in the "Devices" tab.

### Using Amazon Braket with D-Wave QPU
If you want to use [Ocean](https://docs.ocean.dwavesys.com/en/latest/) with the D-Wave QPU, you can install the [amazon-braket-ocean-plugin-python](https://github.com/aws/amazon-braket-ocean-plugin-python). Information about how to install the plugin is provided in the [README](https://github.com/aws/amazon-braket-ocean-plugin-python/blob/master/README.md) for the repo.

## Sample Notebooks
Sample Jupyter notebooks can be found in the [amazon-braket-examples](https://github.com/aws/amazon-braket-examples/) repo.

## Braket Python SDK API Reference Documentation

The API reference, can be found on [Read the Docs](https://amazon-braket-sdk-python.readthedocs.io/en/latest/).

**To generate the API Reference HTML in your local environment**

To generate the HTML, first change directories (`cd`) to position the cursor in the `amazon-braket-sdk-python` directory. Then, run the following command to generate the HTML documentation files:

```bash
pip install tox
tox -e docs
```

To view the generated documentation, open the following file in a browser:
`../amazon-braket-sdk-python/build/documentation/html/index.html`

## Testing

This repository has both unit and integration tests.

To run the tests, make sure to install test dependencies first:

```bash
pip install -e "amazon-braket-sdk-python[test]"
```

### Unit Tests

To run the unit tests:

```bash
tox -e unit-tests
```

You can also pass in various pytest arguments to run selected tests:

```bash
tox -e unit-tests -- your-arguments
```

For more information, please see [pytest usage](https://docs.pytest.org/en/stable/usage.html).

To run linters and doc generators and unit tests:

```bash
tox
```

### Integration Tests

First, configure a profile to use your account to interact with AWS. To learn more, see [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

After you create a profile, use the following command to set the `AWS_PROFILE` so that all future commands can access your AWS account and resources.

```bash
export AWS_PROFILE=YOUR_PROFILE_NAME
```
To run the integration tests for local jobs, you need to have Docker installed and running. To install Docker follow these instructions: [Install Docker](https://docs.docker.com/get-docker/)

Run the tests:

```bash
tox -e integ-tests
```

As with unit tests, you can also pass in various pytest arguments:

```bash
tox -e integ-tests -- your-arguments
```

## Support

### Issues and Bug Reports

If you encounter bugs or face issues while using the SDK, please let us know by posting 
the issue on our [Github issue tracker](https://github.com/aws/amazon-braket-sdk-python/issues/).  
For issues with the Amazon Braket service in general, please use the [Developer Forum](https://forums.aws.amazon.com/forum.jspa?forumID=370).

### Feedback and Feature Requests

If you have feedback or features that you would like to see on Amazon Braket, we would love to hear from you!  
[Github issues](https://github.com/aws/amazon-braket-sdk-python/issues/) is our preferred mechanism for collecting feedback and feature requests, allowing other users 
to engage in the conversation, and +1 issues to help drive priority. 

## License
This project is licensed under the Apache-2.0 License.
