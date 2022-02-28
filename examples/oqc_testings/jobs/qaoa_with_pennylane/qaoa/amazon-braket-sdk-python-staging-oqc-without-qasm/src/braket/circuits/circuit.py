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

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

import numpy as np

from braket.circuits import compiler_directives
from braket.circuits.ascii_circuit_diagram import AsciiCircuitDiagram
from braket.circuits.gate import Gate
from braket.circuits.instruction import Instruction
from braket.circuits.moments import Moments
from braket.circuits.noise import Noise
from braket.circuits.noise_helpers import (
    apply_noise_to_gates,
    apply_noise_to_moments,
    check_noise_target_gates,
    check_noise_target_qubits,
    check_noise_target_unitary,
    wrap_with_list,
)
from braket.circuits.observable import Observable
from braket.circuits.observables import TensorProduct
from braket.circuits.qubit import QubitInput
from braket.circuits.qubit_set import QubitSet, QubitSetInput
from braket.circuits.result_type import ObservableResultType, ResultType
from braket.circuits.unitary_calculation import calculate_unitary
from braket.ir.jaqcd import Program

SubroutineReturn = TypeVar(
    "SubroutineReturn", Iterable[Instruction], Instruction, ResultType, Iterable[ResultType]
)
SubroutineCallable = TypeVar("SubroutineCallable", bound=Callable[..., SubroutineReturn])
AddableTypes = TypeVar("AddableTypes", SubroutineReturn, SubroutineCallable)


