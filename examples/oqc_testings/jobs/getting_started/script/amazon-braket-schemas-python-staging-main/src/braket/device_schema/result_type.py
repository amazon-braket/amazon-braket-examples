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

from typing import List, Optional

from pydantic import BaseModel


class ResultType(BaseModel):
    """
    Provides the result type for a quantum task to return.

    Attributes:

        name: Name of the result type.
        observables: Supported result types for this result type.
        minShots: Minimum number of shots for the results.
        maxShots: Maximum number of shots for the results.

    Examples:
        >>> import json
        >>> input_json = {
        ...     "name": "resultType1",
        ...     "observables": ["observable1"],
        ...     "minShots": 0,
        ...     "maxShots": 4,
        ... }
        >>> ResultType.parse_raw(json.dumps(input_json))
    """

    name: str
    observables: Optional[List[str]]
    minShots: Optional[int]
    maxShots: Optional[int]
