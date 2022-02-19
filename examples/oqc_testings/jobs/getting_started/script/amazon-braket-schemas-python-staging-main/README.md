# Amazon Braket Python Schemas

[![Latest Version](https://img.shields.io/pypi/v/amazon-braket-schemas.svg)](https://pypi.python.org/pypi/amazon-braket-schemas)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/amazon-braket-schemas.svg)](https://pypi.python.org/pypi/amazon-braket-schemas)
[![Build Status](https://img.shields.io/github/workflow/status/aws/amazon-braket-schemas-python/Python%20package/main?logo=github)](https://github.com/aws/amazon-braket-schemas-python/actions?query=workflow%3A%22Python+package%22)
[![codecov](https://codecov.io/gh/aws/amazon-braket-schemas-python/branch/main/graph/badge.svg?token=XV9R0dUbr1)](https://codecov.io/gh/aws/amazon-braket-schemas-python)
[![Documentation Status](https://img.shields.io/readthedocs/amazon-braket-schemas-python.svg?logo=read-the-docs)](https://amazon-braket-schemas-python.readthedocs.io/en/latest/?badge=latest)
[![Code Style: Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)

Amazon Braket Python Schemas is an open source library that contains the schemas for Braket, including:
* intermediate representations (IR) for Amazon Braket quantum tasks and offers serialization and deserialization of those IR payloads. Think of the IR as the contract between the Amazon Braket SDK and Amazon Braket API for quantum programs.
* schemas for the S3 results of each quantum task
* schemas for the device capabilities of each device

## Installation

### Prerequisites
- Python 3.7+

### Steps

The preferred way to get Amazon Braket Python Schemas is by installing the [Amazon Braket Python SDK](https://github.com/aws/amazon-braket-sdk-python), which will pull in the schemas.
Follow the instructions in the [README](https://github.com/aws/amazon-braket-sdk-python/blob/main/README.md) for setup.

However, if you only want to use the schemas, it can be installed on its own as follows:

```shell
pip install amazon-braket-schemas
```

You can install from source by cloning this repository and running a pip install command in the root directory of the repository:

```shell
git clone https://github.com/aws/amazon-braket-schemas-python.git
cd amazon-braket-schemas-python
pip install .
```

You can check your currently installed version of `amazon-braket-schemas` with `pip show`:

```shell
pip show amazon-braket-schemas
```

or alternatively from within Python:

```
>>> import braket._schemas as braket_schemas
>>> braket_schemas.__version__
```

## Usage
There are currently two types of IR, including jaqcd (JsonAwsQuantumCircuitDescription) and annealing. See below for their usage.

**Serializing python structures**
```python
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.ir.jaqcd import CNot, H
from braket.ir.gate_model_shared import Expectation
from braket.ir.jaqcd import Program as JaqcdProgram
from braket.ir.annealing import Problem, ProblemType

program = OpenQASMProgram(source="OPENQASM 3.0; cnot $0, $1;")
print(program.json(indent=2))

"""
{
  "braketSchemaHeader": {
    "name": "braket.ir.openqasm.program",
    "version": "1"
  },
  "source": "OPENQASM 3.0; cnot $0, $1;",
}
"""

program = JaqcdProgram(instructions=[H(target=0), CNot(control=0, target=1)])
print(program.json(indent=2))

"""
{
  "braketSchemaHeader": {
    "name": "braket.ir.jaqcd.program",
    "version": "1"
  },
  "instructions": [
    {
      "target": 0,
      "type": "h"
    },
    {
      "control": 0,
      "target": 1,
      "type": "cnot"
    }
  ],
  "results": null,
  "basis_rotation_instructions": null,
}
"""

program = JaqcdProgram(
    instructions=[H(target=0), CNot(control=0, target=1)],
    results=[Expectation(targets=[0], observable=['x'])],
    basis_rotation_instructions=[H(target=0)]
)
print(program.json(indent=2))

"""
{
  "braketSchemaHeader": {
    "name": "braket.ir.jaqcd.program",
    "version": "1"
  },
  "instructions": [
    {
      "target": 0,
      "type": "h"
    },
    {
      "control": 0,
      "target": 1,
      "type": "cnot"
    }
  ],
  "results": [
    {
      "observable": [
        "x"
      ],
      "targets": [
        0
      ],
      "type": "expectation"
    }
  ],
  "basis_rotation_instructions": [
    {
      "target": 0,
      "type": "h"
    }
  ]
}
"""

problem = Problem(type=ProblemType.QUBO, linear={0: 0.3, 4: -0.3}, quadratic={"0,5": 0.667})
print(problem.json(indent=2))

"""
{
  "braketSchemaHeader": {
    "name": "braket.ir.annealing.problem",
    "version": "1"
  },
  "type": "QUBO",
  "linear": {0: 0.3, 4: -0.3},
  "quadratic": {"0,5": 0.667}
}
"""
```

**Deserializing into python structures**
```python
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.ir.jaqcd import Program as JaqcdProgram
from braket.ir.annealing import Problem

openqasm_string = """
{
  "braketSchemaHeader": {
    "name": "braket.ir.openqasm.program",
    "version": "1"
  },
  "source": "OPENQASM 3.0; cnot $0, $1;",
}"""

program = OpenQASMProgram.parse_raw(openqasm_string)
print(program)

"""
braketSchemaHeader=BraketSchemaHeader(name='braket.ir.openqasm.program', version='1') source='OPENQASM 3.0; cnot $0, $1;'
"""

jaqcd_string = """
{
  "instructions": [
    {
      "target": 0,
      "type": "h"
    },
    {
      "control": 0,
      "target": 1,
      "type": "cnot"
    }
  ],
  "results": [
    {
      "observable": [
        "x"
      ],
      "targets": [
        0
      ],
      "type": "expectation"
    }
  ],
  "basis_rotation_instructions": [
    {
      "target": 0,
      "type": "h"
    }
  ]
}
"""

program = JaqcdProgram.parse_raw(jaqcd_string)
print(program)

"""
braketSchemaHeader=BraketSchemaHeader(name='braket.ir.jaqcd.program', version='1') instructions=[H(target=0, type=<Type.h: 'h'>), CNot(control=0, target=1, type=<Type.cnot: 'cnot'>)] results=[Expectation(observable=['x'], targets=[0], type=<Type.expectation: 'expectation'>)] basis_rotation_instructions=[H(target=0, type=<Type.h: 'h'>)]
"""

annealing_string = """
{
  "type": "QUBO",
  "linear": {0: 0.3, 4: -0.3},
  "quadratic": {"0,5": 0.667}
}
"""

problem = Problem.parse_raw(annealing_string)
print(problem)

"""
braketSchemaHeader=BraketSchemaHeader(name='braket.ir.annealing.problem', version='1') type=<ProblemType.QUBO: 'QUBO'>, linear={0: 0.3, 4: -0.3}, quadratic={'0,5': 0.667}
"""

```

## Documentation

Detailed documentation, including the API reference, can be found on [Read the Docs](https://amazon-braket-schemas-python.readthedocs.io/en/latest/).

You can also generate the docs from source. First, install tox:

```shell
pip install tox
```

To build the Sphinx docs, run the following command in the root repo directory:

```shell
tox -e docs
```

You can then find the generated HTML files in `build/documentation/html`.

## Testing

Make sure to install test dependencies first:

```shell
pip install -e "amazon-braket-schemas-python[test]"
```

To run the unit tests:
```bash
tox -e unit-tests
```

You can also pass in various pytest arguments to run selected tests:

```bash
tox -e unit-tests -- your-arguments
```

To run linters and doc generators and unit tests:
```bash
tox
```

For more information, please see [pytest usage](https://docs.pytest.org/en/stable/usage.html).

## License

This project is licensed under the Apache-2.0 License.
