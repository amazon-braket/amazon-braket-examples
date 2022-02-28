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

from typing import List, Optional, Union

from pydantic import Field

from braket.device_schema.dwave.dwave_provider_level_parameters_v1 import (
    PostProcessingType,
    ResultFormat,
)
from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class Dwave2000QDeviceLevelParameters(BraketSchemaBase):
    """
    This is the description of the D-Wave parameters

    Attributes:
        annealingOffsets (Optional[List[float]]): Provides offsets to annealing paths, per qubit.
        annealingSchedule (Optional[List[List[float]]]): Introduces variations to the global anneal
            schedule.
        annealingDuration (Optional[int] = Field(gt=1)): Sets the duration (in microseconds) of
            quantum annealing time, per read.
        autoScale (Optional[bool]): Indicates whether h and J values are rescaled.
        beta (Optional[float]): Provides a value for the Boltzmann distribution parameter.
            Used when sampling postprocessing is enabled on D-Wave 2000Q and earlier systems.
        chains (Optional[List[List[int]]]): Defines which qubits represent the same logical
            variable. Used only when postprocessing is enabled on D-Wave 2000Q and earlier systems.
            Ensures that all qubits in the same chain have the same value within each sample.
        compensateFluxDrift (Optional[bool]): Boolean flag indicating whether the D-Wave system
            compensates for flux drift.
        fluxBiases (Optional[List[float]]): List of flux-bias offset values with which to calibrate
            a chain. Often required when using the extended J range to create a strongly coupled
            chain for certain embeddings.
        initialState (Optional[List[int]]): When using the reverse annealing feature,
            you must supply the initial state to which the system is set.
        maxResults (Optional[int] = Field(gt=1)): Specifies the maximum number of
            answers returned from the solver.
        postprocessingType (Optional[Union[PostProcessingType, str]]): Defines what type
             of postprocessing the system runs online on raw solutions.
        programmingThermalizationDuration (Optional[int]): Gives the time (in microseconds) to wait
            after programming the QPU for it to cool back to base temperature (i.e.,
            post-programming thermalization time).
        readoutThermalizationDuration (Optional[int]): Gives the time (in microseconds) to wait
            after each state is read from the QPU for it to cool back to base temperature
            (i.e., post-readout thermalization time).
        reduceIntersampleCorrelation (Optional[bool]): Reduces sample-to-sample correlations caused
            by the spin-bath polarization effect by adding a delay between reads.
        reinitializeState (Optional[bool]): When using the reverse annealing feature,
            you must supply the initial state to which the system is set.
        resultFormat (Optional[ResultFormat]): Type of the result format returned by the QPU.
        spinReversalTransformCount (Optional[int] = Field(gt=0)): Specifies the number of
            spin-reversal transforms to perform.

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.dwave.dwave_2000Q_device_level_parameters",
        ...        "version": "1",
        ...    },
        ...    "beta": 1
        ... }
        >>> Dwave2000QDeviceLevelParameters.parse_raw_schema(json.dumps(input_json))

    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.dwave.dwave_2000Q_device_level_parameters", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    annealingOffsets: Optional[List[float]]
    annealingSchedule: Optional[List[List[float]]]
    annealingDuration: Optional[float] = Field(gt=0)
    autoScale: Optional[bool]
    beta: Optional[float]
    chains: Optional[List[List[int]]]
    compensateFluxDrift: Optional[bool]
    fluxBiases: Optional[List[float]]
    initialState: Optional[List[int]]
    maxResults: Optional[int] = Field(gt=0)
    postprocessingType: Optional[Union[PostProcessingType, str]]
    programmingThermalizationDuration: Optional[int]
    readoutThermalizationDuration: Optional[int]
    reduceIntersampleCorrelation: Optional[bool]
    reinitializeState: Optional[bool]
    resultFormat: Optional[ResultFormat]
    spinReversalTransformCount: Optional[int] = Field(gt=0)
