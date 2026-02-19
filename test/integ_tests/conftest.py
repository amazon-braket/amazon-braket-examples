import os

import pytest
from nbconvert import HTMLExporter

if "integ_tests" in os.getcwd():
    os.chdir(os.path.join("..", ".."))

root_path = os.getcwd()



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

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--test-mitiq"):
        skip_mitiq = pytest.mark.skip(reason="need --test-mitiq option to run")
        for item in items:
            if "mitiq" in item.keywords:
                item.add_marker(skip_mitiq)

@pytest.fixture
def mock_level(request):
    return request.config.getoption("--mock-level")

@pytest.fixture(autouse=True)
def restore_cwd():
    """ after each test, move back to root_path - amazon-braket-examples/"""
    yield
    os.chdir(root_path)
    
@pytest.fixture(scope="module")
def html_exporter():
    return HTMLExporter(template_name="classic")

