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

from typing import Dict, Optional, Union

from pydantic import BaseModel, confloat, conint, conlist, constr, root_validator


class SingleTarget(BaseModel):
    """
    Single target index.

    Attributes:
        target (int): The target index. This is an int >= 0.

    Examples:
        >>> SingleTarget(target=0)
    """

    target: conint(ge=0)


class DoubleTarget(BaseModel):
    """
    Target indices of length 2.

    Attributes:
        targets (List[int]): A list with two items and all items are int >= 0.

    Examples:
        >>> DoubleTarget(targets=[0, 1])
    """

    targets: conlist(conint(ge=0), min_items=2, max_items=2)


class MultiTarget(BaseModel):
    """
    Variable length target indices.

    Attributes:
        targets (List[int]): A list with items that are all int >= 0.

    Examples:
        >>> MultiTarget(targets=[0, 1])
    """

    targets: conlist(conint(ge=0), min_items=1)


class OptionalMultiTarget(BaseModel):
    """
    Optional variable length target indices

    Attributes:
        targets (Optional[List[int]]): A list with items that are all int >= 0.

    Examples:
        >>> OptionalMultiTarget(targets=[0, 1])
    """

    targets: Optional[conlist(conint(ge=0), min_items=1)]


class MultiControl(BaseModel):
    """
    Variable length control indices.

    Attributes:
        controls (List[int]): A list with at least two items and all items are int >= 0.

    Examples:
        >>> MultiControl(controls=[0, 1])
    """

    controls: conlist(conint(ge=0), min_items=1)


class DoubleControl(BaseModel):
    """
    Control indices of length 2.

    Attributes:
        controls (List[int]): A list with two items and all items are int >= 0.

    Examples:
        >>> DoubleControl(targets=[0, 1])
    """

    controls: conlist(conint(ge=0), min_items=2, max_items=2)


class SingleControl(BaseModel):
    """
    Single control index.

    Attributes:
        control (int): The control index. This is an int >= 0.

    Examples:
        >>> SingleControl(control=0)
    """

    control: conint(ge=0)


class Angle(BaseModel):
    """
    Single angle in radians (floating point).

    Attributes:
        angle (float): The angle in radians.
            inf, -inf, and NaN are not allowable inputs.

    Examples:
        >>> Angle(angle=0.15)
    """

    angle: confloat(gt=float("-inf"), lt=float("inf"))


class SingleProbability(BaseModel):
    """
    A single probability parameter for bit/phase flip noise channel.
    The probability range is [0,0.5] to make the channel meaningful.

    Attributes:
        probability (float): The probability for noise channel.
            NaN is not an allowable input.

    Examples:
        >>> SingleProbability(probability=0.1)
    """

    probability: confloat(ge=float("0.0"), le=float("0.5"))


class SingleProbability_34(BaseModel):
    """
    A single probability parameter for depolarizing/two-qubit-dephasing noise channel.
    The probability range is [0,3/4], as the channel is fully mixing at p = 3/4.

    Attributes:
        probability (float): The probability for noise channel.
            NaN is not an allowable input.

    Examples:
        >>> SingleProbability_34(probability=0.5)
    """

    probability: confloat(ge=float("0.0"), le=float("0.75"))


class SingleProbability_1516(BaseModel):
    """
    A single probability parameter for two-qubit-depolarizing noise channel.
    The probability range is [0,15/16], as the channel is fully mixing at p = 15/16.

    Attributes:
        probability (float): The probability for noise channel.
            NaN is not an allowable input.

    Examples:
        >>> SingleProbability_1516(probability=0.1)
    """

    probability: confloat(ge=float("0.0"), le=float("0.9375"))


class DampingProbability(BaseModel):
    """
    The parameter for the amplitude/phase damping channel

    Attributes:
        gamma (float): The probability of damping

    Examples:
        >>> DampingProbability(gamma=0.1)
    """

    gamma: confloat(ge=float("0.0"), le=float("1.0"))


class DampingSingleProbability(BaseModel):
    """
    The parameter for the generalized amplitude damping channel

    Attributes:
        gamma (float): The probability of damping

    Examples:
        >>> DampingSingleProbability(probability=0.1)
    """

    probability: confloat(ge=float("0.0"), le=float("1.0"))


class TripleProbability(BaseModel):
    """
    A triple-probability parameter set for the Pauli noise channel.

    Attributes:
        probX (float), probY (float), probZ (float): The coefficients of the
        Pauli channel

    Examples:
        >>> TripleProbability(probX=0.1, probY=0.2, probZ=0.3)
    """

    probX: confloat(ge=float("0.0"), le=float("1.0"))
    probY: confloat(ge=float("0.0"), le=float("1.0"))
    probZ: confloat(ge=float("0.0"), le=float("1.0"))

    @root_validator
    def validate_probabilities(cls, values):
        """
        Pydantic uses the validation subsystem to create objects. This custom validator has
        the purpose to ensure probX + probY + probZ <= 1.
        """
        p1, p2, p3 = values.get("probX"), values.get("probY"), values.get("probZ")
        if p1 + p2 + p3 > 1:
            raise ValueError("Sum of probabilities cannot exceed 1.")
        return values


