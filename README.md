# Braket Tutorials github
Primary repository for Amazon Braket tutorials, in which we provide tutorials on quantum computing, using Amazon Braket. We provide examples for both quantum circuits and quantum annealing. We cover both canonical routines such as the Quantum Fourier Transform as well as hybrid quantum algorithms such as the Variational Quantum Eigensolver. 

The repo is structured as follows:  

* [Circuit-simple] Simple circuits and algorithms
  * Anatomy
  
    In this tutorial we discuss in detail the anatomy of quantum circuits in Amazon Braket's SDK. Specifically, we learn how to build (parametrized) circuits and display them graphically, how to append circuits to each other, and discuss the associated circuit depth and circuit size. Finally we show how to execute our circuit on a device of our choice (defining a quantum task). We then learn how to efficiently track, log, recover or cancel such a _quantum task_. 
    
  * Superdense Coding
  
    In this tutorial, we construct an implementation of the superdense coding protocol via Amazon Braket's SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (aka Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (aka Bob), who is then able to decode the full two-bit message. 
  
* [Circuit-simple / Backends-Devices] Exploring Braket Devices and Backends

  * Running Quantum Circuits on Different Devices
  
    In this hello-world tutorial we prepare a maximally entangled Bell state between two qubits, using both classical simulators as well as QPUs. For classical devices, we can run our circuit on a local simulator or a cloud-based managed simulator. For the quantum devices, we run our circuit on both the superconducting machine from Rigetti and the ion-trap machine provided by IonQ. As shown below, one can seamlessly swap between different devices without any modifications to the circuit definition, by just re-defining the device object. We also show how to recover results using the unique arn associated with every task. This tool is useful in order to deal with potential delays if your quantum task sits in the queue for some time waiting for execution.
    
  * Running GHZ Circuits on Simulators
  
    In this hello-world tutorial we prepare a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. Therefore, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication and quantum metrology. 

* [Circuit-advanced] Advanced circuits and algorithms
  * Grover
  
    In this tutorial, we provide a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks using the Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine. 
  
  * QFT
  
    In this tutorial, we provide a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse thereof, using Amazon Braket's SDK. We provide two different implementations, with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relation to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases Braket's circuit.subroutine functionality, which allows one to define custom methods and add them to the Circuit class.
  
  * QPE
  
    In this tutorial, we provide a detailed implementation of the Quantum Phase Estimation (QPE) algorithm using Amazon Braket's SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning or the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using Amazon Braket's SDK and illustrate the application thereof with simple examples. This notebook also showcases Braket's circuit.subroutine functionality, which allows us to use custom-built gates as any other built-in gates. This tutorial is set up to run either on the local simulator or the cloud-based managed simulator; changing between these devices merely requires changing one line of code as demonstrated below in cell. 
  
  * QAA
  
    In this tutorial, we provide a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm using Amazon Braket's SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.
   
* [Circuit-hybrid] Hybrid quantum algorithms
  * QAOA
  
    In this tutorial we show how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of hybrid quantum algorithms (leveraging both classical as well as quantum compute), that are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era QAOA is also an emerging approach for benchmarking quantum devices and is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach we benchmark our results with exact results as obtained from classical QUBO solvers.
  
  * VQE Transverse Ising Model
  
    In this tutorial we show how to solve for the ground state of the Transverse Ising Model, arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of hybrid quantum algorithms (leveraging both classical as well as quantum compute), that are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach we benchmark our results with exact results as obtained from a Jordan-Wigner transformation. 
  
  * VQE Chemistry
  
    In this notebook, we illustrate how to implement the Variational Quantum Eigensolver (VQE) algorithm in Amazon Braket SDK to compute the potential energy surface (PES) for the Hydrogen molecule. Specifically, we illustrate the following features of Amazon Braket SDK:

    - LocalSimulator which allows one to simulate quantum circuits on their local machine
    - Construction of the ansatz circuit for VQE in Braket SDK
    - Computing expectation values of the individual terms in the Hamiltonian in Braket SDK

* [Annealing] Quantum annealing with D-Wave 
  * Anatomy of annealing with ocean 
  
    In this tutorial notebook we dive deep into the anatomy of quantum annealing with D-Wave on Amazon Braket. First, we introduce the concept of quantum annealing as used by D-Wave to probabilistically find the (approximate) optimum to some optimization problem. We then discuss D-Wave's underlying Chimera graph, explain the problem of finding an embedding of the original problem onto this sparse Chimera graph, and discuss the distinction between logical and physical variables. Finally, we solve an example QUBO problem to analyze the sampling process and provide a breakdown of the QPU access time. 
  
  * Maximum Cut
  
    In this tutorial we solve a small instance of the famous Maximum-Cut (MaxCut) Problem using the D-Wave device on Amazon Braket. The MaxCut problem is one of the most famous NP-hard problems in combinatorial optimization. Given an undirected graph 𝐺(𝑉,𝐸) with a vertex set 𝑉 and an edge set 𝐸, the Max Cut problem seeks to partition 𝑉 into two sets such that the number of edges between the two sets (considered to be severed by the cut), is as large as possible. Applications can be found (for example) in clustering problems for marketing purposes or portfolio optimization problems in finance. 
  
  * Minimum Vertex
  
    In this tutorial we discuss both the BraketSampler and BraketDWaveSampler. In essence, they are both doing the same thing; each one just accepts different parameter names. Specifically, the BraketDWaveSampler allows users familiar with D-Wave to use D-Wave parameter names, e.g., answer_mode, whereas the BraketSampler parameter names are consistent with the rest of the Braket experience.
  
  * Graph partitioning
  
    In this tutorial we solve a small instance of a graph partitioning problem using the D-Wave device on Amazon Braket. The derivation for this QUBO problem is nicely explained here: https://github.com/dwave-examples/graph-partitioning.

## Proposed Curriculum
* Beginner to Intermediate: If you are new to QC or just want to familiarize yourself with the Braket SDK with some simple examples, we recommned to start with the notebook on the paradigmatic _Bell_ circuit. Here you will earn how to construct a simple circuit and run this circuit against different backends on Amazon Braket by just changing one line of code. You may then move on to the _Anatomy_ notebook to dive deeper into the functionalities of the Braket SDK. From there you may dive into one of the canonical quantum algorithms such as _Quantum Phase Estimation_ or immediately jump into one the tutorals on hybrid quantum algorithms which combine parametrized quantum circuits with classical optimization loops. 
In short, one potential curriculum could look like: Bell (Running Quantum Circuits on Different Devices) ---> Anatomy ---> QPE ---> VQE or QAOA. 

* Quantum Annealing (QA): QA is a separate paradigm from universal, circuit-based QC. Amazon Braket offers native support for D-Wave's Ocean tool suite. To see this in practice, we recommend to start with the example on _Minimum Vertex_ or _Maximum Cut_ to solve combinatorial optimization problems using quantum annealing. 
