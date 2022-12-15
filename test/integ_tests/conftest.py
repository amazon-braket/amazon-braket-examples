import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--mock-level', action='store', default='ALL', help='ALL=mock everything, LEAST=mock least possible'
    )


@pytest.fixture
def mock_level(request):
    return request.config.getoption('--mock-level')