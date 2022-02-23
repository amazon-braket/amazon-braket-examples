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
from enum import Enum, unique


@unique
class MetricPeriod(Enum):
    """Period over which the cloudwatch metric is aggregated."""

    ONE_MINUTE: int = 60


@unique
class MetricStatistic(Enum):
    """Metric data aggregation to use over the specified period."""

    MIN: str = "Min"
    MAX: str = "Max"


@unique
class MetricType(Enum):
    """Metric type."""

    TIMESTAMP: str = "Timestamp"
    ITERATION_NUMBER: str = "IterationNumber"
