import glob
import os
import shutil

import pytest
from jupyter_client import kernelspec
from jupyter_client.manager import KernelManager
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
    parser.addoption(
        "--no-kernel-pool",
        action="store_true",
        default=False,
        help="Disable kernel pooling (use original per-test kernel startup)",
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
    yield
    os.chdir(root_path)
    _remove_test_artifacts()


@pytest.fixture(scope="module")
def html_exporter():
    return HTMLExporter(template_name="classic")


def _get_kernel_name():
    return "conda_braket" if "conda_braket" in kernelspec.find_kernel_specs() else "python3"


@pytest.fixture(scope="session")
def shared_kernel_manager():
    """Start a single kernel per session/xdist-worker, reused across all notebook tests."""
    km = KernelManager(kernel_name=_get_kernel_name())
    km.start_kernel(extra_arguments=["--Kernel.stop_on_error_timeout=0"])
    try:
        yield km
    finally:
        km.shutdown_kernel(now=True)
        km.cleanup_resources()


@pytest.fixture
def shared_km(request, shared_kernel_manager):
    """Yields the shared KernelManager and resets kernel state after each test."""
    if request.config.getoption("--no-kernel-pool"):
        yield None
        return

    yield shared_kernel_manager

    kc = shared_kernel_manager.client()
    kc.start_channels()
    try:
        kc.wait_for_ready(timeout=30)
        kc.execute("%reset -f\nimport gc; gc.collect()", reply=True, timeout=30)
    finally:
        kc.stop_channels()
