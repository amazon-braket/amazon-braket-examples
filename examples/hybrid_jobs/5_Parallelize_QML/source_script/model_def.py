import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

import pennylane as qml

from source_script.quantum_circuit import QuantumCircuit


class DressedQNN(nn.Module):
    def __init__(self, qc_dev):
        super(DressedQNN, self).__init__()
        nwires = len(qc_dev.wires)
        q_circuit = QuantumCircuit(qc_dev)
        weights = q_circuit.initialize_weights()
        self.w1 = nn.Parameter(weights[0])
        self.w2 = nn.Parameter(weights[1])
        self.rot = nn.Parameter(weights[2])
        self.circuit = q_circuit.q_circuit()
        
        self.qlayer = qml.qnn.TorchLayer(self.circuit, {"w_layer1": self.w1.shape,
                                                        "w_layer2": self.w2.shape,
                                                        "rotation": self.rot.shape,
                                                        }
                                        )
        self.input_layer = nn.Linear(60, nwires, dtype=torch.float32)
        self.output_layer = nn.Linear(1, 1, dtype=torch.float32)
        # self.bias = nn.Parameter(torch.tensor(0.0))

    def forward(self, x):
        x = self.input_layer(x)
        x = (torch.sigmoid(x)-0.5) * 2 * np.pi
        # x = F.sigmoid(x) * 2 * np.pi

        x = self.qlayer(x)
        # x = torch.stack([self.circuit(f, self.w1 ,self.w2 ,self.rot) for f in x])

        x = self.output_layer(x)
        # x = x + self.bias
        x = torch.squeeze(x)
        return x