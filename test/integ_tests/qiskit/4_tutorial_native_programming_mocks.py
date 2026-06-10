from importlib.machinery import SourceFileLoader
from pathlib import Path


helpers = SourceFileLoader(
    "qiskit_tutorial_mock_helpers",
    str(Path(__file__).with_name("_tutorial_mock_helpers.py")),
).load_module()


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    helpers.configure_qiskit_devices(mock_utils, mocker)


def post_run(tb):
    pass
