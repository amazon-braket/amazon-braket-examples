import numpy as np
import pennylane as qml
import torch
from qml_script.quantum_circuit import QuantumCircuit
from torch import nn


class DressedQNN(nn.Module):
    def __init__(self, qc_dev):
        super().__init__()
        nwires = len(qc_dev.wires)
        q_circuit = QuantumCircuit(qc_dev)
        weights = q_circuit.initialize_weights()
        self.circuit = q_circuit.q_circuit()

        self.qlayer = qml.qnn.TorchLayer(
            self.circuit,
            {
                "w_layer1": weights[0].shape,
                "w_layer2": weights[1].shape,
                "rotation": weights[2].shape,
            },
        )
        self.input_layer = nn.Linear(60, nwires)
        self.output_layer = nn.Linear(1, 1)

    def forward(self, x):
        x = self.input_layer(x)
        x = (torch.sigmoid(x) - 0.5) * 2 * np.pi
        x = self.qlayer(x)
        x = self.output_layer(x)
        x = torch.squeeze(x)
        return x
