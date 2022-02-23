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

from braket.jobs.metrics_data import MetricsRetrievalError
from braket.jobs.metrics_data.cwl_insights_metrics_fetcher import CwlInsightsMetricsFetcher


@pytest.fixture
def aws_session():
    _aws_session = Mock()
    return _aws_session


EXAMPLE_METRICS_LOG_LINES = [
    [
        {"field": "@timestamp", "value": "Test timestamp 0"},
        {"field": "@message", "value": "Test value 0"},
    ],
    [
        {"field": "@timestamp", "value": "Test timestamp 1"},
        {"field": "@message", "value": "Test value 1"},
    ],
    [
        {"field": "@timestamp", "value": "Test timestamp 2"},
    ],
    [
        {"field": "@message", "value": "Test value 3"},
    ],
    [],
]

EXPECTED_CALL_LIST = [
    call("Test timestamp 0", "Test value 0"),
    call("Test timestamp 1", "Test value 1"),
    call(None, "Test value 3"),
]


@patch("braket.jobs.metrics_data.cwl_insights_metrics_fetcher.LogMetricsParser.get_parsed_metrics")
@patch("braket.jobs.metrics_data.cwl_insights_metrics_fetcher.LogMetricsParser.parse_log_message")
def test_get_all_metrics_complete_results(mock_add_metrics, mock_get_metrics, aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.start_query.return_value = {"queryId": "test"}
    logs_client_mock.get_query_results.return_value = {
        "status": "Complete",
        "results": EXAMPLE_METRICS_LOG_LINES,
    }
    expected_result = {"Test": [0]}
    mock_get_metrics.return_value = expected_result

    fetcher = CwlInsightsMetricsFetcher(aws_session)

    result = fetcher.get_metrics_for_job("test_job", job_start_time=1, job_end_time=2)
    logs_client_mock.get_query_results.assert_called_with(queryId="test")
    logs_client_mock.start_query.assert_called_with(
        logGroupName="/aws/braket/jobs",
        startTime=1,
        endTime=2,
        queryString="fields @timestamp, @message | filter @logStream like /^test_job\\//"
        " | filter @message like /^Metrics - /",
        limit=10000,
    )
    assert mock_add_metrics.call_args_list == EXPECTED_CALL_LIST
    assert result == expected_result


def test_get_all_metrics_timeout(aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.start_query.return_value = {"queryId": "test"}
    logs_client_mock.get_query_results.return_value = {"status": "Queued"}

    fetcher = CwlInsightsMetricsFetcher(aws_session, 0.1, 0.2)
    result = fetcher.get_metrics_for_job("test_job")
    logs_client_mock.get_query_results.assert_called()
    assert result == {}


@pytest.mark.xfail(raises=MetricsRetrievalError)
def test_get_all_metrics_failed(aws_session):
    logs_client_mock = Mock()
    aws_session.logs_client = logs_client_mock

    logs_client_mock.start_query.return_value = {"queryId": "test"}
    logs_client_mock.get_query_results.return_value = {"status": "Failed"}

    fetcher = CwlInsightsMetricsFetcher(aws_session)
    fetcher.get_metrics_for_job("test_job")
