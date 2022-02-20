# Changelog

## v1.14.0 (2022-02-02)

### Features

 * adding TwoQubitPauliChannel

## v1.13.0 (2022-01-27)

### Features

 * added controlled-sqrt-not gate

## v1.12.0 (2022-01-25)

### Features

 * Added is_available property to AwsDevice
 * optimize IAM role retrieval

### Bug Fixes and Other Changes

 * Enable jobs integration tests

## v1.11.1 (2021-12-09)

### Bug Fixes and Other Changes

 * remove extraneous reference from local job container setup

## v1.11.0 (2021-12-02)

### Features

 * Adding integration tests for DM1

## v1.10.0 (2021-11-29)

### Features

 * Add support for jobs

### Bug Fixes and Other Changes

 * Skip jobs integration tests

## v1.9.5.post0 (2021-11-04)

### Testing and Release Infrastructure

 * Pin docutils<0.18 in doc requirements

## v1.9.5 (2021-10-05)

### Bug Fixes and Other Changes

- Pin Coverage 5.5

## v1.9.4 (2021-10-04)

### Bug Fixes and Other Changes

- fixed a spelling nit

## v1.9.3 (2021-10-01)

### Bug Fixes and Other Changes

- rigetti typo

## v1.9.2 (2021-09-30)

## v1.9.1 (2021-09-24)

### Bug Fixes and Other Changes

- Have tasks that are failed output the failure reason from tas…

## v1.9.0 (2021-09-09)

### Features

- Verbatim boxes

## v1.8.0 (2021-08-23)

### Features

- Calculate arbitrary observables when `shots=0`

### Bug Fixes and Other Changes

- Remove immutable default args

## v1.7.5 (2021-08-18)

### Bug Fixes and Other Changes

- Add test for local simulator device names

### Documentation Changes

- Add documentation for support

### Testing and Release Infrastructure

- Update copyright notice

## v1.7.4 (2021-08-06)

### Bug Fixes and Other Changes

- Flatten Tensor Products

## v1.7.3.post0 (2021-08-05)

### Documentation Changes

- Modify README.md to include update instructions

## v1.7.3 (2021-07-22)

### Bug Fixes and Other Changes

- Add json schema validation for dwave device schemas.

## v1.7.2 (2021-07-14)

### Bug Fixes and Other Changes

- add json validation for device schema in unit tests

## v1.7.1 (2021-07-02)

### Bug Fixes and Other Changes

- Result Type syntax in IR
- Update test_circuit.py

## v1.7.0 (2021-06-25)

### Features

- code Circuit.as_unitary()

### Bug Fixes and Other Changes

- allow integral number types that aren't type int

## v1.6.5 (2021-06-23)

### Bug Fixes and Other Changes

- Get qubit count without instantiating op
- Require qubit indices to be integers

## v1.6.4 (2021-06-10)

### Bug Fixes and Other Changes

- fallback on empty dict for device level parameters

## v1.6.3 (2021-06-04)

### Bug Fixes and Other Changes

- use device data to create device level parameter data when creating a…

## v1.6.2 (2021-05-28)

### Bug Fixes and Other Changes

- exclude null values from device parameters for annealing tasks

## v1.6.1 (2021-05-25)

### Bug Fixes and Other Changes

- copy the boto3 session using the default botocore session

## v1.6.0.post0 (2021-05-24)

### Documentation Changes

- Add reference to the noise simulation example notebook

## v1.6.0 (2021-05-24)

### Features

- Noise operators

### Testing and Release Infrastructure

- Use GitHub source for tox tests

## v1.5.16 (2021-05-05)

### Bug Fixes and Other Changes

- Added /taskArn to id field in AwsQuantumTask **repr**

### Documentation Changes

- Fix link, typos, order

## v1.5.15 (2021-04-08)

### Bug Fixes and Other Changes

- stop manually managing waiting treads in quantum task batch requests

## v1.5.14 (2021-04-07)

### Bug Fixes and Other Changes

- roll back dwave change
- Dwave roll back
- use device data to create device level parameter data when creating a quantum annealing task

## v1.5.13 (2021-03-26)

### Bug Fixes and Other Changes

- check for task completion before entering async event loop
- remove unneeded get_quantum_task calls

## v1.5.12 (2021-03-25)

### Bug Fixes and Other Changes

- Update user_agent for AwsSession

## v1.5.11 (2021-03-22)

### Bug Fixes and Other Changes

- Fix broken repository links

## v1.5.10.post2 (2021-03-19)

### Testing and Release Infrastructure

- Run unit tests for dependent packages

## v1.5.10.post1 (2021-03-16)

### Documentation Changes

- Remove STS calls from examples

## v1.5.10.post0 (2021-03-11)

### Testing and Release Infrastructure

- Add Python 3.9

## v1.5.10 (2021-03-03)

