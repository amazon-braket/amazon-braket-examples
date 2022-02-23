################################
Quantum annealing with D-Wave
################################

Learn more about quantum annealing with D-Wave.

.. toctree::
    :maxdepth: 2

**************************
`Anatomy of annealing with ocean <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_Anatomy.ipynb>`_
**************************

Learn more about the anatomy of quantum annealing with D-Wave on Amazon Braket. 

**************************
`Running large problems with QBSolv <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Running_large_problems_using_QBSolv.ipynb>`_
**************************

This tutorial demonstrates how to solve problems with sizes larger than a 
D-Wave device can support, by using a hybrid solver called QBSolv. 
QBSolv can decompose large problems into sub-problems, which are solved by the 
QPU and a classical Tabu solver, or by the classical solver alone. The results 
of the sub-problems then construct the solution to the problem.

**************************
`Maximum Cut <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_MaximumCut.ipynb>`_
**************************

This tutorial solves a small instance of the famous maximum cut (MaxCut) problem using 
a D-Wave device on Amazon Braket. The MaxCut problem is one of the most famous NP-hard 
problems in combinatorial optimization. Applications can be found in clustering problems 
for marketing purposes, or for portfolio optimization problems in finance.

**************************
`Minimum Vertex <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_MinimumVertexCoverProblem.ipynb>`_
**************************

This tutorial solves a small instance of the minimum vertex problem 
using BraketSampler and the BraketDWaveSampler. BraketDWaveSampler uses D-Wave parameter names 
(such as answer_mode). BraketSampler uses parameter names that are consistent 
with the rest of the Amazon Braket experience.

**************************
`Graph partitioning <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_GraphPartitioning.ipynb>`_
**************************

This tutorial solves a small instance of a graph partitioning 
problem using a D-Wave device on Amazon Braket. 

**************************
`Factoring <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_Factoring/Dwave_factoring.ipynb>`_
**************************

This tutorial shows how to solve a constraint satisfaction 
problem (CSP) problem, with the example of factoring, using a D-Wave device on 
Amazon Braket. Particularly, factoring is expressed as a CSP using Boolean 
logic operations, and it is converted to a binary quadratic model that can be 
solved by a D-Wave device.

**************************
`Structural Imbalance <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_StructuralImbalance/Dwave_StructuralImbalance.ipynb>`_
**************************

This tutorial solves a structural imbalance problem using a D-Wave device 
on Amazon Braket. Social networks map relationships between people or organizations 
onto graphs. Given a social network as a graph, D-Wave devices can partition the graph 
into two colored sets, and show the frustrated edges.

**************************
`Traveling Salesman Problem <https://github.com/aws/amazon-braket-examples/blob/main/examples/quantum_annealing/Dwave_TravelingSalesmanProblem/Dwave_TravelingSalesmanProblem.ipynb>`_
**************************

This tutorial solves small instances of the famous traveling salesman problem 
(TSP) using D-Wave devices on Amazon Braket. 
