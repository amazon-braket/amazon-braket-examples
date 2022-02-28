# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
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
from importlib import import_module

from pydantic import BaseModel, constr


class BraketSchemaHeader(BaseModel):
    """
    BraketSchemaHeader which dictates the schema and the version.

    Attributes:
        name (str): name of the schema
        version (str): version of the schema

    Examples:
        >>> BraketSchemaHeader(name="braket.task_result.annealing_task_result", version="1.0")
    """

    name: constr(min_length=1)
    version: constr(min_length=1, max_length=50)

    def get_module_name(self):
        return self.name + "_v" + self.version

    def get_package_name(self):
        return ".".join(self.name.split(".")[:-1])

    def import_schema_module(self):
        """
        Imports the module that holds the schema given by the header

        Returns:
            Module of the corresponding schema

        Raises:
            ModuleNotFoundError: If the schema module cannot be found according to
            schema header
        """
        module_name = self.get_module_name()
        package_name = self.get_package_name()
        try:
            return import_module(module_name, package=package_name)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Amazon Braket could not find the module, {module_name}. "
                "To continue, upgrade your installation of amazon-braket-schemas."
            )
