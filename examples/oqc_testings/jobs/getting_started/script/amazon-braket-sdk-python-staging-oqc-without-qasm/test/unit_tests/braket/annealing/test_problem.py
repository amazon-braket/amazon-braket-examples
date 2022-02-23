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

import braket.ir.annealing as ir
from braket.annealing.problem import Problem, ProblemType


def test_creation():
    problem = Problem(ProblemType.ISING, linear={1: 3.14}, quadratic={(1, 2): 10.08})
    assert problem.problem_type == ProblemType.ISING
    assert problem.linear == {1: 3.14}
    assert problem.quadratic == {(1, 2): 10.08}


def test_add_linear_term():
    problem = Problem(ProblemType.QUBO)
    problem.add_linear_term(1, 3.14)
    assert problem.linear == {1: 3.14}


def test_add_linear_terms():
    problem = Problem(ProblemType.QUBO)
    problem.add_linear_terms({1: 3.14})
    assert problem.linear == {1: 3.14}


def test_add_quadratic_term():
    problem = Problem(ProblemType.QUBO)
    problem.add_quadratic_term((1, 2), 10.08)
    assert problem.quadratic == {(1, 2): 10.08}


def test_add_quadratic_terms():
    problem = Problem(ProblemType.QUBO)
    problem.add_quadratic_terms({(1, 2): 10.08})
    assert problem.quadratic == {(1, 2): 10.08}


def test__to_ir():
    problem = Problem(ProblemType.QUBO).add_linear_term(1, 3.14).add_quadratic_term((1, 2), 10.08)
    assert problem.to_ir() == ir.Problem(
        type=ir.ProblemType.QUBO, linear={1: 3.14}, quadratic={"1,2": 10.08}
    )
