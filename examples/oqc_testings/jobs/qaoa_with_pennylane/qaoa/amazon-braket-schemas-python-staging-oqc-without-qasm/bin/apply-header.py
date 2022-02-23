import os

"""
Run from the root of the git repository, will apply contents of header to the beginning of
all *.py files in the chosen directories. Script is idempotent, meaning it won't apply the
header to a file that already contains it.

Usage: python bin/apply-header.py
"""

HEADER = """# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
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

"""

ROOT_DIRS = ["src", "test", "."]


def main():
    for root_dir in ROOT_DIRS:
        for root, dirs, files in os.walk(root_dir):
            for py_file in python_files(files):
                idempotent_prepend(os.path.join(root, py_file), HEADER)

            # don't recurse "." directory, just look at local files
            if root_dir == ".":
                break


def python_files(files):
    return [file for file in files if file.endswith("py")]


def idempotent_prepend(filename: str, new_content: str) -> None:
    with open(filename, "r+") as file:
        existing_content = file.read()

        if existing_content.startswith(new_content):
            print(f"Skipping {filename}, already contains the content.")
        else:
            print(f"Applying content to {filename}...")
            file.seek(0, 0)
            file.write(new_content + existing_content)


if __name__ == "__main__":
    main()
