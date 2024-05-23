import logging
import os
import pytest

from testbook import testbook
from nbconvert import HTMLExporter
from importlib.machinery import SourceFileLoader
from jupyter_client import kernelspec

# These notebooks have syntax or dependency issues that prevent them from being tested.
EXCLUDED_NOTEBOOKS = [
    # These notebooks have cells that have syntax errors
    "bring_your_own_container.ipynb",
    "qnspsa_with_embedded_simulator.ipynb",
    # These notebooks have dependency issues
    "VQE_chemistry_braket.ipynb",
    "6_Adjoint_gradient_computation.ipynb",
    # These notebooks are run from within a job (see Running_notebooks_as_hybrid_jobs.ipynb)
    "0_Getting_started_papermill.ipynb",
    # Some AHS examples are running long especially on Mac. Removing while investigating
    "04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb",
    "05_Running_Analog_Hamiltonian_Simulation_with_local_simulator.ipynb",
]

if os.environ.get("AWS_DEFAULT_REGION") == "eu-north-1" or os.environ.get("AWS_REGION") == "eu-north-1":
    EXTRA_EXCLUDES = [
        "Quantum_machine_learning_in_Amazon_Braket_Hybrid_Jobs.ipynb",
        "Using_PennyLane_with_Braket_Hybrid_Jobs.ipynb",
        "Running_notebooks_as_hybrid_jobs.ipynb",
        "2_Graph_optimization_with_QAOA.ipynb",
        "Using_The_Adjoint_Gradient_Result_Type.ipynb",
        "0_Getting_Started.ipynb",
        "0_Creating_your_first_Hybrid_Job.ipynb",
    ]
    EXCLUDED_NOTEBOOKS.extend(EXTRA_EXCLUDES)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "integ_tests" in os.getcwd():
    os.chdir(os.path.join("..", ".."))

root_path = os.getcwd()
examples_path = "examples"
test_notebooks = []

for dir_, _, files in os.walk(examples_path):
    for file_name in files:
        if file_name.endswith(".ipynb") and ".ipynb_checkpoints" not in dir_:
            test_notebooks.append((dir_, file_name))


def get_mock_paths(notebook_dir, notebook_file):
    mock_file = notebook_file.replace(".ipynb", "_mocks.py")
    split_notebook_dir = notebook_dir.split(os.sep)
    path_to_root = os.path.join(*([".."] * len(split_notebook_dir)))
    mock_dir = os.path.join(*split_notebook_dir[1:])
    path_to_mocks = os.path.join(path_to_root, "test", "integ_tests", mock_dir, mock_file)
    if not os.path.exists(path_to_mocks):
        path_to_mocks = os.path.join(
            path_to_root, "test", "integ_tests", "default_mocks", "default_mocks.py"
        )
    path_to_utils = os.path.join(path_to_root, "test", "integ_tests", "mock_utils.py")
    return path_to_utils, path_to_mocks


@pytest.fixture(scope="module")
def html_exporter():
    return HTMLExporter(template_name="classic")


@pytest.mark.parametrize("notebook_dir, notebook_file", test_notebooks)
def test_all_notebooks(notebook_dir, notebook_file, mock_level):
    if notebook_file in EXCLUDED_NOTEBOOKS:
        pytest.skip(f"Skipping Notebook: '{notebook_file}'")

    os.chdir(root_path)
    os.chdir(notebook_dir)
    path_to_utils, path_to_mocks = get_mock_paths(notebook_dir, notebook_file)
    # Try to use the conda_braket kernel if installed, otherwise fall back to the default value of python3
    kernel = 'conda_braket' if 'conda_braket' in kernelspec.find_kernel_specs().keys() else 'python3'
    with testbook(notebook_file, timeout=600, kernel_name=kernel) as tb:
        # We check the existing notebook output for errors before we execute the
        # notebook because it will change after executing it.
        check_cells_for_error_output(tb.cells)
        execute_with_mocks(tb, mock_level, path_to_utils, path_to_mocks)
        # Check if there are any errors which didn't stop the testbook execution
        # This can happen in the presence of `%%time` magics.
        check_cells_for_error_output(tb.cells)


@pytest.mark.parametrize("notebook_dir, notebook_file", test_notebooks)
def test_notebook_to_html_conversion(notebook_dir, notebook_file, mock_level, html_exporter):
    os.chdir(root_path)
    os.chdir(notebook_dir)

    html_exporter.from_file(notebook_file)


def test_record():
    # Set the path here to record results.
    notebook_file_search = ""
    if not notebook_file_search:
        return
    for dir_, _, files in os.walk(examples_path):
        for file_name in files:
            if notebook_file_search in file_name:
                notebook_file = file_name
                notebook_dir = dir_
                break
    if not notebook_file or not notebook_dir:
        pytest.skip(f"Notebook not found: '{notebook_file_search}'")
    os.chdir(root_path)
    os.chdir(notebook_dir)
    path_to_utils, path_to_mocks = get_mock_paths(notebook_dir, notebook_file)
    path_to_utils = path_to_utils.replace("mock_utils.py", "record_utils.py")
    # Try to use the conda_braket kernel if installed, otherwise fall back to the default value of python3
    kernel = 'conda_braket' if 'conda_braket' in kernelspec.find_kernel_specs().keys() else 'python3'
    with testbook(notebook_file, timeout=600, kernel_name=kernel) as tb:
        tb.inject(
            f"""
            from importlib.machinery import SourceFileLoader
            mock_utils = SourceFileLoader("notebook_mock_utils","{path_to_utils}").load_module()
            """,
            run=False,
            before=0,
        )
        tb.execute()


def check_cells_for_error_output(cells):
    # We do this check to make sure someone didn't accidentally commit a version of a notebook
    # that has error output in it.
    for cell in cells:
        if "outputs" in cell:
            for output in cell["outputs"]:
                if output["output_type"] == "error":
                    pytest.fail("Found error output in cell: " + str(output))


def execute_with_mocks(tb, mock_level, path_to_utils, path_to_mocks):
    # We do this check to make sure that the notebook can be executed (with mocks).
    tb.inject(
        f"""
        from importlib.machinery import SourceFileLoader
        mock_utils = SourceFileLoader("notebook_mock_utils","{path_to_utils}").load_module()
        mock_utils.set_level("{mock_level}")
        test_mocks = SourceFileLoader("notebook_mocks","{path_to_mocks}").load_module()
        test_mocks.pre_run_inject(mock_utils)
        """,
        run=False,
        before=0,
    )
    tb.execute()
    test_mocks = SourceFileLoader("notebook_mocks", path_to_mocks).load_module()
    test_mocks.post_run(tb)
