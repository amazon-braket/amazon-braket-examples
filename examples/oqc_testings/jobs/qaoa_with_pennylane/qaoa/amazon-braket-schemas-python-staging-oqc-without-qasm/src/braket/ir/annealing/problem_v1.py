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

from enum import Enum
from typing import Dict, Union

from pydantic import Field, conint

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class ProblemType(str, Enum):
    """The type of annealing problem.

    QUBO: Quadratic Unconstrained Binary Optimization, with values 1 and 0
    ISING: Ising model, with values +/-1
    """

    QUBO = "QUBO"
    ISING = "ISING"


class Problem(BraketSchemaBase):
    """Specifies a quantum annealing problem.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        type (Union[ProblemType, str]): The type of problem; can be either "QUBO" or "ISING"
        linear (Dict[int, float]): Linear terms of the model.
        quadratic (Dict[str, float]): Quadratic terms of the model, keyed on comma-separated
            variables as strings

    Examples:
        >>> Problem(type=ProblemType.QUBO, linear={0: 0.3, 4: -0.3}, quadratic={"0,5": 0.667})
    """

    _PROBLEM_HEADER = BraketSchemaHeader(name="braket.ir.annealing.problem", version="1")
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROBLEM_HEADER, const=_PROBLEM_HEADER)
    type: Union[ProblemType, str]
    linear: Dict[conint(ge=0), float]
    quadratic: Dict[str, float]