### Bug Fixes and Other Changes

- Don't return NotImplemented for boolean
- Use np.eye for identity
- AngledGate equality checks angles
- Unitary equality checks matrix
- Remove hardcoded device ARNs

### Documentation Changes

- Wording changes
- Add note about AWS region in README

### Testing and Release Infrastructure

- Use main instead of PyPi for build dependencies
- very minor test changes

## v1.5.9.post0 (2021-02-22)

### Documentation Changes

- remove unneeded calls to sts from the README
- adjust s3_folder naming in README to clarify which bucket to use

## v1.5.9 (2021-02-06)

### Bug Fixes and Other Changes

- Search for unknown QPUs

## v1.5.8 (2021-01-29)

### Bug Fixes and Other Changes

- Remove redundant statement, boost coverage
- convert measurements to indices without allocating a high-dimens…

### Testing and Release Infrastructure

- Raise coverage to 100%

## v1.5.7 (2021-01-27)

### Bug Fixes and Other Changes

- More scalable eigenvalue calculation

## v1.5.6 (2021-01-21)

### Bug Fixes and Other Changes

- ensure AngledGate casts its angle argument to float so it can be…

## v1.5.5 (2021-01-15)

### Bug Fixes and Other Changes

- get correct event loop for task results after running a batch over multiple threads

## v1.5.4 (2021-01-12)

### Bug Fixes and Other Changes

- remove window check for polling-- revert to polling at all times
- update result_types to use hashing

### Testing and Release Infrastructure

- Enable Codecov

## v1.5.3 (2020-12-31)

### Bug Fixes and Other Changes

- Update range of random qubit in test_qft_iqft_h

## v1.5.2.post0 (2020-12-30)

### Testing and Release Infrastructure

- Add build badge
- Use GitHub Actions for CI

## v1.5.2 (2020-12-22)

### Bug Fixes and Other Changes

- Get regions for QPUs instead of providers
- Do not search for simulators in wrong region

## v1.5.1 (2020-12-10)

### Bug Fixes and Other Changes

- Use current region for simulators in get_devices

## v1.5.0 (2020-12-04)

### Features

- Always accept identity observable factors

### Documentation Changes

- backticks for batching tasks
- add punctuation to aws_session.py
- fix backticks, missing periods in quantum task docs
- fix backticks, grammar for aws_device.py

## v1.4.1 (2020-12-04)

### Bug Fixes and Other Changes

- Correct integ test bucket

## v1.4.0.post0 (2020-12-03)

### Documentation Changes

- Point README to developer guide

## v1.4.0 (2020-11-26)

### Features

- Enable retries when retrieving results from AwsQuantumTaskBatch.

## v1.3.1 (2020-11-25)

## v1.3.0 (2020-11-23)

### Features

- Enable explicit qubit allocation
- Add support for batch execution

### Bug Fixes and Other Changes

- Correctly cache status

## v1.2.0 (2020-11-02)

### Features

- support tags parameter for create method in AwsQuantumTask

## v1.1.4.post0 (2020-10-30)

### Testing and Release Infrastructure

- update codeowners

## v1.1.4 (2020-10-29)

### Bug Fixes and Other Changes

- Enable simultaneous measurement of observables with shared factors
- Add optimization to only poll during execution window

## v1.1.3 (2020-10-20)

### Bug Fixes and Other Changes

- add observable targets not in instructions to circuit qubit count and qubits

## v1.1.2.post1 (2020-10-15)

### Documentation Changes

- add sample notebooks link

## v1.1.2.post0 (2020-10-05)

### Testing and Release Infrastructure

- change check for s3 bucket exists
- change bucket creation setup for integ tests

## v1.1.2 (2020-10-02)

### Bug Fixes and Other Changes

- Add error for target qubit set size not equal to operator qubit size in instruction
- Add error message for running a circuit without instructions

### Documentation Changes

- Update docstring for measurement_counts

## v1.1.1.post2 (2020-09-29)

### Documentation Changes

- Add D-Wave Advantage_system1 arn

## v1.1.1.post1 (2020-09-10)

### Testing and Release Infrastructure

- fix black formatting

## v1.1.1.post0 (2020-09-09)

### Testing and Release Infrastructure

- Add CHANGELOG.md

## v1.1.1 (2020-09-09)

### Bug Fixes

- Add handling for solution_counts=[] for annealing result

## v1.1.0 (2020-09-08)

### Features

- Add get_devices to search devices based on criteria

### Bug Fixes

- Call async_result() before calling result()
- Convert amplitude result to a complex number

## v1.0.0.post1 (2020-08-14)

### Documentation

- add readthedocs link to README

## v1.0.0 (2020-08-13)

This is the public release of the Amazon Braket Python SDK!

The Amazon Braket Python SDK is an open source library that provides a framework that you can use to interact with quantum computing devices through Amazon Braket.
