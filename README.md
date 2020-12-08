# Braket Tutorials github
Primary repository for Amazon Braket tutorials, in which we provide tutorials on quantum computing, using Amazon Braket. We provide examples for both quantum circuits and quantum annealing. We cover both canonical routines such as the Quantum Fourier Transform as well as hybrid quantum algorithms such as the Variational Quantum Eigensolver. 

The repo is structured as follows:  

* [getting_started] Simple circuits and algorithms
  * Getting started
  
    A hello-world tutorial that shows you how to build a simple circuit and run it on a local simulator.
    
  * Running quantum circuits on simulators
  
    In this tutorial we prepare a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. Therefore, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication and quantum metrology. 
  
  * Running quantum circuits on QPU devices
  
    In this tutorial we prepare a maximally entangled Bell state between two qubits, using both classical simulators as well as QPUs. For classical devices, we can run our circuit on a local simulator or a cloud-based managed simulator. For the quantum devices, we run our circuit on both the superconducting machine from Rigetti and the ion-trap machine provided by IonQ. As shown below, one can seamlessly swap between different devices without any modifications to the circuit definition, by just re-defining the device object. We also show how to recover results using the unique arn associated with every task. This tool is useful in order to deal with potential delays if your quantum task sits in the queue for some time waiting for execution.  
  
  * Deep Dive into the anatomy of quantum circuits
  
    In this tutorial we discuss in detail the anatomy of quantum circuits in Amazon Braket's SDK. Specifically, we learn how to build (parametrized) circuits and display them graphically, how to append circuits to each other, and discuss the associated circuit depth and circuit size. Finally we show how to execute our circuit on a device of our choice (defining a quantum task). We then learn how to efficiently track, log, recover or cancel such a _quantum task_. 
    
  * Superdense coding
  
    In this tutorial, we construct an implementation of the superdense coding protocol via Amazon Braket's SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (aka Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (aka Bob), who is then able to decode the full two-bit message. 
  
* [advanced_circuits_algorithms] Advanced circuits and algorithms
  * Grover
  
    In this tutorial, we provide a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks using the Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine. 
  
  * QFT
  
    In this tutorial, we provide a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse thereof, using Amazon Braket's SDK. We provide two different implementations, with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relation to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases Braket's circuit.subroutine functionality, which allows one to define custom methods and add them to the Circuit class.
  
  * QPE
  
    In this tutorial, we provide a detailed implementation of the Quantum Phase Estimation (QPE) algorithm using Amazon Braket's SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning or the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using Amazon Braket's SDK and illustrate the application thereof with simple examples. This notebook also showcases Braket's circuit.subroutine functionality, which allows us to use custom-built gates as any other built-in gates. This tutorial is set up to run either on the local simulator or the cloud-based managed simulator; changing between these devices merely requires changing one line of code as demonstrated below in cell. 
  
  * QAA
  
    In this tutorial, we provide a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm using Amazon Braket's SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.
   
* [hybrid_quantum_algorithms] Hybrid quantum algorithms
  * QAOA
  
    In this tutorial we show how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of hybrid quantum algorithms (leveraging both classical as well as quantum compute), that are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era QAOA is also an emerging approach for benchmarking quantum devices and is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach we benchmark our results with exact results as obtained from classical QUBO solvers.
  
  * VQE Transverse Ising
  
    In this tutorial we show how to solve for the ground state of the Transverse Ising Model, arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of hybrid quantum algorithms (leveraging both classical as well as quantum compute), that are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach we benchmark our results with exact results as obtained from a Jordan-Wigner transformation. 

* [pennylane] Quantum machine learning and optimization with PennyLane
  * Combining PennyLane with Amazon Braket
  
    This tutorial shows you how to construct circuits and evaluate their gradients in PennyLane with execution performed using Amazon Braket.
    
  * Computing gradients in parallel with PennyLane-Braket
  
    In this tutorial, we explore how to speed up training of quantum circuits by using parallel execution on Amazon Braket. We begin by discussing why quantum circuit training involving gradients requires multiple device executions and motivate how the Braket SV1 simulator can be used to overcome this. The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the local simulator for both executions and gradient calculations. This illustrates how parallel capabilities can be combined between PennyLane and SV1.
    
  * Graph optimization with QAOA
  
    In this tutorial we dig deeper into how quantum circuit training can be applied to a problem of practical relevance in graph optimization. We show how easy it is to train a QAOA circuit in PennyLane to solve the maximum clique problem on a simple example graph. The tutorial then extends to a more difficult 20-node graph and uses the parallel capabilities of the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, using around 1-2 minutes per iteration.
    
  * Quantum chemistry with VQE
  
    In this tutorial, we see how PennyLane and Amazon Braket can be combined to solve an important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how qubit-wise commuting observables can be measured together in PennyLane and Braket, making optimization more efficient.

* [quantum_annealing] Quantum annealing with D-Wave 
  * Anatomy of annealing with ocean 
  
    In this tutorial notebook we dive deep into the anatomy of quantum annealing with D-Wave on Amazon Braket. First, we introduce the concept of quantum annealing as used by D-Wave to probabilistically find the (approximate) optimum to some optimization problem. We then discuss D-Wave's underlying Chimera graph, explain the problem of finding an embedding of the original problem onto this sparse Chimera graph, and discuss the distinction between logical and physical variables. Finally, we solve an example QUBO problem to analyze the sampling process and provide a breakdown of the QPU access time. 
  
  * Maximum Cut
  
    In this tutorial we solve a small instance of the famous Maximum-Cut (MaxCut) Problem using the D-Wave device on Amazon Braket. The MaxCut problem is one of the most famous NP-hard problems in combinatorial optimization. Given an undirected graph 𝐺(𝑉,𝐸) with a vertex set 𝑉 and an edge set 𝐸, the Max Cut problem seeks to partition 𝑉 into two sets such that the number of edges between the two sets (considered to be severed by the cut), is as large as possible. Applications can be found (for example) in clustering problems for marketing purposes or portfolio optimization problems in finance. 
  
  * Minimum Vertex
  
    In this tutorial we discuss both the BraketSampler and BraketDWaveSampler. In essence, they are both doing the same thing; each one just accepts different parameter names. Specifically, the BraketDWaveSampler allows users familiar with D-Wave to use D-Wave parameter names, e.g., answer_mode, whereas the BraketSampler parameter names are consistent with the rest of the Braket experience.
  
  * Graph partitioning
  
    In this tutorial we solve a small instance of a graph partitioning problem using the D-Wave device on Amazon Braket. The derivation for this QUBO problem is nicely explained here: https://github.com/dwave-examples/graph-partitioning.

