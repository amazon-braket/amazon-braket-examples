# Braket Tutorials github
Private repository for Braket tutorials. 
In this repo we collect tutorials for Amazon Braket. 
The repo is structured as follows, with the following sub-folders:  
* [Circuit-simple] Simple circuits and algorithms
  * Anatomy
  * Bell
  * GHZ
  * Superdense Coding
* [Circuit-advanced] Advanced circuits and algorithms
  * Grover
  * QFT
  * QPE
  * QAE 
* [Circuit-hybrid] Hybrid quantum algorithms
  * QAOA
  * VQE Transverse Ising Model
  * VQE Chemistry
  * VQE Linear-Algebra
  * QGAN
* [Circuit-jobs] Managed jobs
  * QAOA 
  * PL hello-world hybrid
  * PL Chemistry
* [Annealing] Quantum annealing with D-Wave 
  * Anatomy of annealing with ocean 
  * Maximum Cut
  * Minimum Vertex
  * Graph partitioning

## Proposed Curriculum
* Beginner to Intermediate: If you are new to QC or just want to familiarize yourself with the Braket SDK with some simple examples, we recommned to start with the notebook on the paradigmatic _Bell_ circuit. Here you will earn how to construct a simple circuit and run this circuit against different backends on Amazon Braket by just changing one line of code. You may then move on to the _Anatomy_ notebook to dive deeper into the functionalities of the Braket SDK. From there you may dive into one of the canonical quantum algorithms such as _Quantum Phase Estimation_ or immediately jump into one the tutorals on hybrid quantum algorithms which combine parametrized quantum circuits with classical optimization loops. 
In short, one potential curriculum could look like: Bell ---> Anatomy ---> QPE ---> VQE or QAOA. 
* Quantum Annealing (QA): QA is a separate paradigm from universal, circuit-based QC. Amazon Braket offers native support for D-Wave's Ocean tool suite. To see this in practice, we recommend to start with the example on _Minimum Vertex_ or _Maximum Cut_ to solve combinatorial optimization problems using quantum annealing. 
