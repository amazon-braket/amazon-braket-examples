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
from typing import (
    Dict,
    ItemsView,
    Iterable,
    KeysView,
    List,
    Mapping,
    NamedTuple,
    OrderedDict,
    ValuesView,
)

from braket.circuits.compiler_directive import CompilerDirective
from braket.circuits.instruction import Instruction
from braket.circuits.noise import Noise
from braket.circuits.qubit import Qubit
from braket.circuits.qubit_set import QubitSet


class MomentType(str, Enum):
    """
    The type of moments.
    GATE: a gate
    NOISE: a noise channel added directly to the circuit
    GATE_NOISE: a gate-based noise channel
    INITIALIZATION_NOISE: a initialization noise channel
    READOUT_NOISE: a readout noise channel
    COMPILER_DIRECTIVE: an instruction to the compiler, external to the quantum program itself
    """

    GATE = "gate"
    NOISE = "noise"
    GATE_NOISE = "gate_noise"
    INITIALIZATION_NOISE = "initialization_noise"
    READOUT_NOISE = "readout_noise"
    COMPILER_DIRECTIVE = "compiler_directive"


class MomentsKey(NamedTuple):
    """Key of the Moments mapping.
    Args:
        time: moment
        qubits: qubit set
        moment_type: The type of the moment
        noise_index: the number of noise channels at the same moment. For gates, this is the
            number of gate_noise channels associated with that gate. For all other noise
            types, noise_index starts from 0; but for gate noise, it starts from 1.
    """

    time: int
    qubits: QubitSet
    moment_type: MomentType
    noise_index: int


