import glob
import os
import shutil

import pytest
from nbconvert import HTMLExporter

if "integ_tests" in os.getcwd():
    os.chdir(os.path.join("..", ".."))

root_path = os.getcwd()


def _remove_test_artifacts():
    test_artifact_globs = (
        os.path.join(root_path, "examples", "nvidia_cuda_q", "cuda-q-applications*"),
        os.path.join(root_path, "examples", "nvidia_cuda_q", "cuda-q-academic*"),
    )
    for pattern in test_artifact_globs:
        for path in glob.glob(pattern):
            shutil.rmtree(path, ignore_errors=True)


_remove_test_artifacts()


def pytest_addoption(parser):
    parser.addoption(
        "--mock-level",
        action="store",
        default="ALL",
        help="ALL=mock everything, LEAST=mock least possible",
    )
    parser.addoption(
        "--test-mitiq",
        action="store_true",
        default=False,
        help="specify to include execute tests requiring mitiq",
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "mitiq: tests only specific to mitiq-related notebooks")

# Known test durations (seconds) to ensure xdist schedules slow tests first.
# This prevents long-running tests from clustering on a single worker.
NOTEBOOK_DURATIONS = {
    "06_Analog_Hamiltonian_simulation_with_PennyLane.ipynb": 70,
    "Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb": 57,
    "QAOA_braket.ipynb": 32,
    "3_Hydrogen_Molecule_geometry_with_VQE.ipynb": 30,
    "Using_PennyLane_with_Braket_Hybrid_Jobs.ipynb": 28,
    "0_Creating_your_first_Hybrid_Job.ipynb": 28,
    "VQE_chemistry_braket.ipynb": 26,
    "2_Graph_optimization_with_QAOA.ipynb": 26,
    "01_Local_Emulation_for_Verbatim_Circuits_on_Amazon_Braket.ipynb": 24,
    "4_Simulation_of_noisy_quantum_circuits_on_Amazon_Braket_with_PennyLane.ipynb": 20,
    "0_Getting_Started.ipynb": 17,
    "VQE_Transverse_Ising_Model.ipynb": 17,
    "05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb": 16,
    "02_Expectation_value_calculations_with_program_sets.ipynb": 16,
    "Advanced_QPU_workflow.ipynb": 14,
    "1_Parallelized_optimization_of_quantum_circuits.ipynb": 14,
    "Running_notebooks_as_hybrid_jobs.ipynb": 14,
}


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--test-mitiq"):
        skip_mitiq = pytest.mark.skip(reason="need --test-mitiq option to run")
        for item in items:
            if "mitiq" in item.keywords:
                item.add_marker(skip_mitiq)

    # Sort by expected duration descending so xdist worksteal starts slow tests first
    def _get_duration(item):
        for name, duration in NOTEBOOK_DURATIONS.items():
            if name in item.nodeid:
                return duration
        return 0

    items.sort(key=_get_duration, reverse=True)

@pytest.fixture
def mock_level(request):
    return request.config.getoption("--mock-level")

@pytest.fixture(autouse=True)
def restore_cwd():
    """ after each test, move back to root_path - amazon-braket-examples/"""
    yield
    os.chdir(root_path)
    _remove_test_artifacts()
    
@pytest.fixture(scope="module")
def html_exporter():
    return HTMLExporter(template_name="classic")

