# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from unittest.mock import Mock, call, patch

import pytest

from braket.jobs.metrics_data.cwl_metrics_fetcher import CwlMetricsFetcher


@pytest.fixture
def aws_session():
    _aws_session = Mock()
    return _aws_session


EXAMPLE_METRICS_LOG_LINES = [
    {
        "timestamp": "Test timestamp 0",
        "message": "Metrics - Test value 0",
    },
    {
        "timestamp": "Test timestamp 1",
        "message": "Metrics - Test value 1",
    },
    {
        "timestamp": "Test timestamp 2",
    },
    {
        "message": "Metrics - Test value 3",
    },
    {
        # This metrics fetcher will filter out log line that don't have a "Metrics -" tag.
        "message": "No prefix, Test value 4",
    },
]

EXPECTED_CALL_LIST = [
    call("Test timestamp 0", "Metrics - Test value 0"),
    call("Test timestamp 1", "Metrics - Test value 1"),
    call(None, "Metrics - Test value 3"),
]


@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.get_parsed_metrics")
@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.parse_log_message")
def test_get_all_metrics_complete_results(mock_add_metrics, mock_get_metrics, aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.describe_log_streams.return_value = {
        "logStreams": [{"logStreamName": "stream name"}, {}]
    }
    logs_client_mock.get_log_events.return_value = {
        "events": EXAMPLE_METRICS_LOG_LINES,
        "nextForwardToken": None,
    }
    expected_result = {"Test": [0]}
    mock_get_metrics.return_value = expected_result

    fetcher = CwlMetricsFetcher(aws_session)
    result = fetcher.get_metrics_for_job("test_job")
    assert mock_add_metrics.call_args_list == EXPECTED_CALL_LIST
    assert result == expected_result


@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.parse_log_message")
def test_get_log_streams_timeout(mock_add_metrics, aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.describe_log_streams.return_value = {
        "logStreams": [{"logStreamName": "stream name"}],
        "nextToken": "forever",
    }
    logs_client_mock.get_log_events.return_value = {
        "events": EXAMPLE_METRICS_LOG_LINES,
    }

    fetcher = CwlMetricsFetcher(aws_session, 0.1)
    result = fetcher.get_metrics_for_job("test_job")
    mock_add_metrics.assert_not_called()
    assert result == {}


@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.parse_log_message")
def test_get_no_streams_returned(mock_add_metrics, aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.describe_log_streams.return_value = {}

    fetcher = CwlMetricsFetcher(aws_session)
    result = fetcher.get_metrics_for_job("test_job")
    logs_client_mock.describe_log_streams.assert_called()
    mock_add_metrics.assert_not_called()
    assert result == {}


@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.get_parsed_metrics")
@patch("braket.jobs.metrics_data.cwl_metrics_fetcher.LogMetricsParser.parse_log_message")
def test_get_metrics_timeout(mock_add_metrics, mock_get_metrics, aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.describe_log_streams.return_value = {
        "logStreams": [{"logStreamName": "stream name"}]
    }
    logs_client_mock.get_log_events.side_effect = get_log_events_forever
    expected_result = {"Test": [0]}
    mock_get_metrics.return_value = expected_result

    fetcher = CwlMetricsFetcher(aws_session, 0.1)
    result = fetcher.get_metrics_for_job("test_job")
    logs_client_mock.get_log_events.assert_called()
    mock_add_metrics.assert_called()
    assert result == expected_result


def get_log_events_forever(*args, **kwargs):
    next_token = "1"
    token = kwargs.get("nextToken")
    if token and token == "1":
        next_token = "2"
    return {"events": EXAMPLE_METRICS_LOG_LINES, "nextForwardToken": next_token}
