import logging
import os
import pytest

from testbook import testbook
from importlib.machinery import SourceFileLoader


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "integ_tests" in os.getcwd():
    os.chdir(os.path.join("..", ".."))

test_path = "examples/"
test_notebooks = []

for dir_, _, files in os.walk(test_path):
    for file_name in files:
        rel_file = os.path.join(dir_, file_name)
        if file_name.endswith("copy.ipynb"):
            os.remove(rel_file)
        if file_name.endswith(".ipynb") and ".ipynb_checkpoints" not in dir_:
            test_notebooks.append((dir_, rel_file))


def get_mock_paths(notebook):
    mock_path = notebook.replace(".ipynb", "_mocks.py")
    split_mock_path = mock_path.split(os.sep)
    path_to_mocks = os.path.join(*split_mock_path[1:])
    path_to_mocks = os.path.join("test", "integ_tests", path_to_mocks)
    # assert os.path.exists(relative_mock_path), f"Test mocks not found. Please add '{relative_mock_path}'"
    if not os.path.exists(path_to_mocks):
        pytest.skip(f"Test mocks not found. Please add '{path_to_mocks}'")
    path_to_utils = os.path.join("test", "integ_tests", "mock_utils.py")
    return path_to_utils, path_to_mocks


@pytest.mark.parametrize("dir_path, notebook", test_notebooks)
def test_all_notebooks(dir_path, notebook, mock_level):
    path_to_utils, path_to_mocks = get_mock_paths(notebook)
    with testbook(notebook) as tb:
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
