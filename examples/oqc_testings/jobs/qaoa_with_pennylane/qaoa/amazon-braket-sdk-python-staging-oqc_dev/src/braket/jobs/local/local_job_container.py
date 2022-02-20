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
# language governing permissions and limitations under the License.
import base64
import re
import subprocess
from logging import Logger, getLogger
from pathlib import Path
from typing import Dict, List

from braket.aws.aws_session import AwsSession


class _LocalJobContainer(object):
    """Uses docker CLI to run Braket Jobs on a local docker container."""

    ECR_URI_PATTERN = r"^((\d+)\.dkr\.ecr\.([^.]+)\.[^/]*)/([^:]*):(.*)$"
    CONTAINER_CODE_PATH = "/opt/ml/code/"

    def __init__(
        self, image_uri: str, aws_session: AwsSession = None, logger: Logger = getLogger(__name__)
    ):
        """Represents and provides functions for interacting with a Braket Jobs docker container.

        The function "end_session" must be called when the container is no longer needed.
        Args:
            image_uri (str): The URI of the container image to run.
            aws_session (AwsSession, Optional): AwsSession for connecting to AWS Services.
                Default: AwsSession()
            logger (Logger): Logger object with which to write logs.
                Default: `getLogger(__name__)`
        """
        self._aws_session = aws_session or AwsSession()
        self.image_uri = image_uri
        self.run_log = None
        self._container_name = None
        self._logger = logger

    def __enter__(self):
        """Creates and starts the local docker container."""
        self._container_name = self._start_container(self.image_uri)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stops and removes the local docker container."""
        self._end_session()

    @staticmethod
    def _envs_to_list(environment_variables: Dict[str, str]) -> List[str]:
        """Converts a dictionary environment variables to a list of parameters that can be
        passed to the container exec/run commands to ensure those env variables are available
        in the container.

        Args:
            environment_variables (Dict[str, str]): A dictionary of environment variables and
             their values.
        Returns:
            List[str]: The list of parameters to use when running a job that will include the
            provided environment variables as part of the runtime.
        """
        env_list = []
        for key in environment_variables:
            env_list.append("-e")
            env_list.append(f"{key}={environment_variables[key]}")
        return env_list

    @staticmethod
    def _check_output_formatted(command: List[str]) -> str:
        """This is a wrapper around the subprocess.check_output command that decodes the output
        to UTF-8 encoding.

        Args:
            command(List[str]): The command to run.

        Returns:
            (str): The UTF-8 encoded output of running the command.
        """
        output = subprocess.check_output(command)
        return output.decode("utf-8").strip()

    def _login_to_ecr(self, account_id: str, ecr_url: str) -> None:
        """Logs in docker to an ECR repository using the client AWS credentials.

        Args:
            account_id(str): The customer account ID.
            ecr_url(str): The URL of the ECR repo to log into.
        """
        ecr_client = self._aws_session.ecr_client
        authorization_data_result = ecr_client.get_authorization_token(registryIds=[account_id])
        if not authorization_data_result:
            raise ValueError(
                "Unable to get permissions to access to log in to docker. "
                "Please pull down the container before proceeding."
            )
        authorization_data = authorization_data_result["authorizationData"][0]
        raw_token = base64.b64decode(authorization_data["authorizationToken"])
        token = raw_token.decode("utf-8").strip("AWS:")
        subprocess.run(["docker", "login", "-u", "AWS", "-p", token, ecr_url])

    def _pull_image(self, image_uri: str) -> None:
        """Pulls an image from ECR.

        Args:
            image_uri(str): The URI of the ECR image to pull.
        """
        ecr_pattern = re.compile(self.ECR_URI_PATTERN)
        ecr_pattern_match = ecr_pattern.match(image_uri)
        if not ecr_pattern_match:
            raise ValueError(
                f"The URL {image_uri} is not available locally and does not seem to "
                f"be a valid AWS ECR URL."
                "Please pull down the container, or specify a valid ECR URL, "
                "before proceeding."
            )
        ecr_url = ecr_pattern_match.group(1)
        account_id = ecr_pattern_match.group(2)
        self._login_to_ecr(account_id, ecr_url)
        self._logger.warning("Pulling docker container image. This may take a while.")
        subprocess.run(["docker", "pull", image_uri])

    def _start_container(self, image_uri: str) -> str:
        """Runs a docker container in a busy loop so that it will accept further commands. The
        call to this function must be matched with end_session to stop the container.

        Args:
            image_uri(str): The URI of the ECR image to run.

        Returns:
            (str): The name of the running container, which can be used to execute further commands.
        """
        image_name = self._check_output_formatted(["docker", "images", "-q", image_uri])
        if not image_name:
            self._pull_image(image_uri)
            image_name = self._check_output_formatted(["docker", "images", "-q", image_uri])
            if not image_name:
                raise ValueError(
                    f"The URL {image_uri} is not available locally and can not be pulled from ECR."
                    " Please pull down the container before proceeding."
                )
        return self._check_output_formatted(
            ["docker", "run", "-d", "--rm", image_name, "tail", "-f", "/dev/null"]
        )

    def makedir(self, dir_path: str) -> None:
        """Creates a directory path in the container.

        Args:
            dir_path(str): The directory path to create.

        Raises:
            subprocess.CalledProcessError: If unable to make the directory.
        """
        try:
            subprocess.check_output(
                ["docker", "exec", self._container_name, "mkdir", "-p", dir_path]
            )
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8").strip()
            self._logger.error(output)
            raise e

    def copy_to(self, source: str, destination: str) -> None:
        """Copies a local file or directory to the container.

        Args:
            source(str): The local file or directory to copy.
            destination(str): The path to the file or directory where the source should be copied.

        Raises:
            subprocess.CalledProcessError: If unable to copy.
        """
        dirname = str(Path(destination).parent)
        try:
            subprocess.check_output(
                ["docker", "exec", self._container_name, "mkdir", "-p", dirname]
            )
            subprocess.check_output(
                ["docker", "cp", source, f"{self._container_name}:{destination}"]
            )
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8").strip()
            self._logger.error(output)
            raise e

    def copy_from(self, source: str, destination: str) -> None:
        """Copies a file or directory from the container locally.

        Args:
            source(str): The container file or directory to copy.
            destination(str): The path to the file or directory where the source should be copied.

        Raises:
            subprocess.CalledProcessError: If unable to copy.
        """
        try:
            subprocess.check_output(
                ["docker", "cp", f"{self._container_name}:{source}", destination]
            )
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8").strip()
            self._logger.error(output)
            raise e

    def run_local_job(self, environment_variables: Dict[str, str]) -> None:
        """Runs a Braket job in a local container.

        Args:
            environment_variables (Dict[str, str]): The environment variables to make available
             as part of running the job.
        """
        start_program_name = self._check_output_formatted(
            ["docker", "exec", self._container_name, "printenv", "SAGEMAKER_PROGRAM"]
        )
        if not start_program_name:
            raise ValueError(
                "Start program not found. "
                "The specified container is not setup to run Braket Jobs. "
                "Please see setup instructions for creating your own containers."
            )

        command = ["docker", "exec", "-w", self.CONTAINER_CODE_PATH]
        command.extend(self._envs_to_list(environment_variables))
        command.append(self._container_name)
        command.append("python")
        command.append(start_program_name)

        try:
            self.run_log = self._check_output_formatted(command)
            print(self.run_log)
        except subprocess.CalledProcessError as e:
            self.run_log = e.output.decode("utf-8").strip()
            self._logger.error(self.run_log)

    def _end_session(self):
        """Stops and removes the local container."""
        subprocess.run(["docker", "stop", self._container_name])
