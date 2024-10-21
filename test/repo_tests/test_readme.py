import os
import pathlib
import re

EXCLUDED_DIRS = [
    # These directories contain notebook files that should not be linked to in the README.
    ".ipynb_checkpoints",
    "7_Running_notebooks_as_hybrid_jobs/result",
    "7_Running_notebooks_as_hybrid_jobs/src",
]

LINK_EXAMPLES_REGEX = re.compile(r"\(\s*(examples.*\.ipynb)\s*\)")


def test_readme():
    root_path = pathlib.Path(__file__).parent.parent.parent.resolve()

    examples_path = os.path.join(root_path, "examples")

    root_path_len = len(str(root_path)) + len(os.pathsep)
    all_notebooks = set()
    for dir_, _, files in os.walk(examples_path):
        for file_name in files:
            if file_name.endswith(".ipynb"):
                is_excluded = [
                    excluded_dir for excluded_dir in EXCLUDED_DIRS if excluded_dir in dir_
                ]
                if not is_excluded:
                    all_notebooks.add(os.path.join(dir_[root_path_len:], file_name))

    with open((os.path.join(root_path, "README.md")), "r") as fh:
        readme_contents = fh.read()
        all_readme_links = set(re.findall(LINK_EXAMPLES_REGEX, readme_contents))

    missing_in_readme = all_notebooks - all_readme_links
    extra_in_readme = all_readme_links - all_notebooks
    assert (
        extra_in_readme == set()
    ), "There are some (dead) links in the README that do not link to a notebook: "
    assert (
        missing_in_readme == set()
    ), "There are some new notebooks that haven't been added to the README summary: "
