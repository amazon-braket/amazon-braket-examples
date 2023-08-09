# Amazon Braket resources organized by topic

Below we have arranged the publicly available Amazon Braket notebooks and blogposts by subject headings. The arrangement of the topics is not prescriptive but is meant to be reflective of what is encountered in standard courses and textbooks on quantum computing and quantum information science.  Note that many of the notebooks and blogposts appear under multiple headings.

Within each subtopic, we have linked the Jupyter notebook and, in parenthesis, the GitHub parent folder for each notebook. Relevant Quantum Technology blogposts are included in brackets. 
* * *

## Outline

* [Quantum concepts](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHR5e42b1f8a8da44368a9eb19e2)
* [Quantum technology](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHR41e806fe1bc142fdb9a385a6f)
* [Quantum noise](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHRf2cd51dfa6894f4db99878755)
* [Quantum algorithms](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHRd259cbb06d3e444098822ad73)
    * [Variational quantum algorithms](https://quip-amazon.com/IxxiAaiaVjwQ#temp:C:eHReaa761d5ef9142d0aef0590ac)
* [Quantum simulation](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHR185b4bdc09124eef9c2e25d05)
* [Amazon Braket usage](https://quip-amazon.com/IxxiAaiaVjwQ/Amazon-Braket-resources-organized-by-topic#temp:C:eHR8c52f18025fc4b8f9d6d275fb)

* * *

## Quantum concepts

#### Entanglement

* [Bells_Inequality](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Bells_Inequality.ipynb) ([Braket algorithms](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [CHSH_Inequality](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/CHSH_Inequality.ipynb) ([Braket algorithms](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [Preparing a GHZ state and running the circuit on simulators](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/1_Running_quantum_circuits_on_simulators/1_Running_quantum_circuits_on_simulators.ipynb) ([***_getting_started/1_Running_quantum_circuits_on_simulators_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/1_Running_quantum_circuits_on_simulators))

#### Quantum communication

* [Superdense Coding](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/4_Superdense_coding/4_Superdense_coding.ipynb) ([***getting_started/4_Superdense_coding***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/4_Superdense_coding))
* {[An Illustrated Introduction to Quantum Networks and Quantum Repeaters...](https://aws.amazon.com/blogs/quantum-computing/an-illustrated-introduction-to-quantum-networks-and-quantum-repeaters/)}
* {[Perfect imperfections: how AWS is innovating on diamond materials for...](https://aws.amazon.com/blogs/quantum-computing/perfect-imperfections-how-aws-is-innovating-on-diamond-materials-for-quantum-communication-with-element-six/)}

#### Models of quantum computation

* [Anatomy of Quantum Circuits and Quantum Tasks in Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb) ([***getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits))
* [Quantum_Walk](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Quantum_Walk.ipynb) ([Braket algorithms](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb) ([***_analog_hamiltonian_simulation_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))

#### Single qubit gates

* [Construct single qubit quantum gates](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/4_Build_single_qubit_gates.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control))

#### Noise in quantum systems

* [Randomness](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Randomness) ([***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms)) {[Bernoulli line and the Bloch sphere: visualizing probability and quant...](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}
* [Noise models on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Noise_models/Noise_models_on_Amazon_Braket.ipynb) ([***braket_features/Noise_models***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features/Noise_models)) {[Noise in Quantum Computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* [Simulation of noisy quantum circuits on Amazon Braket with PennyLane](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb) ([***pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane))

## Quantum technology

#### Analog quantum technology

* [00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/00_Introduction_of_Analog_Hamiltonian_Simulation_with_Rydberg_Atoms.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [01_Introduction_to_Aquila](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/01_Introduction_to_Aquila.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [02_Ordered_phases_in_Rydberg_systems](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [03_Parallel_tasks_on_Aquila](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/03_Parallel_tasks_on_Aquila.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [05_Running_Analog_Hamiltonian_Simulation_with_local_simulator](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb) ([***analog_hamiltonian_simulation)***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation)

#### Getting properties of devices

* [Anatomy of Quantum Circuits and Quantum Tasks in Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb) ([***getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits))
* [Getting Devices and Checking Device Properties](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Getting_Devices_and_Checking_Device_Properties.ipynb) ([braket_features](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))

#### Noise in quantum devices

* {[Bernoulli line and the Bloch sphere: visualizing probability and quant...](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}
* {[Noise in Quantum Computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* [Error mitigation on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Error_Mitigation_on_Amazon_Braket.ipynb) ([braket_features](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Noise models on Rigetti](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Noise_models/Noise_models_on_Rigetti.ipynb) ([***braket_features/Noise_models***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features/Noise_models))
* {[Amazon Braket launches IonQ Aria with built-in error mitigation | AWS...](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-ionq-aria-with-built-in-error-mitigation/)}
* {[Suppressing errors with dynamical decoupling using pulse control on Am...](https://aws.amazon.com/blogs/quantum-computing/suppressing-errors-with-dynamical-decoupling-using-pulse-control-on-amazon-braket/)}

#### Running quantum circuits

* [Running quantum circuits on QPU devices](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/2_Running_quantum_circuits_on_QPU_devices/2_Running_quantum_circuits_on_QPU_devices.ipynb) ([***getting_started/2_Running_quantum_circuits_on_QPU_devices***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/2_Running_quantum_circuits_on_QPU_devices))

#### Pulse control and entanglement generation

* {[Amazon Braket launches Braket Pulse to develop quantum programs at the...](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-braket-pulse-to-develop-quantum-programs-at-the-pulse-level/)}
* [Bringup Experiments](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/1_Bringup_experiments.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control)) 
* [Creating a Bell state with cross-resonance pulses on OQC's Lucy](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/2_Bell_pair_with_pulses_OQC.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control))
* [Creating a Bell state with pulses on Rigetti's Aspen M-3](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/3_Bell_pair_with_pulses_Rigetti.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control))
* {[Suppressing errors with dynamical decoupling using pulse control on Am...](https://aws.amazon.com/blogs/quantum-computing/suppressing-errors-with-dynamical-decoupling-using-pulse-control-on-amazon-braket/)}

## Quantum noise

#### Noise mitigation

* [Error mitigation on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Error_Mitigation_on_Amazon_Braket.ipynb) ([braket_features](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* {[Exploring quantum error mitigation with Mitiq and Amazon Braket | AWS...](https://aws.amazon.com/blogs/quantum-computing/exploring-quantum-error-mitigation-with-mitiq-and-amazon-braket/)}
* {[Amazon Braket launches IonQ Aria with built-in error mitigation | AWS...](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-ionq-aria-with-built-in-error-mitigation/)}

#### Noise in quantum devices

* [Noise models on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Noise_models/Noise_models_on_Amazon_Braket.ipynb) ([***braket_features/Noise_models***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features/Noise_models))
* [Noise models on Rigetti](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Noise_models/Noise_models_on_Rigetti.ipynb) ([***braket_features/Noise_models***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features/Noise_models))
* {[Noise in Quantum Computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* {[Bernoulli line and the Bloch sphere: visualizing probability and quant...](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}

#### Simulating quantum noise

* [Simulating noise on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Simulating_Noise_On_Amazon_Braket.ipynb) ([braket_features](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Simulation of noisy quantum circuits on Amazon Braket with PennyLane](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb) ([***pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane))
* {[Noise in Quantum Computing | AWS Quantum Technologies Blog](https://aws.amazon.com/blogs/quantum-computing/noise-in-quantum-computing/)}
* {[Bernoulli line and the Bloch sphere: visualizing probability and quant...](https://aws.amazon.com/blogs/quantum-computing/bernoulli-line-and-the-bloch-sphere/)}

#### Quantum error correction

* {[Quantum error correction in the presence of biased noise | AWS Quantum...](https://aws.amazon.com/blogs/quantum-computing/quantum-error-correction-in-the-presence-of-biased-noise/)}

## Quantum Algorithms

* {[Introducing the Amazon Braket Algorithm Library | AWS Quantum Technolo...](https://aws.amazon.com/blogs/quantum-computing/introducing-the-amazon-braket-algorithm-library/)}

#### Toy algorithms

* [Deutsch_Jozsa_Algorithm](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Deutsch_Jozsa_Algorithm.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [Simons_Algorithm](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Simons_Algorithm.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook)) {[Exploring Simon’s Algorithm with Daniel Simon | AWS Quantum Technologi...](https://aws.amazon.com/blogs/quantum-computing/simons-algorithm/)}
* [_Simons_Algorithm_](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Simons_Algorithm) ([***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms)) {[Exploring Simon’s Algorithm with Daniel Simon | AWS Quantum Technologi...](https://aws.amazon.com/blogs/quantum-computing/simons-algorithm/)}
* [_Bernstein_Vazirani_Algorithm_](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Bernstein_Vazirani_Algorithm.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))

#### Phase estimation algorithms

* [Quantum_Phase_Estimation_Algorithm](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Quantum_Phase_Estimation_Algorithm.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [_Quantum_Phase_Estimation_](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Quantum_Phase_Estimation) _(_[***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms)_)_
* [_Quantum_Fourier_Transform_](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Quantum_Fourier_Transform.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [Quantum_Fourier_Transform](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Quantum_Fourier_Transform) ([***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms))
* [Shors_Algorithm](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Shors_Algorithm.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))

#### Grover type algorithms

* [Grovers_Search](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Grovers_Search.ipynb) ([***Braket algorithms***](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [Grover](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Grover) ([***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms))
* [Quantum_Amplitude_Amplification](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms/Quantum_Amplitude_Amplification) ([***_advanced_circuits_algorithms_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/advanced_circuits_algorithms))
* {[Solving SAT problems with the Classiq platform on Amazon Braket | AWS...](https://aws.amazon.com/blogs/quantum-computing/solving-sat-problems-with-the-classiq-platform-on-amazon-braket/)}

### Variational quantum algorithms

#### QAOA

* [QUANTUM APPROXIMATE OPTIMIZATION ALGORITHM (QAOA)](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_quantum_algorithms/QAOA/QAOA_braket.ipynb) ([***hybrid_quantum_algorithms/QAOA***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_quantum_algorithms/QAOA))
* [QAOA with Amazon Braket Hybrid Jobs and PennyLane](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs/Using_PennyLane_with_Braket_Jobs.ipynb) ([***hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/2_Using_PennyLane_with_Braket_Jobs))
* [Graph optimization with QAOA](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/2_Graph_optimization_with_QAOA/2_Graph_optimization_with_QAOA.ipynb) ([***pennylane/2_Graph_optimization_with_QAOA***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/2_Graph_optimization_with_QAOA))
* [Benchmarking QN-SPSA optimizer with Amazon Braket Hybrid Jobs and embedded simulators](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator/qnspsa_with_embedded_simulator.ipynb) ([***_hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/6_QNSPSA_optimizer_with_embedded_simulator))

#### Ansatze optimization

* [H2 example with UCC](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_quantum_algorithms/VQE_Chemistry/VQE_chemistry_braket.ipynb) ([***_hybrid_quantum_algorithms/VQE_Chemistry_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_quantum_algorithms/VQE_Chemistry))
* [Hydrogen Molecule geometry with VQE](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb) ([***pennylane/3_Hydrogen_Molecule_geometry_with_VQE***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE))
* [SOLVING THE TRANSVERSE ISING MODEL WITH VQE](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_quantum_algorithms/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb) ([***_hybrid_quantum_algorithms/VQE_Transverse_Ising_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_quantum_algorithms/VQE_Transverse_Ising))

#### Computing gradients for VQA

* [Computing gradients in parallel with PennyLane-Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/1_Parallelized_optimization_of_quantum_circuits/1_Parallelized_optimization_of_quantum_circuits.ipynb) ([***pennylane/1_Parallelized_optimization_of_quantum_circuits***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/1_Parallelized_optimization_of_quantum_circuits))
* [Using the Adjoint Gradient Result Type on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Using_The_Adjoint_Gradient_Result_Type.ipynb) ([braket_features](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Adjoint gradient computation with PennyLane and Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/6_Adjoint_gradient_computation/6_Adjoint_gradient_computation.ipynb) ([***_pennylane/6_Adjoint_gradient_computation_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/6_Adjoint_gradient_computation))

#### Quantum machine learning

* [Quantum machine learning in Amazon Braket Hybrid Jobs](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs/Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb) ([***hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/1_Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs))
* [Quantum_Circuit_Born_Machine](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/textbook/Quantum_Circuit_Born_Machine.ipynb) ([Braket algorithms](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/textbook))
* [Parallelize training for Quantum machine learning](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb) ([***_hybrid_jobs/5_Parallelize_training_for_QML_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/5_Parallelize_training_for_QML))

#### Optimization using Rydberg atom-based quantum processor

* [04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb) ([***_analog_hamiltonian_simulation_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation)) {[Optimization with a Rydberg atom-based quantum processor | AWS Quantum...](https://aws.amazon.com/blogs/quantum-computing/optimization-with-rydberg-atom-based-quantum-processor/)}
* {[Combinatorial Optimization with Physics-Inspired Graph Neural Networks...](https://aws.amazon.com/blogs/quantum-computing/combinatorial-optimization-with-physics-inspired-graph-neural-networks/)}

## Quantum simulation

#### Simulating chemistry

* [H2 example with UCC](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_quantum_algorithms/VQE_Chemistry/VQE_chemistry_braket.ipynb) ([***_hybrid_quantum_algorithms/VQE_Chemistry_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_quantum_algorithms/VQE_Chemistry))
* [Hydrogen Molecule geometry with VQE](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE/3_Hydrogen_Molecule_geometry_with_VQE.ipynb) ([***pennylane/3_Hydrogen_Molecule_geometry_with_VQE***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/3_Hydrogen_Molecule_geometry_with_VQE))
* [Quantum_Computing_Quantum_Monte_Carlo](https://github.com/aws-samples/amazon-braket-algorithm-library/blob/main/notebooks/advanced_algorithms/Quantum_Computing_Quantum_Monte_Carlo.ipynb) ([advanced_algorithms](https://github.com/aws-samples/amazon-braket-algorithm-library/tree/main/notebooks/advanced_algorithms)) {[Quantum Monte Carlo on Quantum Computers | AWS Quantum Technologies Bl...](https://aws.amazon.com/blogs/quantum-computing/quantum-monte-carlo-on-quantum-computers/)}
* {[Exploring quantum chemistry applications with Tangelo and QEMIST Cloud...](https://aws.amazon.com/blogs/quantum-computing/exploring-quantum-chemistry-applications-with-tangelo-and-qemist-cloud-using-amazon-braket/)}
* {[Quantum Chemistry with Qu&Co’s (now Pasqal) QUBEC on Amazon Braket | A...](https://aws.amazon.com/blogs/quantum-computing/quantum-chemistry-with-qucos-qubec-on-amazon-braket/)}
* {[Exploring computational chemistry using Quantinuum’s InQuanto on AWS |...](https://aws.amazon.com/blogs/quantum-computing/exploring-computational-chemistry-using-quantinuums-inquanto-on-aws/)}
* {[Running quantum chemistry calculations using AWS ParallelCluster | AWS...](https://aws.amazon.com/blogs/quantum-computing/running-quantum-chemistry-calculations-using-aws-parallelcluster/)}

#### Simulating magnetism

* [SOLVING THE TRANSVERSE ISING MODEL WITH VQE](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_quantum_algorithms/VQE_Transverse_Ising/VQE_Transverse_Ising_Model.ipynb) ([***_hybrid_quantum_algorithms/VQE_Transverse_Ising_***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_quantum_algorithms/VQE_Transverse_Ising))

#### Simulating condensed matter 

* [02_Ordered_phases_in_Rydberg_systems](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/02_Ordered_phases_in_Rydberg_systems.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation)) 
* {[Realizing quantum spin liquid phase on an analog Hamiltonian Rydberg s...](https://aws.amazon.com/blogs/quantum-computing/realizing-quantum-spin-liquid-phase-on-an-analog-hamiltonian-rydberg-simulator/)}

## Amazon Braket usage

#### Getting started with Amazon Braket

* [Getting started with Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/0_Getting_started/0_Getting_started.ipynb) ([***getting_started/0_Getting_started***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/0_Getting_started))
* {[Setting up your local development environment in Amazon Braket | AWS Q...](https://aws.amazon.com/blogs/quantum-computing/setting-up-your-local-development-environment-in-amazon-braket/)}
* *Cost controls*
    * {[Introducing a cost control solution for Amazon Braket | AWS Quantum Te...](https://aws.amazon.com/blogs/quantum-computing/introducing-a-cost-control-solution-for-amazon-braket/)}
    * https://github.com/aws-samples/cost-control-for-amazon-braket 
    * {[Managing the cost of your experiments in Amazon Braket | AWS Quantum T...](https://aws.amazon.com/blogs/quantum-computing/managing-the-cost-of-your-experiments-in-amazon-braket/)}

#### Building circuits, tasks, and jobs on Amazon Braket

* [Anatomy of Quantum Circuits and Quantum Tasks in Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits/3_Deep_dive_into_the_anatomy_of_quantum_circuits.ipynb) ([***getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits***](https://github.com/aws/amazon-braket-examples/tree/main/examples/getting_started/3_Deep_dive_into_the_anatomy_of_quantum_circuits))
* [Getting Started with OpenQASM on Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Getting_Started_with_OpenQASM_on_Braket.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features)) {[AWS open-sources OQpy to make it easier to write quantum programs in O...](https://aws.amazon.com/blogs/quantum-computing/aws-open-sources-oqpy-to-make-it-easier-to-write-quantum-programs-in-openqasm-3/)}
* [Combining PennyLane with Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/0_Getting_started/0_Getting_started.ipynb) ([***pennylane/0_Getting_started***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/0_Getting_started)) {[Creating a bridge between machine learning and quantum computing with...](https://aws.amazon.com/blogs/opensource/creating-a-bridge-between-machine-learning-and-quantum-computing-with-pennylane/)}
* [How to run Qiskit on Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/qiskit/0_Getting_Started.ipynb) ([***qiskit***](https://github.com/aws/amazon-braket-examples/tree/main/examples/qiskit)) {[Introducing the Qiskit provider for Amazon Braket | AWS Quantum Techno...](https://aws.amazon.com/blogs/quantum-computing/introducing-the-qiskit-provider-for-amazon-braket/)}
* *Hybrid jobs feature*
    * [Getting started with Amazon Braket Hybrid Jobs](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/0_Creating_your_first_Hybrid_Job/Creating_your_first_Hybrid_Job.ipynb) ([hybrid_jobs/0_Creating_your_first_Hybrid_Job](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/0_Creating_your_first_Hybrid_Job))
    * [Bring your own containers to Braket Jobs](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/3_Bring_your_own_container/bring_your_own_container.ipynb) ([***hybrid_jobs/3_Bring_your_own_container***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/3_Bring_your_own_container))
    * [Parallelize training for Quantum machine learning](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/5_Parallelize_training_for_QML/Parallelize_training_for_QML.ipynb) ([***hybrid_jobs/5_Parallelize_training_for_QML***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/5_Parallelize_training_for_QML))

#### Testing with simulators

* [05_Running_Analog_Hamiltonian_Simulation_with_local_simulator](https://github.com/aws/amazon-braket-examples/blob/main/examples/analog_hamiltonian_simulation/05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb) ([***analog_hamiltonian_simulation***](https://github.com/aws/amazon-braket-examples/tree/main/examples/analog_hamiltonian_simulation))
* [Simulating Advanced OpenQASM Programs with the Local Simulator](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Simulating_Advanced_OpenQASM_Programs_with_the_Local_Simulator.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Using the Amazon Braket tensor network simulator TN1](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Using_the_tensor_network_simulator_TN1.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* *Hybrid jobs feature*
    * [Embedded simulators in Braket Jobs](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/4_Embedded_simulators_in_Braket_Jobs/Embedded_simulators_in_Braket_Jobs.ipynb) ([***hybrid_jobs/4_Embedded_simulators_in_Braket_Jobs***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/4_Embedded_simulators_in_Braket_Jobs))
    * [Running notebooks as hybrid jobs with Amazon Braket](https://github.com/aws/amazon-braket-examples/blob/main/examples/hybrid_jobs/7_Running_notebooks_as_jobs/Running_notebooks_as_jobs.ipynb) ([***hybrid_jobs/7_Running_notebooks_as_jobs***](https://github.com/aws/amazon-braket-examples/tree/main/examples/hybrid_jobs/7_Running_notebooks_as_jobs)) {[Running Jupyter notebooks as hybrid jobs with Amazon Braket | AWS Quan...](https://aws.amazon.com/blogs/quantum-computing/running-jupyter-notebooks-as-hybrid-jobs-with-amazon-braket/)}

#### Running on QPUs

* [Allocating Qubits on QPU Devices](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Allocating_Qubits_on_QPU_Devices.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Verbatim compilation](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Verbatim_Compilation.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* [Getting Devices and Checking Device Properties](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Getting_Devices_and_Checking_Device_Properties.ipynb) ([***braket_features***](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features))
* *Braket Pulse*
    * [Bringup Experiments](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/1_Bringup_experiments.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control)) {[Amazon Braket launches Braket Pulse to develop quantum programs at the...](https://aws.amazon.com/blogs/quantum-computing/amazon-braket-launches-braket-pulse-to-develop-quantum-programs-at-the-pulse-level/)}
    * [Construct single qubit quantum gates](https://github.com/aws/amazon-braket-examples/blob/main/examples/pulse_control/4_Build_single_qubit_gates.ipynb) ([pulse_control](https://github.com/aws/amazon-braket-examples/tree/main/examples/pulse_control))

#### Analyzing results

* [Getting notifications when a task completes](https://github.com/aws/amazon-braket-examples/blob/main/examples/braket_features/Getting_notifications_when_a_task_completes/Getting_notifications_when_a_task_completes.ipynb) ([**_braket_features_**](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features)**_/_**[**Getting_notifications_when_a_task_completes**](https://github.com/aws/amazon-braket-examples/tree/main/examples/braket_features/Getting_notifications_when_a_task_completes))
* [Tracking Resource Usage with PennyLane Device Tracker](https://github.com/aws/amazon-braket-examples/blob/main/examples/pennylane/5_Tracking_resource_usage/5_Tracking_resource_usage.ipynb) ([***pennylane/5_Tracking_resource_usage***](https://github.com/aws/amazon-braket-examples/tree/main/examples/pennylane/5_Tracking_resource_usage))