# Amazon Braket resources organized by topic
The publicly available Amazon Braket notebooks and blogposts are arranged below by subject headings. The arrangement of the topics is not prescriptive but is meant to be reflective of what is encountered in standard courses and textbooks on quantum computing and quantum information science.  Note that many of the notebooks and blogposts appear under multiple headings.

Within each subtopic, the relevant Jupyter notebooks are linked. Relevant Quantum Technology blogposts are included in brackets. 
* * *

## Outline

* [Quantum concepts](#concepts)
* [Quantum technology](#technology)
* [Quantum noise](#noise)
* [Quantum algorithms](#algorithms)
    * [Variational quantum algorithms](#variational)
* [Quantum simulation](#simulation)
* [Amazon Braket usage](#usage)

* * *

## <a name="concepts">Quantum concepts</a>

#### Entanglement

* [Bell's inequality](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Bells_Inequality.ipynb)
* [CHSH inequality](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/CHSH_Inequality.ipynb)
* [Preparing a GHZ state and running the circuit on simulators](modules/Getting_Started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb) 

#### Quantum communication

* [Superdense coding](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Superdense_coding/Superdense_coding.ipynb) 
* {[An illustrated introduction to quantum networks and quantum repeaters | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/an-illustrated-introduction-to-quantum-networks-and-quantum-repeaters/)}
* {[Perfect imperfections: how AWS is innovating on diamond materials for quantum communication with element six | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/perfect-imperfections-how-aws-is-innovating-on-diamond-materials-for-quantum-communication-with-element-six/)}

#### Models of quantum computation

* [Anatomy of quantum circuits and quantum tasks in Amazon Braket](modules/Getting_Started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb)
* [Quantum walk](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Walk.ipynb)
* [Introduction of analog Hamiltonian simulation with Rydberg atoms](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb)

#### Single qubit gates

* [Build single qubit gates](modules/Continue_Exploring/quantum_hardware/pulse_control/4_Build_single_qubit_gates.ipynb)

#### Noise in quantum systems

* [Simulation of noisy quantum circuits on Amazon Braket with PennyLane](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb)
* [Noise models on Amazon Braket](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Amazon_Braket.ipynb)
* [Robust randomness generation on quantum processing units](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Randomness/Randomness_Generation.ipynb)
* {[Noise in quantum computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* {[Bernoulli line and the Bloch sphere: visualizing probability and quantum states | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}
* {[Generating quantum randomness with Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/generating-quantum-randomness-with-amazon-braket/)}

## <a name="technology">Quantum technology</a>

#### Analog quantum technology

* [Introduction of analog Hamiltonian simulation with Rydberg atoms](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb)
* [Introduction to Aquila](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/01_Introduction_to_Aquila.ipynb)
* [Ordered phases in Rydberg systems](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb)
* [Parallel tasks on Aquila](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/03_Parallel_tasks_on_Aquila.ipynb)
* [Maximum independent sets with analog Hamiltonian simulation](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb)
* [Running analog Hamiltonian simulation with local simulator](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb)

#### Getting properties of devices

* [Anatomy of quantum circuits and quantum tasks in Amazon Braket](modules/Getting_Started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb)
* [Getting devices and checking device properties](modules/Getting_Started/4_Getting_Devices_and_Checking_Device_Properties/4_Getting_Devices_and_Checking_Device_Properties.ipynb)

#### Noise in quantum devices

* {[Bernoulli line and the Bloch sphere: visualizing probability and quantum states | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}
* {[Noise in quantum computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* [Error mitigation on Amazon Braket](modules/Continue_Exploring/quantum_hardware/error_mitigation/Error_Mitigation_on_Amazon_Braket.ipynb)
* [Noise models on Rigetti](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Rigetti.ipynb)
* {[Amazon Braket launches IonQ Aria with built-in error mitigation | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-ionq-aria-with-built-in-error-mitigation/)}
* {[Suppressing errors with dynamical decoupling using pulse control on Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/suppressing-errors-with-dynamical-decoupling-using-pulse-control-on-amazon-braket/)}

#### Running quantum circuits

* [Running quantum circuits on QPU devices](modules/Getting_Started/2_Running_quantum_circuits_on_QPU_devices/)

#### Pulse control and entanglement generation

* {[Amazon Braket launches Braket Pulse to develop quantum programs at the pulse level | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-braket-pulse-to-develop-quantum-programs-at-the-pulse-level/)}
* [Bringup Experiments](modules/Continue_Exploring/quantum_hardware/pulse_control/1_Bringup_experiments.ipynb)
* [Creating a Bell state with cross-resonance pulses on OQC's Lucy](modules/Continue_Exploring/quantum_hardware/pulse_control/2_Bell_pair_with_pulses_OQC.ipynb)
* [Creating a Bell state with pulses on Rigetti's Aspen M-3](modules/Continue_Exploring/quantum_hardware/pulse_control/3_Bell_pair_with_pulses_Rigetti.ipynb)
* {[Suppressing errors with dynamical decoupling using pulse control on Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/suppressing-errors-with-dynamical-decoupling-using-pulse-control-on-amazon-braket/)}

## <a name="noise">Quantum noise</a>

#### Noise mitigation

* [Error mitigation on Amazon Braket](modules/Continue_Exploring/quantum_hardware/error_mitigation/Error_Mitigation_on_Amazon_Braket.ipynb)
* {[Exploring quantum error mitigation with Mitiq and Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/exploring-quantum-error-mitigation-with-mitiq-and-amazon-braket/)}
* {[Amazon Braket launches IonQ Aria with built-in error mitigation | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-ionq-aria-with-built-in-error-mitigation/)}

#### Noise in quantum devices

* [Noise models on Amazon Braket](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Amazon_Braket.ipynb)
* [Noise models on Rigetti](modules/Continue_Exploring/quantum_sims/noise_simulations/Noise_models_on_Rigetti.ipynb)
* {[Noise in quantum computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* {[Bernoulli line and the Bloch sphere: visualizing probability and quantum states | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}

#### Simulating quantum noise

* [Simulating noise on Amazon Braket](modules/Continue_Exploring/quantum_sims/noise_simulations/Simulating_Noise_On_Amazon_Braket.ipynb)
* [Simulation of noisy quantum circuits on Amazon Braket with PennyLane](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb)
* {[Noise in quantum computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* {[Bernoulli line and the Bloch sphere: visualizing probability and quantum states | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}

#### Quantum error correction

* {[Quantum error correction in the presence of biased noise | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/quantum-error-correction-in-the-presence-of-biased-noise/)}

## <a name="algorithms">Quantum algorithms</a>

* {[Introducing the Amazon Braket Algorithm Library | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/introducing-the-amazon-braket-algorithm-library/)}
* {[Introducing Amazon Braket Hybrid Jobs | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/aws/introducing-amazon-braket-hybrid-jobs-set-up-monitor-and-efficiently-run-hybrid-quantum-classical-workloads/)}

#### Toy algorithms

* [Deutsch-Jozsa algorithm](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Deutsch_Jozsa_Algorithm.ipynb)
* [Simon's algorithm](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Simons_Algorithm/Simons_Algorithm.ipynb)
* [Simon's algorithm (implementation)](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Simons_Algorithm.ipynb)
* {[Exploring Simon’s Algorithm with Daniel Simon | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/simons-algorithm/)}
* [Bernstein-Vazirani algorithm](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Bernstein_Vazirani_Algorithm.ipynb)

#### Phase estimation algorithms

* [Quantum phase estimation](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Phase_Estimation/Quantum_Phase_Estimation.ipynb)
* [Quantum phase estimation algorithm](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Phase_Estimation_Algorithm.ipynb)
* [Quantum Fourier transform](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Fourier_Transform/Quantum_Fourier_Transform.ipynb)
* [Quantum Fourier transform (implementation)](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Fourier_Transform.ipynb)
* [Shor's algorithm](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Shors_Algorithm.ipynb)

#### Grover type algorithms

* [Grover](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Grover/Grover.ipynb)
* [Grover's search](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Grovers_Search.ipynb)
* [Quantum amplitude amplification](modules/Continue_Exploring/quantum_algorithms_and_protocols/canonical/Quantum_Amplitude_Amplification/Quantum_Amplitude_Amplification.ipynb)
* {[Solving SAT problems with the Classiq platform on Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/solving-sat-problems-with-the-classiq-platform-on-amazon-braket/)}

### <a name="variational">Variational quantum algorithms</a>

* {[Introducing Amazon Braket Hybrid Jobs | AWS News Blog](https://aws.amazon.com/blogs/aws/introducing-amazon-braket-hybrid-jobs-set-up-monitor-and-efficiently-run-hybrid-quantum-classical-workloads/)}

#### QAOA

* [Quantum approximate optimization algorithm (QAOA)](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/QAOA/QAOA_braket.ipynb)
* [QAOA with Amazon Braket Hybrid Jobs and PennyLane](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs/Using_PennyLane_with_Braket_Jobs.ipynb)
* [Graph optimization with QAOA](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/2_Graph_optimization_with_QAOA/)
* [Benchmarking QN-SPSA optimizer with Amazon Braket Hybrid Jobs and embedded simulators](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator/qnspsa_with_embedded_simulator.ipynb)

#### Ansatze optimization

* [H2 example with UCC](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Chemistry/VQE_chemistry_braket.ipynb)
* [Hydrogen molecule geometry with VQE](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb)
* [Solving the transverse Ising model with VQE](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb)

#### Computing gradients for VQA

* [Computing gradients in parallel with PennyLane-Braket](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/1_Parallelized_optimization_of_quantum_circuits/1_Parallelized_optimization_of_quantum_circuits.ipynb)
* [Using the 'AdjointGradient' result type on Amazon Braket](modules/Continue_Exploring/quantum_sims/Using_The_Adjoint_Gradient_Result_Type.ipynb)
* [Adjoint gradient computation with PennyLane and Amazon Braket](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/6_Adjoint_gradient_computation/6_Adjoint_gradient_computation.ipynb)

#### Quantum machine learning

* [Quantum machine learning in Amazon Braket Hybrid Jobs](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs/Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb)
* [Quantum circuit Born machine](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Circuit_Born_Machine.ipynb)
* [Parallelize training for quantum machine learning](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb)

#### Optimization using Rydberg atom-based quantum processor

* [Maximum independent sets with analog Hamiltonian simulation](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb)
* {[Combinatorial optimization with physics-inspired graph neural networks | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/combinatorial-optimization-with-physics-inspired-graph-neural-networks/)}

## <a name="simulation">Quantum simulation</a>n

#### Simulating chemistry

* [H2 example with UCC](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Chemistry/VQE_chemistry_braket.ipynb)
* [Hydrogen molecule geometry with VQE](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb)
* [Quantum computing quantum Monte Carlo](modules/Continue_Exploring/quantum_algorithms_and_protocols/algorithm_implementations/Quantum_Computing_Quantum_Monte_Carlo.ipynb)
* {[Exploring quantum chemistry applications with Tangelo and QEMIST Cloud using Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/exploring-quantum-chemistry-applications-with-tangelo-and-qemist-cloud-using-amazon-braket/)}
* {[Quantum chemistry with Qu&Co’s (now Pasqal) QUBEC on Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/quantum-chemistry-with-qucos-qubec-on-amazon-braket/)}
* {[Exploring computational chemistry using Quantinuum’s InQuanto on AWS | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/exploring-computational-chemistry-using-quantinuums-inquanto-on-aws/)}
* {[Running quantum chemistry calculations using AWS ParallelCluster | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/running-quantum-chemistry-calculations-using-aws-parallelcluster/)}

#### Simulating magnetism

* [Solving the transverse Ising model with VQE](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb)

#### Simulating condensed matter 

* [Ordered phases in Rydberg systems](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb)
* {[Realizing quantum spin liquid phase on an analog Hamiltonian Rydberg simulator | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/realizing-quantum-spin-liquid-phase-on-an-analog-hamiltonian-rydberg-simulator/)}

## <a name="usage">Amazon Braket usage</a>n

#### Getting started with Amazon Braket

* [Getting started with Amazon Braket](modules/Getting_Started/0_Getting_started/0_Getting_started.ipynb)
* {[Setting up your local development environment in Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/setting-up-your-local-development-environment-in-amazon-braket/)}
* *Cost controls*
    * {[Introducing a cost control solution for Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/introducing-a-cost-control-solution-for-amazon-braket/)}
    * https://github.com/aws-samples/cost-control-for-amazon-braket 
    * {[Managing the cost of your experiments in Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/managing-the-cost-of-your-experiments-in-amazon-braket/)}

#### Building circuits, tasks, and jobs on Amazon Braket

* [Anatomy of Quantum Circuits and Quantum Tasks in Amazon Braket](modules/Getting_Started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb)
* [Getting Started with OpenQASM on Braket](modules/Continue_Exploring/quantum_hardware/compilation/Getting_Started_with_OpenQASM_on_Braket.ipynb) 
* {[AWS open-sources OQpy to make it easier to write quantum programs in OpenQASM 3 | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/aws-open-sources-oqpy-to-make-it-easier-to-write-quantum-programs-in-openqasm-3/)}
* [Combining PennyLane with Amazon Braket](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/0_Getting_started/0_Getting_started.ipynb) 
* {[Creating a bridge between machine learning and quantum computing with PennyLane](https://aws.amazon.com/blogs/opensource/creating-a-bridge-between-machine-learning-and-quantum-computing-with-pennylane/)}
* [How to run Qiskit on Amazon Braket](modules/Continue_Exploring/quantum_frameworks_and_plugins/qiskit/0_Getting_Started.ipynb)
* {[Introducing the Qiskit provider for Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/introducing-the-qiskit-provider-for-amazon-braket/)}
* *Hybrid jobs feature*
    * {[Introducing Amazon Braket Hybrid Jobs | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/aws/introducing-amazon-braket-hybrid-jobs-set-up-monitor-and-efficiently-run-hybrid-quantum-classical-workloads/)}
    * [Getting started with Amazon Braket Hybrid Jobs](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/0_Creating_your_first_Hybrid_Job/Creating_your_first_Hybrid_Job.ipynb)
    * [Bring your own containers to Braket Jobs](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/3_Bring_your_own_container/bring_your_own_container.ipynb)
    * [Parallelize training for quantum machine learning](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb)

#### Testing with simulators

* [Running analog Hamiltonian simulation with local simulator](modules/Continue_Exploring/quantum_hardware/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb)
* [Simulating advanced OpenQASM programs with the local simulator](modules/Continue_Exploring/quantum_hardware/compilation/Simulating_Advanced_OpenQASM_Programs_with_the_Local_Simulator.ipynb)
* [Using the Amazon Braket tensor network simulator TN1](modules/Continue_Exploring/quantum_sims/Using_the_tensor_network_simulator_TN1.ipynb)
* *Hybrid jobs feature*
    * [Embedded simulators in Braket Jobs](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/4_Embedded_simulators_in_Braket_Jobs/Embedded_simulators_in_Braket_Jobs.ipynb)
    * [Running notebooks as hybrid jobs with Amazon Braket](modules/Continue_Exploring/quantum_algorithms_and_protocols/variational/hybrid_jobs/7_Running_notebooks_as_jobs/Running_notebooks_as_jobs.ipynb)
    * {[Running Jupyter notebooks as hybrid jobs with Amazon Braket | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/running-jupyter-notebooks-as-hybrid-jobs-with-amazon-braket/)}

#### Running on QPUs

* [Allocating qubits on QPU devices](modules/Continue_Exploring/quantum_hardware/Allocating_Qubits_on_QPU_Devices.ipynb)
* [Verbatim compilation](modules/Continue_Exploring/quantum_hardware/compilation/Verbatim_Compilation.ipynb)
* [Getting Devices and Checking Device Properties](modules/Getting_Started/4_Getting_Devices_and_Checking_Device_Properties/4_Getting_Devices_and_Checking_Device_Properties.ipynb)
* *Braket Pulse*
    * [Bringup experiments](modules/Continue_Exploring/quantum_hardware/pulse_control/1_Bringup_experiments.ipynb) 
    * [Construct single qubit quantum gates](modules/Continue_Exploring/quantum_hardware/pulse_control/4_Build_single_qubit_gates.ipynb)
    * {[Amazon Braket launches Braket Pulse to develop quantum programs at the pulse level | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-braket-pulse-to-develop-quantum-programs-at-the-pulse-level/)}

#### Analyzing results

* [Getting notifications when a task completes](modules/Continue_Exploring/advanced_braket_features/Getting_notifications_when_a_task_completes/Getting_notifications_when_a_task_completes.ipynb)
* [Tracking resource usage with PennyLane device tracker](modules/Continue_Exploring/quantum_frameworks_and_plugins/pennylane/5_Tracking_resource_usage/5_Tracking_resource_usage.ipynb)