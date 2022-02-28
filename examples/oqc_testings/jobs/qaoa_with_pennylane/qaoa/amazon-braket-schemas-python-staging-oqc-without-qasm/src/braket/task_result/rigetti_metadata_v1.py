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
# language governing permissions and limitations under the License

from typing import Optional

from pydantic import BaseModel, Field, confloat, conint, conlist, constr

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class NativeQuilMetadata(BaseModel):
    """
    Schema to hold native quil metadata returned by
    Rigetti after compilation.

    Examples:
        >>> NativeQuilMetadata(finalRewiring=[32,21],
                              gateDepth=5,
                              gateVolume=6,
                              multiQubitGateDepth=1,
                              programDuration=300.1,
                              programFidelity=0.8989,
                              qpuRuntimeEstimation=191.21,
                              topologicalSwaps=0)
    """

    finalRewiring: conlist(int)
    gateDepth: conint(ge=0)
    gateVolume: conint(ge=0)
    multiQubitGateDepth: conint(ge=0)
    programDuration: confloat(ge=0)
    programFidelity: confloat(gt=0)
    qpuRuntimeEstimation: confloat(gt=0)
    topologicalSwaps: conint(ge=0)


class RigettiMetadata(BraketSchemaBase):
    """
    The Rigetti metadata result schema.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header.
            Users do not need to set this value. Only default is allowed.
        nativeQuilMetadata (NativeQuilMetadata)
        program (str): The compiled program executed on the QPU

    Examples:
        >>> quil_metadata = NativeQuilMetadata(finalRewiring=[32,21],
                                              gateDepth=5,
                                              gateVolume=6,
                                              multiQubitGateDepth=1,
                                              programDuration=300.1,
                                              programFidelity=0.8989,
                                              qpuRuntimeEstimation=191.21,
                                              topologicalSwaps=0)
        >>> RigettiMetadata(program="DECLARE ro BIT[2]", nativeQuilMetadata=quil_metadata)


    """

    _RIGETTI_METADATA_HEADER = BraketSchemaHeader(
        name="braket.task_result.rigetti_metadata", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_RIGETTI_METADATA_HEADER, const=_RIGETTI_METADATA_HEADER
    )

    nativeQuilMetadata: Optional[NativeQuilMetadata]
    compiledProgram: constr(min_length=2)
