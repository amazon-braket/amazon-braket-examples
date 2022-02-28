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

import pytest

from braket.jobs.metrics_data import LogMetricsParser
from braket.jobs.metrics_data.definitions import MetricStatistic, MetricType

MALFORMED_METRICS_LOG_LINES = [
    {"timestamp": "Test timestamp 0", "message": ""},
    {"timestamp": "Test timestamp 1", "message": "No semicolon metric0=2.0"},
    {"timestamp": "Test timestamp 2", "message": "metric0=not_a_number;"},
    {"timestamp": "Test timestamp 3", "message": "also not a number metric0=2 . 0;"},
    {"timestamp": "Test timestamp 3", "message": "metric0=;"},
    {"timestamp": "Test timestamp 3", "message": "metric0= ;"},
    {"timestamp": "Test timestamp 4"},
    {"unknown": "Unknown"},
]

SIMPLE_METRICS_LOG_LINES = [
    # This is a standard line of what our metrics may look like
    {
        "timestamp": "Test timestamp 0",
        "message": "Metrics - metric0=0.0; metric1=1.0; metric2=2.0 ;",
    },
    # This line overwrites the timestamp by having it output in the metrics.
    {
        "timestamp": "Test timestamp 1",
        "message": "Metrics - timestamp=1628019160; metric0=0.1; metric2= 2.1;",
    },
    # This line adds metric3 that won't have values for any other timestamp
    {
        "timestamp": "Test timestamp 2",
        "message": "Metrics - metric0=0.2; metric1=1.2; metric2= 2.2 ; metric3=0.2;",
    },
    # This line adds metrics expressed as exponents
    {
        "timestamp": "Test timestamp 3",
        "message": "Metrics - metric0=-0.4; metric1=3.14e-22; metric2=3.14E22;",
    },
]

SIMPLE_METRICS_RESULT = {
    "timestamp": [
        "Test timestamp 0",
        1628019160,
        "Test timestamp 2",
        "Test timestamp 3",
    ],
    "metric0": [0.0, 0.1, 0.2, -0.4],
    "metric1": [1.0, None, 1.2, 3.14e-22],
    "metric2": [2.0, 2.1, 2.2, 3.14e22],
    "metric3": [None, None, 0.2, None],
}

# This will test how metrics are combined when the multiple metrics have the same timestamp
SINGLE_TIMESTAMP_METRICS_LOG_LINES = [
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric0=0.0;"},
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric0=0.1; metric1=1.1;"},
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric0=0.2; metric2=2.8;"},
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric0=0.3; metric1=1.3;"},
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric1=1.4; metric2=2.4;"},
    {
        "timestamp": "Test timestamp 0",
        "message": "Metrics - metric0=0.5; metric1=1.5; metric2=2.5;",
    },
    {"timestamp": "Test timestamp 0", "message": "Metrics - metric1=0.6; metric0=0.6;"},
]


ITERATION_AND_TIMESTAMPS_LOG_LINES = [
    {"timestamp": "Test timestamp 0", "message": "Metrics - iteration_number=0; metric0=0.0;"},
    {
        "timestamp": "Test timestamp 1",
        "message": "Metrics - metric0=0.1; metric1=1.1; iteration_number=0;",
    },
    {"timestamp": "Test timestamp 2", "message": "Metrics - metric0=0.2; metric2=2.8;"},
    {"timestamp": "Test timestamp 3", "message": "Metrics - metric0=0.3; metric1=1.3;"},
    {
        "timestamp": "Test timestamp 4",
        "message": "Metrics - metric1=1.4; metric2=2.4; iteration_number=0;",
    },
    {
        "timestamp": "Test timestamp 5",
        "message": "Metrics - metric0=0.5; metric1=1.5; metric2=2.5;",
    },
    {
        "timestamp": "Test timestamp 6",
        "message": "Metrics - metric1=0.6; iteration_number=0; metric0=0.6;",
    },
]


SINGLE_TIMESTAMP_MAX_RESULTS = {
    "timestamp": ["Test timestamp 0"],
    "metric0": [0.6],
    "metric1": [1.5],
    "metric2": [2.8],
}

SINGLE_TIMESTAMP_MIN_RESULTS = {
    "timestamp": ["Test timestamp 0"],
    "metric0": [0.0],
    "metric1": [0.6],
    "metric2": [2.4],
}

ITERATION_NUMBER_MAX_RESULTS = {
    "iteration_number": [0],
    "timestamp": ["Test timestamp 6"],
    "metric0": [0.6],
    "metric1": [1.4],
    "metric2": [2.4],
}


@pytest.mark.parametrize(
    "log_events, metric_type, metric_stat, metrics_results",
    [
        ([], MetricType.TIMESTAMP, MetricStatistic.MAX, {}),
        (MALFORMED_METRICS_LOG_LINES, MetricType.TIMESTAMP, MetricStatistic.MAX, {}),
        (
            SIMPLE_METRICS_LOG_LINES,
            MetricType.TIMESTAMP,
            MetricStatistic.MAX,
            SIMPLE_METRICS_RESULT,
        ),
        (
            SINGLE_TIMESTAMP_METRICS_LOG_LINES,
            MetricType.TIMESTAMP,
            MetricStatistic.MAX,
            SINGLE_TIMESTAMP_MAX_RESULTS,
        ),
        (
            SINGLE_TIMESTAMP_METRICS_LOG_LINES,
            MetricType.TIMESTAMP,
            MetricStatistic.MIN,
            SINGLE_TIMESTAMP_MIN_RESULTS,
        ),
        (
            ITERATION_AND_TIMESTAMPS_LOG_LINES,
            MetricType.ITERATION_NUMBER,
            MetricStatistic.MAX,
            ITERATION_NUMBER_MAX_RESULTS,
        ),
        # TODO: https://app.asana.com/0/1199668788990775/1200502190825620
        #  We should also test some real-world data, once we have it.
    ],
)
def test_get_all_metrics_complete_results(log_events, metric_type, metric_stat, metrics_results):
    parser = LogMetricsParser()
    for log_event in log_events:
        parser.parse_log_message(log_event.get("timestamp"), log_event.get("message"))
    assert parser.get_parsed_metrics(metric_type, metric_stat) == metrics_results
