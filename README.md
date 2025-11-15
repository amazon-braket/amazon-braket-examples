
# Braket Examples

Welcome to the primary repository for Amazon Braket examples and tutorials. Learn how to *build*, *test*, and *run* quantum circuits and programs using Amazon Braket with simulators and quantum hardware. Introductory examples on a variety of topics are included, as well as more canonical quantum algorithms. You also can find information on utilizing particular devices or using Amazon Braket with other supported tools. 

> [!TIP]
> For those who are just getting started with Amazon Braket, see the [Getting Started](#new) examples and the [Amazon Skill Builder](https://aws.amazon.com/blogs/quantum-computing/introducing-the-amazon-braket-learning-plan-and-digital-badge/) learning plan. The [Amazon Braket Algorithm Library](https://github.com/amazon-braket/amazon-braket-algorithm-library/tree/main) also contains detailed examples and preimplemented algorithms. 

**Build**
- [Getting Started](#new)
- [Using Amazon Braket features](#braket)                  
- [Advanced circuits and algorithms](#advanced)      
- [Building hybrid quantum algorithms](#hybrid)   

**Test**
- [Using simulators](#simulators)             
- [Modeling noise on Amazon Braket](#noise)                          
- [Utilizing Amazon Braket hybrid jobs](#jobs)                 

**Run**
- [Using quantum devices](#qhps)                     
- [Controlling pulse sequences](#pulse)                            
- [Analog Hamiltonian Simulation](#ahs)              
- [Accessing experimental capabilities](#experimental-dynamic) 

**Providers**
- [IonQ](#ionq)
- [IQM](#iqm)
- [QuEra](#quera)
- [Rigetti](#rigetti)

**Supported tools**
- [CUDA-Q](#cudaq)                                   
- [PennyLane](#pennylane)                
- [Qiskit](#qiskit)                      

**Index**  
- [Search the notebooks!](#index)             

**Support**
- [Local installations, feature requests, and more](#support)


>[!NOTE]
> Amazon Braket provides [managed Jupyter notebook instances](https://aws.amazon.com/braket/) which can be run and maintained remotely. To run the examples locally, the dependences can be installed [following the instructions](#dependencies) below. 
 
---

## <a name="new">I'm new to quantum</a>

-  [**Getting started**](examples/getting_started/0_Getting_started/0_Getting_started.ipynb) [(GS)](#index_GS)<a name="GS"></a>

  A hello-world tutorial that shows you how to build a simple circuit and run it on a local simulator.

-  [**Running quantum circuits on simulators**](examples/getting_started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb) [(RQCS)](#index_RQCS)<a name="RQCS"></a>

  This tutorial prepares a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne, and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. For this reason, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication, and quantum metrology.

-  [**Running quantum circuits on QPU devices**](examples/getting_started/2_Running_quantum_circuits_on_QPU_devices/2_Running_quantum_circuits_on_QPU_devices.ipynb) [(RQCQ)](#index_RQCQ)<a name="RQCQ"></a>

  This tutorial prepares a maximally-entangled Bell state between two qubits, for classical simulators and for QPUs. For classical devices, we can run the circuit on a local simulator or a cloud-based on-demand simulator. For the quantum devices, we run the circuit on the superconducting machine from Rigetti, and on the ion-trap machine provided by IonQ. As shown, one can swap between different devices seamlessly, without any modifications to the circuit definition, by re-defining the device object. We also show how to recover results using the unique Amazon resource identifier (ARN) associated with every quantum task. This tool is useful if you must deal with potential delays, which can occur if your quantum task sits in the queue awaiting execution.

-  [**Superdense coding**](examples/getting_started/4_Superdense_coding/4_Superdense_coding.ipynb) [(SC)](#index_SC)<a name="SC"></a>

  This tutorial constructs an implementation of the _superdense coding_ protocol, by means of the Amazon Braket SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (_aka_ Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (_aka_ Bob), who is then able to decode the full two-bit message.


---

## <a name="braket">Using Amazon Braket features</a>

-  [**Deep Dive into the anatomy of quantum circuits**](examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb) [(DDQC)](#index_DDQC)<a name="DDQC"></a>

  This tutorial discusses in detail the anatomy of quantum circuits in the Amazon Braket SDK. Specifically, you'll learn how to build (parameterized) circuits and display them graphically, and how to append circuits to each other. We discuss the associated circuit depth and circuit size. Finally we show how to execute the circuit on a device of our choice (defining a quantum task). We then learn how to track, log, recover, or cancel such a _quantum task_ efficiently.

-  [**Getting Started with OpenQASM on Braket**](examples/braket_features/Getting_Started_with_OpenQASM_on_Braket.ipynb) [(GSOQ)](#index_GSOQ)<a name="GSOQ"></a>

  This tutorial demonstrates how to submit OpenQASM quantum tasks to various devices on Braket and introduce some OpenQASM features available on Braket. OpenQASM is a popular, open source, human-readable and hardware-agnostic quantum circuit description language.

-  [**Getting notifications when a quantum task completes**](examples/braket_features/Getting_notifications_when_a_quantum_task_completes/Getting_notifications_when_a_quantum_task_completes.ipynb) [(GNQT)](#index_GNQT)<a name="GNQT"></a>

  This tutorial illustrates how Amazon Braket integrates with Amazon EventBridge for event-based processing. In the tutorial, you will learn how to configure Amazon Braket and Amazon Eventbridge to receive text notification about quantum task completions on your phone. Of course, EventBridge also allows you to build full, event-driven applications based on events emitted by Amazon Braket.

-  [**Adjoint Gradient Result Type**](examples/braket_features/Using_The_Adjoint_Gradient_Result_Type.ipynb) [(AGRT)](#index_AGRT)<a name="AGRT"></a>

  This tutorial introduces the AdjointGradient result type, discusses what a gradient is and how to compute one on a quantum circuit, explains how they can be used to accelerate your workflows, and shows an example of gradients in action on a hybrid quantum algorithm.

-  [**Verbatim Compilation**](examples/braket_features/Verbatim_Compilation.ipynb) [(VC)](#index_VC)<a name="VC"></a>

  This tutorial explains how to use _verbatim compilation_ to run your circuits exactly as defined without any modification during the compilation process that's usually done behind-the-scenes when you run your circuits.

-  [**Getting started with Amazon Braket program sets**](examples/braket_features/program_sets/01_Getting_started_with_program_sets.ipynb) [(GSPrS)](#index_GSPrS)<a name="GSPrS"></a>

  Amazon Braket's program sets feature enables efficient batch processing of quantum computations by allowing multiple quantum circuits to be executed together. The feature provides various ways to combine circuits, parameters, and observables through methods like `CircuitBinding`, `product()`, and `zip()`, making it particularly useful for variational algorithms and parameter sweeps. Program sets can significantly reduce overhead and costs compared to running individual quantum tasks, while maintaining the same computational results.

-  [**Expectation value calculations with Amazon Braket program sets**](examples/braket_features/program_sets/02_Expectation_value_calculations_with_program_sets.ipynb) [(EVPrS)](#index_EVPrS)<a name="EVPrS"></a>

  Amazon Braket program sets make it easier to implement an intelligent shot allocation strategy, which is particularly beneficial for algorithms like the Variational Quantum Eigensolver (VQE). This approach maintains the same total shot budget while significantly improving statistical accuracy in expectation value estimates.


---

## <a name="advanced">Advanced circuits and algorithms</a>

-  [**Grover**](examples/advanced_circuits_algorithms/Grover/Grover.ipynb) [(Grover)](#index_Grover)<a name="Grover"></a>

  This tutorial provides a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks, by means of the Amazon Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine.

-  [**Quantum Amplitude Amplification**](examples/advanced_circuits_algorithms/Quantum_Amplitude_Amplification/Quantum_Amplitude_Amplification.ipynb) [(QAA)](#index_QAA)<a name="QAA"></a>

  This tutorial provides a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm, using the Amazon Braket SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.

-  [**Quantum Fourier Transform**](examples/advanced_circuits_algorithms/Quantum_Fourier_Transform/Quantum_Fourier_Transform.ipynb) [(QFT)](#index_QFT)<a name="QFT"></a>

  This tutorial provides a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse QFT, using the Amazon Braket SDK. We provide two different implementations: with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relationship to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows one to define custom methods and add them to the Circuit class.

-  [**Quantum Phase Estimation**](examples/advanced_circuits_algorithms/Quantum_Phase_Estimation/Quantum_Phase_Estimation.ipynb) [(QPE)](#index_QPE)<a name="QPE"></a>

  This tutorial provides a detailed implementation of the Quantum Phase Estimation (QPE) algorithm, through the Amazon Braket SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning, or in the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using the Amazon Braket SDK, and we illustrate the application of the algorithm with simple examples. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows you to use custom-built gates as if they were any other built-in gates. This tutorial is set up to run on the local simulator or the on-demand simulator. Changing between these devices requires changing only one line of code, as demonstrated below in cell.

-  [**Randomness Generation**](examples/advanced_circuits_algorithms/Randomness/Randomness_Generation.ipynb) [(RNG)](#index_RNG)<a name="RNG"></a>

  This tutorial provides a detailed implementation of a Quantum Random Number Generator (QRNG). It shows how to use two separate quantum processor units (QPUs) from different suppliers in Amazon Braket to supply two streams of weakly random bits. We then show how to generate physically secure randomness from these two weak sources by means of classical post-processing based on randomness extractors.

-  [**Simon's Algorithm**](examples/advanced_circuits_algorithms/Simons_Algorithm/Simons_Algorithm.ipynb) [(Simon)](#index_Simon)<a name="Simon"></a>

  This tutorial provides a detailed implementation of Simon’s algorithm, which shows the first example of an exponential speedup over the best known classical algorithm by using a quantum computer to solve a particular problem. Originally published in 1994, Simon’s algorithm was a precursor to Shor’s well-known factoring algorithm, and it served as inspiration for many of the seminal works in quantum computation that followed.


---

## <a name="hybrid">Hybrid quantum algorithms</a>

-  [**Quantum Approximate Optimization Algorithm**](examples/hybrid_quantum_algorithms/QAOA/QAOA_braket.ipynb) [(QAOA)](#index_QAOA)<a name="QAOA"></a>

  This tutorial shows how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical and quantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era, QAOA is also an emerging approach for benchmarking quantum devices. It is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach, we benchmark our results with exact results as obtained from classical QUBO solvers.

-  [**VQE Chemistry**](examples/hybrid_quantum_algorithms/VQE_Chemistry/VQE_chemistry_braket.ipynb) [(VQEChem)](#index_VQEChem)<a name="VQEChem"></a>

  This tutorial shows how to implement the Variational Quantum Eigensolver (VQE) algorithm in Amazon Braket SDK to compute the potential energy surface (PES) for the Hydrogen molecule.

-  [**VQE Transverse Ising**](examples/hybrid_quantum_algorithms/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb) [(VQETFIM)](#index_VQETFIM)<a name="VQETFIM"></a>

  This tutorial shows how to solve for the ground state of the Transverse Ising Model, which is arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical andquantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach, we benchmark our results with exact results as obtained from a Jordan-Wigner transformation.


---

## <a name="simulators">Using simulators</a>

-  [**Running quantum circuits on simulators**](examples/getting_started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb) [(RQCS)](#index_RQCS)

  This tutorial prepares a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne, and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. For this reason, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication, and quantum metrology.

-  [**Advanced OpenQASM programs using the Local Simulator**](examples/braket_features/Simulating_Advanced_OpenQASM_Programs_with_the_Local_Simulator.ipynb) [(AOQLS)](#index_AOQLS)<a name="AOQLS"></a>

  This notebook serves as a reference of OpenQASM features supported by Braket with the LocalSimulator.

-  [**Using the experimental local simulator**](examples/braket_features/Using_the_experimental_local_simulator.ipynb) [(ExpLS)](#index_ExpLS)<a name="ExpLS"></a>

  This tutorial serves as an introduction to the experimental v2 local simulator for Amazon Braket. This tutorial explains how to use the v2 local simulator and the performance difference you can expect to see.

-  [**Using the tensor network simulator TN1**](examples/braket_features/Using_the_tensor_network_simulator_TN1.ipynb) [(TNSim)](#index_TNSim)<a name="TNSim"></a>

  This notebook introduces the Amazon Braket on-demand tensor network simulator, TN1. You will learn about how TN1 works, how to use it, and which problems are best suited to run on TN1.

-  [**TN1 and Hayden-Preskill circuits**](examples/braket_features/TN1_demo_local_vs_non-local_random_circuits.ipynb) [(TNHP)](#index_TNHP)<a name="TNHP"></a>

  This tutorial dives into showing the degree to which the tensor network simulator is capable of detecting a hidden local structure in a quantum circuit by working with Hayden-Preskill circuits, which are a class of unstructured, random quantum circuits.

-  [**Running on Local Simulator**](examples/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb) [(RLS)](#index_RLS)<a name="RLS"></a>

  This tutorial shows how to test and debug an analog Hamiltonian simulation (AHS) program on the local simulator before submitting it to a QPU. It introduces several features of the local simulator that will be useful to streamline this testing process.

-  [**Simulating quantum programs on GPUs**](examples/nvidia_cuda_q/1_simulation_with_GPUs.ipynb) [(SQPG)](#index_SQPG)<a name="SQPG"></a>

  This tutorial shows you how to perform simulations with CUDA-Q GPU simulators on Amazon-managed GPU instances using Braket Hybrid Jobs. 

-  [**Parallel simulations on multiple GPUs**](examples/nvidia_cuda_q/2_parallel_simulations.ipynb) [(PSG)](#index_PSG)<a name="PSG"></a>

  This tutorial shows you how to parallelize the simulations of observables and circuit batches over multiple GPUs using CUDA-Q with Braket Hybrid Jobs.

-  [**Distributed state vector simulations on multiple GPUs**](examples/nvidia_cuda_q/3_distributed_statevector_simulations.ipynb) [(DSVSG)](#index_DSVSG)<a name="DSVSG"></a>

  This tutorial shows you how to distribute a single state vector simulation across multiple GPUs using CUDA-Q with Braket Hybrid Jobs.

-  [**Using the local emulator**](examples/braket_features/Device_emulation/01_Local_Emulation_for_Verbatim_Circuits_on_Amazon_Braket.ipynb) [(LEmu)](#index_LEmu)<a name="LEmu"></a>

  This tutorial serves as an introduction to the local emulator for validating and debugging verbatim circuits for gate-based devices. This tutorial explains how to instantiate local emulator from up-to-date device calibration data and customize it for emulating verbatim circuits locally.


---

## <a name="noise">Modeling noise on Amazon Braket</a>

-  [**Simulating noise on Amazon Braket**](examples/braket_features/Simulating_Noise_On_Amazon_Braket.ipynb) [(SN)](#index_SN)<a name="SN"></a>

  This notebook provides a detailed overview of noise simulation on Amazon Braket. You will learn how to define noise channels, apply noise to new or existing circuits, and run those circuits on the Amazon Braket noise simulators.

-  [**Error Mitigation on IonQ**](examples/braket_features/Error_Mitigation_on_Amazon_Braket.ipynb) [(EMIQ)](#index_EMIQ)<a name="EMIQ"></a>

  This tutorial explains how to get started with using error mitigation on IonQ’s Aria QPU. You’ll learn how Aria’s two built-in error mitigation techniques work, how to switch between them, and the performance difference you can expect to see with and without these techniques for some problems.

-  [**Noise Models on Amazon Braket**](examples/braket_features/Noise_models/Noise_models_on_Amazon_Braket.ipynb) [(NM)](#index_NM)<a name="NM"></a>

  This tutorial shows how to create noise models containing different types of noise and instructions for how to apply the noise to a circuit. A noise model encapsulates the assumptions on quantum noise channels and how they act on a given circuit. Simulating this noisy circuit gives information about much the noise impacts the results of the quantum computation. By incrementally adjusting the noise model, the impact of noise can be understood on a variety of quantum algorithms.

-  [**Noise Models on Rigetti's device**](examples/braket_features/Noise_models/Noise_models_on_Rigetti.ipynb) [(NM)](#index_NM)

  This tutorial builds on the previous noise model tutorial to show how to construct a noise model from device calibration data for a Rigetti quantum processing unit (QPU). We compare the measurement outcomes of circuits run on a noisy simulator with the same circuits run on a QPU, to show that simulating circuits with noise models more closely mimics the QPU.

-  [**Noisy quantum dynamics**](examples/analog_hamiltonian_simulation/09_Noisy_quantum_dynamics_for_Rydberg_atom_arrays.ipynb) [(NQD)](#index_NQD)<a name="NQD"></a>

  This tutorial shows how to run noise simulation on Braket’s Rydberg atom devices

-  [**Simulation of Noisy Circuits with PennyLane-Braket**](examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb) [(SNCP)](#index_SNCP)<a name="SNCP"></a>

  In this tutorial, we explore the impact of noise on quantum hybrid algorithms and overview of noise simulation on Amazon Braket with PennyLane. The tutorial shows how to use PennyLane to simulate the noisy circuits, on either the local or Braket on-demand noise simulator, and covers the basic concepts of noise channels, using PennyLane to compute cost functions of noisy circuits and optimize them.

-  [**Handling Noise with Dynamic Circuits**](examples/experimental_capabilities/dynamic_circuits/2_Handling_Noise_with_Dynamic_Circuits.ipynb) [(HNDC)](#index_HNDC)<a name="HNDC"></a>

  This tutorial shows how you can harness and mitigate errors with dynamic circuits. The tutorial includes an entanglement stabilization with Bell states and dynamic circuits example, as well as a readout error mitigation example for mid-circuit measurements. 

-  [**Using the local emulator**](examples/braket_features/Device_emulation/01_Local_Emulation_for_Verbatim_Circuits_on_Amazon_Braket.ipynb) [(LEmu)](#index_LEmu)

  This tutorial serves as an introduction to the local emulator for validating and debugging verbatim circuits for gate-based devices. This tutorial explains how to instantiate local emulator from up-to-date device calibration data and customize it for emulating verbatim circuits locally.


---

## <a name="jobs">Utilizing Amazon Braket hybrid jobs</a>

-  [**Getting started with Amazon Braket Hybrid Jobs**](examples/hybrid_jobs/0_Creating_your_first_Hybrid_Job/0_Creating_your_first_Hybrid_Job.ipynb) [(GSHJ)](#index_GSHJ)<a name="GSHJ"></a>

  This notebook provides a demonstration of running a simple Braket Hybrid Job. You will learn how to create a Braket Hybrid Job using the Braket SDK or the Braket console, how to set the output S3 folder for a hybrid job, and how to retrieve results. You will also learn how to specify the Braket device to run your hybrid job on simulators or QPUs. Finally, you will learn how to use local mode to quickly debug your code.

-  [**Quantum machine learning in Amazon Braket Hybrid Jobs**](examples/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs/Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb) [(QMLHJ)](#index_QMLHJ)<a name="QMLHJ"></a>

  This notebook shows a typical quantum machine learning workflow using Braket Hybrid Jobs. In the process, you will learn how to upload input data, how to set up hyperparameters for your hybrid job, and how to retrieve and plot metrics. Finally, you will see how to run multiple Braket Hybrid Jobs in parallel with different sets of hyperparameters.

-  [**QAOA with Amazon Braket Hybrid Jobs and PennyLane**](examples/hybrid_jobs/2_Using_PennyLane_with_Braket_Hybrid_Jobs/Using_PennyLane_with_Braket_Hybrid_Jobs.ipynb) [(QHJP)](#index_QHJP)<a name="QHJP"></a>

  This notebook shows how to run the QAOA algorithm with PennyLane (similar to a [previous notebook](examples/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb)), but this time using Braket Hybrid Jobs. In the process, you will learn how to select a container image that supports PennyLane, and how to use checkpoints to save and load training progress of a hybrid job.

-  [**Bring your own containers to Braket Hybrid Jobs**](examples/hybrid_jobs/3_Bring_your_own_container/bring_your_own_container.ipynb) [(BYOC)](#index_BYOC)<a name="BYOC"></a>

  This notebook demonstrates the use of the Bring-Your-Own-Container (BYOC) functionality of Braket Hybrid Jobs. While Amazon Braket has pre-configured environments which support most use cases of Braket Hybrid Jobs, BYOC enables you to define fully customizable environments using Docker containers. You will learn how to use BYOC, including preparing a Dockerfile, creating a private Amazon Elastic Container Registry (ECR), building the container, and submitting a Braket Hybrid Job using the custom container.

-  [**Embedded simulators in Braket Hybrid Jobs**](examples/hybrid_jobs/4_Embedded_simulators_in_Braket_Hybrid_Jobs/Embedded_simulators_in_Braket_Hybrid_Jobs.ipynb) [(ESHJ)](#index_ESHJ)<a name="ESHJ"></a>

  This notebook shows how to use embedded simulators in Braket Hybrid Jobs. An embedded simulator is a local simulator that runs completely within a hybrid job instance, i.e., the compute resource that is running your algorithm script. In contrast, on-demand simulators, such as SV1, DM1, or TN1, calculate the results of a quantum circuit on dedicated compute infrastructure on-demand by Amazon Braket. Hybrid workloads usually consist of iterations of quantum circuit executions and variational parameter optimizations. By using embedded simulators, we keep all computations in the same environment. This allows the optimization algorithm to access advanced features supported by the embedded simulator.

-  [**Parallelize training for Quantum Machine Learning**](examples/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb) [(PTQML)](#index_PTQML)<a name="PTQML"></a>

  This notebook introduces using data parallelism for Quantum Machine Learning (QML) workloads.

-  [**QN-SPSA optimizer using an Embedded Simulator**](examples/hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator/qnspsa_with_embedded_simulator.ipynb) [(QNES)](#index_QNES)<a name="QNES"></a>

  This notebook demonstrates how to implement and benchmark the QN-SPSA optimizer, a novel quantum optimization algorithm.

-  [**Running Jupyter notebooks as a Hybrid Job**](examples/hybrid_jobs/7_Running_notebooks_as_hybrid_jobs/Running_notebooks_as_hybrid_jobs.ipynb) [(RJNHJ)](#index_RJNHJ)<a name="RJNHJ"></a>

  This tutorial is a step-by-step guide for running a Jupyter notebook as a Hybrid Job.

-  [**Creating Hybrid Job Scripts**](examples/hybrid_jobs/8_Creating_Hybrid_Job_Scripts/Creating_your_first_Hybrid_Job.ipynb) [(CHJS)](#index_CHJS)<a name="CHJS"></a>

  This notebook shows an alternate way to create a Hybrid Job without using a @hybrid_job decorator. The demonstrated method may be useful in some circumstances, such as using older versions of Python.


---

## <a name="qhps">Using quantum devices</a>

-  [**Running quantum circuits on QPU devices**](examples/getting_started/2_Running_quantum_circuits_on_QPU_devices/2_Running_quantum_circuits_on_QPU_devices.ipynb) [(RQCQ)](#index_RQCQ)

  This tutorial prepares a maximally-entangled Bell state between two qubits, for classical simulators and for QPUs. For classical devices, we can run the circuit on a local simulator or a cloud-based on-demand simulator. For the quantum devices, we run the circuit on the superconducting machine from Rigetti, and on the ion-trap machine provided by IonQ. As shown, one can swap between different devices seamlessly, without any modifications to the circuit definition, by re-defining the device object. We also show how to recover results using the unique Amazon resource identifier (ARN) associated with every quantum task. This tool is useful if you must deal with potential delays, which can occur if your quantum task sits in the queue awaiting execution.

-  [**IQM Garnet Native Gates**](examples/braket_features/IQM_Garnet_Native_Gates.ipynb) [(IQMNG)](#index_IQMNG)<a name="IQMNG"></a>

  This tutorial explores the functionality of the native gates of IQM Garnet.

-  [**IonQ Native Gates**](examples/braket_features/IonQ_Native_Gates.ipynb) [(IonNG)](#index_IonNG)<a name="IonNG"></a>

  This tutorial goes into details of IonQ’s native gates and their functionalities, enabling us to realize direct control over the quantum operations on the computer without compiler optimizations or error mitigation. It will discuss the native gates available on IonQ, their mathematical representations, and how they can be used for applications such as the quantum Fourier transform (QFT).

-  [**Allocating Qubits on QPU Devices**](examples/braket_features/Allocating_Qubits_on_QPU_Devices.ipynb) [(AQQD)](#index_AQQD)<a name="AQQD"></a>

  This tutorial explains how you can use the Amazon Braket SDK to allocate the qubit selection for your circuits manually, when running on QPUs.

-  [**Getting Devices and Checking Device Properties**](examples/braket_features/Getting_Devices_and_Checking_Device_Properties.ipynb) [(GDCDP)](#index_GDCDP)<a name="GDCDP"></a>

  This example shows how to interact with the Amazon Braket GetDevice API to retrieve Amazon Braket devices (such as simulators and QPUs) programmatically, and how to gain access to their properties.

-  [**Native Gate Calibrations**](examples/pulse_control/2_Native_gate_calibrations.ipynb) [(NGC)](#index_NGC)<a name="NGC"></a>

  This tutorial shows how to retrieve the calibrations of native gates for Rigetti's Ankaa devices and submit a circuit with custom gate calibrations.


---

## <a name="pulse">Controlling pulse sequences</a>

-  [**Bringup Experiments**](examples/pulse_control/1_Bringup_experiments.ipynb) [(BE)](#index_BE)<a name="BE"></a>

  This tutorial introduces common pulse sequences and calibrating pulses via Rabi spectroscopy.

-  [**Native Gate Calibrations**](examples/pulse_control/2_Native_gate_calibrations.ipynb) [(NGC)](#index_NGC)

  This tutorial shows how to retrieve the calibrations of native gates for Rigetti's Ankaa devices and submit a circuit with custom gate calibrations.

-  [**Bell pair with pulses on Rigetti**](examples/pulse_control/3_Bell_pair_with_pulses_Rigetti.ipynb) [(BPPR)](#index_BPPR)<a name="BPPR"></a>

  This tutorial shows creating a Bell state with cross-resonance pulses on Rigetti's Ankaa device.

-  [**Build single qubit gates**](examples/pulse_control/4_Build_single_qubit_gates.ipynb) [(BSQG)](#index_BSQG)<a name="BSQG"></a>

  This tutorial describes a method to create any single-qubit gate with pulses.


---

## <a name="ahs">Analog Hamiltonian Simulation</a>

-  [**Getting Started with Analog Hamiltonian Simulation**](examples/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb) [(GSAHS)](#index_GSAHS)<a name="GSAHS"></a>

  This tutorial provides an introduction to Analog Hamiltonian Simulation (AHS), a quantum computing paradigm different from gate-based computing. AHS uses a well-controlled quantum system and tunes its parameters to mimic the dynamics of another quantum system, the one we aim to study.

-  [**Getting Started with Aquila**](examples/analog_hamiltonian_simulation/01_Introduction_to_Aquila.ipynb) [(GSA)](#index_GSA)<a name="GSA"></a>

  This tutorial illustrates how to run an AHS program on QuEra’s Aquila, a Rydberg based QPU, via Amazon Braket.

-  [**Ordered Phases in Rydberg Systems**](examples/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb) [(OPRS)](#index_OPRS)<a name="OPRS"></a>

  This tutorial shows how to prepare ordered phases in Rydberg systems, focusing on the 1D phase and the 2D checkerboard phase. It uses an adiabatic time-evolution to prepare these many-body ground states.

-  [**Parallel Tasks on Aquila**](examples/analog_hamiltonian_simulation/03_Parallel_tasks_on_Aquila.ipynb) [(PTA)](#index_PTA)<a name="PTA"></a>

  This tutorial builds on the previous notebook tutorial to use a checkerboard preparation that takes advantage of the full area.

-  [**Maximum Independent Sets**](examples/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb) [(MIS)](#index_MIS)<a name="MIS"></a>

  This tutorial demonstrates how to set up a unit disk graph and solve for its maximum independent set using the Amazon Braket analog Hamiltonian simulation (AHS) local simulator.

-  [**Running on Local Simulator**](examples/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb) [(RLS)](#index_RLS)

  This tutorial shows how to test and debug an analog Hamiltonian simulation (AHS) program on the local simulator before submitting it to a QPU. It introduces several features of the local simulator that will be useful to streamline this testing process.

-  [**Simulation with PennyLane**](examples/analog_hamiltonian_simulation/06_Analog_Hamiltonian_simulation_with_PennyLane.ipynb) [(SPL)](#index_SPL)<a name="SPL"></a>

  This tutorial shows how to run analog Hamiltonian simulation (AHS) on Braket’s Rydberg atom devices leveraging quantum machine learning techniques from PennyLane.

-  [**Simulating lattice gauge theory with Rydberg atoms**](examples/analog_hamiltonian_simulation/07_Simulating_Lattice_Gauge_Theory_with_Rydberg_Atoms.ipynb) [(SLGRA)](#index_SLGRA)<a name="SLGRA"></a>

  This tutorial shows how to prepare a specific initial state, using local detuning, to simulate the dynamics of a lattice gauge theory.

-  [**Maximum weight independent set**](examples/analog_hamiltonian_simulation/08_Maximum_Weight_Independent_Set.ipynb) [(MWIS)](#index_MWIS)<a name="MWIS"></a>

  This tutorial generalizes the approach to solve the maximum weight independent set (MWIS) problem.


---

## <a name="experimental-dynamic">Accessing experimental capabilities</a>

-  [**Dynamic Circuits on Qiskit with Amazon Braket**](examples/experimental_capabilities/dynamic_circuits/4_Dynamic_Circuits_with_Qiskit_Braket_Provider.ipynb) [(DCQis)](#index_DCQis)<a name="DCQis"></a>

  This tutorial shows how we can use the qiskit-braket-provider to run dynamic circuits on IQM using the Amazon Braket service. 

-  [**Getting Started with Dynamic Circuits on IQM**](examples/experimental_capabilities/dynamic_circuits/0_Intro_to_Dynamic_Circuits_on_IQM.ipynb) [(GSDCI)](#index_GSDCI)<a name="GSDCI"></a>

  This tutorial introduces experimental support for dynamic circuits on IQM Garnet, including support for mid-circuit measurements and feedforward control, as well as recommended practices and capabilities of the service. 

-  [**Dynamic Circuit Constructions**](examples/experimental_capabilities/dynamic_circuits/1_Dynamic_Circuit_Constructions.ipynb) [(DCC)](#index_DCC)<a name="DCC"></a>

  This tutorial introduces basic tools and primitives for building more sophisticated dynamic quantum circuits. These include teleportation tools, PARITY gates, and a gate teleportation protocol for realizing remote CNOT applications. 

-  [**Handling Noise with Dynamic Circuits**](examples/experimental_capabilities/dynamic_circuits/2_Handling_Noise_with_Dynamic_Circuits.ipynb) [(HNDC)](#index_HNDC)

  This tutorial shows how you can harness and mitigate errors with dynamic circuits. The tutorial includes an entanglement stabilization with Bell states and dynamic circuits example, as well as a readout error mitigation example for mid-circuit measurements. 

-  [**Open Quantum Systems with Dynamic Circuits**](examples/experimental_capabilities/dynamic_circuits/3_OQS_with_Dynamic_Circuits.ipynb) [(OQSDC)](#index_OQSDC)<a name="OQSDC"></a>

  This tutorial shows how dynamic circuits can be used for creating and applying open quantum system operators, including an ampltiude damping example, as well as a mixed state preparation for ensemble state optimization. 

-  [**Dynamic Circuits with OpenQASM 3.0 on Amazon Braket**](examples/experimental_capabilities/dynamic_circuits/5_Dynamic_Circuits_with_OpenQASM_3.0.ipynb) [(DCOQ3)](#index_DCOQ3)<a name="DCOQ3"></a>

  This tutorial shows how we can specify experimental dynamic circuit instructions using OpenQASM 3.0 on Amazon Braket. 


---

## <a name="ionq">IonQ</a>

-  [**Error Mitigation on IonQ**](examples/braket_features/Error_Mitigation_on_Amazon_Braket.ipynb) [(EMIQ)](#index_EMIQ)

  This tutorial explains how to get started with using error mitigation on IonQ’s Aria QPU. You’ll learn how Aria’s two built-in error mitigation techniques work, how to switch between them, and the performance difference you can expect to see with and without these techniques for some problems.

-  [**IonQ Native Gates**](examples/braket_features/IonQ_Native_Gates.ipynb) [(IonNG)](#index_IonNG)

  This tutorial goes into details of IonQ’s native gates and their functionalities, enabling us to realize direct control over the quantum operations on the computer without compiler optimizations or error mitigation. It will discuss the native gates available on IonQ, their mathematical representations, and how they can be used for applications such as the quantum Fourier transform (QFT).


---

## <a name="iqm">IQM</a>

-  [**IQM Garnet Native Gates**](examples/braket_features/IQM_Garnet_Native_Gates.ipynb) [(IQMNG)](#index_IQMNG)

  This tutorial explores the functionality of the native gates of IQM Garnet.

-  [**Getting Started with Dynamic Circuits on IQM**](examples/experimental_capabilities/dynamic_circuits/0_Intro_to_Dynamic_Circuits_on_IQM.ipynb) [(GSDCI)](#index_GSDCI)

  This tutorial introduces experimental support for dynamic circuits on IQM Garnet, including support for mid-circuit measurements and feedforward control, as well as recommended practices and capabilities of the service. 


---

## <a name="quera">QuEra</a>

-  [**Getting Started with Aquila**](examples/analog_hamiltonian_simulation/01_Introduction_to_Aquila.ipynb) [(GSA)](#index_GSA)

  This tutorial illustrates how to run an AHS program on QuEra’s Aquila, a Rydberg based QPU, via Amazon Braket.

-  [**Parallel Tasks on Aquila**](examples/analog_hamiltonian_simulation/03_Parallel_tasks_on_Aquila.ipynb) [(PTA)](#index_PTA)

  This tutorial builds on the previous notebook tutorial to use a checkerboard preparation that takes advantage of the full area.


---

## <a name="rigetti">Rigetti</a>

-  [**Noise Models on Rigetti's device**](examples/braket_features/Noise_models/Noise_models_on_Rigetti.ipynb) [(NM)](#index_NM)

  This tutorial builds on the previous noise model tutorial to show how to construct a noise model from device calibration data for a Rigetti quantum processing unit (QPU). We compare the measurement outcomes of circuits run on a noisy simulator with the same circuits run on a QPU, to show that simulating circuits with noise models more closely mimics the QPU.

-  [**Bell pair with pulses on Rigetti**](examples/pulse_control/3_Bell_pair_with_pulses_Rigetti.ipynb) [(BPPR)](#index_BPPR)

  This tutorial shows creating a Bell state with cross-resonance pulses on Rigetti's Ankaa device.


---

## <a name="cudaq">CUDA-Q</a>

-  [**Hello CUDA-Q Jobs**](examples/nvidia_cuda_q/0_hello_cudaq_jobs.ipynb) [(HCQJ)](#index_HCQJ)<a name="HCQJ"></a>

  This tutorial introduces CUDA-Q in Amazon Braket. You will learn about configuring a Braket Hybrid Jobs container to run CUDA-Q programs, and you will learn how to run your Braket Hybrid Jobs using CUDA-Q both locally and on AWS. 

-  [**Simulating quantum programs on GPUs**](examples/nvidia_cuda_q/1_simulation_with_GPUs.ipynb) [(SQPG)](#index_SQPG)

  This tutorial shows you how to perform simulations with CUDA-Q GPU simulators on Amazon-managed GPU instances using Braket Hybrid Jobs. 

-  [**Parallel simulations on multiple GPUs**](examples/nvidia_cuda_q/2_parallel_simulations.ipynb) [(PSG)](#index_PSG)

  This tutorial shows you how to parallelize the simulations of observables and circuit batches over multiple GPUs using CUDA-Q with Braket Hybrid Jobs.

-  [**Distributed state vector simulations on multiple GPUs**](examples/nvidia_cuda_q/3_distributed_statevector_simulations.ipynb) [(DSVSG)](#index_DSVSG)

  This tutorial shows you how to distribute a single state vector simulation across multiple GPUs using CUDA-Q with Braket Hybrid Jobs.


---

## <a name="pennylane">Pennylane</a>

-  [**QAOA with Amazon Braket Hybrid Jobs and PennyLane**](examples/hybrid_jobs/2_Using_PennyLane_with_Braket_Hybrid_Jobs/Using_PennyLane_with_Braket_Hybrid_Jobs.ipynb) [(QHJP)](#index_QHJP)

  This notebook shows how to run the QAOA algorithm with PennyLane (similar to a [previous notebook](examples/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb)), but this time using Braket Hybrid Jobs. In the process, you will learn how to select a container image that supports PennyLane, and how to use checkpoints to save and load training progress of a hybrid job.

-  [**Combining PennyLane with Amazon Braket**](examples/pennylane/0_Getting_started/0_Getting_started.ipynb) [(CPL)](#index_CPL)<a name="CPL"></a>

  This tutorial shows you how to construct circuits and evaluate their gradients in PennyLane with execution performed using Amazon Braket.

-  [**Computing gradients in parallel with PennyLane-Braket**](examples/pennylane/1_Parallelized_optimization_of_quantum_circuits/1_Parallelized_optimization_of_quantum_circuits.ipynb) [(CGPPL)](#index_CGPPL)<a name="CGPPL"></a>

  In this tutorial, we explore how to speed up training of quantum circuits by using parallel execution on Amazon Braket. We begin by discussing why quantum circuit training involving gradients requires multiple device executions and motivate how the Braket SV1 simulator can be used to overcome this. The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the local simulator for both executions and gradient calculations. This illustrates how parallel capabilities can be combined between PennyLane and SV1.

-  [**Graph optimization with QAOA**](examples/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb) [(GOQ)](#index_GOQ)<a name="GOQ"></a>

  In this tutorial we dig deeper into how quantum circuit training can be applied to a problem of practical relevance in graph optimization. We show how easy it is to train a QAOA circuit in PennyLane to solve the maximum clique problem on a simple example graph. The tutorial then extends to a more difficult 20-node graph and uses the parallel capabilities of the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, using around 1-2 minutes per iteration.

-  [**Hydrogen geometry with VQE**](examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb) [(HGV)](#index_HGV)<a name="HGV"></a>

  In this tutorial, we see how PennyLane and Amazon Braket can be combined to solve an important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how qubit-wise commuting observables can be measured together in PennyLane and Braket, making optimization more efficient.

-  [**Simulation of Noisy Circuits with PennyLane-Braket**](examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb) [(SNCP)](#index_SNCP)

  In this tutorial, we explore the impact of noise on quantum hybrid algorithms and overview of noise simulation on Amazon Braket with PennyLane. The tutorial shows how to use PennyLane to simulate the noisy circuits, on either the local or Braket on-demand noise simulator, and covers the basic concepts of noise channels, using PennyLane to compute cost functions of noisy circuits and optimize them.

-  [**Tracking Resource Usage**](examples/pennylane/5_Tracking_resource_usage/5_Tracking_resource_usage.ipynb) [(TRU)](#index_TRU)<a name="TRU"></a>

  In this tutorial, we see how to use the PennyLane device tracker feature with Amazon Braket. The PennyLane device resource tracker keeps a record of the usage of a device, such as numbers of circuit evaluations and shots. Amazon Braket extends this information with quantum task IDs and simulator duration to allow further tracking. The device tracker can be combined with additional logic to monitor and limit resource usage on devices.

-  [**Adjoint Gradient Computation**](examples/pennylane/6_Adjoint_gradient_computation/6_Adjoint_gradient_computation.ipynb) [(AGC)](#index_AGC)<a name="AGC"></a>

  In this tutorial, we will show you how to compute gradients of free parameters in a quantum circuit using PennyLane and Amazon Braket. Adjoint differentiation is a technique used to compute gradients of parametrized quantum circuits. It can be used when shots=0 and is available on Amazon Braket’s on-demand state vector simulator, SV1. The adjoint differentiation method allows you to compute the gradient of a circuit with P parameters in only 1+1 circuit executions (one forward and one backward pass, similar to backpropagation), as opposed to the parameter-shift or finite-difference methods, both of which require 2P circuit executions for every gradient calculation. The adjoint method can lower the cost of running variational quantum workflows, especially for circuits with a large number of parameters.

-  [**Simulation with PennyLane**](examples/analog_hamiltonian_simulation/06_Analog_Hamiltonian_simulation_with_PennyLane.ipynb) [(SPL)](#index_SPL)

  This tutorial shows how to run analog Hamiltonian simulation (AHS) on Braket’s Rydberg atom devices leveraging quantum machine learning techniques from PennyLane.


---

## <a name="qiskit">Qiskit</a>

-  [**Getting started with Qiskit on Amazon Braket**](examples/qiskit/0_Getting_Started.ipynb) [(Qis)](#index_Qis)<a name="Qis"></a>

  This tutorial shows how you can run your Qiskit code on Amazon Braket computing services.

-  [**Dynamic Circuits on Qiskit with Amazon Braket**](examples/experimental_capabilities/dynamic_circuits/4_Dynamic_Circuits_with_Qiskit_Braket_Provider.ipynb) [(DCQis)](#index_DCQis)

  This tutorial shows how we can use the qiskit-braket-provider to run dynamic circuits on IQM using the Amazon Braket service. 

## <a name="index">Index</a> 
 |  Terms  | Notebooks  | 
 | -- | -- | 
 | adjoint gradient |  [AGRT](#AGRT)<a name="index_AGRT"></a>, [AGC](#AGC)<a name="index_AGC"></a>| <br>
 | advanced   |  [Grover](#Grover)<a name="index_Grover"></a>| <br>
 | ahs        |  [NQD](#NQD)<a name="index_NQD"></a>, [GSAHS](#GSAHS)<a name="index_GSAHS"></a>, [GSA](#GSA)<a name="index_GSA"></a>, [OPRS](#OPRS)<a name="index_OPRS"></a>, [PTA](#PTA)<a name="index_PTA"></a>, [MIS](#MIS)<a name="index_MIS"></a>, [RLS](#RLS)<a name="index_RLS"></a>, [SPL](#SPL)<a name="index_SPL"></a>, [SLGRA](#SLGRA)<a name="index_SLGRA"></a>, [MWIS](#MWIS)<a name="index_MWIS"></a>| <br>
 | alice      |  [SC](#SC)<a name="index_SC"></a>, [DCC](#DCC)<a name="index_DCC"></a>| <br>
 | allocation |  [AQQD](#AQQD)<a name="index_AQQD"></a>| <br>
 | arn        |  [GSHJ](#GSHJ)<a name="index_GSHJ"></a>| <br>
 | atoms      |  [NQD](#NQD), [GSAHS](#GSAHS), [GSA](#GSA), [OPRS](#OPRS), [PTA](#PTA), [MIS](#MIS), [SPL](#SPL), [SLGRA](#SLGRA), [MWIS](#MWIS)| <br>
 | beginner   |  [GS](#GS)<a name="index_GS"></a>| <br>
 | bell       |  [GS](#GS), [RQCQ](#RQCQ)<a name="index_RQCQ"></a>, [GSOQ](#GSOQ)<a name="index_GSOQ"></a>, [NQD](#NQD), [NGC](#NGC)<a name="index_NGC"></a>, [BPPR](#BPPR)<a name="index_BPPR"></a>, [HCQJ](#HCQJ)<a name="index_HCQJ"></a>, [HNDC](#HNDC)<a name="index_HNDC"></a>| <br>
 | calibration |  [NM](#NM)<a name="index_NM"></a>, [AQQD](#AQQD), [NGC](#NGC), [LEmu](#LEmu)<a name="index_LEmu"></a>| <br>
 | chemistry  |  [VQEChem](#VQEChem)<a name="index_VQEChem"></a>, [HGV](#HGV)<a name="index_HGV"></a>| <br>
 | compilation |  [VC](#VC)<a name="index_VC"></a>| <br>
 | connectivity |  [VC](#VC), [AQQD](#AQQD)| <br>
 | container  |  [BYOC](#BYOC)<a name="index_BYOC"></a>, [ESHJ](#ESHJ)<a name="index_ESHJ"></a>, [CHJS](#CHJS)<a name="index_CHJS"></a>| <br>
 | cost       |  [EVPrS](#EVPrS)<a name="index_EVPrS"></a>, [TRU](#TRU)<a name="index_TRU"></a>| <br>
 | cuda       |  [HCQJ](#HCQJ), [SQPG](#SQPG)<a name="index_SQPG"></a>, [PSG](#PSG)<a name="index_PSG"></a>, [DSVSG](#DSVSG)<a name="index_DSVSG"></a>| <br>
 | device properties |  [GDCDP](#GDCDP)<a name="index_GDCDP"></a>| <br>
 | devices    |  [NM](#NM), [AQQD](#AQQD), [GDCDP](#GDCDP), [NGC](#NGC), [LEmu](#LEmu)| <br>
 | dynamic circuits |  [DCOQ3](#DCOQ3)<a name="index_DCOQ3"></a>| <br>
 | emulator   |  [LEmu](#LEmu)| <br>
 | estimators |  [EVPrS](#EVPrS)| <br>
 | gates      |  [IQMNG](#IQMNG)<a name="index_IQMNG"></a>, [BSQG](#BSQG)<a name="index_BSQG"></a>| <br>
 | gpus       |  [PTQML](#PTQML)<a name="index_PTQML"></a>, [SQPG](#SQPG), [PSG](#PSG), [DSVSG](#DSVSG)| <br>
 | graph      |  [MIS](#MIS), [MWIS](#MWIS)| <br>
 | hamiltonian |  [QAOA](#QAOA)<a name="index_QAOA"></a>, [VQEChem](#VQEChem), [VQETFIM](#VQETFIM)<a name="index_VQETFIM"></a>, [NQD](#NQD), [QNES](#QNES)<a name="index_QNES"></a>, [GOQ](#GOQ)<a name="index_GOQ"></a>, [HGV](#HGV), [AGC](#AGC), [GSAHS](#GSAHS), [GSA](#GSA), [OPRS](#OPRS), [PTA](#PTA), [MIS](#MIS), [RLS](#RLS), [SPL](#SPL), [SLGRA](#SLGRA), [MWIS](#MWIS), [PSG](#PSG), [GSPrS](#GSPrS)<a name="index_GSPrS"></a>, [EVPrS](#EVPrS)| <br>
 | hybrid job |  [GSHJ](#GSHJ), [QMLHJ](#QMLHJ)<a name="index_QMLHJ"></a>, [QHJP](#QHJP)<a name="index_QHJP"></a>, [BYOC](#BYOC), [ESHJ](#ESHJ), [PTQML](#PTQML), [QNES](#QNES), [RJNHJ](#RJNHJ)<a name="index_RJNHJ"></a>, [CHJS](#CHJS), [CPL](#CPL)<a name="index_CPL"></a>, [GOQ](#GOQ), [HGV](#HGV), [HCQJ](#HCQJ), [SQPG](#SQPG)| <br>
 | ionq       |  [RQCQ](#RQCQ), [VC](#VC), [RNG](#RNG)<a name="index_RNG"></a>, [EMIQ](#EMIQ)<a name="index_EMIQ"></a>, [IonNG](#IonNG)<a name="index_IonNG"></a>, [GDCDP](#GDCDP)| <br>
 | iqm        |  [RQCQ](#RQCQ), [VC](#VC), [Grover](#Grover), [IQMNG](#IQMNG), [GSDCI](#GSDCI)<a name="index_GSDCI"></a>, [DCC](#DCC), [HNDC](#HNDC), [OQSDC](#OQSDC)<a name="index_OQSDC"></a>| <br>
 | job        |  [RQCQ](#RQCQ), [GSHJ](#GSHJ), [QMLHJ](#QMLHJ), [QHJP](#QHJP), [BYOC](#BYOC), [ESHJ](#ESHJ), [PTQML](#PTQML), [QNES](#QNES), [RJNHJ](#RJNHJ), [CHJS](#CHJS), [CPL](#CPL), [GOQ](#GOQ), [HGV](#HGV), [HCQJ](#HCQJ), [SQPG](#SQPG), [PSG](#PSG), [DSVSG](#DSVSG)| <br>
 | kraus      |  [GSOQ](#GSOQ), [SN](#SN)<a name="index_SN"></a>, [SNCP](#SNCP)<a name="index_SNCP"></a>| <br>
 | local simulator |  [RQCS](#RQCS)<a name="index_RQCS"></a>, [ExpLS](#ExpLS)<a name="index_ExpLS"></a>, [ESHJ](#ESHJ), [CGPPL](#CGPPL)<a name="index_CGPPL"></a>, [RLS](#RLS), [SPL](#SPL)| <br>
 | model      |  [VQETFIM](#VQETFIM)| <br>
 | moments    |  [DDQC](#DDQC)<a name="index_DDQC"></a>| <br>
 | native gates |  [VC](#VC), [IQMNG](#IQMNG), [IonNG](#IonNG), [LEmu](#LEmu)| <br>
 | noise      |  [GSOQ](#GSOQ), [RNG](#RNG), [SN](#SN), [NM](#NM), [NM](#NM), [NQD](#NQD), [SNCP](#SNCP), [LEmu](#LEmu)| <br>
 | open quantum systems |  [GSOQ](#GSOQ), [SN](#SN), [SNCP](#SNCP), [OQSDC](#OQSDC)| <br>
 | openqasm   |  [GSOQ](#GSOQ), [AOQLS](#AOQLS)<a name="index_AOQLS"></a>, [DCOQ3](#DCOQ3)| <br>
 | optimization |  [QNES](#QNES), [GOQ](#GOQ), [MIS](#MIS), [MWIS](#MWIS)| <br>
 | parallel   |  [CGPPL](#CGPPL), [SQPG](#SQPG), [PSG](#PSG), [DSVSG](#DSVSG)| <br>
 | parameters |  [DDQC](#DDQC), [QAOA](#QAOA), [BE](#BE)<a name="index_BE"></a>, [NGC](#NGC), [BSQG](#BSQG)| <br>
 | pauli operators |  [EVPrS](#EVPrS)| <br>
 | pennylane  |  [GSHJ](#GSHJ), [QHJP](#QHJP), [BYOC](#BYOC), [ESHJ](#ESHJ), [PTQML](#PTQML), [QNES](#QNES), [CHJS](#CHJS), [CPL](#CPL), [CGPPL](#CGPPL), [GOQ](#GOQ), [HGV](#HGV), [SNCP](#SNCP), [TRU](#TRU), [AGC](#AGC), [SPL](#SPL)| <br>
 | physics    |  [VQETFIM](#VQETFIM), [SLGRA](#SLGRA)| <br>
 | pragma     |  [GSOQ](#GSOQ), [AOQLS](#AOQLS)| <br>
 | program sets |  [GSPrS](#GSPrS), [EVPrS](#EVPrS)| <br>
 | pulse      |  [BE](#BE), [NGC](#NGC), [BPPR](#BPPR), [BSQG](#BSQG), [SPL](#SPL)| <br>
 | qaa        |  [QAA](#QAA)<a name="index_QAA"></a>| <br>
 | qaoa       |  [AGRT](#AGRT), [QAOA](#QAOA), [QHJP](#QHJP), [ESHJ](#ESHJ), [QNES](#QNES), [GOQ](#GOQ), [SNCP](#SNCP)| <br>
 | qiskit     |  [Qis](#Qis)<a name="index_Qis"></a>, [DCQis](#DCQis)<a name="index_DCQis"></a>| <br>
 | qml        |  [QMLHJ](#QMLHJ)| <br>
 | qpe        |  [QPE](#QPE)<a name="index_QPE"></a>| <br>
 | reset      |  [GSDCI](#GSDCI), [DCC](#DCC), [HNDC](#HNDC)| <br>
 | result type |  [AGRT](#AGRT)| <br>
 | results    |  [DDQC](#DDQC), [GSOQ](#GSOQ), [AGRT](#AGRT), [QFT](#QFT)<a name="index_QFT"></a>, [GSPrS](#GSPrS), [LEmu](#LEmu)| <br>
 | rigetti    |  [RQCQ](#RQCQ), [GSOQ](#GSOQ), [VC](#VC), [RNG](#RNG), [NM](#NM), [AQQD](#AQQD), [BE](#BE), [BPPR](#BPPR), [CPL](#CPL), [LEmu](#LEmu)| <br>
 | rydberg    |  [NQD](#NQD), [GSAHS](#GSAHS), [GSA](#GSA), [OPRS](#OPRS), [PTA](#PTA), [MIS](#MIS), [RLS](#RLS), [SPL](#SPL), [SLGRA](#SLGRA), [MWIS](#MWIS)| <br>
 | s3         |  [GNQT](#GNQT)<a name="index_GNQT"></a>, [CHJS](#CHJS)| <br>
 | shots      |  [GSPrS](#GSPrS)| <br>
 | simons     |  [Simon](#Simon)<a name="index_Simon"></a>| <br>
 | simulators |  [RQCS](#RQCS), [AOQLS](#AOQLS), [ExpLS](#ExpLS), [TNSim](#TNSim)<a name="index_TNSim"></a>, [TNHP](#TNHP)<a name="index_TNHP"></a>, [SN](#SN)| <br>
 | subroutine |  [Grover](#Grover), [QAA](#QAA), [QFT](#QFT), [QPE](#QPE), [AOQLS](#AOQLS), [IonNG](#IonNG)| <br>
 | superdense |  [SC](#SC)| <br>
 | task       |  [RQCQ](#RQCQ), [SC](#SC), [DDQC](#DDQC), [GSOQ](#GSOQ), [GNQT](#GNQT), [Grover](#Grover), [RNG](#RNG), [TNSim](#TNSim), [TNHP](#TNHP), [GSHJ](#GSHJ), [CHJS](#CHJS), [AQQD](#AQQD), [CPL](#CPL), [TRU](#TRU), [AGC](#AGC), [GSA](#GSA), [PTA](#PTA)| <br>
 | teleportation |  [SC](#SC), [DCC](#DCC)| <br>
 | verbatim   |  [GSOQ](#GSOQ), [VC](#VC), [IQMNG](#IQMNG), [HNDC](#HNDC), [LEmu](#LEmu)| <br>
 | vqe        |  [VQEChem](#VQEChem), [VQETFIM](#VQETFIM), [HGV](#HGV), [AGC](#AGC), [Qis](#Qis)| <br>

---

## <a name="support ">Support</a>

### Installing Dependencies 

To install the dependencies required for running the notebook examples in this repository you can create a conda environment with below commands.

```bash
conda env create -n <your_env_name> -f environment.yml
```

Activate the conda environment using:
ß
```bash
conda activate <your_env_name>
```

To remove the conda environment use:

```bash
conda deactivate
```

For more information, please see [conda usage](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

To run the notebook examples locally on your IDE, first, configure a profile to use your account to interact with AWS. To learn more, see [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

After you create a profile, use the following command to set the `AWS_PROFILE` so that all future commands can access your AWS account and resources.

```bash
export AWS_PROFILE=YOUR_PROFILE_NAME
```

### Issues and Bug Reports

If you encounter bugs or face issues while using the examples, please let us know by posting
the issue on our [Github issue tracker](https://github.com/amazon-braket/amazon-braket-examples/issues/).  
For other issues or general questions, please ask on the [Quantum Computing Stack Exchange](https://quantumcomputing.stackexchange.com/questions/ask) and add the tag [amazon-braket](https://quantumcomputing.stackexchange.com/questions/tagged/amazon-braket).

### Feedback and Feature Requests

If you have feedback or features that you would like to see on Amazon Braket, we would love to hear from you!  
[Github issues](https://github.com/amazon-braket/amazon-braket-examples/issues/) is our preferred mechanism for collecting feedback and feature requests, allowing other users
to engage in the conversation, and +1 issues to help drive priority.
