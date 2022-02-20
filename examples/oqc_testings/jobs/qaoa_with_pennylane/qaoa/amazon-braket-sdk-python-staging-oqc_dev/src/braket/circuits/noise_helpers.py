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

import warnings
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, Union

import numpy as np

from braket.circuits.gate import Gate
from braket.circuits.instruction import Instruction
from braket.circuits.moments import Moments
from braket.circuits.noise import Noise
from braket.circuits.quantum_operator_helpers import is_unitary
from braket.circuits.qubit_set import QubitSet, QubitSetInput

if TYPE_CHECKING:  # pragma: no cover
    from braket.circuits.circuit import Circuit


def no_noise_applied_warning(noise_applied: bool):
    "Helper function to give a warning is noise is not applied"
    if noise_applied is False:
        warnings.warn(
            "Noise is not applied to any gate, as there is no eligible gate in the circuit"
            " with the input criteria or there is no multi-qubit gate to apply"
            " the multi-qubit noise."
        )


def wrap_with_list(an_item: Any):
    "Helper function to make the input parameter a list"
    if an_item is not None and not isinstance(an_item, list):
        an_item = [an_item]
    return an_item


def check_noise_target_gates(noise: Noise, target_gates: Iterable[Type[Gate]]):
    """Helper function to check
    1. whether all the elements in target_gates are a Gate type;
    2. if `noise` is multi-qubit noise and `target_gates` contain gates
    with the number of qubits is the same as `noise.qubit_count`.
    Args:
        noise (Noise): A Noise class object to be applied to the circuit.
        target_gates (Union[Type[Gate], Iterable[Type[Gate]]]): Gate class or
            List of Gate classes which `noise` is applied to.
    """

    if not all(isinstance(g, type) and issubclass(g, Gate) for g in target_gates):
        raise TypeError("All elements in target_gates must be an instance of the Gate class")

    if noise.qubit_count > 1:
        for g in target_gates:
            fixed_qubit_count = g.fixed_qubit_count()
            if fixed_qubit_count is NotImplemented:
                raise ValueError(
                    f"Target gate {g} can be instantiated on a variable number of qubits,"
                    " but noise can only target gates with fixed qubit counts."
                )
            if fixed_qubit_count != noise.qubit_count:
                raise ValueError(
                    f"Target gate {g} acts on {fixed_qubit_count} qubits,"
                    f" but {noise} acts on {noise.qubit_count} qubits."
                )


def check_noise_target_unitary(noise: Noise, target_unitary: np.ndarray):
    """Helper function to check
    1. whether the input matrix is a np.ndarray type;
    2. whether the target_unitary is a unitary;

    Args:
        noise (Noise): A Noise class object to be applied to the circuit.
        target_unitary (np.ndarray): matrix of the target unitary gates
    """

    if not isinstance(target_unitary, np.ndarray):
        raise TypeError("target_unitary must be a np.ndarray type")

    if not is_unitary(target_unitary):
        raise ValueError("target_unitary must be a unitary")


def check_noise_target_qubits(
    circuit: Circuit, target_qubits: Optional[QubitSetInput] = None
) -> QubitSet:
    """
    Helper function to check whether all the target_qubits are positive integers.
    Args:
        target_qubits (Optional[QubitSetInput] = None): Index or indices of qubit(s).
    Returns:
        target_qubits: QubitSet
    """
    if target_qubits is None:
        target_qubits = circuit.qubits
    else:
        target_qubits = wrap_with_list(target_qubits)
        if not all(isinstance(q, int) for q in target_qubits):
            raise TypeError("target_qubits must be integer(s)")
        if not all(q >= 0 for q in target_qubits):
            raise ValueError("target_qubits must contain only non-negative integers.")

        target_qubits = QubitSet(target_qubits)

    return target_qubits


def apply_noise_to_moments(
    circuit: Circuit, noise: Iterable[Type[Noise]], target_qubits: QubitSet, position: str
) -> Circuit:
    """
    Apply initialization/readout noise to the circuit.

    When `noise.qubit_count` == 1, `noise` is added to all qubits in `target_qubits`.

    When `noise.qubit_count` > 1, `noise.qubit_count` must be the same as the length of
    `target_qubits`.

    Args:
        circuit (Circuit): A ciruit where `noise` is applied to.
        noise (Iterable[Type[Noise]]): Noise channel(s) to be applied
            to the circuit.
        target_qubits (QubitSet): Index or indices of qubits. `noise` is applied to.

    Returns:
        Circuit: modified circuit.
    """
    noise_instructions = []
    for noise_channel in noise:
        if noise_channel.qubit_count == 1:
            new = [Instruction(noise_channel, qubit) for qubit in target_qubits]
            noise_instructions = noise_instructions + new
        else:
            noise_instructions.append(Instruction(noise_channel, target_qubits))

    new_moments = Moments()

    if position == "initialization":
        for noise in noise_instructions:
            new_moments.add_noise(noise, "initialization_noise")

    # add existing instructions
    for moment_key in circuit.moments:
        instruction = circuit.moments[moment_key]
        # if the instruction is noise instruction
        if isinstance(instruction.operator, Noise):
            new_moments.add_noise(instruction, moment_key.moment_type, moment_key.noise_index)
        # if the instruction is a gate instruction
        else:
            new_moments.add([instruction], moment_key.noise_index)

    if position == "readout":
        for noise in noise_instructions:
            new_moments.add_noise(noise, "readout_noise")

    circuit._moments = new_moments

    return circuit


