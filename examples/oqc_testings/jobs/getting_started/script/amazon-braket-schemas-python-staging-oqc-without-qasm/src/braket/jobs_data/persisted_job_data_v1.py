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
# language governing permissions and limitations under the License

from enum import Enum
from typing import Any, Dict, Union

from pydantic import Field

from braket.schema_common import BraketSchemaBase, BraketSchemaHeader


class PersistedJobDataFormat(str, Enum):
    """
    Enum class for the the required formats.
    """

    PLAINTEXT = "plaintext"
    # Pickle data format with protocol version 4 (Data is base64 encoded after pickling)
    PICKLED_V4 = "pickled_v4"


class PersistedJobData(BraketSchemaBase):
    """
    The schema used for persisting data during Amazon Braket job executions.

    Attributes:
        braketSchemaHeader (BraketSchemaHeader): Schema header. Users do not need
            to set this value.
        dataDictionary (Dict[str, Any]): Dict representing the data to be persisted.
        dataFormat (Union[PersistedJobDataFormat, str]): Data format used for persisting the
            values in `dataDictionary`.

    Examples:
        >>> data_to_persist = {"some_key": "some_value", "more_keys": True}
        >>> PersistedJobData(dataDictionary=data_to_persist,
        >>>                  dataFormat=PersistedJobDataFormat.PLAINTEXT)
    """

    _PERSISTED_JOB_DATA_HEADER = BraketSchemaHeader(
        name="braket.jobs_data.persisted_job_data", version="1"
    )

    braketSchemaHeader: BraketSchemaHeader = Field(
        default=_PERSISTED_JOB_DATA_HEADER, const=_PERSISTED_JOB_DATA_HEADER
    )
    dataDictionary: Dict[str, Any]
    dataFormat: Union[PersistedJobDataFormat, str]
