import json
import logging
import os
import pytest

from testbook import testbook
from importlib.machinery import SourceFileLoader

# These notebooks have syntax or dependency issues that prevent them from being tested.
EXCLUDED_NOTEBOOKS = [
    "4_Operating_Borealis_beginner_tutorial.ipynb",
    "bring_your_own_container.ipynb",
    "qnspsa_with_embedded_simulator.ipynb",
    "VQE_chemistry_braket.ipynb",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "integ_tests" in os.getcwd():
    os.chdir(os.path.join("..", ".."))

root_path = os.getcwd()
examples_path = "examples/"
test_notebooks = []

for dir_, _, files in os.walk(examples_path):
    for file_name in files:
        if file_name.endswith(".ipynb") and ".ipynb_checkpoints" not in dir_ and file_name not in EXCLUDED_NOTEBOOKS:
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
    os.chdir(root_path)
    os.chdir(notebook_dir)
    path_to_utils, path_to_mocks = get_mock_paths(notebook_dir, notebook_file)
    with testbook(notebook_file, timeout=300) as tb:
        tb.inject(
            f"""
            from importlib.machinery import SourceFileLoader
            mock_utils = SourceFileLoader("notebook_mock_utils","{path_to_utils}").load_module()
            mock_utils.set_level("{mock_level}")
            test_mocks = SourceFileLoader("notebook_mocks","{path_to_mocks}").load_module()
            test_mocks.pre_run(mock_utils)
            """,
            run=False,
            before=0
        )
        tb.execute()
        test_mocks = SourceFileLoader("notebook_mocks", path_to_mocks).load_module()
        test_mocks.post_run(tb)
