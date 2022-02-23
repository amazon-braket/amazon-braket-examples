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

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, validator

from braket.ir.jaqcd.instructions import (
    CV,
    CY,
    CZ,
    ECR,
    XX,
    XY,
    YY,
    ZZ,
    AmplitudeDamping,
    BitFlip,
    CCNot,
    CNot,
    CPhaseShift,
    CPhaseShift00,
    CPhaseShift01,
    CPhaseShift10,
    CSwap,
    Depolarizing,
    EndVerbatimBox,
    GeneralizedAmplitudeDamping,
    H,
    I,
    ISwap,
    Kraus,
    PauliChannel,
    PhaseDamping,
    PhaseFlip,
    PhaseShift,
    PSwap,
    Rx,
    Ry,
    Rz,
    S,
    Si,
    StartVerbatimBox,
    Swap,
    T,
    Ti,
    TwoQubitDephasing,
    TwoQubitDepolarizing,
    Unitary,
    V,
    Vi,
    X,
    Y,
    Z,
)
from braket.ir.jaqcd.results import (
    Amplitude,
    DensityMatrix,
    Expectation,
    Probability,
    Sample,
    StateVector,
    Variance,
)
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader

"""
The pydantic validator requires a constant lookup function. A plain Union[] results
in an O(n) lookup cost for arbitrary payloads, which has a negative impact on model parsing times.
"""
_valid_gates = {
    CCNot.Type.ccnot: CCNot,
    CNot.Type.cnot: CNot,
    CPhaseShift.Type.cphaseshift: CPhaseShift,
    CPhaseShift00.Type.cphaseshift00: CPhaseShift00,
    CPhaseShift01.Type.cphaseshift01: CPhaseShift01,
    CPhaseShift10.Type.cphaseshift10: CPhaseShift10,
    CSwap.Type.cswap: CSwap,
    CV.Type.cv: CV,
    CY.Type.cy: CY,
    CZ.Type.cz: CZ,
    ECR.Type.ecr: ECR,
    H.Type.h: H,
    I.Type.i: I,
    ISwap.Type.iswap: ISwap,
    PhaseShift.Type.phaseshift: PhaseShift,
    PSwap.Type.pswap: PSwap,
    Rx.Type.rx: Rx,
    Ry.Type.ry: Ry,
    Rz.Type.rz: Rz,
    S.Type.s: S,
    Swap.Type.swap: Swap,
    Si.Type.si: Si,
    T.Type.t: T,
    Ti.Type.ti: Ti,
    Unitary.Type.unitary: Unitary,
    V.Type.v: V,
    Vi.Type.vi: Vi,
    X.Type.x: X,
    XX.Type.xx: XX,
    XY.Type.xy: XY,
    Y.Type.y: Y,
    YY.Type.yy: YY,
    Z.Type.z: Z,
    ZZ.Type.zz: ZZ,
}

_valid_noise_channels = {
    BitFlip.Type.bit_flip: BitFlip,
    PhaseFlip.Type.phase_flip: PhaseFlip,
    Depolarizing.Type.depolarizing: Depolarizing,
    AmplitudeDamping.Type.amplitude_damping: AmplitudeDamping,
    GeneralizedAmplitudeDamping.Type.generalized_amplitude_damping: GeneralizedAmplitudeDamping,
    PauliChannel.Type.pauli_channel: PauliChannel,
    PhaseDamping.Type.phase_damping: PhaseDamping,
    TwoQubitDephasing.Type.two_qubit_dephasing: TwoQubitDephasing,
    TwoQubitDepolarizing.Type.two_qubit_depolarizing: TwoQubitDepolarizing,
    Kraus.Type.kraus: Kraus,
}

_valid_compiler_directives = {
    StartVerbatimBox.Type.start_verbatim_box: StartVerbatimBox,
    EndVerbatimBox.Type.end_verbatim_box: EndVerbatimBox,
}

Results = Union[Amplitude, Expectation, Probability, Sample, StateVector, DensityMatrix, Variance]


class Program(BraketSchemaBase):
    """
    Root object of the JsonAwsQuantumCircuitDescription IR.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value. Only default is allowed.
        instructions (List[Any]): List of instructions.
        basis_rotation_instructions (List[Any]): List of instructions for
            rotation to desired measurement bases. Default is None.
        results (List[Union[Amplitude, Expectation, Probability, Sample, StateVector,
        DensityMatrix, Variance]]):
            List of requested results. Default is None.

    Examples:
        >>> Program(instructions=[H(target=0), Rz(angle=0.15, target=1)])
        >>> Program(instructions=[H(target=0), CNot(control=0, target=1)],
        ...     results=[Expectation(targets=[0], observable=['x'])],
        ...     basis_rotation_instructions=[H(target=0)])


    Note:
        The following instructions are supported:
        AmplitudeDamping,
        BitFlip,
        CCNot,
        CNot,
        CPhaseShift,
        CPhaseShift00,
        CPhaseShift01,
        CPhaseShift10,
        CSwap,
        CV,
        CY,
        CZ,
        ECR,
        Depolarizing,
        GeneralizedAmplitudeDamping,
        Pauli_channel,
        H,
        I,
        ISwap,
        Kraus,
        PhaseDamping
        PhaseFlip,
        PhaseShift,
        PSwap,
        Rx,
        Ry,
        Rz,
        S,
        Swap,
        Si,
        T,
        Ti,
        TwoQubitDephasing,
        TwoQubitDepolarizing,
        Unitary,
        V,
        Vi,
        X,
        XX,
        XY,
        Y,
        YY,
        Z,
        ZZ
    """

    _PROGRAM_HEADER = BraketSchemaHeader(name="braket.ir.jaqcd.program", version="1")
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    instructions: List[Any]
    results: Optional[List[Results]]
    basis_rotation_instructions: Optional[List[Any]]

    @validator("instructions", "basis_rotation_instructions", each_item=True, pre=True)
    def validate_instructions(cls, value, field):
        """
        Pydantic uses the validation subsystem to create objects. This custom validator has
        2 purposes:
        1. Implement O(1) deserialization
        2. Validate that the input instructions are supported
        """
        if isinstance(value, BaseModel):
            if (
                (value.type not in _valid_gates)
                and (value.type not in _valid_noise_channels)
                and (value.type not in _valid_compiler_directives)
            ):
                raise ValueError(f"Invalid value.type specified: {value} for field: {field}")
            return value

        if value is not None and "type" in value:
            if value["type"] in _valid_gates:
                return _valid_gates[value["type"]](**value)
            elif value["type"] in _valid_noise_channels:
                return _valid_noise_channels[value["type"]](**value)
            elif value["type"] in _valid_compiler_directives:
                return _valid_compiler_directives[value["type"]](**value)
            else:
                raise ValueError(f"Invalid instruction specified: {value} for field: {field}")
        else:
            raise ValueError(f"Invalid type or value specified: {value} for field: {field}")
