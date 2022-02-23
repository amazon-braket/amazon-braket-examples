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

from __future__ import annotations

from enum import Enum
from typing import Dict, Tuple

import braket.ir.annealing as ir


class ProblemType(str, Enum):
    """The type of annealing problem.

    QUBO: Quadratic Unconstrained Binary Optimization, with values 1 and 0

    ISING: Ising model, with values +/-1
    """

    QUBO = "QUBO"
    ISING = "ISING"


class Problem:
    """Represents an annealing problem."""

    def __init__(
        self,
        problem_type: ProblemType,
        linear: Dict[int, float] = None,
        quadratic: Dict[Tuple[int, int], float] = None,
    ):
        """

        Args:
            problem_type (ProblemType): The type of annealing problem
            linear (Dict[int, float]): The linear terms of this problem,
                as a map of variable to coefficient
            quadratic (Dict[Tuple[int, int], float]): The quadratic terms of this problem,
                as a map of variables to coefficient

        Examples:
            >>> problem = Problem(
            >>>     ProblemType.ISING,
            >>>     linear={1: 3.14},
            >>>     quadratic={(1, 2): 10.08},
            >>> )
            >>> problem.add_linear_term(2, 1.618).add_quadratic_term((3, 4), 1337)
        """
        self._problem_type = problem_type
        self._linear = linear or {}
        self._quadratic = quadratic or {}

    @property
    def problem_type(self) -> ProblemType:
        """The type of annealing problem.

        Returns:
            ProblemType: The type of annealing problem
        """
        return self._problem_type

    @property
    def linear(self) -> Dict[int, float]:
        """The linear terms of this problem.

        Returns:
            Dict[int, float]: The linear terms of this problem, as a map of variable to coefficient
        """
        return self._linear

    @property
    def quadratic(self) -> Dict[Tuple[int, int], float]:
        """The quadratic terms of this problem.

        Returns:
            Dict[Tuple[int, int], float]: The quadratic terms of this problem,
                as a map of variables to coefficient
        """
        return self._quadratic

    def add_linear_term(self, term: int, coefficient: float) -> Problem:
        """Adds a linear term to the problem.

        Args:
            term (int): The variable of the linear term
            coefficient (float): The coefficient of the linear term

        Returns:
            Problem: This problem object
        """
        self._linear[term] = coefficient
        return self

    def add_linear_terms(self, coefficients: Dict[int, float]) -> Problem:
        """Adds linear terms to the problem.

        Args:
            coefficients (Dict[int, float]): A map of variable to coefficient

        Returns:
            Problem: This problem object
        """
        self._linear.update(coefficients)
        return self

    def add_quadratic_term(self, term: Tuple[int, int], coefficient: float) -> Problem:
        """Adds a quadratic term to the problem.

        Args:
            term (Tuple[int, int]): The variables of the quadratic term
            coefficient (flost): The coefficient of the quadratic term

        Returns:
            Problem: This problem object
        """
        self._quadratic[term] = coefficient
        return self

    def add_quadratic_terms(self, coefficients: Dict[Tuple[int, int], float]) -> Problem:
        """Adds quadratic terms to the problem.

        Args:
            coefficients (Dict[Tuple[int, int], float]): A map of variables to coefficient

        Returns:
            Problem: This problem object
        """
        self._quadratic.update(coefficients)
        return self

    def to_ir(self):
        """Converts this problem into IR representation.

        Returns:
            ir.Problem: IR representation of this problem object
        """
        return ir.Problem(
            type=ir.ProblemType[self._problem_type.value],
            linear=self._linear,
            quadratic={
                ",".join((str(q1), str(q2))): self._quadratic[(q1, q2)]
                for q1, q2 in self._quadratic
            },
        )
