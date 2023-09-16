# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from abc import ABC, abstractmethod


class QAOAInterface(ABC):
    @classmethod
    @abstractmethod
    def initialize_params(cls, np_array):
        """Initialize the parameters to the appropriate format for the autodiff library.
        Args:
            np_array (np.ndarray): Input parameters in Numpy array format.
        Returns:
            array_like: Parameter format needed for the autodiff library.
        """
        pass

    @classmethod
    @abstractmethod
    def get_sgd_optimizer(cls, stepsize, params):
        """Returns the gradient descent optimizer to use, based on the ML framework.
        Args:
            stepsize (float): Step size for the gradient descent optimizer.
            params (array_like): Input parameters, required for the PyTorch optimizer.
        Returns:
            callable: Gradient descent optimizer for the ML framework.
        """
        pass

    @classmethod
    @abstractmethod
    def convert_params_to_numpy(cls, params):
        """Convert params to base Numpy arrays.
        Args:
            params (array_like): A set of parameters.
        Returns:
            np.ndarray: The parameters converted to a Numpy array.
        """
        pass

    @classmethod
    @abstractmethod
    def get_cost_and_step(cls, cost_function, params, optimizer):
        """Evaluate the cost function, then take a step.
        Args:
            cost_function (callable): The cost function.
            params (array_like): The current set of parameters.
            optimizer (callable): The optimizer.
        Returns:
            tuple(array_like, float): The updated set of parameters, and the cost function evaluated
            before the update.
        """
        pass

    @staticmethod
    def get_interface(interface):
        """Get the appropriate interface to use based on the string input.
        Args:
            interface (string): A string specifying the interface to use.
            Must be "autograd", "tf", or "torch".
        Returns:
            QAOAInterface: An interface matching the specified string.
        """
        if interface == "autograd":
            return AutogradInterface()
        elif interface == "tf":
            return TensorFlowInterface()
        elif interface == "torch":
            return PyTorchInterface()
        else:
            raise ValueError(f"Interface {interface} is invalid.")


class AutogradInterface(QAOAInterface):
    # Import only in __init__ so we don't import a library that doesn't exist in the container.
    def __init__(self):
        global qml
        qml = __import__("pennylane", globals(), locals())
        # Equiv to: import pennylane as qml

    @classmethod
    def initialize_params(cls, np_array):
        return qml.numpy.array(np_array, requires_grad=True)

    @classmethod
    def get_sgd_optimizer(cls, stepsize, params):
        return qml.GradientDescentOptimizer(stepsize=stepsize)

    @classmethod
    def convert_params_to_numpy(cls, params):
        return params.numpy()

    @classmethod
    def get_cost_and_step(cls, cost_function, params, optimizer):
        params, cost_before = optimizer.step_and_cost(cost_function, params)
        return params, float(cost_before)


class TensorFlowInterface(QAOAInterface):
    # Import only in __init__ so we don't import a library that doesn't exist in the container.
    def __init__(self):
        global tf
        tf = __import__("tensorflow", globals(), locals())
        # Equiv to: import tensorflow as tf

    @classmethod
    def initialize_params(cls, np_array):
        return tf.Variable(np_array, dtype=tf.float64)

    @classmethod
    def get_sgd_optimizer(cls, stepsize, params):
        return tf.keras.optimizers.legacy.SGD(learning_rate=stepsize)

    @classmethod
    def convert_params_to_numpy(cls, params):
        return params.numpy()

    @classmethod
    def get_cost_and_step(cls, cost_function, params, optimizer):
        def tf_cost():
            global _cached_cost_before
            _cached_cost_before = cost_function(params)
            return _cached_cost_before

        optimizer.minimize(tf_cost, params)
        cost_before = _cached_cost_before

        # Alternative:
        # with tf.GradientTape() as tape:
        #     cost_before = cost_function(params)
        #
        # gradients = tape.gradient(cost_before, params)
        # optimizer.apply_gradients(((gradients, params),))

        return params, float(cost_before)


class PyTorchInterface(QAOAInterface):
    # Import only in __init__ so we don't import a library that doesn't exist in the container.
    def __init__(self):
        global torch
        torch = __import__("torch", globals(), locals())
        # Equiv to: import torch

    @classmethod
    def initialize_params(cls, np_array):
        return torch.tensor(np_array, requires_grad=True)

    @classmethod
    def get_sgd_optimizer(cls, stepsize, params):
        return torch.optim.SGD([params], lr=stepsize)

    @classmethod
    def convert_params_to_numpy(cls, params):
        return params.detach().numpy()

    @classmethod
    def get_cost_and_step(cls, cost_function, params, optimizer):
        optimizer.zero_grad()
        cost_before = cost_function(params)
        cost_before.backward()
        optimizer.step()
        return params, float(cost_before)
