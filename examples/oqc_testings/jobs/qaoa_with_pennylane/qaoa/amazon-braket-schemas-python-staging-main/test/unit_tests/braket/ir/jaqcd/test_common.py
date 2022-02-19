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


def single_target_valid_input():
    return {"target": 0}


def two_target_valid_input():
    return {"targets": [0, 1]}


def multi_target_valid_input():
    return {"targets": [0, 1, 2]}


def angle_valid_input():
    return {"angle": 0.123}


def single_probability_valid_input():
    return {"probability": 0.321}


def single_probability_34_valid_input():
    return {"probability": 0.321}


def single_probability_1516_valid_input():
    return {"probability": 0.321}


def damping_probability_valid_input():
    return {"gamma": 0.321}


def damping_single_probability_valid_input():
    return {"probability": 0.321}


def triple_probability_valid_input():
    return {"probX": 0.121, "probY": 0.112, "probZ": 0.132}


def single_control_valid_input():
    return {"control": 0}


def two_control_valid_input():
    return {"controls": [0, 1]}


def multi_control_valid_input():
    return {"controls": [0, 1, 2]}


def two_dimensional_matrix_valid_input():
    return {"matrix": [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]}


def two_dimensional_matrix_list_valid_input():
    return {
        "matrices": [[[[1, 0], [0, 0]], [[0, 0], [1, 0]]], [[[0, 0], [1, 0]], [[1, 0], [0, 0]]]]
    }


def observable_valid_input():
    return {"observable": [[[[0, 0], [1, 0]], [[1, 0], [0, 0]]], "x"]}


def multi_state_valid_input():
    return {"states": ["100", "010"]}


def create_class_instance(switcher, testclass, subclasses):
    input = create_json(switcher, subclasses)
    return testclass(**input)


def create_json(switcher, subclasses):
    input = {}
    for subclass in subclasses:
        input.update(switcher.get(subclass.__name__, lambda: "Invalid subclass")())
    input.update(switcher.get("Type")())
    return input


def create_switcher(type):
    def type_valid_input():
        return {"type": type}

    switcher = {
        "SingleTarget": single_target_valid_input,
        "DoubleTarget": two_target_valid_input,
        "MultiTarget": multi_target_valid_input,
        "Angle": angle_valid_input,
        "SingleProbability": single_probability_valid_input,
        "SingleProbability_34": single_probability_34_valid_input,
        "SingleProbability_1516": single_probability_1516_valid_input,
        "DampingProbability": damping_probability_valid_input,
        "DampingSingleProbability": damping_single_probability_valid_input,
        "TripleProbability": triple_probability_valid_input,
        "SingleControl": single_control_valid_input,
        "DoubleControl": two_control_valid_input,
        "MultiControl": multi_control_valid_input,
        "TwoDimensionalMatrix": two_dimensional_matrix_valid_input,
        "TwoDimensionalMatrixList": two_dimensional_matrix_list_valid_input,
        "Observable": observable_valid_input,
        "MultiState": multi_state_valid_input,
        "OptionalMultiTarget": multi_target_valid_input,
        "Type": type_valid_input,
    }

    return switcher


def create_valid_json(subclasses, type):
    return create_json(create_switcher(type), subclasses)


def create_valid_class_instance(testclass, subclasses, type):
    input = create_valid_json(subclasses, type)
    return testclass(**input)


def idfn(val):
    if isinstance(val, list):
        return "_".join([item.__name__ for item in val])
    elif hasattr(val, __name__):
        return val.__name__
    else:
        return str(val)
