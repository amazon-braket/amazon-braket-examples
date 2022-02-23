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

from pydantic import BaseModel


class DeviceConnectivity(BaseModel):

    """
    This schema defines the common properties that need to be existent if a connection is defined.

    Attributes:

        fullyConnected: If each qubit is connected to all other qubits then
            it called fully connected. true if fully connected else it will be false.

        connectivityGraph: It defines for each qubit what are the connected qubits.
            For a fullyConnected graph it will be empty since all the qubits are
            connected to each other


    Examples:
        >>> import json
        >>> input_json = {
        ...    "fullyConnected": False,
        ...    "connectivityGraph": {"1": ["2", "3"]},
        ... }
        >>> DeviceConnectivity.parse_raw(json.dumps(input_json))
    """

    fullyConnected: bool
    connectivityGraph: dict
