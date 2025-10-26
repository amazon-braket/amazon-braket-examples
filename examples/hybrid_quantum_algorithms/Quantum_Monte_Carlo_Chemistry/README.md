# Quantum Classical-Auxilary field Quantum Monte Carlo

This repository contains open-source code and tutorials for performing hybrid quantum-classical quantum Monte Carlo simulations for finding the ground state of the hydrogen molecule. This algorithm has the potential for realizing accuracy benefits over its purely classical counterpart when scaled up. In recent years, this algorithm has attracted attention from both academia and industry, and several variants have been proposed [1-5]. Broadly speaking, these variants differ in how the overlap amplitude $\langle\Psi_T|\phi\rangle$ is evaluated, where $|\Psi_T\rangle, |\phi\rangle$ represent the quantum trial state and classical walker state, respectively. Ref.[1] employs a Hadamard-test type circuits, namely vacuum reference circuits, to evaluate the overlap, and results in an iterative implementation of the algorithm. This approach has a relatively low scaling in both the quantum ($O(N^4)$) and classical resources ($O(N^3)$), but a rather large prefactor in the number of circuits to be executed and therefore less suitable for near-term quantum hardware. On the other hand, Ref.[2-4] employ shadow tomography and don't require iterative communication between the quantum and classical hardware. In addition, this approach exhibits an intrinsic noise robustness, meaning no error mitigation required for obtaining "good" results. This makes the second approach more suitable for near-term quantum hardware. We explore both approaches in this repo, allowing you to make a comparison and have a better understanding of the pros and cons of each method. And our implementation is primarily based on Ref.[1,4].

![workflow](images/workflow.png)

For the second approach, we employ the following code by Andrew Zhao: [fermionic-classical-shadows](https://github.com/zhao-andrew/symmetry-adjusted-classical-shadows) to construct the Matchgate circuits.

The notebooks are organized as follows:
1). Vacuum_reference.ipynb - This notebook contains a general introduction to QC-AFQMC, the motivation and how it compares to the classical AFQMC. For the quantum component, we explore the vacuum reference circuit approach to evaluate the overlap and local energy of walkers.
2). Matchgate_shadow.ipynb - This notebook investigates the shadow tomography approach to evaluate the overlap and local energy on classical computers.

If you have any questions, please do not hesitate to reach out.

[1] Xu, Xiaosi, and Ying Li. "Quantum-assisted Monte Carlo algorithms for fermions." [arXiv:2205.14903 (2022)](https://arxiv.org/abs/2205.14903).
[2] Huggins, William J., et al. "Unbiasing fermionic quantum Monte Carlo with a quantum computer." [Nature 603.7901 (2022): 416-420](https://www.nature.com/articles/s41586-021-04351-z).
[3] Wan, Kianna, et al. "Matchgate Shadows for Fermionic Quantum Simulation." [Communications in Mathematical Physics 404.2 (2023): 629-700](https://link.springer.com/article/10.1007/s00220-023-04844-0).
[4] Huang, Benchen, et al. "Evaluating a quantum classical quantum Monte Carlo algorithm with Matchgate shadows." [Physical Review Research 6.4 (2024): 043063](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.6.043063)
[5] Zhao, Luning, et al. "Quantum-Classical Auxiliary Field Quantum Monte Carlo with Matchgate Shadows on Trapped Ion Quantum Computers." [arXiv:2506.22408 (2025)](https://arxiv.org/abs/2506.22408)
