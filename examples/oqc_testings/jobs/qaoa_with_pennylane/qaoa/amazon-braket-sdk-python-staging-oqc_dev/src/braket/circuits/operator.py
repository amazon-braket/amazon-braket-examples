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

from abc import ABC, abstractmethod


class Operator(ABC):
    """An operator is the abstract definition of an operation for a quantum device."""

    @property
    @abstractmethod
    def name(self) -> str:
        """str: The name of the operator."""

    @abstractmethod
    def to_ir(self, *args, **kwargs):
        """
        Converts the operator into the canonical intermediate representation.
        If the operator is passed in a request, this method is called before it is passed.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
