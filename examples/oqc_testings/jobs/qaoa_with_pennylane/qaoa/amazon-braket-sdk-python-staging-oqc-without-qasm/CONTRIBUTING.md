# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional
documentation, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.


## Table of Contents

* [Report Bugs/Feature Requests](#report-bugsfeature-requests)
* [Contribute via Pull Requests (PRs)](#contribute-via-pull-requests-prs)
  * [Pull Down the Code](#pull-down-the-code)
  * [Run the Unit Tests](#run-the-unit-tests)
  * [Run the Integration Tests](#run-the-integration-tests)
  * [Make and Test Your Change](#make-and-test-your-change)
  * [Commit Your Change](#commit-your-change)
  * [Send a Pull Request](#send-a-pull-request)
* [Documentation Guidelines](#documentation-guidelines)
  * [API References (docstrings)](#api-references-docstrings)
  * [Build and Test Documentation](#build-and-test-documentation)
* [Find Contributions to Work On](#find-contributions-to-work-on)
* [Code of Conduct](#code-of-conduct)
* [Security Issue Notifications](#security-issue-notifications)
* [Licensing](#licensing)

## Report Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check [existing open](https://github.com/aws/amazon-braket-sdk-python/issues) and [recently closed](https://github.com/aws/amazon-braket-sdk-python/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aclosed%20) issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps.
* The version of our code being used.
* Any modifications you've made relevant to the bug.
* A description of your environment or deployment.


## Contribute via Pull Requests (PRs)

Contributions via pull requests are much appreciated.

Before sending us a pull request, please ensure that:

* You are working against the latest source on the *main* branch.
* You check the existing open and recently merged pull requests to make sure someone else hasn't already addressed the problem.
* You open an issue to discuss any significant work - we would hate for your time to be wasted.


### Pull Down the Code

1. If you do not already have one, create a GitHub account by following the prompts at [Join Github](https://github.com/join).
1. Create a fork of this repository on GitHub. You should end up with a fork at `https://github.com/<username>/amazon-braket-sdk-python`.
   1. Follow the instructions at [Fork a Repo](https://help.github.com/en/articles/fork-a-repo) to fork a GitHub repository.
1. Clone your fork of the repository: `git clone https://github.com/<username>/amazon-braket-sdk-python` where `<username>` is your github username.


### Run the Unit Tests

1. Install tox using `pip install tox`
1. Install coverage using `pip install '.[test]'`
1. cd into the amazon-braket-sdk-python folder: `cd amazon-braket-sdk-python` or `cd /environment/amazon-braket-sdk-python`
1. Run the following tox command and verify that all unit tests pass: `tox -e unit-tests`

You can also pass in various pytest arguments `tox -e unit-tests -- your-arguments` to run selected tests. For more information, please see [pytest usage](https://docs.pytest.org/en/stable/usage.html).


### Run the Integration Tests

Run the integration tests to make sure that the system as a whole still works.

1. Follow the instructions at [Set Up the AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html).
1. Set the `AWS_PROFILE` information
     ```bash
     export AWS_PROFILE=Your_Profile_Name
     ```
1. Run the following tox command and verify that integ tests pass: `tox -e integ-tests`

You can also pass in various pytest arguments `tox -e integ-tests -- your-arguments` to run selected tests. For more information, please see [pytest usage](https://docs.pytest.org/en/stable/usage.html).

### Make and Test Your Change

1. Create a new git branch:
     ```shell
     git checkout -b my-fix-branch main
     ```
1. Make your changes, **including unit tests** and, if appropriate, integration tests.
   1. Include unit tests when you contribute new features or make bug fixes, as they help to:
      1. Prove that your code works correctly.
      1. Guard against future breaking changes to lower the maintenance cost.
   1. Please focus on the specific change you are contributing. If you also reformat all the code, it will be hard for us to focus on your change.
1. Run `tox`, to run all the unit tests, linters, and documentation creation, and verify that all checks and tests pass.
1. If your changes include documentation changes, please see the [Documentation Guidelines](#documentation-guidelines).


### Commit Your Change

We use commit messages to update the project version number and generate changelog entries, so it's important for them to follow the right format. Valid commit messages include a prefix, separated from the rest of the message by a colon and a space. Here are a few examples:

```
feature: support new parameter for `xyz`
fix: fix flake8 errors
documentation: add documentation for `xyz`
```

Valid prefixes are listed in the table below.

| Prefix          | Use for...                                                                                     |
|----------------:|:-----------------------------------------------------------------------------------------------|
| `breaking`      | Incompatible API changes.                                                                      |
| `deprecation`   | Deprecating an existing API or feature, or removing something that was previously deprecated.  |
| `feature`       | Adding a new feature.                                                                          |
| `fix`           | Bug fixes.                                                                                     |
| `change`        | Any other code change.                                                                         |
| `documentation` | Documentation changes.                                                                         |

Some of the prefixes allow abbreviation ; `break`, `feat`, `depr`, and `doc` are all valid. If you omit a prefix, the commit will be treated as a `change`.

For the rest of the message, use imperative style and keep things concise but informative. See [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) for guidance.


### Send a Pull Request

GitHub provides additional documentation on [Creating a Pull Request](https://help.github.com/articles/creating-a-pull-request/).

Please remember to:
* Use commit messages (and PR titles) that follow the guidelines under [Commit Your Change](#commit-your-change).
* Send us a pull request, answering any default questions in the pull request interface.
* Pay attention to any automated CI failures reported in the pull request, and stay involved in the conversation.


## Documentation Guidelines

We use reStructuredText (RST) for most of our documentation. For a quick primer on the syntax,
see [the Sphinx documentation](https://www.sphinx-doc.org/en/main/usage/restructuredtext/basics.html).

In this repository, we the docstrings create the API reference found on readthedocs.

Here are some general guidelines to follow when writing either kind of documentation:
* Use present tense.
  * 👍 "The device has this property..."
  * 👎 "The device will have this property."
* When referring to an AWS product, use its full name in the first invocation.
  (This applies only to prose; use what makes sense when it comes to writing code, etc.)
  * 👍 "Amazon S3"
  * 👎 "s3"
* Provide links to other ReadTheDocs pages, AWS documentation, etc. when helpful.
  Try to not duplicate documentation when you can reference it instead.
  * Use meaningful text in a link.


### API References (docstrings)

The API references are generated from docstrings.
A docstring is the comment in the source code that describes a module, class, function, or variable.

```python
def foo():
    """This comment is a docstring for the function foo."""
```

We use [Google-style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
There should be a docstring for every public module, class, and function.
For functions, make sure your docstring covers all of the arguments, exceptions, and any other relevant information.
When possible, link to classes and functions, e.g. use ":class:~\`braket.aws.AwsSession\`" over just "AwsSession."

If a parameter of a function has a default value, please note what the default is.
If that default value is `None`, it can also be helpful to explain what happens when the parameter is `None`.
If `**kwargs` is part of the function signature, link to the parent class(es) or method(s) so that the reader knows where to find the available parameters.

For an example file with docstrings, see [the `circuit` module](https://github.com/aws/amazon-braket-sdk-python/blob/main/src/braket/circuits/circuit.py).


### Build and Test Documentation

To build the Sphinx docs, run the following command in the root repo directory:

```shell
tox -e docs
```

You can then find the generated HTML files in `build/documentation/html`.


## Find Contributions to Work On

Looking at the existing issues is a great way to find something to contribute on. As our projects, by default, use the default GitHub issue labels ((enhancement/bug/duplicate/help wanted/invalid/question/wontfix), looking at any ['help wanted'](https://github.com/aws/amazon-braket-sdk-python/labels/help%20wanted) issues is a great place to start.


## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.


## Security Issue Notifications

If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public github issue.


## Licensing

See the [LICENSE](https://github.com/aws/amazon-braket-sdk-python/blob/main/LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.
