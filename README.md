# Braket Tutorials GitHub
Welcome to the primary repository for Amazon Braket tutorials. We provide tutorials on quantum computing, using Amazon Braket. We provide examples for quantum circuits and quantum annealing. We cover canonical routines, such as the Quantum Fourier Transform (QFT), as well as hybrid quantum algorithms, such as the Variational Quantum Eigensolver (VQE).

The repository is structured as follows:  

- [Getting Started: Simple circuits and algorithms](#simple)
- [Advanced circuits and algorithms](#advanced)
- [Hybrid quantum algorithms](#hybrid)
- [Quantum machine learning and optimization with PennyLane](#pennylane)
- [Amazon Braket features](#braket)
- [Amazon Braket Hybrid Jobs](#jobs)
- [Photonic quantum computing with Strawberry Fields](#photonics)
- [Creating a Conda environment](#conda)

---
## <a name="simple">Simple circuits and algorithms</a>

  * [**Getting started**](examples/getting_started/0_Getting_started/0_Getting_started.ipynb)

    A hello-world tutorial that shows you how to build a simple circuit and run it on a local simulator.

  * [**Running quantum circuits on simulators**](examples/getting_started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb)

    This tutorial prepares a paradigmatic example for a multi-qubit entangled state, the so-called GHZ state (named after the three physicists Greenberger, Horne, and Zeilinger). The GHZ state is extremely non-classical, and therefore very sensitive to decoherence. For this reason, it is often used as a performance benchmark for today's hardware. Moreover, in many quantum information protocols it is used as a resource for quantum error correction, quantum communication, and quantum metrology.

  * [**Running quantum circuits on QPU devices**](examples/getting_started/2_Running_quantum_circuits_on_QPU_devices/2_Running_quantum_circuits_on_QPU_devices.ipynb)

    This tutorial prepares a maximally-entangled Bell state between two qubits, for classical simulators and for QPUs. For classical devices, we can run the circuit on a local simulator or a cloud-based on-demand simulator. For the quantum devices, we run the circuit on the superconducting machine from Rigetti, and on the ion-trap machine provided by IonQ. As shown, one can swap between different devices seamlessly, without any modifications to the circuit definition, by re-defining the device object. We also show how to recover results using the unique Amazon resource identifier (ARN) associated with every task. This tool is useful if you must deal with potential delays, which can occur if your quantum task sits in the queue awaiting execution.  

  * [**Deep Dive into the anatomy of quantum circuits**](examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb)

    This tutorial discusses in detail the anatomy of quantum circuits in the Amazon Braket SDK. Specifically, you'll learn how to build (parameterized) circuits and display them graphically, and how to append circuits to each other. We discuss the associated circuit depth and circuit size. Finally we show how to execute the circuit on a device of our choice (defining a quantum task). We then learn how to track, log, recover, or cancel such a _quantum task_ efficiently.

  * [**Superdense coding**](examples/getting_started/4_Superdense_coding/4_Superdense_coding.ipynb)

    This tutorial constructs an implementation of the _superdense coding_ protocol, by means of the Amazon Braket SDK. Superdense coding is a method of transmitting two classical bits by sending only one qubit. Starting with a pair of entanged qubits, the sender (_aka_ Alice) applies a certain quantum gate to their qubit and sends the result to the receiver (_aka_ Bob), who is then able to decode the full two-bit message.     

---  
## <a name="advanced">Advanced circuits and algorithms</a>

  * [**Grover**](examples/advanced_circuits_algorithms/Grover/Grover.ipynb)

    This tutorial provides a step-by-step walkthrough explaining Grover's quantum algorithm. We show how to build the corresponding quantum circuit with simple modular building blocks, by means of the Amazon Braket SDK. Specifically, we demonstrate how to build custom gates that are not part of the basic gate set provided by the SDK. A custom gate can used as a core quantum gate by registering it as a subroutine.

  * [**Quantum Fourier Transform**](examples/advanced_circuits_algorithms/Quantum_Fourier_Transform/Quantum_Fourier_Transform.ipynb)

    This tutorial provides a detailed implementation of the Quantum Fourier Transform (QFT) and the inverse QFT, using the Amazon Braket SDK. We provide two different implementations: with and without recursion. The QFT is an important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the quantum phase estimation (QPE) algorithm for estimating the eigenvalues of a unitary operator. The QFT can be performed efficiently on a quantum computer, using only O(n<sup>2</sup>) single-qubit Hadamard gates and two-qubit controlled phase shift gates, where 𝑛 is the number of qubits. We first review the basics of the quantum Fourier transform, and its relationship to the discrete (classical) Fourier transform. We then implement the QFT in code two ways: recursively and non-recursively. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows one to define custom methods and add them to the Circuit class.

  * [**Quantum Phase Estimation**](examples/advanced_circuits_algorithms/Quantum_Phase_Estimation/Quantum_Phase_Estimation.ipynb)

    This tutorial provides a detailed implementation of the Quantum Phase Estimation (QPE) algorithm, through the Amazon Braket SDK. The QPE algorithm is designed to estimate the eigenvalues of a unitary operator 𝑈; it is a very important subroutine to many quantum algorithms, most famously Shor's algorithm for factoring, and the HHL algorithm (named after the physicists Harrow, Hassidim and Lloyd) for solving linear systems of equations on a quantum computer. Moreover, eigenvalue problems can be found across many disciplines and application areas, including (for example) principal component analysis (PCA) as used in machine learning, or in the solution of differential equations as relevant across mathematics, physics, engineering and chemistry. We first review the basics of the QPE algorithm. We then implement the QPE algorithm in code using the Amazon Braket SDK, and we illustrate the application of the algorithm with simple examples. This notebook also showcases the Amazon Braket `circuit.subroutine` functionality, which allows you to use custom-built gates as if they were any other built-in gates. This tutorial is set up to run on the local simulator or the on-demand simulator. Changing between these devices requires changing only one line of code, as demonstrated below in cell.

  * [**Quantum Amplitude Amplification**](examples/advanced_circuits_algorithms/Quantum_Amplitude_Amplification/Quantum_Amplitude_Amplification.ipynb)

    This tutorial provides a detailed discussion and implementation of the Quantum Amplitude Amplification (QAA) algorithm, using the Amazon Braket SDK. QAA is a routine in quantum computing which generalizes the idea behind Grover's famous search algorithm, with applications across many quantum algorithms. In short, QAA uses an iterative approach to systematically increase the probability of finding one or multiple target states in a given search space. In a quantum computer, QAA can be used to obtain a quadratic speedup over several classical algorithms.

---
##  <a name="hybrid">Hybrid quantum algorithms</a>

  * [**QAOA**](examples/hybrid_quantum_algorithms/QAOA/QAOA_braket.ipynb)

    This tutorial shows how to (approximately) solve binary combinatorial optimization problems, using the Quantum Approximate Optimization Algorithm (QAOA). The QAOA algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical and quantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. In this NISQ era, QAOA is also an emerging approach for benchmarking quantum devices. It is a prime candidate for demonstrating a practical quantum speed-up on near-term NISQ device. To validate our approach, we benchmark our results with exact results as obtained from classical QUBO solvers.

  * [**VQE Transverse Ising**](examples/hybrid_quantum_algorithms/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb)

    This tutorial shows how to solve for the ground state of the Transverse Ising Model, which is arguably one of the most prominent, canonical quantum spin systems, using the variational quantum eigenvalue solver (VQE). The VQE algorithm belongs to the class of _hybrid quantum algorithms_ (leveraging classical andquantum computers), which are widely believed to be the working horse for the current NISQ (noisy intermediate-scale quantum) era. To validate our approach, we benchmark our results with exact results as obtained from a Jordan-Wigner transformation.

---
## <a name="pennylane">Quantum machine learning and optimization with PennyLane</a>
  * [**Combining PennyLane with Amazon Braket**](examples/pennylane/0_Getting_started/0_Getting_started.ipynb)

    This tutorial shows you how to construct circuits and evaluate their gradients in PennyLane with execution performed using Amazon Braket.

  * [**Computing gradients in parallel with PennyLane-Braket**](examples/pennylane/1_Parallelized_optimization_of_quantum_circuits/1_Parallelized_optimization_of_quantum_circuits.ipynb)

    In this tutorial, we explore how to speed up training of quantum circuits by using parallel execution on Amazon Braket. We begin by discussing why quantum circuit training involving gradients requires multiple device executions and motivate how the Braket SV1 simulator can be used to overcome this. The tutorial benchmarks SV1 against a local simulator, showing that SV1 outperforms the local simulator for both executions and gradient calculations. This illustrates how parallel capabilities can be combined between PennyLane and SV1.

  * [**Graph optimization with QAOA**](examples/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb)

    In this tutorial we dig deeper into how quantum circuit training can be applied to a problem of practical relevance in graph optimization. We show how easy it is to train a QAOA circuit in PennyLane to solve the maximum clique problem on a simple example graph. The tutorial then extends to a more difficult 20-node graph and uses the parallel capabilities of the Amazon Braket SV1 simulator to speed up gradient calculations and hence train the quantum circuit faster, using around 1-2 minutes per iteration.

  * [**Hydrogen geometry with VQE**](examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb)

    In this tutorial, we see how PennyLane and Amazon Braket can be combined to solve an important problem in quantum chemistry. The ground state energy of molecular hydrogen is calculated by optimizing a VQE circuit using the local Braket simulator. This tutorial highlights how qubit-wise commuting observables can be measured together in PennyLane and Braket, making optimization more efficient.

---
## <a name="braket">Amazon Braket features</a>
This folder contains examples that illustrate the usage of individual features of Amazon Braket

* [**Getting notifications when a task completes**](examples/braket_features/Getting_notifications_when_a_task_completes/Getting_notifications_when_a_task_completes.ipynb)

    This tutorial illustrates how Amazon Braket integrates with Amazon EventBridge for event-based processing. In the tutorial, you will learn how to configure Amazon Braket and Amazon Eventbridge to receive text notification about task completions on your phone. Of course, EventBridge also allows you to build full, event-driven applications based on events emitted by Amazon Braket.

* [**Allocating Qubits on QPU Devices**](examples/braket_features/Allocating_Qubits_on_QPU_Devices.ipynb)

    This tutorial explains how you can use the Amazon Braket SDK to allocate the qubit selection for your circuits manually, when running on QPUs.

* [**Getting Devices and Checking Device Properties**](examples/braket_features/Getting_Devices_and_Checking_Device_Properties.ipynb)

    This example shows how to interact with the Amazon Braket GetDevice API to retrieve Amazon Braket devices (such as simulators and QPUs) programmatically, and how to gain access to their properties.

* [**Using the tensor network simulator TN1**](examples/braket_features/Using_the_tensor_network_simulator_TN1.ipynb)

    This notebook introduces the Amazon Braket on-demand tensor network simulator, TN1. You will learn about how TN1 works, how to use it, and which problems are best suited to run on TN1.

* [**Simulating noise on Amazon Braket**](examples/braket_features/Simulating_Noise_On_Amazon_Braket.ipynb)

    This notebook provides a detailed overview of noise simulation on Amazon Braket. You will learn how to define noise channels, apply noise to new or existing circuits, and run those circuits on the Amazon Braket noise simulators.

---
## <a name="jobs">Amazon Braket Hybrid Jobs</a>
This folder contains examples that illustrate the use of Amazon Braket Hybrid Jobs (Braket Jobs for short).

* [**Getting started with Amazon Braket Hybrid Jobs**](examples/hybrid_jobs/0_Creating_your_first_Hybrid_Job/Creating_your_first_Hybrid_Job.ipynb)

    This notebook provides a demonstration of running a simple Braket Job. You will learn how to create a Braket Job using the Braket SDK or the Braket console, how to set the output S3 folder for a job, and how to retrieve results. You will also learn how to specify the Braket device to run your job on simulators or QPUs. Finally, you will learn how to use local mode to quickly debug your code.

* [**Quantum machine learning in Amazon Braket Hybrid Jobs**](examples/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs/Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb)

    This notebook shows a typical quantum machine learning workflow using Braket Jobs. In the process, you will learn how to upload input data, how to set up hyperparameters for your job, and how to retrieve and plot metrics. Finally, you will see how to run multiple Braket Jobs in parallel with different sets of hyperparameters.

* [**QAOA with Amazon Braket Hybrid Jobs and PennyLane**](examples/hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs/Using_PennyLane_with_Braket_Jobs.ipynb)

    This notebook shows how to run the QAOA algorithm with PennyLane (similar to a [previous notebook](examples/pennylane/2_Graph_optimization_with_QAOA.ipynb)), but this time using Braket Jobs. In the process, you will learn how to select a container image that supports PennyLane, and how to use checkpoints to save and load training progress of a job.

* [**Bring your own containers to Braket Jobs**](examples/hybrid_jobs/3_Bring_your_own_container/bring_your_own_container.ipynb)

    This notebook demonstrates the use of the Bring-Your-Own-Container (BYOC) functionality of Braket Jobs. While Amazon Braket has pre-configured environments which support most use cases of Braket Jobs, BYOC enables you to define fully customizable environments using Docker containers. You will learn how to use BYOC, including preparing a Dockerfile, creating a private Amazon Elastic Container Registry (ECR), building the container, and submitting a Braket Job using the custom container.
    
---
## <a name="jobs">Photonic quantum computing with Strawberry Fields</a>
This folder contains examples that illustrate the use of Strawberry Fields to run photonic quantum circuits on both Strawberry Field's built-in local simulators and Xanadu's Borealis device. These examples are based on existing tutorials on the [Strawberry Fields website](https://strawberryfields.ai/photonics/demonstrations.html).

* [**Borealis Quickstart**](examples/photonics/Borealis_quickstart.ipynb)

    This notebook provides a demonstration of running a circuit on Xanadu's Borealis device. Through the use of helper functions, you will learn how to generate random [Gaussian Boson Sampling](examples/photonics/2_Gaussian_boson_sampling_and_the_Hafnian.ipynb) (GBS) circuits closely resembling the circuits used in Xanadu's quantum advantage experiment, and submit them to Borealis via the [Amazon Braket Strawberry Fields plugin](https://github.com/aws/amazon-braket-strawberryfields-plugin-python). For more details, see the [Borealis beginner tutorial](examples/photonics/4_Operating_Borealis_beginner_tutorial.ipynb) and other introductory tutorials to Strawberry Fields. 

* [**Introduction to Blackbird**](examples/photonics/0_Introduction_to_Blackbird.ipynb)

    This notebook introduces Blackbird, an open source programming language for expressing photonic quantum circuits. Blackbird is built into, and used by, Strawberry Fields. You will learn how to create simple circuits in Blackbird.

* [**Basic tutorial: quantum teleportation**](examples/photonics/1_Basic_tutorial_quantum_teleportation.ipynb)

    In this notebook, you will learn how to write a continuous-variable program in Strawberry Fields end-to-end by studying the problem of quantum teleportation, and execute the program on a Strawberry Fields built-in local simulator.

* [**Gaussian boson sampling**](examples/photonics/2_Gaussian_boson_sampling_and_the_Hafnian.ipynb)

    This notebook explains the problem of Gaussian boson sampling (GBS), the computational problem that the Borealis quantum computer solves, and explains why it is believed to be difficult to simulate classically. You will construct a small GBS circuit, execute it on a local simulator, and compare the results to theoretically expected values.
    
* [**Time-domain multiplexing**](examples/photonics/3_Time_domain_photonic_circuits.ipynb)

    This notebook introduces the concept of time-domain multiplexing (TDM), a technique for creating large entangled quantum systems in a limited size photonic quantum computer by sending the qumodes at different times. You will learn the basic ideas of TDM, construct a small TDM program, and execute it on a built-in local simulator.
    
* [**Operating Borealis: beginner tutorial**](examples/photonics/4_Operating_Borealis_beginner_tutorial.ipynb)

    In this example, you will learn how to create and run circuits on Borealis. You will learn how to write a time-domain program for Borealis and specify the gate parameters to customize your own GBS experiment. You will learn how to run GBS circuits on Borealis via the [Amazon Braket Strawberry Fields plugin](https://github.com/aws/amazon-braket-strawberryfields-plugin-python). Finally, you will learn how to do basic analysis to compare the experimental results with theory.

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
