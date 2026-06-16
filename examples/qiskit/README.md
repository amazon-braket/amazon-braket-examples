# Qiskit-Braket Provider Examples

This directory contains notebooks demonstrating how to use the [Qiskit-Braket Provider](https://github.com/amazon-braket/qiskit-braket-provider) to run Qiskit circuits on Amazon Braket devices.

## Notebooks

| Notebook | Description |
|----------|-------------|
| [0_Getting_Started.ipynb](0_Getting_Started.ipynb) | Getting started with the Qiskit-Braket provider |
| [1_Compilation_with_the_Qiskit_Braket_provider.ipynb](1_Compilation_with_the_Qiskit_Braket_provider.ipynb) | Circuit compilation with the Qiskit-Braket provider |
| [2_Overview_of_the_Qiskit_Braket_provider.ipynb](2_Overview_of_the_Qiskit_Braket_provider.ipynb) | Overview of provider features: listing backends, running circuits, retrieving results |
| [3_Running_VQE_on_Braket.ipynb](3_Running_VQE_on_Braket.ipynb) | Running the Variational Quantum Eigensolver (VQE) on a Braket local backend |
| [4_Hybrid_Jobs_with_Qiskit.ipynb](4_Hybrid_Jobs_with_Qiskit.ipynb) | Running variational quantum algorithms with Amazon Braket Hybrid Jobs and Qiskit |
| [5_Minimum_Eigen_Optimizer.ipynb](5_Minimum_Eigen_Optimizer.ipynb) | Solving combinatorial optimization with the Minimum Eigen Optimizer |
| [6_Native_Programming.ipynb](6_Native_Programming.ipynb) | Native gate programming on QPU devices (Rigetti, IQM, IonQ) |
| [7_Transpilation.ipynb](7_Transpilation.ipynb) | Transpiling Qiskit circuits to Braket using pass managers |
| [8_Braket_Native_Primitives.ipynb](8_Braket_Native_Primitives.ipynb) | Using Braket-native Estimator and Sampler primitives |

## Local Testing

Run the Qiskit notebook integration tests with mocked AWS calls. See [TESTING.md](../../TESTING.md) for the full testing guide.

```bash
pytest test/integ_tests/test_all_notebooks.py -q -k "examples/qiskit"
```

## Additional Resources

For step-by-step guides, see the **[How-tos](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/index.html)** documentation:

- [How-to: Access devices on Amazon Braket](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/0_how_to_access_devices_on_amazon_braket.html)
- [How-to: Run circuits on Braket devices](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/1_how_to_run_circuits_on_braket_devices.html)
- [How-to: Retrieve results from a backend](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/2_how_to_retrieve_results_from_backend.html)
- [How-to: Hybrid Job on Qiskit](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/3_how_to_qiskit_hybrid_job.html)
- [How-to: Run verbatim circuits](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/4_how_to_verbatim_circuits.html)
- [How-to: Run circuits on the Braket local backend](https://qiskit-braket-provider.readthedocs.io/en/stable/how_tos/5_how_to_run_circuits_on_Braket_local_backend.html)

See the [Qiskit-Braket Provider documentation](https://qiskit-braket-provider.readthedocs.io/en/stable/) and [repository](https://github.com/amazon-braket/qiskit-braket-provider) for additional resources.
