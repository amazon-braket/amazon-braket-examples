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

import numbers
from typing import Union

QubitInput = Union["Qubit", int]


class Qubit(int):
    """
    A quantum bit index. The index of this qubit is locally scoped towards the contained
    circuit. This may not be the exact qubit index on the quantum device.
    """

    def __new__(cls, index: int):
        """
        Args:
            index (int): Index of the qubit.

        Raises:
            ValueError: If `index` is less than zero.

        Examples:
            >>> Qubit(0)
            >>> Qubit(1)
        """
        if not isinstance(index, numbers.Integral):
            raise TypeError(f"Supplied qubit index, {index}, must be an integer.")
        if index < 0:
            raise ValueError(f"Supplied qubit index, {index}, cannot be less than zero.")
        return super().__new__(cls, index)

    def __repr__(self):
        return f"Qubit({super().__repr__()})"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def new(qubit: QubitInput) -> Qubit:
        """
        Helper constructor - if input is a `Qubit` it returns the same value,
        else a new `Qubit` is constructed.

        Args:
            qubit (int or Qubit): `Qubit` index. If `type == Qubit` then the `qubit` is returned.
        """

        if isinstance(qubit, Qubit):
            return qubit
        else:
            return Qubit(qubit)
