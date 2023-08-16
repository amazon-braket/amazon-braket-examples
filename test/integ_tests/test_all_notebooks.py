import logging
import os
import pytest

from testbook import testbook
from nbconvert import HTMLExporter
from importlib.machinery import SourceFileLoader

# These notebooks have syntax or dependency issues that prevent them from being tested.
EXCLUDED_NOTEBOOKS = [
    # These notebooks have cells that have syntax errors
    "bring_your_own_container.ipynb",
    "qnspsa_with_embedded_simulator.ipynb",
    # These notebooks have dependency issues
    "VQE_chemistry_braket.ipynb",
    "6_Adjoint_gradient_computation.ipynb",
    # These notebooks are in flux
    "Using_The_Adjoint_Gradient_Result_Type.ipynb",
    "04_Maximum_Independent_Sets_with_Analog_Hamiltonian_Simulation.ipynb",
    "Error_Mitigation_on_Amazon_Braket.ipynb",
    # These notebooks are run from within a job (see Running_notebooks_as_jobs.ipynb)
    "0_Getting_started_papermill.ipynb"
]

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
        path_to_mocks = os.path.join(path_to_root, "test", "integ_tests", "default_mocks", "default_mocks.py")
    path_to_utils = os.path.join(path_to_root, "test", "integ_tests", "mock_utils.py")
    return path_to_utils, path_to_mocks


@pytest.mark.parametrize("notebook_dir, notebook_file", test_notebooks)
def test_all_notebooks(notebook_dir, notebook_file, mock_level):
    if notebook_file in EXCLUDED_NOTEBOOKS:
        pytest.skip(f"Skipping Notebook: '{notebook_file}'")

    os.chdir(root_path)
    os.chdir(notebook_dir)
    path_to_utils, path_to_mocks = get_mock_paths(notebook_dir, notebook_file)
    with testbook(notebook_file, timeout=600) as tb:
        tb.inject(
            f"""
            from importlib.machinery import SourceFileLoader
            mock_utils = SourceFileLoader("notebook_mock_utils","{path_to_utils}").load_module()
            mock_utils.set_level("{mock_level}")
            test_mocks = SourceFileLoader("notebook_mocks","{path_to_mocks}").load_module()
            test_mocks.pre_run_inject(mock_utils)
            """,
            run=False,
            before=0
        )
        tb.execute()
        test_mocks = SourceFileLoader("notebook_mocks", path_to_mocks).load_module()
        test_mocks.post_run(tb)


@pytest.mark.parametrize("notebook_dir, notebook_file", test_notebooks)
def test_notebook_to_html_conversion(notebook_dir, notebook_file, mock_level):
    os.chdir(root_path)
    os.chdir(notebook_dir)

    html_exporter = HTMLExporter(template_name='classic')

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
    with testbook(notebook_file, timeout=600) as tb:
        tb.inject(
            f"""
            from importlib.machinery import SourceFileLoader
            mock_utils = SourceFileLoader("notebook_mock_utils","{path_to_utils}").load_module()
            """,
            run=False,
            before=0
        )
        tb.execute()