class MultiProbability(BaseModel):
    """A multi-value-probability parameter set for the Pauli noise channel.

    Attributes:
        probabilities [Dict[str, float]]: The coefficients of the Pauli channel

    Examples:
        >>> MultiProbability(probabilities={"X": 0.1})
        >>> MultiProbability(probabilities={"XY": 0.1, "YX": 0.01})
    """

    probabilities: Dict[
        constr(regex="^[IXYZ]+$", min_length=1), confloat(ge=float("0.0"), le=float("1.0"))
    ]

    @root_validator
    def validate_probabilities(cls, values):
        """
        Pydantic uses the validation subsystem to create objects.
        This custom validator has the purpose to ensure sum(probabilities) <= 1
        and that the lengths of each Pauli string are equal.
        """

        probabilities = values.get("probabilities")
        if not probabilities:
            raise ValueError("Pauli dictionary must not be empty.")

        qubit_count = len(list(probabilities)[0])

        if qubit_count * "I" in probabilities.keys():
            i = qubit_count * "I"
            raise ValueError(
                f"{i} is not allowed as a key. Please enter only non-identity Pauli strings."
            )

        for pauli_string, prob in probabilities.items():
            if len(pauli_string) != qubit_count:
                raise ValueError("Length of each Pauli string must be equal to number of qubits.")

        total_prob = sum(probabilities.values())
        if total_prob > 1.0 or total_prob < 0.0:
            raise ValueError(
                f"Total probability must be a real number in the interval [0, 1]. Total probability was {total_prob}."  # noqa: E501
            )

        return values


class TwoDimensionalMatrix(BaseModel):
    """
    Two-dimensional non-empty matrix.

    Attributes:
        matrix (List[List[List[float]]]): Two-dimensional matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.

    Examples:
        >>> TwoDimensionalMatrix(matrix=[[[0, 0], [1, 0]], [[1, 0], [0, 0]]])
    """

    matrix: conlist(
        conlist(
            conlist(confloat(gt=float("-inf"), lt=float("inf")), min_items=2, max_items=2),
            min_items=1,
        ),
        min_items=1,
    )


class TwoDimensionalMatrixList(BaseModel):
    """
    List of two-dimensional non-empty matrices.

    Attributes:
        matrix (List[List[List[List[float]]]]): Two-dimensional matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.
            The number of matrices is limited to 16 and the size of each matrix is limited to 4*4.

    Examples:
        >>> TwoDimensionalMatrixList(matrices=[[[[1, 0], [0, 0]], [[0, 0], [1, 0]]],
                                               [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]
                                              ]
                                    )
    """

    matrices: conlist(
        conlist(
            conlist(
                conlist(confloat(gt=float("-inf"), lt=float("inf")), min_items=2, max_items=2),
                min_items=1,
                max_items=4,
            ),
            min_items=1,
            max_items=4,
        ),
        min_items=1,
        max_items=16,
    )


class Observable(BaseModel):
    """
    An observable. If given list is more than one element, this is the tensor product
    of each operator in the list.

    Attributes:
        observable (List[Union[str, List[List[List[float]]]]): A list with at least
            one item and items are strings matching the observable regex
            or a two-dimensional hermitian matrix with complex entries.
            Each complex number is represented using a List[float] of size 2, with
            element[0] being the real part and element[1] imaginary.
            inf, -inf, and NaN are not allowable inputs for the element.

    Examples:
        >>> Observable(observable=["x"])
        >>> Observable(observable=[[[0, 0], [1, 0]], [[1, 0], [0, 0]]])
    """

    observable: conlist(
        Union[
            constr(regex="(x|y|z|h|i)"),
            conlist(
                conlist(
                    conlist(confloat(gt=float("-inf"), lt=float("inf")), min_items=2, max_items=2),
                    min_items=2,
                ),
                min_items=2,
            ),
        ],
        min_items=1,
    )


class MultiState(BaseModel):
    """
    A list of states in bitstring form.

    Attributes:
        states (List[string]): Variable length list with all strings matching the
            state regex

    Examples:
        >>> lMultiState(states=["10", "10"])
    """

    states: conlist(constr(regex="^[01]+$", min_length=1), min_items=1)


class CompilerDirective(BaseModel):
    """
    A Compiler Directive to preserve a block of code between StartVerbatimBlock
    and EndVerbatimBlock directives.

    Attributes:
        directive (List [StartVerbatimBlock | EndVerbatimBlock])

    Examples:
        >>> CompilerDirective (directive="StartVerbatimBlock")
        >>> CompilerDirective (directive="EndVerbatimBlock")
    """

    directive: constr(regex="^(Start|End)VerbatimBlock$")