class Circuit:
    """
    A representation of a quantum circuit that contains the instructions to be performed on a
    quantum device and the requested result types.

    See :mod:`braket.circuits.gates` module for all of the supported instructions.

    See :mod:`braket.circuits.result_types` module for all of the supported result types.

    `AddableTypes` are `Instruction`, iterable of `Instruction`, `ResultType`,
    iterable of `ResultType`, or `SubroutineCallable`
    """

    _ALL_QUBITS = "ALL"  # Flag to indicate all qubits in _qubit_observable_mapping

    @classmethod
    def register_subroutine(cls, func: SubroutineCallable) -> None:
        """
        Register the subroutine `func` as an attribute of the `Circuit` class. The attribute name
        is the name of `func`.

        Args:
            func (Callable[..., Union[Instruction, Iterable[Instruction], ResultType,
                Iterable[ResultType]]): The function of the subroutine to add to the class.

        Examples:
            >>> def h_on_all(target):
            ...     circ = Circuit()
            ...     for qubit in target:
            ...         circ += Instruction(Gate.H(), qubit)
            ...     return circ
            ...
            >>> Circuit.register_subroutine(h_on_all)
            >>> circ = Circuit().h_on_all(range(2))
            >>> for instr in circ.instructions:
            ...     print(instr)
            ...
            Instruction('operator': 'H', 'target': QubitSet(Qubit(0),))
            Instruction('operator': 'H', 'target': QubitSet(Qubit(1),))
        """

        def method_from_subroutine(self, *args, **kwargs) -> SubroutineReturn:
            return self.add(func, *args, **kwargs)

        function_name = func.__name__
        setattr(cls, function_name, method_from_subroutine)

        function_attr = getattr(cls, function_name)
        setattr(function_attr, "__doc__", func.__doc__)

    def __init__(self, addable: AddableTypes = None, *args, **kwargs):
        """
        Args:
            addable (AddableTypes): The item(s) to add to self.
                Default = None.
            *args: Variable length argument list. Supports any arguments that `add()` offers.
            **kwargs: Arbitrary keyword arguments. Supports any keyword arguments that `add()`
                offers.

        Raises:
            TypeError: If `addable` is an unsupported type.

        Examples:
            >>> circ = Circuit([Instruction(Gate.H(), 4), Instruction(Gate.CNot(), [4, 5])])
            >>> circ = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().h(0).cnot(0, 1).probability([0, 1])

            >>> @circuit.subroutine(register=True)
            >>> def bell_pair(target):
            ...     return Circ().h(target[0]).cnot(target[0:2])
            ...
            >>> circ = Circuit(bell_pair, [4,5])
            >>> circ = Circuit().bell_pair([4,5])

        """
        self._moments: Moments = Moments()
        self._result_types: Dict[ResultType] = {}
        self._qubit_observable_mapping: Dict[Union[int, Circuit._ALL_QUBITS], Observable] = {}
        self._qubit_observable_target_mapping: Dict[int, Tuple[int]] = {}
        self._qubit_observable_set = set()
        self._observables_simultaneously_measurable = True
        self._has_compiler_directives = False

        if addable is not None:
            self.add(addable, *args, **kwargs)

    @property
    def depth(self) -> int:
        """int: Get the circuit depth."""
        return self._moments.depth

    @property
    def instructions(self) -> Iterable[Instruction]:
        """Iterable[Instruction]: Get an `iterable` of instructions in the circuit."""

        return self._moments.values()

    @property
    def result_types(self) -> List[ResultType]:
        """List[ResultType]: Get a list of requested result types in the circuit."""
        return list(self._result_types.keys())

    @property
    def basis_rotation_instructions(self) -> List[Instruction]:
        """List[Instruction]: Get a list of basis rotation instructions in the circuit.
        These basis rotation instructions are added if result types are requested for
        an observable other than Pauli-Z.

        This only makes sense if all observables are simultaneously measurable;
        if not, this method will return an empty list.
        """
        # Note that basis_rotation_instructions can change each time a new instruction
        # is added to the circuit because `self._moments.qubits` would change
        basis_rotation_instructions = []
        all_qubit_observable = self._qubit_observable_mapping.get(Circuit._ALL_QUBITS)
        if all_qubit_observable:
            for target in self.qubits:
                basis_rotation_instructions += Circuit._observable_to_instruction(
                    all_qubit_observable, target
                )
            return basis_rotation_instructions

        target_lists = sorted(set(self._qubit_observable_target_mapping.values()))
        for target_list in target_lists:
            observable = self._qubit_observable_mapping[target_list[0]]
            basis_rotation_instructions += Circuit._observable_to_instruction(
                observable, target_list
            )
        return basis_rotation_instructions

    @staticmethod
    def _observable_to_instruction(observable: Observable, target_list: List[int]):
        return [Instruction(gate, target_list) for gate in observable.basis_rotation_gates]

    @property
    def moments(self) -> Moments:
        """Moments: Get the `moments` for this circuit. Note that this includes observables."""
        return self._moments

    @property
    def qubit_count(self) -> int:
        """Get the qubit count for this circuit. Note that this includes observables."""
        all_qubits = self._moments.qubits.union(self._qubit_observable_set)
        return len(all_qubits)

    @property
    def qubits(self) -> QubitSet:
        """QubitSet: Get a copy of the qubits for this circuit."""
        return QubitSet(self._moments.qubits.union(self._qubit_observable_set))

    def add_result_type(
        self,
        result_type: ResultType,
        target: QubitSetInput = None,
        target_mapping: Dict[QubitInput, QubitInput] = None,
    ) -> Circuit:
        """
        Add a requested result type to `self`, returns `self` for chaining ability.

        Args:
            result_type (ResultType): `ResultType` to add into `self`.
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits for the
                `result_type`.
                Default = `None`.
            target_mapping (dictionary[int or Qubit, int or Qubit], optional): A dictionary of
                qubit mappings to apply to the `result_type.target`. Key is the qubit in
                `result_type.target` and the value is what the key will be changed to.
                Default = `None`.


        Note: target and target_mapping will only be applied to those requested result types with
        the attribute `target`. The result_type will be appended to the end of the dict keys of
        `circuit.result_types` only if it does not already exist in `circuit.result_types`

        Returns:
            Circuit: self

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.

        Examples:
            >>> result_type = ResultType.Probability(target=[0, 1])
            >>> circ = Circuit().add_result_type(result_type)
            >>> print(circ.result_types[0])
            Probability(target=QubitSet([Qubit(0), Qubit(1)]))

            >>> result_type = ResultType.Probability(target=[0, 1])
            >>> circ = Circuit().add_result_type(result_type, target_mapping={0: 10, 1: 11})
            >>> print(circ.result_types[0])
            Probability(target=QubitSet([Qubit(10), Qubit(11)]))

            >>> result_type = ResultType.Probability(target=[0, 1])
            >>> circ = Circuit().add_result_type(result_type, target=[10, 11])
            >>> print(circ.result_types[0])
            Probability(target=QubitSet([Qubit(10), Qubit(11)]))

            >>> result_type = ResultType.StateVector()
            >>> circ = Circuit().add_result_type(result_type)
            >>> print(circ.result_types[0])
            StateVector()
        """
        if target_mapping and target is not None:
            raise TypeError("Only one of 'target_mapping' or 'target' can be supplied.")

        if not target_mapping and not target:
            # Nothing has been supplied, add result_type
            result_type_to_add = result_type
        elif target_mapping:
            # Target mapping has been supplied, copy result_type
            result_type_to_add = result_type.copy(target_mapping=target_mapping)
        else:
            # ResultType with target
            result_type_to_add = result_type.copy(target=target)

        if result_type_to_add not in self._result_types:
            observable = Circuit._extract_observable(result_type_to_add)
            if observable and self._observables_simultaneously_measurable:
                # Only check if all observables can be simultaneously measured
                self._add_to_qubit_observable_mapping(observable, result_type_to_add.target)
            self._add_to_qubit_observable_set(result_type_to_add)
            # using dict as an ordered set, value is arbitrary
            self._result_types[result_type_to_add] = None
        return self

    @staticmethod
    def _extract_observable(result_type: ResultType) -> Optional[Observable]:
        if isinstance(result_type, ResultType.Probability):
            return Observable.Z()  # computational basis
        elif isinstance(result_type, ObservableResultType):
            return result_type.observable
        else:
            return None

    def _add_to_qubit_observable_mapping(
        self, observable: Observable, observable_target: QubitSet
    ) -> None:
        targets = observable_target or list(self._qubit_observable_set)
        all_qubits_observable = self._qubit_observable_mapping.get(Circuit._ALL_QUBITS)
        tensor_product_dict = (
            Circuit._tensor_product_index_dict(observable, observable_target)
            if isinstance(observable, TensorProduct)
            else None
        )
        identity = Observable.I()
        for i in range(len(targets)):
            target = targets[i]
            new_observable = tensor_product_dict[i][0] if tensor_product_dict else observable
            current_observable = all_qubits_observable or self._qubit_observable_mapping.get(target)

            add_observable = not current_observable or (
                current_observable == identity and new_observable != identity
            )
            if (
                not add_observable
                and current_observable != identity
                and new_observable != identity
                and current_observable != new_observable
            ):
                return self._encounter_noncommuting_observable()

            if observable_target:
                new_targets = (
                    tensor_product_dict[i][1] if tensor_product_dict else tuple(observable_target)
                )

                if add_observable:
                    self._qubit_observable_target_mapping[target] = new_targets
                    self._qubit_observable_mapping[target] = new_observable
                elif new_observable.qubit_count > 1:
                    current_target = self._qubit_observable_target_mapping.get(target)
                    if current_target and current_target != new_targets:
                        return self._encounter_noncommuting_observable()

        if not observable_target:
            if all_qubits_observable and all_qubits_observable != observable:
                return self._encounter_noncommuting_observable()
            self._qubit_observable_mapping[Circuit._ALL_QUBITS] = observable

    @staticmethod
    def _tensor_product_index_dict(
        observable: TensorProduct, observable_target: QubitSet
    ) -> Dict[int, Tuple[Observable, Tuple[int, ...]]]:
        obj_dict = {}
        i = 0
        factors = list(observable.factors)
        total = factors[0].qubit_count
        while factors:
            if i >= total:
                factors.pop(0)
                if factors:
                    total += factors[0].qubit_count
            if factors:
                first = total - factors[0].qubit_count
                obj_dict[i] = (factors[0], tuple(observable_target[first:total]))
            i += 1
        return obj_dict

    def _add_to_qubit_observable_set(self, result_type: ResultType) -> None:
        if isinstance(result_type, ObservableResultType) and result_type.target:
            self._qubit_observable_set.update(result_type.target)

    def add_instruction(
        self,
        instruction: Instruction,
        target: QubitSetInput = None,
        target_mapping: Dict[QubitInput, QubitInput] = None,
    ) -> Circuit:
        """
        Add an instruction to `self`, returns `self` for chaining ability.

        Args:
            instruction (Instruction): `Instruction` to add into `self`.
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits for the
                `instruction`. If a single qubit gate, an instruction is created for every index
                in `target`.
                Default = `None`.
            target_mapping (dictionary[int or Qubit, int or Qubit], optional): A dictionary of
                qubit mappings to apply to the `instruction.target`. Key is the qubit in
                `instruction.target` and the value is what the key will be changed to.
                Default = `None`.

        Returns:
            Circuit: self

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.

        Examples:
            >>> instr = Instruction(Gate.CNot(), [0, 1])
            >>> circ = Circuit().add_instruction(instr)
            >>> print(circ.instructions[0])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(0), Qubit(1)))

            >>> instr = Instruction(Gate.CNot(), [0, 1])
            >>> circ = Circuit().add_instruction(instr, target_mapping={0: 10, 1: 11})
            >>> print(circ.instructions[0])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(10), Qubit(11)))

            >>> instr = Instruction(Gate.CNot(), [0, 1])
            >>> circ = Circuit().add_instruction(instr, target=[10, 11])
            >>> print(circ.instructions[0])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(10), Qubit(11)))

            >>> instr = Instruction(Gate.H(), 0)
            >>> circ = Circuit().add_instruction(instr, target=[10, 11])
            >>> print(circ.instructions[0])
            Instruction('operator': 'H', 'target': QubitSet(Qubit(10),))
            >>> print(circ.instructions[1])
            Instruction('operator': 'H', 'target': QubitSet(Qubit(11),))
        """
        if target_mapping and target is not None:
            raise TypeError("Only one of 'target_mapping' or 'target' can be supplied.")

        if not target_mapping and not target:
            # Nothing has been supplied, add instruction
            instructions_to_add = [instruction]
        elif target_mapping:
            # Target mapping has been supplied, copy instruction
            instructions_to_add = [instruction.copy(target_mapping=target_mapping)]
        elif hasattr(instruction.operator, "qubit_count") and instruction.operator.qubit_count == 1:
            # single qubit operator with target, add an instruction for each target
            instructions_to_add = [instruction.copy(target=qubit) for qubit in target]
        else:
            # non single qubit operator with target, add instruction with target
            instructions_to_add = [instruction.copy(target=target)]

        self._moments.add(instructions_to_add)

        return self

    def add_circuit(
        self,
        circuit: Circuit,
        target: QubitSetInput = None,
        target_mapping: Dict[QubitInput, QubitInput] = None,
    ) -> Circuit:
        """
        Add a `circuit` to self, returns self for chaining ability.

        Args:
            circuit (Circuit): Circuit to add into self.
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits for the
                supplied circuit. This is a macro over `target_mapping`; `target` is converted to
                a `target_mapping` by zipping together a sorted `circuit.qubits` and `target`.
                Default = `None`.
            target_mapping (dictionary[int or Qubit, int or Qubit], optional): A dictionary of
                qubit mappings to apply to the qubits of `circuit.instructions`. Key is the qubit
                to map, and the value is what to change it to. Default = `None`.

        Returns:
            Circuit: self

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.

        Note:
            Supplying `target` sorts `circuit.qubits` to have deterministic behavior since
            `circuit.qubits` ordering is based on how instructions are inserted.
            Use caution when using this with circuits that with a lot of qubits, as the sort
            can be resource-intensive. Use `target_mapping` to use a linear runtime to remap
            the qubits.

            Requested result types of the circuit that will be added will be appended to the end
            of the list for the existing requested result types. A result type to be added that is
            equivalent to an existing requested result type will not be added.

        Examples:
            >>> widget = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().add_circuit(widget)
            >>> instructions = list(circ.instructions)
            >>> print(instructions[0])
            Instruction('operator': 'H', 'target': QubitSet(Qubit(0),))
            >>> print(instructions[1])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(0), Qubit(1)))

            >>> widget = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().add_circuit(widget, target_mapping={0: 10, 1: 11})
            >>> instructions = list(circ.instructions)
            >>> print(instructions[0])
            Instruction('operator': 'H', 'target': QubitSet(Qubit(10),))
            >>> print(instructions[1])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(10), Qubit(11)))

            >>> widget = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().add_circuit(widget, target=[10, 11])
            >>> instructions = list(circ.instructions)
            >>> print(instructions[0])
            Instruction('operator': 'H', 'target': QubitSet(Qubit(10),))
            >>> print(instructions[1])
            Instruction('operator': 'CNOT', 'target': QubitSet(Qubit(10), Qubit(11)))
        """
        if target_mapping and target is not None:
            raise TypeError("Only one of 'target_mapping' or 'target' can be supplied.")
        elif target is not None:
            keys = sorted(circuit.qubits)
            values = target
            target_mapping = dict(zip(keys, values))

        for instruction in circuit.instructions:
            self.add_instruction(instruction, target_mapping=target_mapping)

        for result_type in circuit.result_types:
            self.add_result_type(result_type, target_mapping=target_mapping)

        return self

    def add_verbatim_box(
        self,
        verbatim_circuit: Circuit,
        target: QubitSetInput = None,
        target_mapping: Dict[QubitInput, QubitInput] = None,
    ) -> Circuit:
        """
        Add a verbatim `circuit` to self, that is, ensures that `circuit` is not modified in any way
        by the compiler.

        Args:
            verbatim_circuit (Circuit): Circuit to add into self.
            target (int, Qubit, or iterable of int / Qubit, optional): Target qubits for the
                supplied circuit. This is a macro over `target_mapping`; `target` is converted to
                a `target_mapping` by zipping together a sorted `circuit.qubits` and `target`.
                Default = `None`.
            target_mapping (dictionary[int or Qubit, int or Qubit], optional): A dictionary of
                qubit mappings to apply to the qubits of `circuit.instructions`. Key is the qubit
                to map, and the value is what to change it to. Default = `None`.

        Returns:
            Circuit: self

        Raises:
            TypeError: If both `target_mapping` and `target` are supplied.
            ValueError: If `circuit` has result types attached

        Examples:
            >>> widget = Circuit().h(0).h(1)
            >>> circ = Circuit().add_verbatim_box(widget)
            >>> print(list(circ.instructions))
            [Instruction('operator': StartVerbatimBox, 'target': QubitSet([])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(0)])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(1)])),
             Instruction('operator': EndVerbatimBox, 'target': QubitSet([]))]

            >>> widget = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().add_verbatim_box(widget, target_mapping={0: 10, 1: 11})
            >>> print(list(circ.instructions))
            [Instruction('operator': StartVerbatimBox, 'target': QubitSet([])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(10)])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(11)])),
             Instruction('operator': EndVerbatimBox, 'target': QubitSet([]))]

            >>> widget = Circuit().h(0).cnot(0, 1)
            >>> circ = Circuit().add_verbatim_box(widget, target=[10, 11])
            >>> print(list(circ.instructions))
            [Instruction('operator': StartVerbatimBox, 'target': QubitSet([])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(10)])),
             Instruction('operator': H('qubit_count': 1), 'target': QubitSet([Qubit(11)])),
             Instruction('operator': EndVerbatimBox, 'target': QubitSet([]))]
        """
        if target_mapping and target is not None:
            raise TypeError("Only one of 'target_mapping' or 'target' can be supplied.")
        elif target is not None:
            keys = sorted(verbatim_circuit.qubits)
            values = target
            target_mapping = dict(zip(keys, values))

        if verbatim_circuit.result_types:
            raise ValueError("Verbatim subcircuit is not measured and cannot have result types")

        if verbatim_circuit.instructions:
            self.add_instruction(Instruction(compiler_directives.StartVerbatimBox()))
            for instruction in verbatim_circuit.instructions:
                self.add_instruction(instruction, target_mapping=target_mapping)
            self.add_instruction(Instruction(compiler_directives.EndVerbatimBox()))
            self._has_compiler_directives = True
        return self

    def apply_gate_noise(
        self,
        noise: Union[Type[Noise], Iterable[Type[Noise]]],
        target_gates: Optional[Union[Type[Gate], Iterable[Type[Gate]]]] = None,
        target_unitary: np.ndarray = None,
        target_qubits: Optional[QubitSetInput] = None,
    ) -> Circuit:
        """Apply `noise` to the circuit according to `target_gates`, `target_unitary` and
        `target_qubits`.

        For any parameter that is None, that specification is ignored (e.g. if `target_gates`
        is None then the noise is applied after every gate in `target_qubits`).
        If `target_gates` and `target_qubits` are both None, then `noise` is
        applied to every qubit after every gate.

        Noise is either applied to `target_gates` or `target_unitary`, so they cannot be
        provided at the same time.

        When `noise.qubit_count` == 1, ie. `noise` is single-qubit, `noise` is added to all
        qubits in `target_gates` or `target_unitary` (or to all qubits in `target_qubits`
        if `target_gates` is None).

        When `noise.qubit_count` > 1 and `target_gates` is not None, the number of qubits of
        any gate in `target_gates` must be the same as `noise.qubit_count`.

        When `noise.qubit_count` > 1, `target_gates` and `target_unitary` is None, noise is
        only applied to gates with the same qubit_count in target_qubits.

        Args:
            noise (Union[Type[Noise], Iterable[Type[Noise]]]): Noise channel(s) to be applied
            to the circuit.
            target_gates (Union[Type[Gate], Iterable[Type[Gate]], optional]): Gate class or
                List of Gate classes which `noise` is applied to. Default=None.
            target_unitary (np.ndarray): matrix of the target unitary gates. Default=None.
            target_qubits (Union[QubitSetInput, optional]): Index or indices of qubit(s).
                Default=None.

        Returns:
            Circuit: self

        Raises:
            TypeError:
                If `noise` is not Noise type.
                If `target_gates` is not a Gate type, Iterable[Gate].
                If `target_unitary` is not a np.ndarray type.
                If `target_qubits` has non-integers or negative integers.
            IndexError:
                If applying noise to an empty circuit.
                If `target_qubits` is out of range of circuit.qubits.
            ValueError:
                If both `target_gates` and `target_unitary` are provided.
                If `target_unitary` is not a unitary.
                If `noise` is multi-qubit noise and `target_gates` contain gates
                with the number of qubits not the same as `noise.qubit_count`.
            Warning:
                If `noise` is multi-qubit noise while there is no gate with the same
                number of qubits in `target_qubits` or in the whole circuit when
                `target_qubits` is not given.
                If no `target_gates` or  `target_unitary` exist in `target_qubits` or
                in the whole circuit when they are not given.

        Examples:
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ)
            T  : |0|1|2|

            q0 : -X-Z-C-
                      |
            q1 : -Y-X-X-

            T  : |0|1|2|

            >>> noise = Noise.Depolarizing(probability=0.1)
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_gate_noise(noise, target_gates = Gate.X))
            T  : |     0     |     1     |2|

            q0 : -X-DEPO(0.1)-Z-----------C-
                                          |
            q1 : -Y-----------X-DEPO(0.1)-X-

            T  : |     0     |     1     |2|

            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_gate_noise(noise, target_qubits = 1))
            T  : |     0     |     1     |     2     |

            q0 : -X-----------Z-----------C-----------
                                          |
            q1 : -Y-DEPO(0.1)-X-DEPO(0.1)-X-DEPO(0.1)-

            T  : |     0     |     1     |     2     |

            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_gate_noise(noise,
            ...                             target_gates = [Gate.X,Gate.Y],
            ...                             target_qubits = [0,1])
            ... )
            T  : |     0     |     1     |2|

            q0 : -X-DEPO(0.1)-Z-----------C-
                                          |
            q1 : -Y-DEPO(0.1)-X-DEPO(0.1)-X-

            T  : |     0     |     1     |2|

        """
        # check whether gate noise is applied to an empty circuit
        if not self.qubits:
            raise IndexError("Gate noise cannot be applied to an empty circuit.")

        # check if target_gates and target_unitary are both given
        if (target_unitary is not None) and (target_gates is not None):
            raise ValueError("target_unitary and target_gates cannot be input at the same time.")

        # check target_qubits
        target_qubits = check_noise_target_qubits(self, target_qubits)
        if not all(qubit in self.qubits for qubit in target_qubits):
            raise IndexError("target_qubits must be within the range of the current circuit.")

        # make noise a list
        noise = wrap_with_list(noise)

        # make target_gates a list
        if target_gates is not None:
            target_gates = wrap_with_list(target_gates)
            # remove duplicate items
            target_gates = list(dict.fromkeys(target_gates))

        for noise_channel in noise:
            if not isinstance(noise_channel, Noise):
                raise TypeError("Noise must be an instance of the Noise class")
                # check whether target_gates is valid
            if target_gates is not None:
                check_noise_target_gates(noise_channel, target_gates)
            if target_unitary is not None:
                check_noise_target_unitary(noise_channel, target_unitary)

        if target_unitary is not None:
            return apply_noise_to_gates(self, noise, target_unitary, target_qubits)
        else:
            return apply_noise_to_gates(self, noise, target_gates, target_qubits)

    def apply_initialization_noise(
        self,
        noise: Union[Type[Noise], Iterable[Type[Noise]]],
        target_qubits: Optional[QubitSetInput] = None,
    ) -> Circuit:
        """Apply `noise` at the beginning of the circuit for every qubit (default) or target_qubits`.

        Only when `target_qubits` is given can the noise be applied to an empty circuit.

        When `noise.qubit_count` > 1, the number of qubits in target_qubits must be equal
        to `noise.qubit_count`.

        Args:
            noise (Union[Type[Noise], Iterable[Type[Noise]]]): Noise channel(s) to be applied
            to the circuit.
            target_qubits (Union[QubitSetInput, optional]): Index or indices of qubit(s).
                Default=None.

        Returns:
            Circuit: self

        Raises:
            TypeError:
                If `noise` is not Noise type.
                If `target_qubits` has non-integers or negative integers.
            IndexError:
                If applying noise to an empty circuit when `target_qubits` is not given.
            ValueError:
                If `noise.qubit_count` > 1 and the number of qubits in target_qubits is
                not the same as `noise.qubit_count`.

        Examples:
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ)

            >>> noise = Noise.Depolarizing(probability=0.1)
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_initialization_noise(noise))

            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_initialization_noise(noise, target_qubits = 1))

            >>> circ = Circuit()
            >>> print(circ.apply_initialization_noise(noise, target_qubits = [0, 1]))

        """
        if (len(self.qubits) == 0) and (target_qubits is None):
            raise IndexError(
                "target_qubits must be provided in order to"
                " apply the initialization noise to an empty circuit."
            )

        target_qubits = check_noise_target_qubits(self, target_qubits)

        # make noise a list
        noise = wrap_with_list(noise)
        for noise_channel in noise:
            if not isinstance(noise_channel, Noise):
                raise TypeError("Noise must be an instance of the Noise class")
            if noise_channel.qubit_count > 1 and noise_channel.qubit_count != len(target_qubits):
                raise ValueError(
                    "target_qubits needs to be provided for this multi-qubit noise channel,"
                    " and the number of qubits in target_qubits must be the same as defined by"
                    " the multi-qubit noise channel."
                )

        return apply_noise_to_moments(self, noise, target_qubits, "initialization")

    def apply_readout_noise(
        self,
        noise: Union[Type[Noise], Iterable[Type[Noise]]],
        target_qubits: Optional[QubitSetInput] = None,
    ) -> Circuit:
        """Apply `noise` right before measurement in every qubit (default) or target_qubits`.

        Only when `target_qubits` is given can the noise be applied to an empty circuit.

        When `noise.qubit_count` > 1, the number of qubits in target_qubits must be equal
        to `noise.qubit_count`.

        Args:
            noise (Union[Type[Noise], Iterable[Type[Noise]]]): Noise channel(s) to be applied
            to the circuit.
            target_qubits (Union[QubitSetInput, optional]): Index or indices of qubit(s).
                Default=None.

        Returns:
            Circuit: self

        Raises:
            TypeError:
                If `noise` is not Noise type.
                If `target_qubits` has non-integers.
            IndexError:
                If applying noise to an empty circuit.
            ValueError:
                If `target_qubits` has negative integers.
                If `noise.qubit_count` > 1 and the number of qubits in target_qubits is
                not the same as `noise.qubit_count`.

        Examples:
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ)

            >>> noise = Noise.Depolarizing(probability=0.1)
            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_initialization_noise(noise))

            >>> circ = Circuit().x(0).y(1).z(0).x(1).cnot(0,1)
            >>> print(circ.apply_initialization_noise(noise, target_qubits = 1))

            >>> circ = Circuit()
            >>> print(circ.apply_initialization_noise(noise, target_qubits = [0, 1]))

        """
        if (len(self.qubits) == 0) and (target_qubits is None):
            raise IndexError(
                "target_qubits must be provided in order to"
                " apply the readout noise to an empty circuit."
            )

        if target_qubits is None:
            target_qubits = self.qubits
        else:
            if not isinstance(target_qubits, list):
                target_qubits = [target_qubits]
            if not all(isinstance(q, int) for q in target_qubits):
                raise TypeError("target_qubits must be integer(s)")
            if not all(q >= 0 for q in target_qubits):
                raise ValueError("target_qubits must contain only non-negative integers.")
            target_qubits = QubitSet(target_qubits)

        # make noise a list
        noise = wrap_with_list(noise)
        for noise_channel in noise:
            if not isinstance(noise_channel, Noise):
                raise TypeError("Noise must be an instance of the Noise class")
            if noise_channel.qubit_count > 1 and noise_channel.qubit_count != len(target_qubits):
                raise ValueError(
                    "target_qubits needs to be provided for this multi-qubit noise channel,"
                    " and the number of qubits in target_qubits must be the same as defined by"
                    " the multi-qubit noise channel."
                )

        return apply_noise_to_moments(self, noise, target_qubits, "readout")

    def add(self, addable: AddableTypes, *args, **kwargs) -> Circuit:
        """
        Generic add method for adding item(s) to self. Any arguments that
        `add_circuit()` and / or `add_instruction()` and / or `add_result_type`
        supports are supported by this method. If adding a
        subroutine, check with that subroutines documentation to determine what
        input it allows.

        Args:
            addable (AddableTypes): The item(s) to add to self. Default = `None`.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Circuit: self

        Raises:
            TypeError: If `addable` is an unsupported type

        See Also:
            `add_circuit()`

            `add_instruction()`

            `add_result_type()`

        Examples:
            >>> circ = Circuit().add([Instruction(Gate.H(), 4), Instruction(Gate.CNot(), [4, 5])])
            >>> circ = Circuit().add([ResultType.StateVector()])

            >>> circ = Circuit().h(4).cnot([4, 5])

            >>> @circuit.subroutine()
            >>> def bell_pair(target):
            ...     return Circuit().h(target[0]).cnot(target[0: 2])
            ...
            >>> circ = Circuit().add(bell_pair, [4,5])
        """

        def _flatten(addable):
            if isinstance(addable, Iterable):
                for item in addable:
                    yield from _flatten(item)
            else:
                yield addable

        for item in _flatten(addable):
            if isinstance(item, Instruction):
                self.add_instruction(item, *args, **kwargs)
            elif isinstance(item, ResultType):
                self.add_result_type(item, *args, **kwargs)
            elif isinstance(item, Circuit):
                self.add_circuit(item, *args, **kwargs)
            elif callable(item):
                self.add(item(*args, **kwargs))
            else:
                raise TypeError(f"Cannot add a '{type(item)}' to a Circuit")

        return self

    def diagram(self, circuit_diagram_class=AsciiCircuitDiagram) -> str:
        """
        Get a diagram for the current circuit.

        Args:
            circuit_diagram_class (Class, optional): A `CircuitDiagram` class that builds the
                diagram for this circuit. Default = `AsciiCircuitDiagram`.

        Returns:
            str: An ASCII string circuit diagram.
        """
        return circuit_diagram_class.build_diagram(self)

    def to_ir(self) -> Program:
        """
        Converts the circuit into the canonical intermediate representation.
        If the circuit is sent over the wire, this method is called before it is sent.

        Returns:
            (Program): An AWS quantum circuit description program in JSON format.
        """
        ir_instructions = [instr.to_ir() for instr in self.instructions]
        ir_results = [result_type.to_ir() for result_type in self.result_types]
        ir_basis_rotation_instructions = [
            instr.to_ir() for instr in self.basis_rotation_instructions
        ]
        return Program.construct(
            instructions=ir_instructions,
            results=ir_results,
            basis_rotation_instructions=ir_basis_rotation_instructions,
        )

    def as_unitary(self) -> np.ndarray:
        """
        Returns the unitary matrix representation of the entire circuit.
        *Note*: The performance of this method degrades with qubit count. It might be slow for
        qubit count > 10.

        Returns:
            np.ndarray: A numpy array with shape (2^qubit_count, 2^qubit_count) representing the
                circuit as a unitary. *Note*: For an empty circuit, an empty numpy array is
                returned (`array([], dtype=complex128)`)

        Raises:
            TypeError: If circuit is not composed only of `Gate` instances,
                i.e. a circuit with `Noise` operators will raise this error.

        Examples:
            >>> circ = Circuit().h(0).cnot(0, 1)
            >>> circ.as_unitary()
            array([[ 0.70710678+0.j,  0.70710678+0.j,  0.        +0.j,
                     0.        +0.j],
                   [ 0.        +0.j,  0.        +0.j,  0.70710678+0.j,
                    -0.70710678+0.j],
                   [ 0.        +0.j,  0.        +0.j,  0.70710678+0.j,
                     0.70710678+0.j],
                   [ 0.70710678+0.j, -0.70710678+0.j,  0.        +0.j,
                     0.        +0.j]])
        """
        qubits = self.qubits
        if not qubits:
            return np.zeros(0, dtype=complex)
        qubit_count = max(qubits) + 1

        return calculate_unitary(qubit_count, self.instructions)

    @property
    def qubits_frozen(self) -> bool:
        """bool: Whether the circuit's qubits are frozen, that is, cannot be remapped.

        This may happen because the circuit contains compiler directives preventing compilation
        of a part of the circuit, which consequently means that none of the other qubits can be
        rewired either for the program to still make sense.
        """
        return self._has_compiler_directives

    @property
    def observables_simultaneously_measurable(self) -> bool:
        """bool: Whether the circuit's observables are simultaneously measurable

        If this is False, then the circuit can only be run when shots = 0, as sampling (shots > 0)
        measures the circuit in the observables' shared eigenbasis.
        """
        return self._observables_simultaneously_measurable

    def _encounter_noncommuting_observable(self):
        self._observables_simultaneously_measurable = False
        # No longer simultaneously measurable, so no need to track
        self._qubit_observable_mapping.clear()
        self._qubit_observable_target_mapping.clear()

    def _copy(self) -> Circuit:
        copy = Circuit().add(self.instructions)
        copy.add(self.result_types)
        return copy

    def copy(self) -> Circuit:
        """
        Return a shallow copy of the circuit.

        Returns:
            Circuit: A shallow copy of the circuit.
        """
        return self._copy()

    def __iadd__(self, addable: AddableTypes) -> Circuit:
        return self.add(addable)

    def __add__(self, addable: AddableTypes) -> Circuit:
        new = self._copy()
        new.add(addable)
        return new

    def __repr__(self) -> str:
        if not self.result_types:
            return f"Circuit('instructions': {list(self.instructions)})"
        else:
            return (
                f"Circuit('instructions': {list(self.instructions)}"
                + f", 'result_types': {self.result_types})"
            )

    def __str__(self):
        return self.diagram(AsciiCircuitDiagram)

    def __eq__(self, other):
        if isinstance(other, Circuit):
            return (
                list(self.instructions) == list(other.instructions)
                and self.result_types == other.result_types
            )
        return NotImplemented


def subroutine(register=False):
    """
    Subroutine is a function that returns instructions, result types, or circuits.

    Args:
        register (bool, optional): If `True`, adds this subroutine into the `Circuit` class.
            Default = `False`.

    Examples:
        >>> @circuit.subroutine(register=True)
        >>> def bell_circuit():
        ...     return Circuit().h(0).cnot(0, 1)
        ...
        >>> circ = Circuit().bell_circuit()
        >>> for instr in circ.instructions:
        ...     print(instr)
        ...
        Instruction('operator': 'H', 'target': QubitSet(Qubit(0),))
        Instruction('operator': 'H', 'target': QubitSet(Qubit(1),))
    """

    def subroutine_function_wrapper(func: Callable[..., SubroutineReturn]) -> SubroutineReturn:
        if register:
            Circuit.register_subroutine(func)
        return func

    return subroutine_function_wrapper
