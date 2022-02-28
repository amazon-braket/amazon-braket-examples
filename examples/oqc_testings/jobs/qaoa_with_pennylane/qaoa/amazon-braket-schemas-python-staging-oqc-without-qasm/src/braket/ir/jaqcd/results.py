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

from pydantic import BaseModel

from braket.ir.jaqcd.shared_models import MultiState, Observable, OptionalMultiTarget


class Expectation(OptionalMultiTarget, Observable):
    """
    Expectation of specified targets and observable as requested result.
    If no targets are specified, the observable must only operate on 1 qubit and it
    will be applied to all qubits in parallel. Otherwise, the number of specified targets
    must be equivalent to the number of qubits the observable can be applied to.

    Attributes:
        type (str): The result type. default = "expectation". (type) is optional.
            This should be unique among all result types.
        targets (Optional[List[int]]): The target qubits. This is a list of int >= 0.
        observable (List[Union[str, List[List[List[float]]]]): A list with at least
            one item and items are strings matching the observable regex
            or a two dimensional hermitian matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.

    Examples:
        >>> Expectation(targets=[1], observable=["x"])
    """

    class Type(str, Enum):
        expectation = "expectation"

    type = Type.expectation


class Sample(OptionalMultiTarget, Observable):
    """
    Sample for specified targets and observable as requested result.
    If no targets are specified, the observable must only operate on 1 qubit and it
    will be applied to all qubits in parallel. Otherwise, the number of specified targets
    must be equivalent to the number of qubits the observable can be applied to.

    Attributes:
        type (str): The result type. default = "sample". (type) is optional.
            This should be unique among all result types.
        targets (Optional[List[int]]): The target qubits. This is a list of int >= 0.
        observable (List[Union[str, List[List[List[float]]]]): A list with at least
            one item and items are strings matching the observable regex
            or a two dimensional hermitian matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.

    Examples:
        >>> Sample(targets=[1], observable=["x"])
    """

    class Type(str, Enum):
        sample = "sample"

    type = Type.sample


class Variance(OptionalMultiTarget, Observable):
    """
    Variance of specified targets and observables as requested result.
    If no targets are specified, the observable must only operate on 1 qubit and it
    will be applied to all qubits in parallel. Otherwise, the number of specified targets
    must be equivalent to the number of qubits the observable can be applied to.

    Attributes:
        type (str): The result type. default = "variance". (type) is optional.
            This should be unique among all result types.
        targets (List[int]): The target qubits. This is a list of int >= 0.
        observable (List[Union[str, List[List[List[float]]]]): A list with at least
            one item and items are strings matching the observable regex
            or a two dimensional hermitian matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.

    Examples:
        >>> Variance(targets=[1], observable=["x"])
    """

    class Type(str, Enum):
        variance = "variance"

    type = Type.variance


class StateVector(BaseModel):
    """
    The full state vector as requested result.

    Attributes:
        type (str): The result type. default = "statevector". (type) is optional.
            This should be unique among all result types.

    Examples:
        >>> StateVector()
    """

    class Type(str, Enum):
        statevector = "statevector"

    type = Type.statevector


class DensityMatrix(OptionalMultiTarget):
    """
    The density matrix as requested result.

    Attributes:
        type (str): The result type. default = "densitymatrix". (type) is optional.
            This should be unique among all result types.
        targets (Optional[List[int]]): The target qubits of the reduced density matrix.
        This is a list of int >= 0.

    Examples:
        >>> DensityMatrix()
    """

    class Type(str, Enum):
        densitymatrix = "densitymatrix"

    type = Type.densitymatrix


class Amplitude(MultiState):
    """
    Amplitudes of specified states as requested result.

    Attributes:
        type (str): The result type. default = "amplitude". (type) is optional.
            This should be unique among all result types.
        states (List[string]): Variable length list with with all strings
            matching the state regex

    Examples:
        >>> Amplitude(states=["01", "10"])
    """

    class Type(str, Enum):
        amplitude = "amplitude"

    type = Type.amplitude


class Probability(OptionalMultiTarget):
    """
    Probability of all states if no targets are specified or the marginal probability
        of a restricted set of states if only a subset of all qubits are specified as targets

    Attributes:
        type (str): The result type. default = "probability". (type) is optional.
            This should be unique among all result types.
        targets (Optional[List[int]]): The target qubits. This is a list of int >= 0.

    Examples:
        >>> Probability(targets=[1, 2])
    """

    class Type(str, Enum):
        probability = "probability"

    type = Type.probability
