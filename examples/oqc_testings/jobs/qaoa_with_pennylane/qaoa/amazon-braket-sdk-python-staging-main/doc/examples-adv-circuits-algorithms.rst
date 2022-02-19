################################
Advanced circuits and algorithms
################################

Learn more about working with advanced circuits and algoritms.

.. toctree::
    :maxdepth: 2
  
**************************
`Grover's search algorithm <https://github.com/aws/amazon-braket-examples/blob/main/examples/advanced_circuits_algorithms/Grover/Grover.ipynb>`_
**************************

This tutorial provides a step-by-step walkthrough of Grover's quantum algorithm. 
You learn how to build the corresponding quantum circuit with simple modular building 
blocks using the Amazon Braket SDK. You will learn how to build custom 
gates that are not part of the basic gate set provided by the SDK. A custom gate can used 
as a core quantum gate by registering it as a subroutine.

*******************************
`Quantum amplitude amplification <https://github.com/aws/amazon-braket-examples/blob/main/examples/advanced_circuits_algorithms/QAA/QAA_tutorial.ipynb>`_
*******************************

This tutorial provides a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) 
algorithm using the Amazon Braket SDK. QAA is a routine in quantum computing which generalizes the idea behind 
Grover's famous search algorithm, with applications across many quantum algorithms. QAA uses an iterative 
approach to systematically increase the probability of finding one or multiple 
target states in a given search space. In a quantum computer, QAA can be used to obtain a 
quadratic speedup over several classical algorithms.


*************************
`Quantum Fourier transform <https://github.com/aws/amazon-braket-examples/blob/main/examples/advanced_circuits_algorithms/QFT/QFT.ipynb>`_
*************************

This tutorial provides a detailed implementation of the Quantum Fourier Transform (QFT) and 
its inverse using Amazon Braket's SDK. The QFT is an important subroutine to many quantum algorithms, 
most famously Shor's algorithm for factoring and the quantum phase estimation (QPE) algorithm 
for estimating the eigenvalues of a unitary operator. 

************************
`Quantum phase estimation <https://github.com/aws/amazon-braket-examples/blob/main/examples/advanced_circuits_algorithms/QPE/QPE.ipynb>`_
************************

This tutorial provides a detailed implementation of the Quantum Phase Estimation (QPE) 
algorithm using the Amazon Braket SDK. The QPE algorithm is designed to estimate the 
eigenvalues of a unitary operator. Eigenvalue problems can be found across many 
disciplines and application areas, including principal component analysis (PCA) 
as used in machine learning and the solution of differential equations in mathematics, physics, 
engineering and chemistry. 
