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


class IonqProviderProperties(BraketSchemaBase):
    """
    This defines the properties common to all the IonQ devices.

    Attributes:
        fidelity(Dict[str, Dict[str, float]]): Average fidelity, the measured success
            to perform operations of the given type.
        timing(Dict[str, float]): The timing characteristics of the device. 1Q, 2Q, readout,
            and reset are the operation times. T1 and T2 are decoherence times

    Examples:
        >>> import json
        >>> input_json = {
        ...    "braketSchemaHeader": {
        ...        "name": "braket.device_schema.ionq.ionq_provider_properties",
        ...        "version": "1",
        ...    },
        ...    "fidelity": {
        ...        "1Q": {
        ...          "mean": 0.99717
        ...        },
        ...        "2Q": {
        ...          "mean": 0.9696
        ...        },
        ...        "spam": {
        ...          "mean": 0.9961
        ...        }
        ...      },
        ...      "timing": {
        ...        "T1": 10000000000,
        ...        "T2": 500000,
        ...        "1Q": 1.1e-05,
        ...        "2Q": 0.00021,
        ...        "readout": 0.000175,
        ...        "reset": 3.5e-05
        ...      },
        ...}
        >>> IonqProviderProperties.parse_raw_schema(json.dumps(input_json))
    """

    _PROGRAM_HEADER = BraketSchemaHeader(
        name="braket.device_schema.ionq.ionq_provider_properties", version="1"
    )
    braketSchemaHeader: BraketSchemaHeader = Field(default=_PROGRAM_HEADER, const=_PROGRAM_HEADER)
    fidelity: Dict[str, Dict[str, float]]
    timing: Dict[str, float]