class Moments(Mapping[MomentsKey, Instruction]):
    """
    An ordered mapping of `MomentsKey` or `NoiseMomentsKey` to `Instruction`. The
    core data structure that contains instructions, ordering they are inserted in, and
    time slices when they occur. `Moments` implements `Mapping` and functions the same as
    a read-only dictionary. It is mutable only through the `add()` method.

    This data structure is useful to determine a dependency of instructions, such as
    printing or optimizing circuit structure, before sending it to a quantum
    device. The original insertion order is preserved and can be retrieved via the `values()`
    method.

    Args:
        instructions (Iterable[Instruction], optional): Instructions to initialize self.
            Default = None.

    Examples:
        >>> moments = Moments()
        >>> moments.add([Instruction(Gate.H(), 0), Instruction(Gate.CNot(), [0, 1])])
        >>> moments.add([Instruction(Gate.H(), 0), Instruction(Gate.H(), 1)])
        >>> for i, item in enumerate(moments.items()):
        ...     print(f"Item {i}")
        ...     print(f"\\tKey: {item[0]}")
        ...     print(f"\\tValue: {item[1]}")
        ...
        Item 0
            Key: MomentsKey(time=0, qubits=QubitSet([Qubit(0)]))
            Value: Instruction('operator': H, 'target': QubitSet([Qubit(0)]))
        Item 1
            Key: MomentsKey(time=1, qubits=QubitSet([Qubit(0), Qubit(1)]))
            Value: Instruction('operator': CNOT, 'target': QubitSet([Qubit(0), Qubit(1)]))
        Item 2
            Key: MomentsKey(time=2, qubits=QubitSet([Qubit(0)]))
            Value: Instruction('operator': H, 'target': QubitSet([Qubit(0)]))
        Item 3
            Key: MomentsKey(time=2, qubits=QubitSet([Qubit(1)]))
            Value: Instruction('operator': H, 'target': QubitSet([Qubit(1)]))
    """

    def __init__(self, instructions: Iterable[Instruction] = None):
        self._moments: OrderedDict[MomentsKey, Instruction] = OrderedDict()
        self._max_times: Dict[Qubit, int] = {}
        self._qubits = QubitSet()
        self._depth = 0
        self._time_all_qubits = -1

        self.add(instructions or [])

    @property
    def depth(self) -> int:
        """int: Get the depth (number of slices) of self."""
        return self._depth

    @property
    def qubit_count(self) -> int:
        """int: Get the number of qubits used across all of the instructions."""
        return len(self._qubits)

    @property
    def qubits(self) -> QubitSet:
        """
        QubitSet: Get the qubits used across all of the instructions. The order of qubits is based
        on the order in which the instructions were added.

        Note:
            Don't mutate this object, any changes may impact the behavior of this class and / or
            consumers. If you need to mutate this, then copy it via `QubitSet(moments.qubits())`.
        """
        return self._qubits

    def time_slices(self) -> Dict[int, List[Instruction]]:
        """
        Get instructions keyed by time.

        Returns:
            Dict[int, List[Instruction]]: Key is the time and value is a list of instructions that
            occur at that moment in time. The order of instructions is in no particular order.

        Note:
            This is a computed result over self and can be freely mutated. This is re-computed with
            every call, with a computational runtime O(N) where N is the number
            of instructions in self.
        """

        time_slices = {}
        self.sort_moments()
        for key, instruction in self._moments.items():
            instructions = time_slices.get(key.time, [])
            instructions.append(instruction)
            time_slices[key.time] = instructions

        return time_slices

    def add(self, instructions: Iterable[Instruction], noise_index: int = 0) -> None:
        """
        Add instructions to self.

        Args:
            instructions (Iterable[Instruction]): Instructions to add to self. The instruction is
                added to the max time slice in which the instruction fits.
        """
        for instruction in instructions:
            self._add(instruction, noise_index)

    def _add(self, instruction: Instruction, noise_index: int = 0) -> None:
        operator = instruction.operator
        if isinstance(operator, CompilerDirective):
            time = self._update_qubit_times(self._qubits)
            self._moments[MomentsKey(time, None, MomentType.COMPILER_DIRECTIVE, 0)] = instruction
            self._depth = time + 1
            self._time_all_qubits = time
        elif isinstance(operator, Noise):
            self.add_noise(instruction)
        else:
            qubit_range = instruction.target
            time = self._update_qubit_times(qubit_range)
            self._moments[
                MomentsKey(time, instruction.target, MomentType.GATE, noise_index)
            ] = instruction
            self._qubits.update(instruction.target)
            self._depth = max(self._depth, time + 1)

    def _update_qubit_times(self, qubits):
        qubit_max_times = [self._max_time_for_qubit(qubit) for qubit in qubits] + [
            self._time_all_qubits
        ]
        time = max(qubit_max_times) + 1
        # Update time for all specified qubits
        for qubit in qubits:
            self._max_times[qubit] = time
        return time

    def add_noise(
        self, instruction: Instruction, input_type: str = "noise", noise_index: int = 0
    ) -> None:

        qubit_range = instruction.target
        time = max(0, *[self._max_time_for_qubit(qubit) for qubit in qubit_range])
        if input_type == MomentType.INITIALIZATION_NOISE:
            time = 0

        while MomentsKey(time, qubit_range, input_type, noise_index) in self._moments:
            noise_index = noise_index + 1

        self._moments[MomentsKey(time, qubit_range, input_type, noise_index)] = instruction
        self._qubits.update(qubit_range)

    def sort_moments(self) -> None:
        """
        Make the disordered moments in order.

        1. Make the readout noise in the end
        2. Make the initialization noise at the beginning
        """
        # key for NOISE, GATE and GATE_NOISE
        key_noise = []
        # key for INITIALIZATION_NOISE
        key_initialization_noise = []
        # key for READOUT_NOISE
        key_readout_noise = []
        moment_copy = OrderedDict()
        sorted_moment = OrderedDict()

        for key, instruction in self._moments.items():
            moment_copy[key] = instruction
            if key.moment_type == MomentType.READOUT_NOISE:
                key_readout_noise.append(key)
            elif key.moment_type == MomentType.INITIALIZATION_NOISE:
                key_initialization_noise.append(key)
            else:
                key_noise.append(key)

        for key in key_initialization_noise:
            sorted_moment[key] = moment_copy[key]
        for key in key_noise:
            sorted_moment[key] = moment_copy[key]
        # find the max time in the circuit and make it the time for readout noise
        max_time = max(self._depth - 1, 0)

        for key in key_readout_noise:
            sorted_moment[
                MomentsKey(max_time, key.qubits, MomentType.READOUT_NOISE, key.noise_index)
            ] = moment_copy[key]

        self._moments = sorted_moment

    def _max_time_for_qubit(self, qubit: Qubit) -> int:
        # -1 if qubit is unoccupied because the first instruction will have an index of 0
        return self._max_times.get(qubit, -1)

    #
    # Implement abstract methods, default to calling selfs underlying dictionary
    #

    def keys(self) -> KeysView[MomentsKey]:
        """Return a view of self's keys."""
        return self._moments.keys()

    def items(self) -> ItemsView[MomentsKey, Instruction]:
        """Return a view of self's (key, instruction)."""
        return self._moments.items()

    def values(self) -> ValuesView[Instruction]:
        """Return a view of self's instructions."""
        self.sort_moments()
        return self._moments.values()

    def get(self, key: MomentsKey, default=None) -> Instruction:
        """
        Get the instruction in self by key.

        Args:
            key (MomentsKey): Key of the instruction to fetch.
            default (Any, optional): Value to return if `key` is not in `moments`. Default = `None`.

        Returns:
            Instruction: `moments[key]` if `key` in `moments`, else `default` is returned.
        """
        return self._moments.get(key, default)

    def __getitem__(self, key):
        return self._moments.__getitem__(key)

    def __iter__(self):
        return self._moments.__iter__()

    def __len__(self):
        return self._moments.__len__()

    def __contains__(self, item):
        return self._moments.__contains__(item)

    def __eq__(self, other):
        if isinstance(other, Moments):
            return self._moments == other._moments
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is not NotImplemented:
            return not result
        return NotImplemented

    def __repr__(self):
        return self._moments.__repr__()

    def __str__(self):
        return self._moments.__str__()
