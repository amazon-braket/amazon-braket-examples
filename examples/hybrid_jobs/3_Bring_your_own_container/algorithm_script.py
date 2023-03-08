import os
import time
from datetime import datetime

import pennylane as qml
import spacy_sentence_bert
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric
from braket.tracking import Tracker
from pennylane import numpy as np
from pennylane.templates import AmplitudeEmbedding


def main():
    cost_tracker = Tracker().start()
    np.random.seed(42)

    #################### Set up ####################
    # Set up the problem
    print("=" * 23 + "  Initializing  " + "=" * 23)
    nlp = spacy_sentence_bert.load_model("xx_distiluse_base_multilingual_cased_v2")

    banana_string = [
        "I eat a banana every day.",
        "Bananas are not for her.",
        "Banana shakes are delicious.",
        "How can you like bananas?",
    ]
    banana_embeding = [nlp(d) for d in banana_string]
    data = [d.vector for d in banana_embeding]
    label = [1, -1, 1, -1]
    print("Done.")

    ###################### QML ######################
    # Initialize and train the quantum model
    print("=" * 25 + "  Training  " + "=" * 25)
    qml_model = CCQC(nwires=9)
    opt = qml.AdamOptimizer(stepsize=0.1)
    weights = qml_model.initialize_weights()
    nsteps = 10

    for i in range(1, nsteps + 1):
        weights, cost = opt.step_and_cost(qml_model.cost_batch, *weights, data=data, label=label)

        # echo progress
        current_time = datetime.now().strftime("%H:%M:%S")
        print(
            current_time + " progress: {} / {}   " "cost: {}".format(i, nsteps, np.round(cost, 3))
        )

        # log the cost function as a metric

        braket_tasks_cost = float(
            cost_tracker.simulator_tasks_cost() + cost_tracker.qpu_tasks_cost()
        )

        timestamp = time.time()
        log_metric(
            metric_name="braket_tasks_cost",
            value=braket_tasks_cost,
            iteration_number=i,
            timestamp=timestamp,
        )

        log_metric(metric_name="Cost", value=cost, iteration_number=i, timestamp=timestamp)

    weights = [w.tolist() for w in weights]
    save_job_result(
        {
            "weights": weights,
            "task summary": cost_tracker.quantum_tasks_statistics(),
            "estimated cost": braket_tasks_cost,
        }
    )


class CCQC:
    """Circuit-Centric Quantum Classifier
    Reference: https://arxiv.org/abs/1804.00633
    """

    def __init__(self, nwires, device=None):
        """
        Args:
            nwires (int): Number of qubits.
            device (str): arn of a Braket QPU or simulator.
        """
        self.nwires = nwires
        if device is None:
            self.device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
        else:
            self.device_arn = device

    def q_circuit(self):
        """Quantum circuit for CCQC.
        See figure 4 of https://arxiv.org/abs/1804.00633
        """
        nwires = self.nwires
        dev = qml.device(
            "braket.aws.qubit",
            device_arn=self.device_arn,
            wires=nwires,
            parallel=True,
            max_parallel=30,
            # Set s3_destination_folder=None to output task
            # results to a default folder
            s3_destination_folder=None,
        )

        @qml.qnode(dev, interface="autograd")
        def circuit(*weights, features=np.zeros(2**nwires)):
            AmplitudeEmbedding(features=features, wires=range(nwires), normalize=True, pad_with=0.0)
            w_layer1, w_layer2, rotation = weights
            self._entangle_layer(p1=w_layer1[0], p2=w_layer1[1], rng=1)
            self._entangle_layer(p1=w_layer2[0], p2=w_layer2[1], rng=3)
            qml.Rot(rotation[0], rotation[1], rotation[2], wires=0)
            return qml.expval(qml.PauliZ(0))

        return circuit

    def initialize_weights(self):
        """Initialize the weights in CCQC quantum circuit."""
        w_layer1 = np.random.uniform(size=(2, self.nwires, 3))
        w_layer2 = np.random.uniform(size=(2, self.nwires, 3))
        rotation = np.random.uniform(size=3)
        weights = [w_layer1, w_layer2, rotation]
        return weights

    def cost_batch(self, *w, data=None, label=None):
        """Compute the averaged cost from a list of data and a list of label
        Args:
            w (List[np.ndarray]): The weights of the quantum model.
            data (List[List]): A list of data points.
            label (List): A list of labels.
        """
        result = 0
        for d, l in zip(data, label):
            result += self.cost(*w, data=d, label=l)
        return result / len(data)

    def cost(self, *w, data=None, label=None):
        """Compute the cost from a data point, a pair of data and label.
        Args:
            w (List[np.ndarray]): The weights of the quantum model.
            data (List): A data point.
            label (int): A label.
        """
        cost = -label * self.score(*w, data=data)
        return self._ReLU(cost, margin=0.2)

    def score(self, *w, data=None):
        """Compute the score of a data point, defined by the measuremnt
        in Z basis at the first qubit.
        Args:
            w (List[np.ndarray]): The weights of the quantum model.
            data (List): A data point.
        """
        circuit = self.q_circuit()
        return circuit(*w, features=data)

    def predict(self, *w, data=None):
        """Compute the prediction for a data point. Predict +1 if score is > 0,
        and -1 if the score is <0.
        Args:
            w (List[np.ndarray]): The weights of the quantum model.
            data (List): A data point.
        """
        score = self.score(*w, data=data)
        prediction = 1 if score >= 0 else -1
        return prediction

    def _entangle_layer(self, p1, p2, rng):
        """
        The entanglement block of quantum circuit for CCQC.
        See figure 4 of https://arxiv.org/abs/1804.00633
        Args:
            p1 (np.ndarray): The parameters of rotation gates.
            p1 (np.ndarray): The parameters of controlled rotation gates.
            rng (int): The distance between qubits to apply controlled gates.
        """
        wirelist = range(self.nwires)
        for iw, params in zip(wirelist, p1):
            qml.Rot(params[0], params[1], params[2], wires=iw)
        wire1 = 0
        for _, params in zip(wirelist, p2):
            wire2 = (wire1 - rng) % self.nwires
            qml.CRot(params[0], params[1], params[2], wires=[wire1, wire2])
            wire1 = wire2

    def _ReLU(self, x, margin=0.0):
        """Modified rectified linear unit for the purpose of this exercise.
        Args:
            x (float): Data.
            margin (float): The margin of the ReLU function.
        """
        return max(x + margin, 0)
