# Changelog

## v1.7.1 (2022-02-01)

### Bug Fixes and Other Changes

- multiqubit pauli channel with multitarget

## v1.7.0 (2022-02-01)

### Features

- adding MultiQubitPauliChannel to ir

### Bug Fixes and Other Changes

- Relax requirements from pydantic

## v1.6.0 (2022-01-27)

### Features

- add control-sqrt-not gate

## v1.5.1 (2022-01-04)

### Bug Fixes and Other Changes

- change annealingDurationRange to a list of floats.

## v1.5.0 (2021-11-29)

### Features

- Add support for jobs

## v1.4.1 (2021-09-30)

## v1.4.0.post0 (2021-09-10)

### Documentation Changes

- Fix jaqcd typo in README.md

## v1.4.0 (2021-09-02)

### Features

- StartVerbatimBox and EndVerbatimBox

### Bug Fixes and Other Changes

- Update copyright headers

## v1.3.0 (2021-08-05)

### Features

- support for StartPreserveBlock and EndPreserveBlock instructions.

## v1.2.2 (2021-06-04)

### Bug Fixes and Other Changes

- fix d-wave schema constraints

## v1.2.1 (2021-05-26)

### Bug Fixes and Other Changes

- Add schema helper methods, modify device level tests, and fix some docs

## v1.2.0 (2021-05-24)

### Features

- Noise operators

### Bug Fixes and Other Changes

- Revert "fix: change documentation for deviceLevelParameters (#86)"
- change documentation for deviceLevelParameters

### Testing and Release Infrastructure

- tox for GitHub checks

## v1.1.4 (2021-05-11)

### Bug Fixes and Other Changes

- allow null values to be passed in for optional parameters

## v1.1.3 (2021-04-16)

### Bug Fixes and Other Changes

- move device-specific schemas into their own files

## v1.1.2 (2021-04-15)

### Bug Fixes and Other Changes

- error message typo

## v1.1.1 (2021-03-26)

### Bug Fixes and Other Changes

- add device level parameters and device-specific parameters

## v1.1.0.post6 (2021-03-19)

### Testing and Release Infrastructure

- Run unit tests for dependent packages

## v1.1.0.post5 (2021-03-11)

### Testing and Release Infrastructure

- Add Python 3.9

## v1.1.0.post4 (2021-03-03)

### Testing and Release Infrastructure

- Make python-package consistent with other repos

## v1.1.0.post3 (2021-03-01)

### Documentation Changes

- fix time unit for D-Wave metadata from milliseconds to microseconds

## v1.1.0.post2 (2021-01-06)

### Testing and Release Infrastructure

- Add CodeCov badge
- Upload coverage report to Codecov

## v1.1.0.post1 (2020-12-30)

### Testing and Release Infrastructure

- Add build badge
- Use GitHub Actions for CI

## v1.1.0.post0 (2020-12-04)

### Testing and Release Infrastructure

- Make tox commands consistent with other repos

## v1.1.0 (2020-11-23)

### Features

- Add explicit qubit allocation

## v1.0.3 (2020-11-03)

### Bug Fixes and Other Changes

- Feature/lower latency

## v1.0.2.post2 (2020-10-30)

### Testing and Release Infrastructure

- updating codeowners

## v1.0.2.post1 (2020-09-10)

### Testing and Release Infrastructure

- fix black formatting

## v1.0.2.post0 (2020-09-09)

### Testing and Release Infrastructure

- Add CHANGELOG.md

## v1.0.2 (2020-09-04)

## Bug Fixes

- Update the schema validation for GateModelParameters to be more strict, this will avoid Pydantic to auto convert String integers to int.

## v1.0.1 (2020-08-25)

## Bug Fixes

- Update the Rigetti task result schema to allow for the program duration to be zero.

## v1.0.0.post1 (2020-08-14)

The only way to update a description in PyPi is to upload new files;
however, uploading an existing version is prohibited. The recommended
way to deal with this is with
[post-releases](https://www.python.org/dev/peps/pep-0440/#post-releases).

## v1.0.0 (2020-08-13)

This is the public release of the Amazon Braket Python Schemas!

Amazon Braket Python Schemas is an open source library that contains the schemas for Braket, including:

- intermediate representations (IR) for Amazon Braket quantum tasks and offers serialization and deserialization of those IR payloads. Think of the IR as the contract between the Amazon Braket SDK and Amazon Braket API for quantum programs.
- schemas for the S3 results of each quantum task
- schemas for the device capabilities of each device
