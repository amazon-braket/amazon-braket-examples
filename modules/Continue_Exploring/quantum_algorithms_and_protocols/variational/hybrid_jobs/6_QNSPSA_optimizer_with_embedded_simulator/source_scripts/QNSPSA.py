import random
import pennylane as qml
from pennylane import numpy as np
from scipy.linalg import sqrtm
import warnings


class QNSPSA:
    """Quantum natural SPSA optimizer. Refer to https://quantum-journal.org/papers/q-2021-10-20-567/
    for a detailed description of the methodology. When disable_metric_tensor
    is set to be True, the metric tensor estimation is disabled, and QNSPSA is
    reduced to be a SPSA optimizer.

    Args:
        stepsize (float): The learn rate.
        regularization (float): Regularitzation term to the Fubini-Study
            metric tensor for numerical stability.
        finite_diff_step (float): step size to compute the finite difference
            gradient and the Fubini-Study metric tensor.
        resamplings (int): The number of samples to average for each parameter
            update.
        blocking (boolean): When set to be True, the optimizer only accepts
            updates that leads to a loss value no larger than the loss value
            before update, plus a tolerance. The tolerance is set with the
            parameter history_length.
        history_length (int): When blocking is True, the tolerance is set to be
            the average of the cost values in the last history_length steps.
        disable_metric_tensor (boolean): When set to be True, the optimizer is
            reduced to be a (1st-order) SPSA optimizer.
        seed (int): Seed for the random sampling.
    """

    def __init__(
        self,
        stepsize=1e-3,
        regularization=1e-3,
        finite_diff_step=1e-2,
        resamplings=1,
        blocking=True,
        history_length=5,
        disable_metric_tensor=False,
        seed=None,
    ):
        self.stepsize = stepsize
        self.reg = regularization
        self.finite_diff_step = finite_diff_step
        self.metric_tensor = None
        self.k = 1
        self.resamplings = resamplings
        self.blocking = blocking
        self.last_n_steps = np.zeros(history_length)
        self.history_length = history_length
        self.disable_metric_tensor = disable_metric_tensor
        random.seed(seed)
        return

    def step(self, cost, params):
        """Update trainable arguments with one step of the optimizer.

        .. warning::
            When blocking is set to be True, use step_and_cost instead, as loss
            measurements are required for the updates for the case.

        Args:
            cost (qml.QNode): the QNode wrapper for the objective function for
            optimization
            params (np.array): Parameter before update.

        Returns:
            np.array: The new variable values after step-wise update.
        """
        if self.blocking:
            warnings.warn(
                "step_and_cost() instead of step() is called when "
                "blocking is turned on, as the step-wise loss value "
                "is required by the algorithm.",
                stacklevel=2,
            )
            return self.step_and_cost(cost, params)[0]

        if self.disable_metric_tensor:
            return self.__step_core_first_order(cost, params)
        return self.__step_core(cost, params)

    def step_and_cost(self, cost, params):
        """Update trainable parameters with one step of the optimizer and return
        the corresponding objective function value after the step.

        Args:
            cost (qml.QNode): the QNode wrapper for the objective function for
                optimization
            params (np.array): Parameter before update.

        Returns:
            tuple[np.array, float]: the updated parameter and the objective
                function output before the step.
        """
        params_next = (
            self.__step_core_first_order(cost, params)
            if self.disable_metric_tensor
            else self.__step_core(cost, params)
        )

        if not self.blocking:
            loss_curr = cost(params)
            return params_next, loss_curr
        params_next, loss_curr = self.__apply_blocking(cost, params, params_next)
        return params_next, loss_curr

    def __step_core(self, cost, params):
        grad_avg = np.zeros(params.shape)
        tensor_avg = np.zeros((params.size, params.size))
        for i in range(self.resamplings):
            grad_tapes, grad_dir = self.__get_spsa_grad_tapes(cost, params)
            metric_tapes, tensor_dirs = self.__get_tensor_tapes(cost, params)
            raw_results = qml.execute(grad_tapes + metric_tapes, cost.device, None)
            grad = self.__post_process_grad(raw_results[:2], grad_dir)
            metric_tensor = self.__post_process_tensor(raw_results[2:], tensor_dirs)
            grad_avg = grad_avg * i / (i + 1) + grad / (i + 1)
            tensor_avg = tensor_avg * i / (i + 1) + metric_tensor / (i + 1)

        self.__update_tensor(tensor_avg)
        return self.__get_next_params(params, grad_avg)

    def __step_core_first_order(self, cost, params):
        grad_avg = np.zeros(params.shape)
        for i in range(self.resamplings):
            grad_tapes, grad_dir = self.__get_spsa_grad_tapes(cost, params)
            raw_results = qml.execute(grad_tapes, cost.device, None)
            grad = self.__post_process_grad(raw_results, grad_dir)
            grad_avg = grad_avg * i / (i + 1) + grad / (i + 1)
        return params - self.stepsize * grad_avg

    def __post_process_grad(self, grad_raw_results, grad_dir):
        loss_forward, loss_backward = grad_raw_results
        grad = (loss_forward - loss_backward) / (2 * self.finite_diff_step) * grad_dir
        return grad

    def __post_process_tensor(self, tensor_raw_results, tensor_dirs):
        tensor_finite_diff = (
            tensor_raw_results[0][0][0]
            - tensor_raw_results[1][0][0]
            - tensor_raw_results[2][0][0]
            + tensor_raw_results[3][0][0]
        )
        metric_tensor = (
            -(
                np.tensordot(tensor_dirs[0], tensor_dirs[1], axes=0)
                + np.tensordot(tensor_dirs[1], tensor_dirs[0], axes=0)
            )
            * tensor_finite_diff
            / (8 * self.finite_diff_step * self.finite_diff_step)
        )
        return metric_tensor

    def __get_next_params(self, params, gradient):
        grad_vec, params_vec = gradient.reshape(-1), params.reshape(-1)
        new_params_vec = np.linalg.solve(
            self.metric_tensor,
            (-self.stepsize * grad_vec + np.matmul(self.metric_tensor, params_vec)),
        )
        return new_params_vec.reshape(params.shape)

    def __get_perturbation_direction(self, params):
        param_number = len(params) if isinstance(params, list) else params.size
        sample_list = random.choices([-1, 1], k=param_number)
        direction = np.array(sample_list).reshape(params.shape)
        return direction

    def __get_spsa_grad_tapes(self, cost, params):
        direction = self.__get_perturbation_direction(params)
        cost.construct([params + self.finite_diff_step * direction], {})
        tape_forward = cost.tape.copy(copy_operations=True)
        cost.construct([params - self.finite_diff_step * direction], {})
        tape_backward = cost.tape.copy(copy_operations=True)
        return [tape_forward, tape_backward], direction

    def __update_tensor(self, tensor_raw):
        tensor_avg = self.__get_tensor_moving_avg(tensor_raw)
        tensor_regularized = self.__regularize_tensor(tensor_avg)
        self.metric_tensor = tensor_regularized
        self.k += 1

    def __get_tensor_tapes(self, cost, params):
        dir1 = self.__get_perturbation_direction(params)
        dir2 = self.__get_perturbation_direction(params)
        perturb1 = dir1 * self.finite_diff_step
        perturb2 = dir2 * self.finite_diff_step
        dir_vecs = dir1.reshape(-1), dir2.reshape(-1)

        tapes = [
            self.__get_overlap_tape(cost, params, params + perturb1 + perturb2),
            self.__get_overlap_tape(cost, params, params + perturb1),
            self.__get_overlap_tape(cost, params, params - perturb1 + perturb2),
            self.__get_overlap_tape(cost, params, params - perturb1),
        ]
        return tapes, dir_vecs

    def __get_overlap_tape(self, cost, params1, params2):
        op_forward = self.__get_operations(cost, params1)
        op_inv = self.__get_operations(cost, params2)

        with qml.tape.QuantumTape() as tape:
            for op in op_forward:
                qml.apply(op)
            for op in reversed(op_inv):
                op.adjoint()
            qml.probs(wires=cost.tape.wires.labels)
        return tape

    def __get_operations(self, cost, params):
        cost.construct([params], {})
        return cost.tape.operations

    def __get_tensor_moving_avg(self, metric_tensor):
        if self.metric_tensor is None:
            self.metric_tensor = np.identity(metric_tensor.shape[0])
        return (
            self.k / (self.k + 1) * self.metric_tensor
            + 1 / (self.k + 1) * metric_tensor
        )

    def __regularize_tensor(self, metric_tensor):
        tensor_reg = np.real(sqrtm(np.matmul(metric_tensor, metric_tensor)))
        return (tensor_reg + self.reg * np.identity(metric_tensor.shape[0])) / (
            1 + self.reg
        )

    def __apply_blocking(self, cost, params_curr, params_next):
        cost.construct([params_curr], {})
        tape_loss_curr = cost.tape.copy(copy_operations=True)
        cost.construct([params_next], {})
        tape_loss_next = cost.tape.copy(copy_operations=True)

        loss_curr, loss_next = qml.execute(
            [tape_loss_curr, tape_loss_next], cost.device, None
        )
        # self.k has been updated earlier
        ind = (self.k - 2) % self.history_length
        self.last_n_steps[ind] = loss_curr

        tol = (
            2 * self.last_n_steps.std()
            if self.k > self.history_length
            else 2 * self.last_n_steps[: self.k - 1].std()
        )

        if loss_curr + tol < loss_next:
            params_next = params_curr
        return params_next, loss_curr
