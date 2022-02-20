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

import numpy as np

from braket.circuits import AsciiCircuitDiagram, Circuit, Gate, Instruction, Observable, Operator


def test_empty_circuit():
    assert AsciiCircuitDiagram.build_diagram(Circuit()) == ""


def test_one_gate_one_qubit():
    circ = Circuit().h(0)
    expected = ("T  : |0|", "        ", "q0 : -H-", "", "T  : |0|")
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_qubit_width():
    circ = Circuit().h(0).h(100)
    expected = (
        "T    : |0|",
        "          ",
        "q0   : -H-",
        "          ",
        "q100 : -H-",
        "",
        "T    : |0|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_gate_width():
    class Foo(Gate):
        def __init__(self):
            super().__init__(qubit_count=1, ascii_symbols=["FOO"])

        def to_ir(self, target):
            return "foo"

    circ = Circuit().h(0).h(1).add_instruction(Instruction(Foo(), 0))
    expected = (
        "T  : |0| 1 |",
        "            ",
        "q0 : -H-FOO-",
        "            ",
        "q1 : -H-----",
        "",
        "T  : |0| 1 |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_time_width():
    circ = Circuit()
    num_qubits = 15
    for qubit in range(num_qubits):
        if qubit == num_qubits - 1:
            break
        circ.cnot(qubit, qubit + 1)
    expected = (
        "T   : |0|1|2|3|4|5|6|7|8|9|10|11|12|13|",
        "                                       ",
        "q0  : -C-------------------------------",
        "       |                               ",
        "q1  : -X-C-----------------------------",
        "         |                             ",
        "q2  : ---X-C---------------------------",
        "           |                           ",
        "q3  : -----X-C-------------------------",
        "             |                         ",
        "q4  : -------X-C-----------------------",
        "               |                       ",
        "q5  : ---------X-C---------------------",
        "                 |                     ",
        "q6  : -----------X-C-------------------",
        "                   |                   ",
        "q7  : -------------X-C-----------------",
        "                     |                 ",
        "q8  : ---------------X-C---------------",
        "                       |               ",
        "q9  : -----------------X-C-------------",
        "                         |             ",
        "q10 : -------------------X-C-----------",
        "                           |           ",
        "q11 : ---------------------X--C--------",
        "                              |        ",
        "q12 : ------------------------X--C-----",
        "                                 |     ",
        "q13 : ---------------------------X--C--",
        "                                    |  ",
        "q14 : ------------------------------X--",
        "",
        "T   : |0|1|2|3|4|5|6|7|8|9|10|11|12|13|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_connector_across_two_qubits():
    circ = Circuit().cnot(3, 4).h(range(2, 6))
    expected = (
        "T  : |0|1|",
        "          ",
        "q2 : -H---",
        "          ",
        "q3 : -C-H-",
        "      |   ",
        "q4 : -X-H-",
        "          ",
        "q5 : -H---",
        "",
        "T  : |0|1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_overlapping_qubits():
    circ = Circuit().cnot(0, 2).cnot(1, 3).h(0)
    expected = (
        "T  : | 0 |1|",
        "            ",
        "q0 : -C---H-",
        "      |     ",
        "q1 : -|-C---",
        "      | |   ",
        "q2 : -X-|---",
        "        |   ",
        "q3 : ---X---",
        "",
        "T  : | 0 |1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_overlapping_qubits_angled_gates():
    circ = Circuit().zz(0, 2, 0.15).cnot(1, 3).h(0)
    expected = (
        "T  : |    0     |1|",
        "                   ",
        "q0 : -ZZ(0.15)---H-",
        "      |            ",
        "q1 : -|--------C---",
        "      |        |   ",
        "q2 : -ZZ(0.15)-|---",
        "               |   ",
        "q3 : ----------X---",
        "",
        "T  : |    0     |1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_connector_across_gt_two_qubits():
    circ = Circuit().h(4).cnot(3, 5).h(4).h(2)
    expected = (
        "T  : | 0 |1|",
        "            ",
        "q2 : -H-----",
        "            ",
        "q3 : ---C---",
        "        |   ",
        "q4 : -H-|-H-",
        "        |   ",
        "q5 : ---X---",
        "",
        "T  : | 0 |1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_connector_across_non_used_qubits():
    circ = Circuit().h(4).cnot(3, 100).h(4).h(101)
    expected = (
        "T    : | 0 |1|",
        "              ",
        "q3   : ---C---",
        "          |   ",
        "q4   : -H-|-H-",
        "          |   ",
        "q100 : ---X---",
        "              ",
        "q101 : -H-----",
        "",
        "T    : | 0 |1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_1q_no_preceding():
    circ = Circuit().add_verbatim_box(Circuit().h(0))
    expected = (
        "T  : |      0      |1|     2     |",
        "                                  ",
        "q0 : -StartVerbatim-H-EndVerbatim-",
        "",
        "T  : |      0      |1|     2     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_1q_preceding():
    circ = Circuit().h(0).add_verbatim_box(Circuit().h(0))
    expected = (
        "T  : |0|      1      |2|     3     |",
        "                                    ",
        "q0 : -H-StartVerbatim-H-EndVerbatim-",
        "",
        "T  : |0|      1      |2|     3     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_1q_following():
    circ = Circuit().add_verbatim_box(Circuit().h(0)).h(0)
    expected = (
        "T  : |      0      |1|     2     |3|",
        "                                    ",
        "q0 : -StartVerbatim-H-EndVerbatim-H-",
        "",
        "T  : |      0      |1|     2     |3|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_2q_no_preceding():
    circ = Circuit().add_verbatim_box(Circuit().h(0).cnot(0, 1))
    expected = (
        "T  : |      0      |1|2|     3     |",
        "                                    ",
        "q0 : -StartVerbatim-H-C-EndVerbatim-",
        "      |               | |           ",
        "q1 : -*************---X-***********-",
        "",
        "T  : |      0      |1|2|     3     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_2q_preceding():
    circ = Circuit().h(0).add_verbatim_box(Circuit().h(0).cnot(0, 1))
    expected = (
        "T  : |0|      1      |2|3|     4     |",
        "                                      ",
        "q0 : -H-StartVerbatim-H-C-EndVerbatim-",
        "        |               | |           ",
        "q1 : ---*************---X-***********-",
        "",
        "T  : |0|      1      |2|3|     4     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_2q_following():
    circ = Circuit().add_verbatim_box(Circuit().h(0).cnot(0, 1)).h(0)
    expected = (
        "T  : |      0      |1|2|     3     |4|",
        "                                      ",
        "q0 : -StartVerbatim-H-C-EndVerbatim-H-",
        "      |               | |             ",
        "q1 : -*************---X-***********---",
        "",
        "T  : |      0      |1|2|     3     |4|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_3q_no_preceding():
    circ = Circuit().add_verbatim_box(Circuit().h(0).cnot(0, 1).cnot(1, 2))
    expected = (
        "T  : |      0      |1|2|3|     4     |",
        "                                      ",
        "q0 : -StartVerbatim-H-C---EndVerbatim-",
        "      |               |   |           ",
        "q1 : -|---------------X-C-|-----------",
        "      |                 | |           ",
        "q2 : -*************-----X-***********-",
        "",
        "T  : |      0      |1|2|3|     4     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_3q_preceding():
    circ = Circuit().h(0).add_verbatim_box(Circuit().h(0).cnot(0, 1).cnot(1, 2))
    expected = (
        "T  : |0|      1      |2|3|4|     5     |",
        "                                        ",
        "q0 : -H-StartVerbatim-H-C---EndVerbatim-",
        "        |               |   |           ",
        "q1 : ---|---------------X-C-|-----------",
        "        |                 | |           ",
        "q2 : ---*************-----X-***********-",
        "",
        "T  : |0|      1      |2|3|4|     5     |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_3q_following():
    circ = Circuit().add_verbatim_box(Circuit().h(0).cnot(0, 1).cnot(1, 2)).h(0)
    expected = (
        "T  : |      0      |1|2|3|     4     |5|",
        "                                        ",
        "q0 : -StartVerbatim-H-C---EndVerbatim-H-",
        "      |               |   |             ",
        "q1 : -|---------------X-C-|-------------",
        "      |                 | |             ",
        "q2 : -*************-----X-***********---",
        "",
        "T  : |      0      |1|2|3|     4     |5|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_different_qubits():
    circ = Circuit().h(1).add_verbatim_box(Circuit().h(0)).cnot(3, 4)
    expected = (
        "T  : |0|      1      |2|     3     |4|",
        "                                      ",
        "q0 : ---StartVerbatim-H-EndVerbatim---",
        "        |               |             ",
        "q1 : -H-|---------------|-------------",
        "        |               |             ",
        "q3 : ---|---------------|-----------C-",
        "        |               |           | ",
        "q4 : ---*************---***********-X-",
        "",
        "T  : |0|      1      |2|     3     |4|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_verbatim_qubset_qubits():
    circ = Circuit().h(1).cnot(0, 1).cnot(1, 2).add_verbatim_box(Circuit().h(1)).cnot(2, 3)
    expected = (
        "T  : |0|1|2|      3      |4|     5     |6|",
        "                                          ",
        "q0 : ---C---StartVerbatim---EndVerbatim---",
        "        |   |               |             ",
        "q1 : -H-X-C-|-------------H-|-------------",
        "          | |               |             ",
        "q2 : -----X-|---------------|-----------C-",
        "            |               |           | ",
        "q3 : -------*************---***********-X-",
        "",
        "T  : |0|1|2|      3      |4|     5     |6|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_ignore_non_gates():
    class Foo(Operator):
        @property
        def name(self) -> str:
            return "foo"

        def to_ir(self, target):
            return "foo"

    circ = Circuit().h(0).h(1).cnot(1, 2).add_instruction(Instruction(Foo(), 0))
    expected = (
        "T  : |0|1|",
        "          ",
        "q0 : -H---",
        "          ",
        "q1 : -H-C-",
        "        | ",
        "q2 : ---X-",
        "",
        "T  : |0|1|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_result_types_target_none():
    circ = Circuit().h(0).h(100).probability()
    expected = (
        "T    : |0|Result Types|",
        "                       ",
        "q0   : -H-Probability--",
        "          |            ",
        "q100 : -H-Probability--",
        "",
        "T    : |0|Result Types|",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_result_types_target_some():
    circ = (
        Circuit()
        .h(0)
        .h(1)
        .h(100)
        .expectation(observable=Observable.Y() @ Observable.Z(), target=[0, 100])
    )
    expected = (
        "T    : |0|  Result Types  |",
        "                           ",
        "q0   : -H-Expectation(Y@Z)-",
        "          |                ",
        "q1   : -H-|----------------",
        "          |                ",
        "q100 : -H-Expectation(Y@Z)-",
        "",
        "T    : |0|  Result Types  |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_additional_result_types():
    circ = Circuit().h(0).h(1).h(100).state_vector().amplitude(["110", "001"])
    expected = (
        "T    : |0|",
        "          ",
        "q0   : -H-",
        "          ",
        "q1   : -H-",
        "          ",
        "q100 : -H-",
        "",
        "T    : |0|",
        "",
        "Additional result types: StateVector, Amplitude(110,001)",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_multiple_result_types():
    circ = (
        Circuit()
        .cnot(0, 2)
        .cnot(1, 3)
        .h(0)
        .variance(observable=Observable.Y(), target=0)
        .expectation(observable=Observable.Y(), target=2)
        .sample(observable=Observable.Y())
    )
    expected = (
        "T  : | 0 |1|      Result Types      |",
        "                                     ",
        "q0 : -C---H-Variance(Y)----Sample(Y)-",
        "      |                    |         ",
        "q1 : -|-C------------------Sample(Y)-",
        "      | |                  |         ",
        "q2 : -X-|---Expectation(Y)-Sample(Y)-",
        "        |                  |         ",
        "q3 : ---X------------------Sample(Y)-",
        "",
        "T  : | 0 |1|      Result Types      |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_multiple_result_types_with_state_vector_amplitude():
    circ = (
        Circuit()
        .cnot(0, 2)
        .cnot(1, 3)
        .h(0)
        .variance(observable=Observable.Y(), target=0)
        .expectation(observable=Observable.Y(), target=3)
        .expectation(observable=Observable.Hermitian(np.array([[1.0, 0.0], [0.0, 1.0]])), target=1)
        .amplitude(["0001"])
        .state_vector()
    )
    expected = (
        "T  : | 0 |1|     Result Types     |",
        "                                   ",
        "q0 : -C---H-Variance(Y)------------",
        "      |                            ",
        "q1 : -|-C---Expectation(Hermitian)-",
        "      | |                          ",
        "q2 : -X-|--------------------------",
        "        |                          ",
        "q3 : ---X---Expectation(Y)---------",
        "",
        "T  : | 0 |1|     Result Types     |",
        "",
        "Additional result types: Amplitude(0001), StateVector",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_multiple_result_types_with_custom_hermitian_ascii_symbol():
    herm_matrix = (Observable.Y() @ Observable.Z()).to_matrix()
    circ = (
        Circuit()
        .cnot(0, 2)
        .cnot(1, 3)
        .h(0)
        .variance(observable=Observable.Y(), target=0)
        .expectation(observable=Observable.Y(), target=3)
        .expectation(
            observable=Observable.Hermitian(
                matrix=herm_matrix,
                display_name="MyHerm",
            ),
            target=[1, 2],
        )
    )
    expected = (
        "T  : | 0 |1|   Result Types    |",
        "                                ",
        "q0 : -C---H-Variance(Y)---------",
        "      |                         ",
        "q1 : -|-C---Expectation(MyHerm)-",
        "      | |   |                   ",
        "q2 : -X-|---Expectation(MyHerm)-",
        "        |                       ",
        "q3 : ---X---Expectation(Y)------",
        "",
        "T  : | 0 |1|   Result Types    |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_noise_1qubit():
    circ = Circuit().h(0).x(1).bit_flip(1, 0.1)
    expected = (
        "T  : |    0    |",
        "                ",
        "q0 : -H---------",
        "                ",
        "q1 : -X-BF(0.1)-",
        "",
        "T  : |    0    |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected


def test_noise_2qubit():
    circ = Circuit().h(1).kraus((0, 2), [np.eye(4)])
    expected = (
        "T  : | 0  |",
        "           ",
        "q0 : ---KR-",
        "        |  ",
        "q1 : -H-|--",
        "        |  ",
        "q2 : ---KR-",
        "",
        "T  : | 0  |",
    )
    expected = "\n".join(expected)
    assert AsciiCircuitDiagram.build_diagram(circ) == expected
