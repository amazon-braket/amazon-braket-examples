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

import math
from typing import Dict, List

import matplotlib.pyplot as plt


# deutsch jozsa
# bernstein vazirani
def plot_bitstrings(
    probabilities: Dict[str, float],
    title: str = None,
) -> None:
    """Plot the measurement results.

    Args:
        probabilities (Dict[str, float]): Measurement probabilities.
        title (str): Title for the plot.
        xlabel (str): xlabel for the plot.
        ylabel (str): ylabel for the plot.
    """
    plt.bar(probabilities.keys(), probabilities.values())
    plt.xlabel("bitstrings")
    plt.ylabel("probabilities")
    plt.title(title)
    plt.xticks(rotation=90)


# grovers and quantum fourier transform
def plot_bitstrings_formatted(probabilities: List[float]) -> None:
    """Format the bistring and plot the measure results.

    Args:
        probabilities (List[float]): Probabilities of measuring each bitstring.
    """
    num_qubits = int(math.log2(len(probabilities)))
    format_bitstring = "{0:0" + str(num_qubits) + "b}"
    bitstring_keys = [format_bitstring.format(ii) for ii in range(2**num_qubits)]

    plt.bar(bitstring_keys, probabilities)
    plt.xlabel("bitstrings")
    plt.ylabel("probability")
    plt.xticks(rotation=90)
