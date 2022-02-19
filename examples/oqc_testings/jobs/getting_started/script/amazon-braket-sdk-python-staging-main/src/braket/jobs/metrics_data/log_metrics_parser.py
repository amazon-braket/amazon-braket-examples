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

import re
from logging import Logger, getLogger
from typing import Dict, Iterator, List, Optional, Tuple, Union

from braket.jobs.metrics_data.definitions import MetricStatistic, MetricType


class LogMetricsParser(object):
    """
    This class is used to parse metrics from log lines, and return them in a more
    convenient format.
    """

    METRICS_DEFINITIONS = re.compile(r"(\w+)\s*=\s*([^;]+)\s*;")
    TIMESTAMP = "timestamp"
    ITERATION_NUMBER = "iteration_number"

    def __init__(
        self,
        logger: Logger = getLogger(__name__),
    ):
        self._logger = logger
        self.all_metrics = []

    @staticmethod
    def _get_value(
        current_value: Optional[Union[str, float, int]],
        new_value: Union[str, float, int],
        statistic: MetricStatistic,
    ) -> Union[str, float, int]:
        """
        Gets the value based on a statistic.

        Args:
            current_value (Optional[Union[str, float, int]]): The current value.

            new_value: (Union[str, float, int]) The new value.

            statistic (MetricStatistic): The statistic to determine which value to use.

        Returns:
            Union[str, float, int]: the value.
        """
        if current_value is None:
            return new_value
        if statistic == MetricStatistic.MAX:
            return max(current_value, new_value)
        return min(current_value, new_value)

    def _get_metrics_from_log_line_matches(
        self, all_matches: Iterator
    ) -> Dict[str, Union[str, float, int]]:
        """
        Converts matches from a RegEx to a set of metrics.

        Args:
            all_matches (Iterator): An iterator for RegEx matches on a log line.

        Returns:
            Dict[str, Union[str, float, int]]: The set of metrics found by the RegEx. The result
            is in the format {<metric name> : <value>}. This implies that multiple metrics
            with the same name are deduped to the last instance of that metric.
        """
        metrics = {}
        for match in all_matches:
            subgroup = match.groups()
            value = subgroup[1]
            try:
                metrics[subgroup[0]] = float(value)
            except ValueError:
                self._logger.warning(f"Unable to convert value {value} to a float.")
        return metrics

    def parse_log_message(self, timestamp: str, message: str) -> None:
        """
        Parses a line from logs, adding all the metrics that have been logged
        on that line. The timestamp is also added to match the corresponding values.

        Args:
            timestamp (str): A formatted string representing the timestamp for any found metrics.

            message (str): A log line from a log.
        """
        if not message:
            return
        all_matches = self.METRICS_DEFINITIONS.finditer(message)
        parsed_metrics = self._get_metrics_from_log_line_matches(all_matches)
        if not parsed_metrics:
            return
        if timestamp and self.TIMESTAMP not in parsed_metrics:
            parsed_metrics[self.TIMESTAMP] = timestamp
        self.all_metrics.append(parsed_metrics)

    def get_columns_and_pivot_indices(
        self, pivot: str
    ) -> Tuple[Dict[str, List[Union[str, float, int]]], Dict[int, int]]:
        """
        Parses the metrics to find all the metrics that have the pivot column. The values of
        the pivot column are assigned a row index, so that all metrics with the same pivot value
        are stored in the same row.
        Args:
            pivot (str): The name of the pivot column. Must be TIMESTAMP or ITERATION_NUMBER.

        Returns:
            Tuple[Dict[str, List[Any]], Dict[int, int]]:
                The Dict[str, List[Any]] the result table with all the metrics values initialized
                    to None
                The Dict[int, int] is the list of pivot indices, where the value of a pivot column
                    is mapped to a row index.
        """
        row_count = 0
        pivot_indices: dict[int, int] = {}
        table: dict[str, list[Optional[Union[str, float, int]]]] = {}
        for metric in self.all_metrics:
            if pivot in metric:
                if metric[pivot] not in pivot_indices:
                    pivot_indices[metric[pivot]] = row_count
                    row_count += 1
                for column_name in metric:
                    table[column_name] = [None]
        for column_name in table:
            table[column_name] = [None] * row_count
        return table, pivot_indices

    def get_metric_data_with_pivot(
        self, pivot: str, statistic: MetricStatistic
    ) -> Dict[str, List[Union[str, float, int]]]:
        """
        Gets the metric data for a given pivot column name. Metrics without the pivot column
        are not included in the results. Metrics that have the same value in the pivot column
        are returned in the same row. If the a metric has multiple values for the pivot value,
        the statistic is used to determine which value is returned.
        For example, for the metrics:
        "iteration_number" : 0, "metricA" : 2, "metricB" : 1,
        "iteration_number" : 0, "metricA" : 1,
        "no_pivot_column" : 0,  "metricA" : 0,
        "iteration_number" : 1, "metricA" : 2,

        The result with iteration_number as the pivot, statistic of MIN the result will be:
            iteration_number metricA metricB
            0                1       1
            1                2       None

        Args:
            pivot (str): The name of the pivot column. Must be TIMESTAMP or ITERATION_NUMBER.
            statistic (MetricStatistic): The statistic to determine which value to use.

        Returns:
            Dict[str, List[Union[str, float, int]]] : The metrics data.
        """
        table, pivot_indices = self.get_columns_and_pivot_indices(pivot)
        for metric in self.all_metrics:
            if pivot in metric:
                row = pivot_indices[metric[pivot]]
                for column_name in metric:
                    table[column_name][row] = self._get_value(
                        table[column_name][row], metric[column_name], statistic
                    )
        return table

    def get_parsed_metrics(
        self, metric_type: MetricType, statistic: MetricStatistic
    ) -> Dict[str, List[Union[str, float, int]]]:
        """
        Gets all the metrics data, where the keys are the column names and the values are a list
        containing the values in each row. For example, the table:
            timestamp energy
              0         0.1
              1         0.2
        would be represented as:
        { "timestamp" : [0, 1], "energy" : [0.1, 0.2] }
        values may be integers, floats, strings or None.

        Args:
            metric_type (MetricType): The type of metrics to get.

            statistic (MetricStatistic): The statistic to determine which metric value to use
             when there is a conflict.

        Returns:
            Dict[str, List[Union[str, float, int]]] : The metrics data.
        """
        if metric_type == MetricType.ITERATION_NUMBER:
            return self.get_metric_data_with_pivot(self.ITERATION_NUMBER, statistic)
        return self.get_metric_data_with_pivot(self.TIMESTAMP, statistic)
