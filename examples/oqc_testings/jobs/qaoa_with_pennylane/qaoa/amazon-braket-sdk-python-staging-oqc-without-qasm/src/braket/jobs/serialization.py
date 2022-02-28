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

import codecs
import pickle
from typing import Any, Dict

from braket.jobs_data import PersistedJobDataFormat


def serialize_values(
    data_dictionary: Dict[str, Any], data_format: PersistedJobDataFormat
) -> Dict[str, Any]:
    """
    Serializes the `data_dictionary` values to the format specified by `data_format`.

    Args:
        data_dictionary (Dict[str, Any]): Dict whose values are to be serialized.
        data_format (PersistedJobDataFormat): The data format used to serialize the
            values. Note that for `PICKLED` data formats, the values are base64 encoded
            after serialization, so that they represent valid UTF-8 text and are compatible
            with `PersistedJobData.json()`.

    Returns:
        Dict[str, Any]: Dict with same keys as `data_dictionary` and values serialized to
        the specified `data_format`.
    """
    return (
        {
            k: codecs.encode(pickle.dumps(v, protocol=4), "base64").decode()
            for k, v in data_dictionary.items()
        }
        if data_format == PersistedJobDataFormat.PICKLED_V4
        else data_dictionary
    )


def deserialize_values(
    data_dictionary: Dict[str, Any], data_format: PersistedJobDataFormat
) -> Dict[str, Any]:
    """
    Deserializes the `data_dictionary` values from the format specified by `data_format`.

    Args:
        data_dictionary (Dict[str, Any]): Dict whose values are to be deserialized.
        data_format (PersistedJobDataFormat): The data format that the `data_dictionary` values
            are currently serialized with.

    Returns:
        Dict[str, Any]: Dict with same keys as `data_dictionary` and values deserialized from
        the specified `data_format` to plaintext.
    """
    return (
        {k: pickle.loads(codecs.decode(v.encode(), "base64")) for k, v in data_dictionary.items()}
        if data_format == PersistedJobDataFormat.PICKLED_V4
        else data_dictionary
    )