def _apply_noise_to_gates_helper(
    noise: Iterable[Type[Noise]],
    target_qubits: QubitSet,
    instruction: Instruction,
    noise_index: int,
    intersection: QubitSet,
    noise_applied: bool,
    new_noise_instruction: Iterable,
):
    """Helper function to work out the noise instructions to be attached to a gate.

    Args:
        noise (Iterable[Type[Noise]]): Noise channel(s) to be applied
            to the circuit.
        target_qubits (QubitSet): Index or indices of qubits which `noise` is applied to.
        instruction (Instruction): Instruction of the gate which `noise` is applied to.
        noise_index (int): The number of noise channels applied to the gate.
            intersection (QubitSet): Intersection of target_qubits and the qubits associated
            with the gate.
        noise_applied (bool): Whether noise is applied or not.
            new_noise_instruction (Iterable): current new noise instructions to be attached
            to the circuit.

    Returns:
        new_noise_instruction: A list of noise intructions
        noise_index: The number of noise channels applied to the gate
        noise_applied: Whether noise is applied or not
    """

    for noise_channel in noise:
        if noise_channel.qubit_count == 1:
            for qubit in intersection:
                # apply noise to the qubit if it is in target_qubits
                noise_index += 1
                new_noise_instruction.append((Instruction(noise_channel, qubit), noise_index))
                noise_applied = True
        else:
            # only apply noise to the gates that have the same qubit_count as the noise.
            if (
                instruction.operator.qubit_count == noise_channel.qubit_count
                and instruction.target.issubset(target_qubits)
            ):
                noise_index += 1
                new_noise_instruction.append(
                    (Instruction(noise_channel, instruction.target), noise_index)
                )
                noise_applied = True

    return new_noise_instruction, noise_index, noise_applied


def apply_noise_to_gates(
    circuit: Circuit,
    noise: Iterable[Type[Noise]],
    target_gates: Union[Iterable[Type[Gate]], np.ndarray],
    target_qubits: QubitSet,
) -> Circuit:
    """Apply noise after target gates in target qubits.

    When `noise.qubit_count` == 1, `noise` is applied to target_qubits after `target_gates`.

    When `noise.qubit_count` > 1, all elements in `target_gates`, if is given, must have
    the same number of qubits as `noise.qubit_count`.

    Args:
        circuit (Circuit): A ciruit where `noise` is applied to.
        noise (Iterable[Type[Noise]]): Noise channel(s) to be applied
            to the circuit.
        target_gates (Union[Iterable[Type[Gate]], np.ndarray]): List of gates, or a unitary matrix
            which `noise` is applied to.
        target_qubits (QubitSet): Index or indices of qubits which `noise` is applied to.

    Returns:
        Circuit: modified circuit.

    Raises:
        Warning:
            If `noise` is multi-qubit noise while there is no gate with the same
            number of qubits in `target_qubits` or in the whole circuit when
            `target_qubits` is not given.
            If no `target_gates` exist in `target_qubits` or in the whole circuit
            when `target_qubits` is not given.
    """

    new_moments = Moments()
    noise_applied = False

    for moment_key in circuit.moments:
        instruction = circuit.moments[moment_key]

        # add the instruction to new_moments if it is noise instruction
        if isinstance(instruction.operator, Noise):
            new_moments.add_noise(instruction, moment_key.moment_type, moment_key.noise_index)

        # if the instruction is a gate instruction
        else:
            new_noise_instruction = []
            noise_index = moment_key.noise_index
            if isinstance(target_gates, np.ndarray):
                if (instruction.operator.name == "Unitary") and (
                    np.array_equiv(instruction.operator._matrix, target_gates)
                ):
                    intersection = list(set(instruction.target) & set(target_qubits))
                    (
                        new_noise_instruction,
                        noise_index,
                        noise_applied,
                    ) = _apply_noise_to_gates_helper(
                        noise,
                        target_qubits,
                        instruction,
                        noise_index,
                        intersection,
                        noise_applied,
                        new_noise_instruction,
                    )

            elif (target_gates is None) or (
                instruction.operator.name in [g.__name__ for g in target_gates]
            ):
                intersection = list(set(instruction.target) & set(target_qubits))
                new_noise_instruction, noise_index, noise_applied = _apply_noise_to_gates_helper(
                    noise,
                    target_qubits,
                    instruction,
                    noise_index,
                    intersection,
                    noise_applied,
                    new_noise_instruction,
                )

            # add the gate and gate noise instructions to new_moments
            new_moments.add([instruction], noise_index=noise_index)
            for instruction, noise_index in new_noise_instruction:
                new_moments.add_noise(instruction, "gate_noise", noise_index)

    no_noise_applied_warning(noise_applied)
    circuit._moments = new_moments
    return circuit
