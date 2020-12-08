# Braket Tutorials GitHub
Welcome to the primary repository for Amazon Braket tutorials. We provide tutorials on quantum computing, using Amazon Braket. We provide examples for quantum circuits and quantum annealing. We cover canonical routines, such as the Quantum Fourier Transform (QFT), as well as hybrid quantum algorithms, such as the Variational Quantum Eigensolver 9VQE). 

The repository is structured as follows:  

## [getting_started] Simple circuits and algorithms
  * **Getting started**
  
    A hello-world tutorial that shows you how to build a simple circuit and run it on a local simulator.
    
  * **Running quantum circuits on simulators**
  
    This tutorial prepares a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne, and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. For this reason, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication, and quantum metrology. 
  
  * **Running quantum circuits on QPU devices**
  
    This tutorial prepares a maximally-entangled Bell state between two qubits, for classical simulators and for QPUs. For classical devices, we can run the circuit on a local simulator or a cloud-based managed simulator. For the quantum devices, we run the circuit on the superconducting machine from Rigetti, and on the ion-trap machine provided by IonQ. As shown, one can swap between different devices seamlessly, without any modifications to the circuit definition, by re-defining the device object. We also show how to recover results using the unique Amazon resource identifier (ARN) associated with every task. This tool is useful if you must deal with potential delays, which can occur if your quantum task sits in the queue awaiting execution.  
  
  * **Deep Dive into the anatomy of quantum circuits**
  
    This tutorial discusses in detail the anatomy of quantum circuits in the Amazon Braket SDK. Specifically, you'll learn how to build (parameterized) circuits and display them graphically, and how to append circuits to each other. We discuss the associated circuit depth and circuit size. Finally we show how to execute the circuit on a device of our choice (defining a quantum task). We then learn how to track, log, recover, or cancel such a _quantum task_ efficiently. 
    
  * **Superdense coding**
  
    This tutorial constructs an implementation of the _superdense coding_ protocol, by means of the Amazon Braket SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (_aka_ Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (_aka_ Bob), who is then able to decode the full two-bit message.     
  
## [advanced_circuits_algorithms] Advanced circuits and algorithms
  * **Grover**
  
    This tutorial provides a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks, by means of the Amazon Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine. 
  
  * **QFT**
  
    This tutorial provides a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse QFT, using the Amazon Braket SDK. We provide two different implementations: with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relationship to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows one to define custom methods and add them to the Circuit class.
  
  * **QPE**
  
    This tutorial provides a detailed implementation of the Quantum Phase Estimation (QPE) algorithm, through the Amazon Braket SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning, or in the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using the Amazon Braket SDK, and we illustrate the application of the algorithm with simple examples. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows you to use custom-built gates as if they were any other built-in gates. This tutorial is set up to run on the local simulator or the cloud-based managed simulator. Changing between these devices requires changing only one line of code, as demonstrated below in cell. 
    
  * **QAA**
  
    This tutorial provides a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm, using the Amazon Braket SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.
   
## [hybrid_quantum_algorithms] Hybrid quantum algorithms
  * **QAOA**
  
    This tutorial shows how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical and quantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era, QAOA is also an emerging approach for benchmarking quantum devices. It is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach, we benchmark our results with exact results as obtained from classical QUBO solvers.
  
  * **VQE Transverse Ising**
  
    This tutorial shows how to solve for the ground state of the Transverse Ising Model, which is arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical andquantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach, we benchmark our results with exact results as obtained from a Jordan-Wigner transformation. 

## [pennylane] Quantum machine learning and optimization with PennyLane
  * **Combining PennyLane with Amazon Braket**
  
    This tutorial shows you how to construct circuits and evaluate their gradients in PennyLane with execution performed using Amazon Braket.
    
  * **Computing gradients in parallel with PennyLane-Braket**
  
    In this tutorial, we explore how to speed up training of quantum circuits by using parallel execution on Amazon Braket. We begin by discussing why quantum circuit training involving gradients requires multiple device executions and motivate how the Braket SV1 simulator can be used to overcome this. The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the local simulator for both executions and gradient calculations. This illustrates how parallel capabilities can be combined between PennyLane and SV1.
    
  * **Graph optimization with QAOA**
  
    In this tutorial we dig deeper into how quantum circuit training can be applied to a problem of practical relevance in graph optimization. We show how easy it is to train a QAOA circuit in PennyLane to solve the maximum clique problem on a simple example graph. The tutorial then extends to a more difficult 20-node graph and uses the parallel capabilities of the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, using around 1-2 minutes per iteration.
    
  * **Quantum chemistry with VQE**
  
    In this tutorial, we see how PennyLane and Amazon Braket can be combined to solve an important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how qubit-wise commuting observables can be measured together in PennyLane and Braket, making optimization more efficient.

## [quantum_annealing] Quantum annealing with D-Wave 
  * **Anatomy of annealing with ocean**
  
    This tutorial notebook dives deep into the anatomy of quantum annealing with D-Wave on Amazon Braket. First, we introduce the concept of quantum annealing, as used by D-Wave, to probabilistically find the (approximate) optimum to some optimization problem. We then discuss D-Wave's underlying Chimera graph, explain the problem of finding an embedding of the original problem onto this sparse Chimera graph, and discuss the distinction between logical and physical variables. Finally, we solve an example QUBO problem to analyze the sampling process and provide a breakdown of the QPU access time. 
  
  * **Maximum Cut**
  
    This tutorial solves a small instance of the famous Maximum-Cut (MaxCut) Problem using the D-Wave device on Amazon Braket. The MaxCut problem is one of the most famous NP-hard problems in combinatorial optimization. Given an undirected graph 𝐺(𝑉,𝐸) with a vertex set 𝑉 and an edge set 𝐸, the Max Cut problem seeks to partition 𝑉 into two sets, such that the number of edges between the two sets (considered to be severed by the cut), is as large as possible. Applications can be found in clustering problems for marketing purposes, or for portfolio optimization problems in finance. 
  
  * **Minimum Vertex**
  
    This tutorial discusses the BraketSampler and the BraketDWaveSampler. In essence, they are doing the same thing; however, each accepts different parameter names. Specifically, the BraketDWaveSampler allows users familiar with D-Wave to use D-Wave parameter names, such as `answer_mode`, whereas the BraketSampler parameter names are consistent with the rest of the Amazon Braket experience.
  
  * **Graph partitioning**
  
    This tutorial solves a small instance of a graph partitioning problem using the D-Wave device on Amazon Braket. The derivation for this QUBO problem is nicely explained here: https://github.com/dwave-examples/graph-partitioning.

## [braket_features] Amazon Braket features
This folder contains examples that illustrate the usage of individual features of Amazon Braket

* **Getting notifications when a task completes**

    This tutorial illustrates how Amazon Braket integrates with Amazon EventBridge for event-based processing. In the tutorial, you will learn how to configure Amazon Braket and Amazon Eventbridge to receive text notification about task completions on your phone. Of course, EventBridge also allows you to build full, event-driven applications based on events emitted by Amazon Braket.

* **Allocating Qubits on QPU Devices**

    This tutorial explains how you can use the Amazon Braket SDK to allocate the qubit selection for your circuits manually, when running on QPUs. 

* **Getting Devices and Checking Device Properties**

    This example shows how to interact with the Amazon Braket GetDevice API to retrieve Amazon Braket devices (such as simulators and QPUs) programatically, and how to gain access to their properties.

* **Using the tensor network simulator TN1**

    This notebook introduces the Amazon Braket managed tensor network simulator, TN1. You will learn about how TN1 works, how to use it, and which problems are best suited to run on TN1. 

