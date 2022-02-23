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

from typing import Dict

from pydantic import Field

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class RigettiProviderProperties(BraketSchemaBase):
    """
    This defines the parameters common to all Rigetti devices.

    Attributes:
        specs (Dict[str, Dict[str, Dict[str, float]]]): Basic specifications for the device,
            such as gate fidelities and coherence times. More details at
            https://pyquil-docs.rigetti.com/en/stable/apidocs/autogen/pyquil.device.Specs.html

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.rigetti.rigetti_provider_properties",
        ...        "version": "1",
        ...    },
        ...    "specs": {
        ...        "1Q": {
        ...            "0": {
        ...                "T1": 1.69308193540552e-05,
        ...                "T2": 1.8719137150144e-05,
        ...                "f1QRB": 0.995048041389577,
        ...                "f1QRB_std_err": 0.000244061520274907,
        ...                "f1Q_simultaneous_RB": 0.989821537688075,
        ...                "f1Q_simultaneous_RB_std_err": 0.000699235456806402,
        ...                "fActiveReset": 0.978,
        ...                "fRO": 0.919,
        ...            },
        ...        },
        ...        "2Q": {
        ...            "0-1": {
        ...                "Avg_T1": 2.679913663417025e-05,
        ...                "Avg_T2": 2.957247297939755e-05,
        ...                "Avg_f1QRB": 0.9973200289413551,
        ...                "Avg_f1QRB_std_err": 0.000219048562898114,
        ...                "Avg_f1Q_simultaneous_RB": 0.9933270881335465,
        ...                "Avg_f1Q_simultaneous_RB_std_err": 0.000400066119480196,
        ...                "Avg_fActiveReset": 0.8425,
        ...                "Avg_fRO": 0.9165000000000001,
        ...                "fCZ": 0.843255182448229,
        ...                "fCZ_std_err": 0.00806009046760912,
        ...            }
        ...        },
        ...  }
        >>> RigettiProviderProperties.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.rigetti.rigetti_provider_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    specs: Dict[str, Dict[str, Dict[str, float]]]
