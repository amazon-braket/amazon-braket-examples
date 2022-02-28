# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
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

import pytest
from pydantic import ValidationError

from braket.ir.annealing.problem_v1 import Problem, ProblemType


def test_creation():
    problem = Problem(
        type=ProblemType.QUBO,
        linear={0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333},
        quadratic={"0,4": 0.667, "0,5": -1, "1,4": 0.667, "1,5": 0.667},
    )
    assert problem.type == ProblemType.QUBO
    assert problem.linear == {0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333}
    assert problem.quadratic == {"0,4": 0.667, "0,5": -1, "1,4": 0.667, "1,5": 0.667}
    assert Problem.parse_raw(problem.json()) == problem
    assert problem == Problem.parse_raw_schema(problem.json())


@pytest.mark.xfail(raises=ValidationError)
def test__missing_type():
    Problem(
        linear={0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333},
        quadratic={"0,4": 0.667, "0,5": -1, (1, 4): 0.667, "1,5": 0.667},
    )


@pytest.mark.xfail(raises=ValidationError)
def test_missing_linear():
    Problem(type=ProblemType.QUBO, quadratic={"0,4": 0.667, "0,5": -1, "1,4": 0.667, "1,5": 0.667})


@pytest.mark.xfail(raises=ValidationError)
def test_missing_quadratic():
    Problem(type=ProblemType.ISING, linear={0: 0.3333, 1: -0.333, 4: -0.333, 5: 0.333})
