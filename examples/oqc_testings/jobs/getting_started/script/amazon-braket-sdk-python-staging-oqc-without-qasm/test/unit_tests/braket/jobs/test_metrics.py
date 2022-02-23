from unittest.mock import patch

import pytest

from braket.jobs.metrics import log_metric


@pytest.mark.parametrize(
    "test_value, test_timestamp, test_iteration, result_string",
    [
        # Happy case
        (0.1, 1, 2, "Metrics - timestamp=1; TestName=0.1; iteration_number=2;"),
        # We handle exponent values
        (3.14e-22, 1, 2, "Metrics - timestamp=1; TestName=3.14e-22; iteration_number=2;"),
        # When iteration number is not provided, we don't print it
        (5, 1, None, "Metrics - timestamp=1; TestName=5;"),
        # When iteration number is 0, we do print it
        (5, 1, 0, "Metrics - timestamp=1; TestName=5; iteration_number=0;"),
        # When timestamp is not provided, we use time.time()
        (-3.14, None, 2, "Metrics - timestamp=time_mocked; TestName=-3.14; iteration_number=2;"),
    ],
)
@patch("time.time")
@patch("builtins.print")
def test_log_metric(
    print_mock, time_mock, test_value, test_timestamp, test_iteration, result_string
):
    time_mock.return_value = "time_mocked"
    log_metric(
        metric_name="TestName",
        value=test_value,
        timestamp=test_timestamp,
        iteration_number=test_iteration,
    )
    print_mock.assert_called_with(result_string)
