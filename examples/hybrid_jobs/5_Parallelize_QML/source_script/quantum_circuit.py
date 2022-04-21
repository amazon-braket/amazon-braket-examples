import os
import numpy as np
import pennylane as qml
from pennylane.templates import AngleEmbedding
import torch


class QuantumCircuit:
    def __init__(self, qc_dev):
        """
        Args:
            qc_dev (qml.device): a pennylane device.
        """
        self.qc_dev = qc_dev
        self.nwires = len(qc_dev.wires)

    def q_circuit(self):
        """Quantum circuit
        """
        nwires = self.nwires
        qc_dev = self.qc_dev

        @qml.qnode(qc_dev, interface="torch", diff_method="adjoint")
        def circuit(inputs, w_layer1, w_layer2, rotation):
            AngleEmbedding(features=inputs, wires=range(nwires))
            self._entangle_layer(p1=w_layer1[0], p2=w_layer1[1], rng=1)
            self._entangle_layer(p1=w_layer2[0], p2=w_layer2[1], rng=3)
            qml.Rot(rotation[0], rotation[1], rotation[2], wires=0)
            return [qml.expval(qml.PauliZ(0))]

        return circuit

    def initialize_weights(self):
        """Initialize the weights in CCQC quantum circuit."""
        w_layer1 = torch.randn((2, self.nwires, 3), dtype=torch.float64) 
        w_layer2 = torch.randn((2, self.nwires, 3), dtype=torch.float64) 
        rotation = torch.randn((3,), dtype=torch.float64) 
        weights = [w_layer1, w_layer2, rotation]
        return weights

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
            qml.CRot.compute_decomposition(params[0], params[1], params[2], wires=[wire1, wire2])
            wire1 = wire2        