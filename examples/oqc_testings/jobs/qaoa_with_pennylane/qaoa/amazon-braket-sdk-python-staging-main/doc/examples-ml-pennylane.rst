################################
Quantum machine learning and optimization with PennyLane
################################

Learn more about how to combine PennyLane with Amazon Braket.

.. toctree::
    :maxdepth: 2

**************************
`Combining PennyLane with Amazon Braket <https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/0_Getting_started.ipynb>`_
**************************

This tutorial shows you how to construct circuits and evaluate their gradients in 
PennyLane with execution performed using Amazon Braket.

**************************
`Computing gradients in parallel with PennyLane-Braket <https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/1_Parallelized_optimization_of_quantum_circuits.ipynb>`_
**************************

Learn how to speed up training of quantum circuits by using parallel execution on 
Amazon Braket. Quantum circuit training involving gradients 
requires multiple device executions. The Amazon Braket SV1 simulator can be used to overcome this. 
The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the 
local simulator for both executions and gradient calculations. This illustrates how 
parallel capabilities can be combined between PennyLane and SV1.

**************************
`Graph optimization with QAOA <https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/2_Graph_optimization_with_QAOA.ipynb>`_
**************************

In this tutorial, you learn how quantum circuit training can be applied to a problem 
of practical relevance in graph optimization. It easy it is to train a QAOA circuit in 
PennyLane to solve the maximum clique problem on a simple example graph. The tutorial 
then extends to a more difficult 20-node graph and uses the parallel capabilities of 
the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, 
using around 1-2 minutes per iteration.

**************************
`Quantum chemistry with VQE <https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/3_Quantum_chemistry_with_VQE.ipynb>`_
**************************

In this tutorial, you will learn how PennyLane and Amazon Braket can be combined to solve an 
important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated 
by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how 
qubit-wise commuting observables can be measured together in PennyLane and Amazon Braket, 
making optimization more efficient.
