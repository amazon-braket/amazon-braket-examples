# Amazon Braket Examples 
Welcome to the primary repository for Amazon Braket tutorials. We provide tutorials on quantum computing, using Amazon Braket. We provide examples for quantum circuits and quantum annealing. We cover canonical routines, such as the Quantum Fourier Transform (QFT), as well as hybrid quantum algorithms, such as the Variational Quantum Eigensolver (VQE).

The repository is structured as follows:  

- [Getting started: Simple circuits and algorithms](#start)
- [Continue exploring](#continue)
  - [Quantum hardware](#hardware)
  - [Quantum simulations](#simulations)
  - [Quantum algorithms and protocols](#algorithms)
    - [Canonical](#canonical)
    - [Variational](#variational)
    - [Algorithm implementation library](#implementations)
  - [Quantum frameworks and plugins](#frameworks)
  - [Advanced Braket features](#advanced)
  - [Applications and industry uses](#applications)
- [Braket through qBraid](#qbraid)
- [Braket courses](#courses)
- [Creating a Conda environment](#conda)

---
## Alternative exploration sequence
An arrangement of the Amazon Braket tutorials meant to be reflective of what is encountered in standard courses and textbooks on quantum computing and quantum information science can be found [here](./alternative_organization.md). In addition to the notebooks found in this repository, relevant Amazon Braket blogposts are featured as well.

---
## <a name="start">Getting started</a>

  * [**Getting started with Amazon Braket**](modules/Getting_Started/0_Getting_started/0_Getting_started.ipynb)

    A hello-world tutorial that shows you how to build a simple circuit and run it on a local simulator.

  * [**Running quantum circuits on simulators**](modules/Getting_Started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb)

    This tutorial prepares a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne, and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. For this reason, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication, and quantum metrology.

  * [**Running quantum circuits on QPU devices**](modules/Getting_Started/2_Running_quantum_circuits_on_QPU_devices/2_Running_quantum_circuits_on_QPU_devices.ipynb)

    This tutorial prepares a maximally-entangled Bell state between two qubits, for classical simulators and for QPUs. For classical devices, we can run the circuit on a local simulator or a cloud-based on-demand simulator. For the quantum devices, we run the circuit on the superconducting machine from Rigetti, and on the ion-trap machine provided by IonQ. As shown, one can swap between different devices seamlessly, without any modifications to the circuit definition, by re-defining the device object. We also show how to recover results using the unique Amazon resource identifier (ARN) associated with every task. This tool is useful if you must deal with potential delays, which can occur if your quantum task sits in the queue awaiting execution.  

  * [**Deep dive into the anatomy of quantum circuits**](modules/Getting_Started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb)

    This tutorial discusses in detail the anatomy of quantum circuits in the Amazon Braket SDK. Specifically, you'll learn how to build (parameterized) circuits and display them graphically, and how to append circuits to each other. We discuss the associated circuit depth and circuit size. Finally we show how to execute the circuit on a device of our choice (defining a quantum task). We then learn how to track, log, recover, or cancel such a _quantum task_ efficiently.

  * [**Getting devices and checking device properties**](modules/Getting_Started/4_Getting_Devices_and_Checking_Device_Properties/4_Getting_Devices_and_Checking_Device_Properties.ipynb)

    This tutorial shows how to interact with the Amazon Braket GetDevice API to retrieve Amazon Braket devices (such as simulators and QPUs) programmatically, and how to gain access to their properties.

---  
## <a name="continue">Continue exploring</a>

### <a name="hardware">Quantum hardware</a>

  * [**Allocating qubits on QPU devices**](modules/Continue_Exploring/quantum_hardware/Allocating_Qubits_on_QPU_Devices.ipynb)

    This tutorial explains how you can use the Amazon Braket SDK to allocate the qubit selection for your circuits manually, when running on QPUs.

  * [**Analog Hamiltonian simulation**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation)

    This tutorial series provides a step-by-step walkthrough explaining analog Hamiltonian simulations (AHS) and how to run AHS programs on local simulators and Rydberg-based QPUs via Amazon Braket. AHS is a quantum computing paradigm different from gate-based computing. AHS uses a well-controlled quantum system and tunes its parameters to mimic the dynamics of another quantum system, the one we aim to study. In the gate-based quantum computation, the program is a quantum circuit consisting of a series of quantum gates, each of which acts only a small subset of qubits. In contrast, an AHS program is a sequence of time-dependent Hamiltonians that govern the quantum dynamics of all qubits; during AHS, the effect of the evolution under a Hamiltonian can be understood as a unitary acting simultaneously on all qubits.

    * [**Introduction of analog Hamiltonian simulation**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb)
    * [**Introduction to Aquila**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/01_Introduction_to_Aquila.ipynb)
    * [**Ordered phases in Rydberg systems**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb)
    * [**Parallel tasks on Aquila**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/03_Parallel_tasks_on_Aquila.ipynb)
    * [**Maximum independent sets with analog Hamiltonian simulation**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb)
    * [**Running analog Hamiltonian simulation with local simulator**](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb)

    <br />

  * [**Compilation**](modules/Continue_Exploring/quantum_hardware/compilation)

    This notebook collection shows how to run your circuits on Braket devices exactly as defined without any modification during the compilation process, a feature known as verbatim compilation. Usually, when you run a circuit on a QPU, behind the scenes, Amazon Braket will do a series of compilation steps to optimize your circuit and map the abstract circuit to the physical qubits on the QPU. However, in many situations, such as for error mitigation or benchmarking experiments, researchers require full control of the qubits and the gates that are being applied, thereby motivating the use of verbatim compilation.
    
    OpenQASM, a popular human-readable and hardware-agnostic quantum circuit description language currently supported as an *Intermediate Representation* (IR) on Amazon Braket, is also introduced. The associated tutorials show how to submit OpenQASM tasks to various devices on Braket and introduce some OpenQASM features available on Braket. In addition, verbatim compilation can be performed with OpenQASM by specifying a verbatim pragma around a box of code.

    * [**Getting Started with OpenQASM on Braket**](modules/Continue_Exploring/quantum_hardware/compilation/Getting_Started_with_OpenQASM_on_Braket.ipynb) 
    * [**Simulating advanced OpenQASM programs with the local simulator**](modules/Continue_Exploring/quantum_hardware/compilation/Simulating_Advanced_OpenQASM_Programs_with_the_Local_Simulator.ipynb)
    * [**Verbatim compilation**](modules/Continue_Exploring/quantum_hardware/compilation/Verbatim_Compilation.ipynb)

    <br />

  * [**Error mitigation**](modules/Continue_Exploring/quantum_hardware/error_mitigation/Error_Mitigation_on_Amazon_Braket.ipynb)

    This tutorial shows how to get started with using IonQ's Aria QPU on Amazon Braket. You’ll learn how Aria's two built-in error mitigation techniques work, how to switch between them, and the performance difference you can expect to see with and without these techniques for toy problems. 

  * [**Pulse control**](modules/Continue_Exploring/quantum_hardware/pulse_control/)

    This tutorial series explains how to use pulse control on various QPUs in Amazon Braket. Pulses are the analog signals that control the qubits in a quantum computer. With certain devices on Amazon Braket, you can access the pulse control feature to submit circuits using pulses.

    * [**Bringup experiments**](modules/Continue_Exploring/quantum_hardware/pulse_control/1_Bringup_experiments.ipynb) 
    * [**Creating a Bell state with cross-resonance pulses on OQC's Lucy**](modules/Continue_Exploring/quantum_hardware/pulse_control/2_Bell_pair_with_pulses_OQC.ipynb)
    * [**Creating a Bell state with pulses on Rigetti's Aspen M-3**](modules/Continue_Exploring/quantum_hardware/pulse_control/3_Bell_pair_with_pulses_Rigetti.ipynb)
    * [**Build single qubit quantum gates**](modules/Continue_Exploring/quantum_hardware/pulse_control/4_Build_single_qubit_gates.ipynb)

    <br />

---
### <a name="simulations">Quantum simulations</a>

  * [**Noise simulations**](modules/Continue_Exploring/quantum_sims/noise_simulations)

    This notebook collection provides a detailed overview of noise simulation on Amazon Braket. You will learn how to define noise channels, apply noise to new or existing circuits, and run those circuits on the Amazon Braket noise simulators. We also introduce noise models on Amazon Braket, along with details on how to create noise models containing different types of noise and instructions for how to apply the noise to a circuit. We show how to construct a noise model from device calibration data for real quantum processing units (QPUs) and also compare the measurement outcomes of circuits run on a noisy simulator with the same circuits run on QPUs to show that simulating circuits with noise models more closely mimics QPUs.

    * [**Noise models on Amazon Braket**](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Amazon_Braket.ipynb)
    * [**Noise models on Rigetti**](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Rigetti.ipynb)
    * [**Simulating noise on Amazon Braket**](modules/Continue_Exploring/quantum_sims/noise_simulations/Simulating_Noise_On_Amazon_Braket.ipynb)

    <br />

  * [**Testing the tensor network simulator with local and non-local random quantum circuits**](modules/Continue_Exploring/quantum_sims/TN1_demo_local_vs_non-local_random_circuits.ipynb)

    This notebook explores a class of random quantum circuits known as Hayden-Preskill circuits using the tensor network simulator backend in Amazon Braket. The goal is to understand the degree to which the tensor network simulator is capable of detecting a hidden local structure in a quantum circuit, while simultaneously building experience with the Amazon Braket service and SDK. We find that the TN1 tensor network simulator can efficiently simulate local random quantum circuits, even when the local structure is obfuscated by permuting the qubit indices. Conversely, when running genuinely non-local versions of the quantum circuits, the simulator's performance is significantly degraded.

  * [**Using the 'AdjointGradient' result type on Amazon Braket**](modules/Continue_Exploring/quantum_sims/Using_The_Adjoint_Gradient_Result_Type.ipynb)

    This notebook introduces the `AdjointGradient` result type, discusses what a gradient is and how to compute one on a quantum circuit, explains how they can be used to accelerate your workflows, and shows an example of gradients in action on a hybrid quantum algorithm.

  * [**Using the Amazon Braket tensor network simulator TN1**](modules/Continue_Exploring/quantum_sims/Using_the_tensor_network_simulator_TN1.ipynb)

    This notebook introduces the Amazon Braket on-demand tensor network simulator, TN1. You will learn about how TN1 works, how to use it, and which problems are best suited to run on TN1.

---
### <a name="algorithms">Quantum algorithms and protocols</a>

#### <a name="canonical">Canonical</a>

  * [**Grover**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Grover/Grover.ipynb)

    This tutorial provides a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks, by means of the Amazon Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine.

  * [**Quantum Fourier transform**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Fourier_Transform/Quantum_Fourier_Transform.ipynb)

    This tutorial provides a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse QFT, using the Amazon Braket SDK. We provide two different implementations: with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relationship to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows one to define custom methods and add them to the Circuit class.

  * [**Quantum phase estimation**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Phase_Estimation/Quantum_Phase_Estimation.ipynb)

    This tutorial provides a detailed implementation of the Quantum Phase Estimation (QPE) algorithm, through the Amazon Braket SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning, or in the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using the Amazon Braket SDK, and we illustrate the application of the algorithm with simple examples. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows you to use custom-built gates as if they were any other built-in gates. This tutorial is set up to run on the local simulator or the on-demand simulator. Changing between these devices requires changing only one line of code, as demonstrated below in cell.

  * [**Quantum amplitude amplification**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Amplitude_Amplification/Quantum_Amplitude_Amplification.ipynb)

    This tutorial provides a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm, using the Amazon Braket SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.

  * [**Randomness generation**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Randomness/Randomness_Generation.ipynb)

    This tutorial provides a detailed implementation of a quantum random number generation (QRNG). Random numbers are a ubiquitous resource in computation and cryptography. For example, in security, random numbers are crucial to creating keys for encryption. QRNGs, which make use of the inherent unpredictability in quantum physics, promise enhanced security compared to standard cryptographic pseudo-random number generators (CPRNGs) based on classical technologies. In the notebook, we program two separate quantum processor units (QPUs) from different suppliers in Amazon Braket to supply two streams of weakly random bits. We then show how to generate physically secure randomness from these two weak sources by means of classical post-processing based on randomness extractors.

  * [**Simon's algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Simons_Algorithm/Simons_Algorithm.ipynb)

    This tutorial provides a detailed discussion and implementation of Simon's algorithm, which provided the first example of an exponential speedup over the best known classical algorithm by using a quantum computer to solve a particular problem. Originally published in 1994, Simon's algorithm was a precursor to Shor's well-known factoring algorithm, and it served as inspiration for many of the seminal works in quantum computation that followed.

  * [**Superdense coding**](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Superdense_coding/Superdense_coding.ipynb) 
  
    This tutorial constructs an implementation of the *superdense coding protocol*, by means of the Amazon Braket SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (*aka* Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (*aka* Bob), who is then able to decode the full two-bit message.

#### <a name="variational">Variational</a>

  * [**QAOA**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/QAOA/QAOA_braket.ipynb)

    This tutorial shows how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical and quantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era, QAOA is also an emerging approach for benchmarking quantum devices. It is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach, we benchmark our results with exact results as obtained from classical QUBO solvers.

  * [**VQE transverse Ising**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb)

    This tutorial shows how to solve for the ground state of the Transverse Ising Model, which is arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical andquantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach, we benchmark our results with exact results as obtained from a Jordan-Wigner transformation.

  * [**VQE chemistry**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Chemistry/VQE_chemistry_braket.ipynb)

    This tutorial shows how to implement the Variational Quantum Eigensolver (VQE) algorithm in Amazon Braket SDK to compute the potential energy surface (PES) for the Hydrogen molecule. Specifically, we illustrate the following features of Amazon Braket SDK: `LocalSimulator` which allows one to simulate quantum circuits on their local machine; construction of the ansatz circuit for VQE in Braket SDK; and computing expectation values of the individual terms in the Hamiltonian in Braket SDK.

  * [**Amazon Braket Hybrid Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs)
  
    This folder contains examples that illustrate the use of Amazon Braket Hybrid Jobs (Braket Jobs for short).

      * [**When to use Braket Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/README_hybrid_jobs.md)

      * [**Getting started with Braket Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/0_Creating_your_first_Hybrid_Job/Creating_your_first_Hybrid_Job.ipynb)

        This notebook provides a demonstration of running a simple Braket Job. You will learn how to create a Braket Job using the Braket SDK or the Braket console, how to set the output S3 folder for a job, and how to retrieve results. You will also learn how to specify the Braket device to run your job on simulators or QPUs. Finally, you will learn how to use local mode to quickly debug your code.

      * [**Quantum machine learning in Braket Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs/Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb)

        This notebook shows a typical quantum machine learning workflow using Braket Jobs. In the process, you will learn how to upload input data, how to set up hyperparameters for your job, and how to retrieve and plot metrics. Finally, you will see how to run multiple Braket Jobs in parallel with different sets of hyperparameters.

      * [**QAOA with Braket Jobs and PennyLane**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs/Using_PennyLane_with_Braket_Jobs.ipynb)

        This notebook shows how to run the QAOA algorithm with PennyLane (similar to a [previous notebook](examples/pennylane/2_Graph_optimization_with_QAOA.ipynb)), but this time using Braket Jobs. In the process, you will learn how to select a container image that supports PennyLane, and how to use checkpoints to save and load training progress of a job.

      * [**Bring your own containers to Braket Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/3_Bring_your_own_container/bring_your_own_container.ipynb)

        This notebook demonstrates the use of the Bring-Your-Own-Container (BYOC) functionality of Braket Jobs. While Amazon Braket has pre-configured environments which support most use cases of Braket Jobs, BYOC enables you to define fully customizable environments using Docker containers. You will learn how to use BYOC, including preparing a Dockerfile, creating a private Amazon Elastic Container Registry (ECR), building the container, and submitting a Braket Job using the custom container.

      * [**Embedded simulators in Braket Jobs**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/4_Embedded_simulators_in_Braket_Jobs/Embedded_simulators_in_Braket_Jobs.ipynb)

        This notebook introduces embedded simulators in Braket Jobs. An embedded simulator is a local simulator that runs completely within a job instance, i.e., the compute resource that is running your algorithm script. In contrast, [on-demand simulators](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html#braket-simulator-sv1), such as SV1, DM1, or TN1, calculate the results of a quantum circuit on dedicated compute infrastructure on-demand by Amazon Braket. By using embedded simulators, we keep all computations in the same environment. This allows the optimization algorithm to access advanced features supported by the embedded simulator. Furthermore, with the [Bring Your Own Container (BYOC)](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-byoc.html) feature of Jobs, users may choose to use open source simulators or their own proprietary simulation tools.

      * [**Parallelize training for quantum machine learning**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb)

        This notebook shows how to use [SageMaker's distributed data parallel library](https://docs.aws.amazon.com/sagemaker/latest/dg/data-parallel.html) in Braket Jobs to accelerate the training of your quantum model. We go through examples to show you how to parallelize trainings across multiple GPUs in an instance, and even multiple GPUs over multiple instances. 

      * [**Benchmarking QN-SPSA optimizer with Braket Jobs and embedded simulators**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator/qnspsa_with_embedded_simulator.ipynb)

        This notebook demonstrates how to implement and benchmark the QN-SPSA optimizer, a novel quantum optimization algorithm proposed by Gacon et al. Following this example, we will show how you can use Amazon Braket Hybrid Jobs to iterate faster on variational algorithm research, discuss best practices, and help you scale up your simulations with embedded simulators.

      * [**Running notebooks as hybrid jobs with Amazon Braket**](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/7_Running_notebooks_as_jobs/Running_notebooks_as_jobs.ipynb)

        This notebook shows how users can run notebooks on different quantum hardware with priority access by using Amazon Braket Hybrid Jobs.

#### <a name="implementations">Algorithm implementation library</a>
  The Braket Algorithm Library Notebooks provide ready-to-run example notebooks of algorithm implementations.

  * [**Local setup instructions**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/README.md)

  * [**Bell's inequality**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Bells_Inequality.ipynb)
  
  * [**Bernstein-Vazirani algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Bernstein_Vazirani_Algorithm.ipynb)

  * [**CHSH inequality**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/CHSH_Inequality.ipynb)

  * [**Deutsch-Jozsa algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Deutsch_Jozsa_Algorithm.ipynb)

  * [**Grover's search algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Grovers_Search.ipynb)

  * [**Quantum approximate optimization algorithm (QAOA)**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Approximate_Optimization_Algorithm.ipynb)

  * [**Quantum circuit born machine**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Circuit_Born_Machine.ipynb)

  * [**Quantum Monte Carlo**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Computing_Quantum_Monte_Carlo.ipynb)

  * [**Quantum Fourier transform**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Fourier_Transform.ipynb)

  * [**Quantum phase estimation**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Phase_Estimation_Algorithm.ipynb)

  * [**Quantum walk**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Walk.ipynb)

  * [**Shor's algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Shors_Algorithm.ipynb)

  * [**Simon's algorithm**](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Simons_Algorithm.ipynb)

---
### <a name="frameworks">Quantum frameworks and plugins</a>

#### <a name="pennylane">Quantum machine learning and optimization with PennyLane</a>
  * [**Combining PennyLane with Amazon Braket**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/0_Getting_started/0_Getting_started.ipynb)

    This tutorial shows you how to construct circuits and evaluate their gradients in PennyLane with execution performed using Amazon Braket.

  * [**Computing gradients in parallel with PennyLane-Braket**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/1_Parallelized_optimization_of_quantum_circuits/1_Parallelized_optimization_of_quantum_circuits.ipynb)

    This tutorial explores how to speed up training of quantum circuits by using parallel execution on Amazon Braket. We begin by discussing why quantum circuit training involving gradients requires multiple device executions and motivate how the Braket SV1 simulator can be used to overcome this. The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the local simulator for both executions and gradient calculations. This illustrates how parallel capabilities can be combined between PennyLane and SV1.

  * [**Graph optimization with QAOA**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb)

    This tutorial digs deeper into how quantum circuit training can be applied to a problem of practical relevance in graph optimization. We show how easy it is to train a QAOA circuit in PennyLane to solve the maximum clique problem on a simple example graph. The tutorial then extends to a more difficult 20-node graph and uses the parallel capabilities of the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, using around 1-2 minutes per iteration.

  * [**Hydrogen geometry with VQE**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb)

    This tutorial shows how PennyLane and Amazon Braket can be combined to solve an important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how qubit-wise commuting observables can be measured together in PennyLane and Braket, making optimization more efficient.

  * [**Simulation of noisy quantum circuits on Amazon Braket with PennyLane**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb)

    This tutorial explores the impact of noise on quantum hybrid algorithms. We will take QAOA as an example to benchmark performance in the presence of noise. Additionally, the tutorial gives an overview of noise simulation on Amazon Braket with PennyLane, such that the user will be able to use PennyLane to simulate the noisy circuits, on either the local or Braket on-demand noise simulator. In particular, the notebook covers the basic concepts of noise channels and uses PennyLane to compute cost functions of noisy circuits and optimize them. 

  * [**Tracking Resource Usage with PennyLane Device Tracker**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/5_Tracking_resource_usage/5_Tracking_resource_usage.ipynb)

    This tutorial shows how to use the PennyLane device tracker feature with Amazon Braket. Computing gradients of quantum circuits involves multiple devices executions, which can lead to a large number of executions when optimizing quantum circuits. So to help users keep track of their usage, Amazon Braket works with PennyLane to record and make available useful information during the computation. The PennyLane device resource tracker keeps a record of the usage of a device, such as numbers of circuit evaluations and shots. Amazon Braket extends this information with task IDs and simulator duration to allow further tracking. The device tracker can be combined with additional logic to monitor and limit resource usage on devices.

  * [**Adjoint gradient computation with PennyLane and Amazon Braket**](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/6_Adjoint_gradient_computation/6_Adjoint_gradient_computation.ipynb)

    This tutorial shows how to compute gradients of free parameters in a quantum circuit using PennyLane and Amazon Braket.

#### <a name="qiskit">Qiskit with the Qiskit-Braket provider</a>
  * [**How to run Qiskit on Amazon Braket**](modules/Continue_Exploring/quantum_frameworks_and_plugins/qiskit/0_Getting_Started.ipynb)

    This tutorial shows you how to run your [Qiskit](https://qiskit.org) code across any of the gate-based devices on Amazon Braket with the [Qiskit-Braket provider](https://github.com/qiskit-community/qiskit-braket-provider/blob/main/docs/tutorials/0_tutorial_qiskit-braket-provider_overview.ipynb).

---
### <a name="advanced">Advanced Braket features</a>

  * [**Getting notifications when a task completes**](modules/Continue_Exploring/advanced_braket_features/Getting_notifications_when_a_task_completes/Getting_notifications_when_a_task_completes.ipynb)

    This tutorial illustrates how Amazon Braket integrates with Amazon EventBridge for event-based processing. In the tutorial, you will learn how to configure Amazon Braket and Amazon Eventbridge to receive text notification about task completions on your phone. Of course, EventBridge also allows you to build full, event-driven applications based on events emitted by Amazon Braket.

---
### <a name="applications">Applications and industry uses</a>
  *Currently under development.*

---
## <a name="courses">Braket courses</a>
  *Currently under development.*

---
## <a name="qbraid">Braket through QBraid</a>

  * [**Getting started with Braket through QBraid**](modules/QBraid/README.md)

---
## <a name="conda">Creating a conda environment</a>
To install the dependencies required for running the notebook examples in this repository you can create a conda environment with below commands.

```bash
conda env create -n <your_env_name> -f environment.yml
```

Activate the conda environment using:
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

---
## Support

### Issues and bug reports

If you encounter bugs or face issues while using the examples, please let us know by posting 
the issue on our [Github issue tracker](https://github.com/aws/amazon-braket-examples/issues/).  
For other issues or general questions, please ask on the [Quantum Computing Stack Exchange](https://quantumcomputing.stackexchange.com/questions/ask) and add the tag [amazon-braket](https://quantumcomputing.stackexchange.com/questions/tagged/amazon-braket).

### Feedback and feature requests

If you have feedback or features that you would like to see on Amazon Braket, we would love to hear from you!  
[Github issues](https://github.com/aws/amazon-braket-examples/issues/) is our preferred mechanism for collecting feedback and feature requests, allowing other users 
to engage in the conversation, and +1 issues to help drive priority. 